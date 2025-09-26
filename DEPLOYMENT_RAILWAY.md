# 🚀 Guía de Despliegue en Railway

## Problemas Identificados y Soluciones

### ❌ Error Principal: Modelo Gemini No Disponible
**Error:** `404 Publisher Model gemini-1.5-flash-002 was not found`

**Causa:** El modelo `gemini-1.5-flash-002` no está disponible o no tienes acceso a él.

**Solución Aplicada:**
- ✅ Cambiado a `gemini-1.5-flash-001` (modelo estable y disponible)
- ✅ Agregada verificación de disponibilidad del modelo
- ✅ Mejorado el manejo de errores de API

### ⚠️ Advertencia: Redis No Disponible
**Advertencia:** `Redis no disponible, usando memoria local`

**Impacto:** La aplicación funciona pero sin persistencia de sesiones.

**Solución:** La aplicación está configurada para funcionar sin Redis usando memoria local.

## Variables de Entorno Requeridas en Railway

Configura estas variables en tu proyecto de Railway:

```bash
# API de Google Gemini (OBLIGATORIA)
GEMINI_API_KEY=tu_api_key_aqui

# Twilio (OBLIGATORIAS)
TWILIO_ACCOUNT_SID=tu_account_sid
TWILIO_AUTH_TOKEN=tu_auth_token

# Redis (OPCIONAL - si no está configurado, usa memoria local)
REDIS_URL=redis://localhost:6379

# Puerto (Railway lo configura automáticamente)
PORT=8080
```

## Pasos para Desplegar

1. **Sube el código a Railway:**
   ```bash
   git add .
   git commit -m "Fix: Corregir modelo Gemini y mejorar manejo de errores"
   git push
   ```

2. **Configura las variables de entorno en Railway:**
   - Ve a tu proyecto en Railway
   - Ve a la pestaña "Variables"
   - Agrega las variables listadas arriba

3. **Verifica el despliegue:**
   - Visita `https://tu-app.railway.app/health`
   - Deberías ver: `{"status": "ok", "model_available": true}`

## Verificación de Funcionamiento

### Endpoint de Salud
```
GET https://tu-app.railway.app/health
```

Respuesta esperada:
```json
{
  "status": "ok",
  "timestamp": "2024-01-26T12:00:00",
  "gemini_model": "gemini-1.5-flash-001",
  "model_available": true
}
```

### Webhook de WhatsApp
```
POST https://tu-app.railway.app/whatsapp
```

## Solución de Problemas

### Si el modelo sigue fallando:
1. Verifica que `GEMINI_API_KEY` esté configurada correctamente
2. Asegúrate de que la API key tenga permisos para usar Gemini
3. Revisa los logs de Railway para errores específicos

### Si Redis no está disponible:
- Es normal y no afecta la funcionalidad básica
- La aplicación usará memoria local para las sesiones
- Para producción, considera configurar Redis

### Si el webhook no responde:
1. Verifica que la URL del webhook en Twilio sea correcta
2. Asegúrate de que `TWILIO_ACCOUNT_SID` y `TWILIO_AUTH_TOKEN` estén configurados
3. Revisa los logs de Railway para errores de Twilio

## Mejoras Implementadas

- ✅ Modelo Gemini corregido a versión estable
- ✅ Verificación automática de disponibilidad del modelo
- ✅ Mejor manejo de errores y logging
- ✅ Endpoint de salud mejorado
- ✅ Validación de variables de entorno
- ✅ Funcionamiento sin Redis (fallback a memoria local)

## Próximos Pasos

1. Despliega la versión corregida
2. Prueba el webhook con mensajes de WhatsApp
3. Monitorea los logs para confirmar que no hay más errores 404
4. Considera configurar Redis para mejor rendimiento en producción
