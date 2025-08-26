"""
Configuración para camelot-py con Ghostscript
Este archivo configura el entorno para que camelot-py pueda usar Ghostscript
"""

import os
import sys

def setup_ghostscript():
    """
    Configura el PATH para que camelot pueda encontrar Ghostscript
    """
    # Rutas comunes donde puede estar instalado Ghostscript en Windows
    possible_gs_paths = [
        r"C:\Program Files\PDF24\gs\bin",
        r"C:\Program Files\QGIS 3.38.0\apps\gs\bin",
        r"C:\Program Files\gs\bin",
        r"C:\Program Files (x86)\gs\bin",
        r"C:\Program Files\Ghostgum\gsview",
    ]
    
    # Buscar la instalación de Ghostscript
    gs_path = None
    for path in possible_gs_paths:
        if os.path.exists(path):
            # Verificar si existe algún ejecutable de Ghostscript
            for exe in ['gswin64c.exe', 'gswin32c.exe', 'gs.exe']:
                if os.path.exists(os.path.join(path, exe)):
                    gs_path = path
                    break
            if gs_path:
                break
    
    if gs_path:
        # Añadir al PATH si no está ya
        current_path = os.environ.get('PATH', '')
        if gs_path not in current_path:
            os.environ['PATH'] = current_path + os.pathsep + gs_path
            print(f"✅ Ghostscript encontrado y configurado en: {gs_path}")
        else:
            print(f"✅ Ghostscript ya está en el PATH: {gs_path}")
        return True
    else:
        print("❌ No se encontró Ghostscript. Por favor, instala Ghostscript:")
        print("   - Descarga desde: https://www.ghostscript.com/download/gsdnld.html")
        print("   - O usa: winget install Ghostgum.GSview")
        return False

def test_camelot():
    """
    Prueba básica de camelot-py
    """
    try:
        import camelot
        print(f"✅ camelot-py versión {camelot.__version__} instalado correctamente")
        return True
    except ImportError:
        print("❌ camelot-py no está instalado. Ejecuta: pip install camelot-py[cv]")
        return False

if __name__ == "__main__":
    print("🔧 Configurando camelot-py...")
    
    # Configurar Ghostscript
    gs_ok = setup_ghostscript()
    
    # Probar camelot
    camelot_ok = test_camelot()
    
    if gs_ok and camelot_ok:
        print("\n🎉 ¡Configuración completada! Ya puedes usar camelot-py con Ghostscript.")
        print("\nEjemplo de uso:")
        print("import camelot")
        print("tables = camelot.read_pdf('archivo.pdf', flavor='lattice')")
        print("print(f'Se encontraron {len(tables)} tablas')")
    else:
        print("\n⚠️  Hay problemas con la configuración. Revisa los mensajes anteriores.")
