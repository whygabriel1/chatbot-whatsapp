import os
import json
import requests
import pandas as pd
from flask import Flask, request
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

# Fix: Usar gemini-pro para API gratuita

# Inicializar Flask
app = Flask(__name__)

# Configurar Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Cargar configuración del agente
SYSTEM_PROMPT = obtener_system_prompt()
CONFIG = obtener_configuracion()
LIMITES = obtener_limites()
MENSAJES = obtener_mensajes()

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
    model = genai.GenerativeModel('gemini-pro')
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
        model = genai.GenerativeModel('gemini-pro')
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
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.route("/", methods=['GET'])
def home():
    """Página de inicio"""
    return """
    <h1>🤖 Agente de IA para WhatsApp</h1>
    <p>Servidor funcionando correctamente.</p>
    <p>Webhook configurado en: /whatsapp</p>
    <p>Estado: <a href="/health">Verificar salud</a></p>
    """

if __name__ == '__main__':
    # Verificar configuración
    if not os.getenv('GEMINI_API_KEY'):
        logger.error("GEMINI_API_KEY no configurada")
        exit(1)
    
    if not os.getenv('TWILIO_ACCOUNT_SID'):
        logger.error("TWILIO_ACCOUNT_SID no configurada")
        exit(1)
    
    # Obtener puerto de Railway o usar 5000 por defecto
    port = int(os.getenv('PORT', 5000))
    
    logger.info("Iniciando servidor Flask...")
    app.run(debug=False, host='0.0.0.0', port=port)



