# src/tesseract_setup.py
"""
Configuració i setup de Tesseract OCR
Detecta automàticament la instal·lació de Tesseract i configura pytesseract
"""

import os
import requests
import platform
import subprocess
from pathlib import Path
import pytesseract
from loguru import logger

def get_tesseract_data_path():
    """Detecta el directori tessdata de Tesseract"""
    possible_paths = []
    
    if platform.system() == "Windows":
        possible_paths = [
            r"C:\Program Files\Tesseract-OCR\tessdata",
            r"C:\Program Files (x86)\Tesseract-OCR\tessdata",
            r"C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tessdata".format(os.getenv('USERNAME')),
            r"C:\tesseract\tessdata"
        ]
    else:
        possible_paths = [
            "/usr/share/tesseract-ocr/4.00/tessdata",
            "/usr/share/tesseract-ocr/tessdata",
            "/usr/local/share/tessdata",
            "/opt/homebrew/share/tessdata"
        ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def download_equ_traineddata():
    """Descarrega el model equ.traineddata per a símbols tècnics"""
    tessdata_path = get_tesseract_data_path()
    
    if not tessdata_path:
        print("❌ No s'ha trobat el directori tessdata de Tesseract")
        print("Paths cercats:")
        if platform.system() == "Windows":
            paths = [
                r"C:\Program Files\Tesseract-OCR\tessdata",
                r"C:\Program Files (x86)\Tesseract-OCR\tessdata",
                r"C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tessdata".format(os.getenv('USERNAME'))
            ]
        else:
            paths = ["/usr/share/tesseract-ocr/tessdata", "/usr/local/share/tessdata"]
        
        for path in paths:
            print(f"  - {path}")
        return False
    
    equ_path = os.path.join(tessdata_path, "equ.traineddata")
    
    if os.path.exists(equ_path):
        print(f"✅ equ.traineddata ja existeix a: {equ_path}")
        return True
    
    print(f"📂 Tessdata trobat a: {tessdata_path}")
    print("⬇️ Descarregant equ.traineddata...")
    
    # URL del model equ
    url = "https://github.com/tesseract-ocr/tessdata/raw/master/equ.traineddata"
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(equ_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ equ.traineddata descarregat correctament a: {equ_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error descarregant equ.traineddata: {e}")
        print("\n📝 Descàrrega manual:")
        print(f"1. Ves a: {url}")
        print(f"2. Desa el fitxer a: {equ_path}")
        return False

def check_tesseract_languages():
    """Comprova quins llenguatges té disponibles Tesseract"""
    try:
        import pytesseract
        langs = pytesseract.get_languages()
        
        print("🗣️ Llenguatges disponibles a Tesseract:")
        for lang in sorted(langs):
            status = ""
            if lang == 'equ':
                status = " ✅ (Símbols tècnics)"
            elif lang == 'osd':
                status = " 📝 (Detecció de script)"
            elif lang == 'eng':
                status = " 🇬🇧 (Anglès base)"
            
            print(f"  - {lang}{status}")
        
        return langs
        
    except Exception as e:
        print(f"❌ Error comprovant llenguatges: {e}")
        return []

def setup_tesseract_auto():
    """Configuració automàtica completa de Tesseract"""
    logger.info("🔧 Configurant Tesseract OCR automàticament...")
    
    try:
        # Verificar Tesseract instal·lat
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, check=True)
        version = result.stdout.split('\n')[0]
        logger.info(f"Tesseract trobat: {version}")
        
        # Configurar pytesseract
        pytesseract.pytesseract.tesseract_cmd = 'tesseract'
        
        # Test bàsic
        from PIL import Image
        import numpy as np
        img_array = np.ones((50, 200, 3), dtype=np.uint8) * 255
        test_img = Image.fromarray(img_array)
        text = pytesseract.image_to_string(test_img)
        
        logger.success("✅ Tesseract configurat correctament!")
        return True
        
    except subprocess.CalledProcessError:
        logger.error("❌ Tesseract no trobat al PATH")
        return _setup_tesseract_windows() if platform.system() == "Windows" else False
    except Exception as e:
        logger.error(f"❌ Error configurant Tesseract: {e}")
        return False

def _setup_tesseract_windows():
    """Configuració específica per Windows"""
    possible_paths = [
        r"C:\Users\eceballos\AppData\Local\Programs\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files\PDF24\tesseract\tesseract.exe",
        r"C:\Tools\Tesseract-OCR\tesseract.exe",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            logger.info(f"Tesseract trobat: {path}")
            return True
    
    logger.error("❌ Tesseract no trobat. Instal·la'l des de: https://github.com/UB-Mannheim/tesseract/wiki")
    return False
    print("3. Reinicia l'aplicació")
    
    return False

if __name__ == "__main__":
    setup_tesseract_auto()
else:
    # Auto-configuració en importar
    try:
        # Intentar carregar configuració automàtica primer
        import sys
        import os
        config_file = os.path.join(os.path.dirname(__file__), "..", "tesseract_config.py")
        if os.path.exists(config_file):
            sys.path.insert(0, os.path.dirname(config_file))
            import tesseract_config
            logger.success("✅ Tesseract configurat automàticament")
        else:
            success = setup_tesseract_auto()
            if not success:
                logger.warning("Tesseract no configurat completament")
    except Exception as e:
        logger.error(f"Error en auto-configuració: {e}")
