# 🤖 Personalización del Agente de IA

## 📋 **Configuración del Comportamiento**

El archivo `config_agente.py` te permite personalizar completamente el comportamiento de tu chatbot. Aquí te explico cómo modificar cada aspecto:

## 🔧 **System Prompt**

El `SYSTEM_PROMPT` define las reglas y límites del agente:

```python
SYSTEM_PROMPT = """
Eres un asistente de inventario especializado para WhatsApp...

REGLAS Y LÍMITES:
1. SOLO puedes responder preguntas relacionadas con el inventario
2. NO puedes realizar compras, ventas o transacciones
3. NO puedes acceder a información personal de usuarios
...
"""
```

### **Personalizar Reglas:**
- **Agregar reglas**: Añade nuevas líneas en la sección "REGLAS Y LÍMITES"
- **Modificar formato**: Cambia la sección "FORMATO DE RESPUESTAS"
- **Cambiar personalidad**: Modifica el tono y estilo del prompt

## ⚙️ **Configuración General**

```python
CONFIG_AGENTE = {
    "max_respuesta_caracteres": 500,  # Límite de caracteres
    "usar_emojis": True,              # Habilitar/deshabilitar emojis
    "formato_respuesta": "amigable",  # "amigable", "profesional", "técnico"
    "incluir_precios": True,          # Mostrar precios
    "incluir_stock": True,            # Mostrar stock
    "incluir_proveedores": True,      # Mostrar proveedores
    "saludo_personalizado": "¡Hola! 👋 Soy tu asistente...",
}
```

### **Opciones de Personalización:**

#### **Límite de Caracteres:**
```python
"max_respuesta_caracteres": 300,  # Respuestas más cortas
"max_respuesta_caracteres": 1000, # Respuestas más largas
```

#### **Formato de Respuesta:**
```python
"formato_respuesta": "amigable",    # Con emojis y tono casual
"formato_respuesta": "profesional", # Tono formal y directo
"formato_respuesta": "técnico",     # Información detallada
```

#### **Saludo Personalizado:**
```python
"saludo_personalizado": "¡Bienvenido! 🏪 Soy el asistente de la tienda TechStore. ¿En qué puedo ayudarte?",
```

## 🛡️ **Límites de Seguridad**

```python
LIMITES_SEGURIDAD = {
    "palabras_prohibidas": [
        "comprar", "vender", "transacción", "pago", "dinero"
    ],
    "temas_prohibidos": [
        "información personal", "datos bancarios", "contraseñas"
    ],
    "max_intentos_consulta": 3,
}
```

### **Agregar Palabras Prohibidas:**
```python
"palabras_prohibidas": [
    "comprar", "vender", "transacción", "pago", "dinero",
    "tarjeta", "contraseña", "usuario", "login", "acceso",
    "hackear", "virus", "malware"  # Nuevas palabras
],
```

### **Cambiar Límite de Intentos:**
```python
"max_intentos_consulta": 5,  # Permitir más consultas
```

## 💬 **Mensajes Personalizados**

```python
MENSAJES = {
    "sin_informacion": "❌ No hay información disponible...",
    "consulta_fuera_tema": "🤖 Solo puedo ayudarte con consultas...",
    "error_general": "❌ Lo siento, ocurrió un error...",
    "limite_excedido": "⚠️ Has alcanzado el límite...",
    "archivo_no_soportado": "❌ Tipo de archivo no soportado...",
}
```

### **Personalizar Mensajes:**
```python
"sin_informacion": "🔍 No encontré información sobre eso en nuestro inventario. ¿Podrías ser más específico?",
"consulta_fuera_tema": "🏪 Solo manejo consultas sobre productos. ¿Hay algo específico que te interese?",
```

## 🎯 **Ejemplos de Personalización**

### **Agente Más Formal:**
```python
SYSTEM_PROMPT = """
Eres un asistente profesional de inventario empresarial...

REGLAS Y LÍMITES:
1. Mantén un tono profesional y formal
2. Proporciona información precisa y detallada
3. Usa terminología técnica cuando sea apropiado
...
"""

CONFIG_AGENTE = {
    "formato_respuesta": "profesional",
    "usar_emojis": False,
    "saludo_personalizado": "Buenos días. Soy el asistente de inventario. ¿En qué puedo asistirle?",
}
```

### **Agente Más Casual:**
```python
SYSTEM_PROMPT = """
Eres un asistente amigable y divertido para consultas de inventario...

REGLAS Y LÍMITES:
1. Sé amigable y usa un tono casual
2. Usa emojis para hacer las respuestas más divertidas
3. Haz que la experiencia sea entretenida
...
"""

CONFIG_AGENTE = {
    "formato_respuesta": "amigable",
    "usar_emojis": True,
    "saludo_personalizado": "¡Hola! 😊 Soy tu asistente súper cool del inventario. ¿Qué necesitas saber?",
}
```

### **Agente Especializado en Ventas:**
```python
SYSTEM_PROMPT = """
Eres un asistente de ventas especializado en productos tecnológicos...

REGLAS Y LÍMITES:
1. Enfócate en las características y beneficios de los productos
2. Sugiere productos relacionados cuando sea apropiado
3. Destaca las ofertas y promociones
...
"""

CONFIG_AGENTE = {
    "incluir_precios": True,
    "incluir_stock": True,
    "saludo_personalizado": "¡Hola! 🛒 Soy tu asistente de ventas. ¿Qué producto te interesa?",
}
```

## 🔄 **Aplicar Cambios**

Después de modificar `config_agente.py`:

1. **Reinicia el servidor:**
   ```bash
   # Detener con Ctrl+C
   python app.py
   ```

2. **Verifica los cambios:**
   - Envía un mensaje de prueba
   - Verifica que el comportamiento sea el esperado

## 📝 **Consejos de Personalización**

### **Do's (Hacer):**
- ✅ Mantén las reglas claras y específicas
- ✅ Prueba diferentes configuraciones
- ✅ Usa un tono consistente
- ✅ Incluye información relevante para tu negocio

### **Don'ts (No hacer):**
- ❌ No hagas el prompt demasiado largo
- ❌ No contradigas las reglas de seguridad
- ❌ No uses un tono que no represente tu marca
- ❌ No olvides probar los cambios

## 🧪 **Testing**

Para probar tu configuración:

1. **Mensajes de prueba:**
   - "Hola" - Verifica el saludo
   - "¿Cuántos productos hay?" - Verifica consultas normales
   - "Quiero comprar algo" - Verifica límites de seguridad

2. **Archivos de prueba:**
   - Envía una imagen de un producto
   - Envía un audio con una consulta

3. **Límites de prueba:**
   - Intenta consultas fuera del tema
   - Verifica que se respeten los límites de caracteres

---

**¡Personaliza tu agente según las necesidades de tu negocio! 🚀**
