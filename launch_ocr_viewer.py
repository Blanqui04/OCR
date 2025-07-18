"""
Llançador de l'aplicació OCR Viewer
Aplicació d'escriptori professional per a Windows amb Google Cloud Document AI
"""

import sys
import os
import warnings

# Elimina les advertències de Google Cloud
warnings.filterwarnings("ignore", message="La vostra aplicació s'ha autenticat utilitzant credencials d'usuari final")

# Afegir el directori actual a la ruta de Python
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def check_dependencies():
    """Comprova si totes les dependències requerides estan disponibles"""
    missing_deps = []
    
    try:
        import tkinter
    except ImportError:
        missing_deps.append("tkinter")
        
    try:
        from PIL import Image
    except ImportError:
        missing_deps.append("Pillow")
        
    try:
        import fitz
    except ImportError:
        missing_deps.append("PyMuPDF")
        
    try:
        from google.cloud import documentai_v1
    except ImportError:
        missing_deps.append("google-cloud-documentai")
        
    return missing_deps

if __name__ == "__main__":
    print("🚀 Visor OCR Professional")
    print("=" * 50)
    print("📋 Funcionalitats:")
    print("   • Visualització de PDF amb zoom i navegació")
    print("   • Integració amb Google Cloud Document AI") 
    print("   • Visualització interactiva de blocs de text")
    print("   • Cerca i exportació de text")
    print("   • Interfície professional per a Windows")
    print("=" * 50)
    
    # Check dependencies
    print("🔍 Comprovant dependències...")
    missing = check_dependencies()
    
    if missing:
        print(f"❌ Dependències mancants: {', '.join(missing)}")
        print("\n📦 Si us plau, instal·leu els paquets que falten:")
        for dep in missing:
            print(f"   pip install {dep}")
        input("\nPrem Enter per sortir...")
        sys.exit(1)

    print("✅ Totes les dependències s'han trobat!")

    try:
        print("\n🎯 Obrint l'aplicació...")
        from ocr_viewer_app import main
        main()
        
    except ImportError as e:
        print(f"❌ Error en importar l'aplicació: {e}")
        print("\n🔧 Solució de problemes:")
        print("   • Assegureu-vos que tots els fitxers són al mateix directori")
        print("   • Comproveu els permisos dels fitxers")
        print("   • Verifiqueu l'entorn de Python")
        input("\nPrem Enter per sortir...")
        
    except KeyboardInterrupt:
        print("\n🛑 L'aplicació s'ha interromput per l'usuari")

    except Exception as e:
        print(f"❌ Error inesperat: {e}")
        print("\n📞 Si aquest problema persisteix, si us plau, comproveu:")
        print("   • L'autenticació de Google Cloud està funcionant")
        print("   • La connexió a Internet està disponible")
        print("   • No hi ha antivirus bloquejant l'aplicació")
        input("\nPrem Enter per sortir...")
