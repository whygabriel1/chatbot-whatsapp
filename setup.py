#!/usr/bin/env python3
"""
Script de configuración inicial para el Agente de IA de WhatsApp
"""

import os
import subprocess
import sys

def crear_entorno_virtual():
    """Crea un entorno virtual si no existe"""
    if not os.path.exists('venv'):
        print("🔧 Creando entorno virtual...")
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        print("✅ Entorno virtual creado")
    else:
        print("✅ Entorno virtual ya existe")

def instalar_dependencias():
    """Instala las dependencias del proyecto"""
    print("📦 Instalando dependencias...")
    
    # Determinar el comando pip según el SO
    if os.name == 'nt':  # Windows
        pip_cmd = os.path.join('venv', 'Scripts', 'pip')
    else:  # Linux/Mac
        pip_cmd = os.path.join('venv', 'bin', 'pip')
    
    subprocess.run([pip_cmd, 'install', '-r', 'requirements.txt'], check=True)
    print("✅ Dependencias instaladas")

def crear_archivo_env():
    """Crea el archivo .env si no existe"""
    if not os.path.exists('.env'):
        print("📝 Creando archivo .env...")
        with open('.env', 'w', encoding='utf-8') as f:
            f.write("""# Configuración de APIs
GEMINI_API_KEY=tu_clave_de_gemini_aqui
TWILIO_ACCOUNT_SID=tu_account_sid_de_twilio
TWILIO_AUTH_TOKEN=tu_auth_token_de_twilio
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Configuración de Redis (opcional para memoria)
REDIS_URL=redis://localhost:6379

# Configuración del servidor
FLASK_ENV=development
FLASK_DEBUG=True
""")
        print("✅ Archivo .env creado")
        print("⚠️  IMPORTANTE: Edita el archivo .env con tus credenciales reales")
    else:
        print("✅ Archivo .env ya existe")

def crear_inventario_ejemplo():
    """Crea el archivo Excel de inventario de ejemplo"""
    if not os.path.exists('inventario.xlsx'):
        print("📊 Creando inventario de ejemplo...")
        
        # Importar pandas después de la instalación
        try:
            import pandas as pd
        except ImportError:
            print("❌ Error: pandas no está instalado. Ejecutando instalación...")
            instalar_dependencias()
            import pandas as pd
        
        datos_inventario = {
            'ID': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'Producto': [
                'Laptop Dell XPS 13',
                'Mouse Logitech MX Master 3',
                'Teclado Mecánico Razer',
                'Monitor Samsung 27" 4K',
                'Auriculares Sony WH-1000XM4',
                'Webcam Logitech C920',
                'Tablet iPad Air',
                'Smartphone iPhone 14',
                'Cargador USB-C 65W',
                'Disco Duro SSD 1TB'
            ],
            'Categoria': [
                'Computadoras',
                'Periféricos',
                'Periféricos',
                'Monitores',
                'Audio',
                'Video',
                'Tablets',
                'Smartphones',
                'Accesorios',
                'Almacenamiento'
            ],
            'Precio': [1200, 99, 150, 350, 280, 80, 600, 800, 45, 120],
            'Stock': [5, 25, 15, 8, 12, 30, 6, 4, 50, 20],
            'Proveedor': [
                'Dell Technologies',
                'Logitech',
                'Razer',
                'Samsung',
                'Sony',
                'Logitech',
                'Apple',
                'Apple',
                'Anker',
                'Samsung'
            ],
            'Descripcion': [
                'Laptop ultradelgada con pantalla 13.3" y procesador Intel i7',
                'Mouse inalámbrico ergonómico con sensor de alta precisión',
                'Teclado gaming con switches mecánicos RGB',
                'Monitor 4K con tecnología HDR y 60Hz',
                'Auriculares inalámbricos con cancelación de ruido',
                'Webcam HD 1080p con micrófono integrado',
                'Tablet con chip M1 y pantalla Liquid Retina',
                'Smartphone con cámara de 48MP y iOS 16',
                'Cargador rápido compatible con múltiples dispositivos',
                'SSD NVMe con velocidad de lectura hasta 3500MB/s'
            ]
        }
        
        df = pd.DataFrame(datos_inventario)
        df.to_excel('inventario.xlsx', index=False)
        print("✅ Inventario de ejemplo creado")
    else:
        print("✅ Archivo inventario.xlsx ya existe")

def mostrar_instrucciones():
    """Muestra las instrucciones finales"""
    print("\n" + "="*60)
    print("🎉 ¡CONFIGURACIÓN COMPLETADA!")
    print("="*60)
    print("\n📋 PRÓXIMOS PASOS:")
    print("\n1. 🔑 Configurar APIs:")
    print("   • Edita el archivo .env con tus credenciales")
    print("   • Obtén tu API key de Gemini: https://aistudio.google.com/")
    print("   • Configura Twilio WhatsApp: https://console.twilio.com/")
    
    print("\n2. 🚀 Ejecutar el servidor:")
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
    else:  # Linux/Mac
        print("   source venv/bin/activate")
    print("   python app.py")
    
    print("\n3. 🌐 Exponer con ngrok:")
    print("   ngrok http 5000")
    print("   (Usa la URL HTTPS como webhook en Twilio)")
    
    print("\n4. 💬 Probar el chatbot:")
    print("   • Envía 'Hola' a tu número de WhatsApp")
    print("   • Prueba: '¿Cuántas laptops Dell hay en stock?'")
    print("   • Envía una imagen para análisis")
    
    print("\n📚 Documentación completa en README.md")
    print("🐛 Si tienes problemas, revisa los logs del servidor")
    print("\n¡Disfruta tu nuevo chatbot! 🤖✨")

def main():
    """Función principal de configuración"""
    print("🤖 Configurando Agente de IA para WhatsApp...")
    print("="*50)
    
    try:
        crear_entorno_virtual()
        instalar_dependencias()
        crear_archivo_env()
        crear_inventario_ejemplo()
        mostrar_instrucciones()
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error durante la instalación: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

