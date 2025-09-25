# 🚀 Instrucciones Rápidas - Chatbot WhatsApp

## ✅ **¡INSTALACIÓN COMPLETADA!**

Tu chatbot de IA para WhatsApp está listo y funcionando. El servidor está ejecutándose en `http://localhost:5000`.

## 🔑 **Configuración de APIs (OBLIGATORIO)**

### 1. Google Gemini API
1. Ve a: https://aistudio.google.com/
2. Haz clic en "Create API key"
3. Copia la clave generada
4. Edita el archivo `.env` y reemplaza `tu_clave_de_gemini_aqui` con tu clave real

### 2. Twilio WhatsApp
1. Ve a: https://console.twilio.com/
2. Crea una cuenta o inicia sesión
3. Activa WhatsApp Sandbox
4. Copia tu Account SID y Auth Token
5. Edita el archivo `.env` con tus credenciales de Twilio

## 🌐 **Exponer el Servidor (ngrok)**

```bash
# Instalar ngrok (si no lo tienes)
# Descarga desde: https://ngrok.com/download

# Exponer el puerto 5000
ngrok http 5000
```

**Copia la URL HTTPS** que aparece (ejemplo: `https://abc123.ngrok.io`)

## 📱 **Configurar Webhook en Twilio**

1. Ve a tu consola de Twilio
2. WhatsApp > Sandbox Settings
3. En "Webhook URL" pega: `https://tu-url-ngrok.ngrok.io/whatsapp`
4. Guarda los cambios

## 💬 **Probar el Chatbot**

1. Envía un mensaje a tu número de WhatsApp sandbox
2. Prueba estos comandos:
   - "Hola" - Saludo
   - "¿Cuántas laptops Dell hay en stock?" - Consulta inventario
   - Envía una imagen - Análisis multimodal

## 📊 **Inventario Disponible**

El sistema incluye un inventario de ejemplo con:
- 10 productos (laptops, mouses, teclados, etc.)
- Información de precios, stock, proveedores
- Descripciones detalladas

## 🛠️ **Comandos Útiles**

```bash
# Verificar que el servidor funciona
curl http://localhost:5000/health

# Ver logs del servidor
# (Los logs aparecen en la consola donde ejecutaste python app.py)

# Detener el servidor
# Ctrl+C en la consola del servidor
```

## 🐛 **Solución de Problemas**

### Error: "GEMINI_API_KEY no configurada"
- Verifica que el archivo `.env` existe
- Confirma que la variable está correctamente escrita

### Webhook no recibe mensajes
- Verifica que ngrok esté ejecutándose
- Confirma que la URL del webhook en Twilio sea correcta
- Revisa los logs del servidor Flask

### Error: "Archivo inventario.xlsx no encontrado"
- El archivo ya existe, pero si hay problemas, puedes recrearlo manualmente

## 📚 **Documentación Completa**

Para más detalles, consulta el archivo `README.md`

---

**¡Tu chatbot está listo para usar! 🤖✨**


