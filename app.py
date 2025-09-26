import os
import json
import requests
import pandas as pd
from flask import Flask, request, render_template, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import google.generativeai as genai
from dotenv import load_dotenv
import redis
from datetime import datetime
import logging
from config_agente import obtener_system_prompt, obtener_configuracion, obtener_limites, obtener_mensajes, validar_consulta

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fix: Usar gemini-1.5-flash (modelo disponible en API gratuita) - v3

# Inicializar Flask
app = Flask(__name__)

# Configurar Gemini
gemini_api_key = os.getenv('GEMINI_API_KEY')
if not gemini_api_key:
    logger.error("GEMINI_API_KEY no configurada en variables de entorno")
    raise ValueError("GEMINI_API_KEY es requerida")

genai.configure(api_key=gemini_api_key)
logger.info("Gemini API configurada correctamente")

# Verificar qué modelos están disponibles
def listar_modelos_disponibles():
    """Lista los modelos disponibles en la API de Gemini"""
    try:
        models = genai.list_models()
        available_models = []
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                available_models.append(model.name)
        logger.info(f"Modelos disponibles: {available_models}")
        return available_models
    except Exception as e:
        logger.error(f"Error listando modelos: {e}")
        return []

# Verificar que el modelo esté disponible
def verificar_modelo_disponible():
    """Verifica que el modelo de Gemini esté disponible"""
    try:
        # Primero listar modelos disponibles
        modelos_disponibles = listar_modelos_disponibles()
        
        # Intentar con diferentes modelos en orden de preferencia
        modelos_a_probar = [
            'gemini-1.5-flash',
            'gemini-1.5-flash-001', 
            'gemini-1.5-flash-002',
            'gemini-1.5-pro',
            'gemini-pro'
        ]
        
        for modelo in modelos_a_probar:
            try:
                model = genai.GenerativeModel(modelo)
                response = model.generate_content("Hola")
                logger.info(f"Modelo {modelo} verificado correctamente")
                return True, modelo
            except Exception as e:
                logger.warning(f"Modelo {modelo} no disponible: {e}")
                continue
        
        logger.error("Ningún modelo de Gemini está disponible")
        return False, None
        
    except Exception as e:
        logger.warning(f"Advertencia verificando modelo: {e}")
        logger.warning("La aplicación continuará, pero el modelo podría no estar disponible")
        return False, None

# Cargar configuración del agente
def cargar_configuracion_dinamica():
    """Carga configuración dinámica si existe, sino usa la por defecto"""
    try:
        if os.path.exists('config_dinamico.json'):
            with open('config_dinamico.json', 'r', encoding='utf-8') as f:
                config_dinamico = json.load(f)
            logger.info("Configuración dinámica cargada desde config_dinamico.json")
            return (
                config_dinamico.get("system_prompt", obtener_system_prompt()),
                config_dinamico.get("config_agente", obtener_configuracion()),
                config_dinamico.get("limites", obtener_limites()),
                config_dinamico.get("mensajes", obtener_mensajes())
            )
        else:
            logger.info("Usando configuración por defecto")
            return (
                obtener_system_prompt(),
                obtener_configuracion(),
                obtener_limites(),
                obtener_mensajes()
            )
    except Exception as e:
        logger.error(f"Error cargando configuración dinámica: {e}")
        logger.info("Usando configuración por defecto como fallback")
        return (
            obtener_system_prompt(),
            obtener_configuracion(),
            obtener_limites(),
            obtener_mensajes()
        )

SYSTEM_PROMPT, CONFIG, LIMITES, MENSAJES = cargar_configuracion_dinamica()

# Variable global para almacenar el modelo que funciona
MODELO_DISPONIBLE = None

def obtener_modelo_funcional():
    """Obtiene un modelo de Gemini que funcione"""
    global MODELO_DISPONIBLE
    
    if MODELO_DISPONIBLE:
        return MODELO_DISPONIBLE
    
    # Intentar con diferentes modelos en orden de preferencia
    # Basado en los modelos disponibles según el debug
    modelos_a_probar = [
        'gemini-1.5-flash-latest',
        'gemini-1.5-flash',
        'gemini-1.5-pro-latest',
        'gemini-1.5-pro',
        'gemini-2.0-flash',
        'gemini-2.0-flash-001',
        'gemini-2.5-flash',
        'gemini-pro-latest',
        'gemini-pro'
    ]
    
    for modelo in modelos_a_probar:
        try:
            logger.info(f"Probando modelo: {modelo}")
            model = genai.GenerativeModel(modelo)
            logger.info(f"Modelo {modelo} inicializado correctamente")
            
            # Hacer una prueba rápida
            response = model.generate_content("test")
            logger.info(f"Modelo {modelo} respondió correctamente: {response.text[:50]}...")
            
            MODELO_DISPONIBLE = modelo
            logger.info(f"Modelo funcional encontrado: {modelo}")
            return modelo
        except Exception as e:
            logger.error(f"Modelo {modelo} falló con error: {str(e)}")
            logger.error(f"Tipo de error: {type(e).__name__}")
            continue
    
    logger.error("Ningún modelo de Gemini está disponible")
    return None

# Configurar Twilio
twilio_client = Client(
    os.getenv('TWILIO_ACCOUNT_SID'),
    os.getenv('TWILIO_AUTH_TOKEN')
)

# Configurar Redis para memoria (opcional)
try:
    redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))
    redis_client.ping()
    logger.info("Redis conectado exitosamente")
except:
    redis_client = None
    logger.warning("Redis no disponible, usando memoria local")

# Cargar datos del Excel
def cargar_inventario():
    """Carga el archivo Excel de inventario"""
    try:
        df = pd.read_excel('inventario.xlsx')
        logger.info(f"Inventario cargado: {len(df)} productos")
        return df
    except FileNotFoundError:
        logger.error("Archivo inventario.xlsx no encontrado")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error cargando inventario: {e}")
        return pd.DataFrame()

# Función para obtener/crear sesión de chat
def obtener_sesion_chat(usuario_id):
    """Obtiene o crea una sesión de chat para el usuario"""
    if redis_client:
        # Intentar obtener sesión desde Redis
        sesion_data = redis_client.get(f"chat_session_{usuario_id}")
        if sesion_data:
            return json.loads(sesion_data)
    
    # Crear nueva sesión
    modelo_funcional = obtener_modelo_funcional()
    if not modelo_funcional:
        logger.error("No hay modelos disponibles para crear sesión de chat")
        return None
    
    model = genai.GenerativeModel(modelo_funcional)
    chat = model.start_chat(history=[])
    
    # Guardar en Redis si está disponible
    if redis_client:
        redis_client.setex(f"chat_session_{usuario_id}", 3600, json.dumps({
            'history': chat.history
        }))
    
    return chat

def guardar_sesion_chat(usuario_id, chat):
    """Guarda la sesión de chat en Redis"""
    if redis_client:
        redis_client.setex(f"chat_session_{usuario_id}", 3600, json.dumps({
            'history': chat.history
        }))

def consultar_excel(query_texto, df):
    """Consulta el Excel usando Gemini para interpretar la consulta"""
    if df.empty:
        return MENSAJES["error_general"]
    
    # Validar consulta de seguridad
    es_valida, mensaje_error = validar_consulta(query_texto)
    if not es_valida:
        return mensaje_error
    
    # Crear contexto para Gemini con system prompt
    contexto_excel = f"""
    {SYSTEM_PROMPT}
    
    DATOS DEL INVENTARIO:
    Columnas disponibles: {list(df.columns)}
    
    Inventario completo:
    {df.to_string()}
    
    CONSULTA DEL USUARIO: {query_texto}
    
    Responde siguiendo las reglas establecidas y usando solo la información del inventario.
    """
    
    try:
        modelo_funcional = obtener_modelo_funcional()
        if not modelo_funcional:
            logger.error("No hay modelos disponibles para consultar Excel")
            return MENSAJES["error_general"]
        
        model = genai.GenerativeModel(modelo_funcional)
        response = model.generate_content(contexto_excel)
        
        # Limitar longitud de respuesta
        respuesta = response.text
        if len(respuesta) > CONFIG["max_respuesta_caracteres"]:
            respuesta = respuesta[:CONFIG["max_respuesta_caracteres"]] + "..."
        
        return respuesta
    except Exception as e:
        logger.error(f"Error consultando Excel: {e}")
        return MENSAJES["error_general"]

def procesar_archivo_multimodal(url_archivo, tipo_archivo, usuario_id, df):
    """Procesa archivos de audio o imagen"""
    try:
        # Descargar archivo
        response = requests.get(url_archivo)
        if response.status_code != 200:
            return "Error al descargar el archivo."
        
        # Guardar temporalmente
        extension = 'jpg' if tipo_archivo == 'image' else 'wav'
        archivo_temp = f"temp_{usuario_id}.{extension}"
        
        with open(archivo_temp, 'wb') as f:
            f.write(response.content)
        
        # Subir a Gemini
        file_ref = genai.upload_file(archivo_temp)
        
        # Crear prompt contextualizado con system prompt
        prompt = f"""
        {SYSTEM_PROMPT}
        
        DATOS DEL INVENTARIO:
        {df.to_string() if not df.empty else "No hay datos de inventario"}
        
        TAREA: Analiza este {tipo_archivo} y busca información relacionada en el inventario.
        
        Responde siguiendo las reglas establecidas y usando solo la información del inventario.
        """
        
        # Obtener sesión de chat
        chat = obtener_sesion_chat(usuario_id)
        
        # Enviar mensaje con archivo
        response = chat.send_message([prompt, file_ref])
        
        # Guardar sesión
        guardar_sesion_chat(usuario_id, chat)
        
        # Limpiar archivo temporal
        os.remove(archivo_temp)
        
        return response.text
        
    except Exception as e:
        logger.error(f"Error procesando archivo multimodal: {e}")
        return "Error al procesar el archivo. Intenta de nuevo."

@app.route("/whatsapp", methods=['POST'])
def whatsapp_webhook():
    """Webhook principal para recibir mensajes de WhatsApp"""
    try:
        # Obtener datos del mensaje
        incoming_msg = request.values.get('Body', '')
        from_number = request.values.get('From', '')
        media_url = request.values.get('MediaUrl0', '')
        media_content_type = request.values.get('MediaContentType0', '')
        
        logger.info(f"Mensaje recibido de {from_number}: {incoming_msg}")
        
        # Cargar inventario
        df = cargar_inventario()
        
        # Determinar tipo de mensaje
        if media_url:
            # Mensaje con archivo (imagen o audio)
            if 'image' in media_content_type:
                respuesta = procesar_archivo_multimodal(media_url, 'image', from_number, df)
            elif 'audio' in media_content_type:
                respuesta = procesar_archivo_multimodal(media_url, 'audio', from_number, df)
            else:
                respuesta = MENSAJES["archivo_no_soportado"]
        else:
            # Mensaje de texto
            if incoming_msg.lower() in ['hola', 'hi', 'hello', 'buenos días']:
                respuesta = CONFIG["saludo_personalizado"]
            else:
                # Consultar inventario con Gemini
                respuesta = consultar_excel(incoming_msg, df)
        
        # Crear respuesta TwiML
        resp = MessagingResponse()
        resp.message(respuesta)
        
        return str(resp)
        
    except Exception as e:
        logger.error(f"Error en webhook: {e}")
        resp = MessagingResponse()
        resp.message("Lo siento, ocurrió un error. Intenta de nuevo.")
        return str(resp)

@app.route("/health", methods=['GET'])
def health_check():
    """Endpoint de salud para verificar que el servidor funciona"""
    modelo_funcional = obtener_modelo_funcional()
    return {
        "status": "ok" if modelo_funcional else "error",
        "timestamp": datetime.now().isoformat(),
        "gemini_model": modelo_funcional or "none",
        "model_available": bool(modelo_funcional),
        "available_models": listar_modelos_disponibles()
    }

@app.route("/debug", methods=['GET'])
def debug_api():
    """Endpoint de debug para probar la API de Gemini"""
    try:
        # Probar la API key
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return {"error": "GEMINI_API_KEY no configurada"}
        
        # Listar modelos
        models = genai.list_models()
        available_models = []
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                available_models.append({
                    "name": model.name,
                    "display_name": model.display_name,
                    "supported_methods": list(model.supported_generation_methods)
                })
        
        # Probar un modelo simple
        test_result = None
        modelos_debug = ['gemini-1.5-flash-latest', 'gemini-1.5-flash', 'gemini-2.0-flash']
        
        for modelo_debug in modelos_debug:
            try:
                model = genai.GenerativeModel(modelo_debug)
                response = model.generate_content("Hola, ¿funcionas?")
                test_result = {
                    "success": True,
                    "response": response.text[:100],
                    "model_used": modelo_debug
                }
                break  # Si funciona, salir del bucle
            except Exception as e:
                test_result = {
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "model_tested": modelo_debug
                }
                continue
        
        return {
            "api_key_configured": bool(api_key),
            "api_key_length": len(api_key) if api_key else 0,
            "available_models": available_models,
            "test_result": test_result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": str(e), "timestamp": datetime.now().isoformat()}

@app.route("/", methods=['GET'])
def home():
    """Página de inicio"""
    return render_template('index.html')

@app.route("/config", methods=['GET'])
def config_page():
    """Página de configuración del agente"""
    return render_template('config.html')

@app.route("/api/config", methods=['GET'])
def get_config():
    """Obtener configuración actual del agente"""
    try:
        config = {
            "system_prompt": SYSTEM_PROMPT,
            "config_agente": CONFIG,
            "limites": LIMITES,
            "mensajes": MENSAJES
        }
        return jsonify({"success": True, "config": config})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/config", methods=['POST'])
def save_config():
    """Guardar nueva configuración del agente"""
    try:
        data = request.get_json()
        
        # Validar datos
        if not data:
            return jsonify({"success": False, "error": "No se recibieron datos"})
        
        # Guardar en archivo de configuración
        config_data = {
            "system_prompt": data.get("system_prompt", SYSTEM_PROMPT),
            "config_agente": data.get("config_agente", CONFIG),
            "limites": data.get("limites", LIMITES),
            "mensajes": data.get("mensajes", MENSAJES)
        }
        
        # Guardar en archivo JSON
        with open('config_dinamico.json', 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        
        # Recargar configuración en memoria
        global SYSTEM_PROMPT, CONFIG, LIMITES, MENSAJES
        SYSTEM_PROMPT = config_data["system_prompt"]
        CONFIG = config_data["config_agente"]
        LIMITES = config_data["limites"]
        MENSAJES = config_data["mensajes"]
        
        return jsonify({"success": True, "message": "Configuración guardada exitosamente"})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/api/config/reset", methods=['POST'])
def reset_config():
    """Restablecer configuración a valores por defecto"""
    try:
        # Recargar configuración desde archivos originales
        global SYSTEM_PROMPT, CONFIG, LIMITES, MENSAJES
        SYSTEM_PROMPT = obtener_system_prompt()
        CONFIG = obtener_configuracion()
        LIMITES = obtener_limites()
        MENSAJES = obtener_mensajes()
        
        # Eliminar archivo de configuración dinámica si existe
        if os.path.exists('config_dinamico.json'):
            os.remove('config_dinamico.json')
        
        return jsonify({"success": True, "message": "Configuración restablecida a valores por defecto"})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    # Verificar configuración
    if not os.getenv('GEMINI_API_KEY'):
        logger.error("GEMINI_API_KEY no configurada")
        exit(1)
    
    if not os.getenv('TWILIO_ACCOUNT_SID'):
        logger.error("TWILIO_ACCOUNT_SID no configurada")
        exit(1)
    
    # Verificar que el modelo esté disponible (no crítico para el inicio)
    modelo_disponible, modelo_usado = verificar_modelo_disponible()
    if not modelo_disponible:
        logger.warning("El modelo de Gemini no está disponible al inicio, pero la aplicación continuará")
        logger.warning("Se intentará encontrar un modelo funcional cuando se reciba el primer mensaje")
    else:
        logger.info(f"Modelo verificado al inicio: {modelo_usado}")
    
    # Obtener puerto de Railway o usar 5000 por defecto
    port = int(os.getenv('PORT', 5000))
    
    logger.info("Iniciando servidor Flask...")
    app.run(debug=False, host='0.0.0.0', port=port)



