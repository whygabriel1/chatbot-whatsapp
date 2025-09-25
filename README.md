# 🤖 Agente de IA Multimodal para WhatsApp

Un chatbot inteligente para WhatsApp que puede consultar inventarios desde archivos Excel y procesar mensajes de texto, audio e imágenes usando Google Gemini AI.

## ✨ Características

- 📱 **Integración con WhatsApp** via Twilio
- 🧠 **IA Multimodal** con Google Gemini 1.5 Flash
- 📊 **Consulta de Excel** con Pandas para inventarios
- 🎤 **Procesamiento de Audio** y 🖼️ **Imágenes**
- 💾 **Memoria Conversacional** con Redis
- 🔄 **Webhook en Tiempo Real**

## 🚀 Instalación Rápida

### 1. Clonar y Configurar

```bash
# Clonar el repositorio
git clone <tu-repositorio>
cd Chatbot

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

```bash
# Copiar plantilla
copy .env.template .env

# Editar .env con tus credenciales
```

**Variables requeridas en `.env`:**
```env
GEMINI_API_KEY=tu_clave_de_gemini_aqui
TWILIO_ACCOUNT_SID=tu_account_sid_de_twilio
TWILIO_AUTH_TOKEN=tu_auth_token_de_twilio
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

### 3. Crear Inventario de Ejemplo

```bash
python crear_inventario_ejemplo.py
```

### 4. Ejecutar el Servidor

```bash
python app.py
```

El servidor estará disponible en `http://localhost:5000`

## 🔧 Configuración de APIs

### Google Gemini API

1. Ve a [Google AI Studio](https://aistudio.google.com/)
2. Haz clic en "Create API key"
3. Copia la clave y agrégala a tu `.env`

**Límites gratuitos:**
- 1,500-2,000 peticiones/día
- 60 peticiones/minuto
- 1M tokens de contexto

### Twilio WhatsApp

1. Crea cuenta en [Twilio](https://www.twilio.com/)
2. Activa WhatsApp Sandbox
3. Obtén Account SID y Auth Token
4. Configura el número de WhatsApp

## 📱 Configuración de Webhook

### Para Desarrollo Local (ngrok)

```bash
# Instalar ngrok
npm install -g ngrok

# Exponer puerto local
ngrok http 5000

# Usar la URL HTTPS generada como webhook en Twilio
# Ejemplo: https://abc123.ngrok.io/whatsapp
```

### Para Producción

Configura tu servidor en la nube (Heroku, AWS, etc.) y usa la URL de tu dominio.

## 💬 Uso del Chatbot

### Comandos de Texto

- **Saludo**: "Hola", "Buenos días"
- **Consultas de inventario**: 
  - "¿Cuántas laptops Dell hay en stock?"
  - "Muéstrame todos los productos de Apple"
  - "¿Cuál es el precio del mouse Logitech?"
  - "Productos con stock menor a 10"

### Archivos Multimodales

- **Imágenes**: Envía fotos de productos para análisis
- **Audio**: Envía mensajes de voz con consultas

## 📊 Estructura del Inventario Excel

El archivo `inventario.xlsx` debe contener estas columnas:

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| ID | Identificador único | 1, 2, 3... |
| Producto | Nombre del producto | "Laptop Dell XPS 13" |
| Categoria | Categoría del producto | "Computadoras" |
| Precio | Precio en USD | 1200 |
| Stock | Cantidad disponible | 5 |
| Proveedor | Nombre del proveedor | "Dell Technologies" |
| Descripcion | Descripción detallada | "Laptop ultradelgada..." |

## 🛠️ Personalización

### Agregar Nuevas Funcionalidades

1. **Nuevos comandos**: Modifica `app.py` en la función `whatsapp_webhook()`
2. **Más tipos de archivo**: Extiende `procesar_archivo_multimodal()`
3. **Integración con BD**: Reemplaza Pandas con SQLAlchemy

### Ejemplo de Comando Personalizado

```python
# En whatsapp_webhook()
if incoming_msg.lower() == 'estadisticas':
    total_productos = len(df)
    stock_bajo = len(df[df['Stock'] < 10])
    respuesta = f"📊 Estadísticas del inventario:\n• Total productos: {total_productos}\n• Stock bajo: {stock_bajo}"
```

## 🔍 Endpoints Disponibles

- `GET /` - Página de inicio
- `GET /health` - Verificación de salud
- `POST /whatsapp` - Webhook de WhatsApp

## 🐛 Solución de Problemas

### Error: "GEMINI_API_KEY no configurada"
- Verifica que el archivo `.env` existe
- Confirma que la variable está correctamente escrita

### Error: "Redis no disponible"
- Es opcional, el sistema funciona sin Redis
- Para habilitar: instala Redis y configura `REDIS_URL`

### Error: "Archivo inventario.xlsx no encontrado"
- Ejecuta `python crear_inventario_ejemplo.py`
- O crea tu propio archivo Excel con las columnas requeridas

### Webhook no recibe mensajes
- Verifica que ngrok esté ejecutándose
- Confirma que la URL del webhook en Twilio sea correcta
- Revisa los logs del servidor Flask

## 📈 Monitoreo y Logs

El sistema incluye logging detallado:

```python
# Ver logs en tiempo real
tail -f app.log

# O en la consola de Flask
```

## 🔒 Seguridad

- ✅ Variables de entorno para credenciales
- ✅ Validación de entrada
- ✅ Manejo de errores
- ✅ Logs de auditoría

## 📝 Licencia

MIT License - Libre para uso personal y comercial.

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📞 Soporte

Si tienes problemas:

1. Revisa la sección de solución de problemas
2. Verifica los logs del servidor
3. Abre un issue en GitHub

---

**¡Disfruta tu nuevo chatbot de WhatsApp! 🚀**



