# src/tesseract_setup.py
import os
import requests
import platform
import subprocess
from pathlib import Path

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

def setup_technical_ocr():
    """Configuració completa per OCR tècnic"""
    print("🔧 Configurant OCR per a símbols tècnics...")
    print()
    
    # Comprovar llenguatges actuals
    langs = check_tesseract_languages()
    print()
    
    if 'equ' in langs:
        print("✅ Configuració perfecta! 'equ' ja està disponible.")
        return True
    
    print("⚠️ El model 'equ' no està disponible.")
    print("Aquest model millora la detecció de símbols tècnics com ⌖, ±, Ø, etc.")
    print()
    
    choice = input("Vols descarregar 'equ.traineddata'? (s/n): ").lower().strip()
    
    if choice in ['s', 'si', 'y', 'yes']:
        success = download_equ_traineddata()
        if success:
            print()
            print("🎉 Instal·lació completada!")
            print("🔄 Reinicia l'aplicació per utilitzar el nou model.")
            return True
    
    print()
    print("📋 Instruccions manuals:")
    print("1. Descarrega equ.traineddata de:")
    print("   https://github.com/tesseract-ocr/tessdata/raw/master/equ.traineddata")
    tessdata_path = get_tesseract_data_path()
    if tessdata_path:
        print(f"2. Copia'l a: {tessdata_path}")
    else:
        print("2. Copia'l al directori tessdata de Tesseract")
    print("3. Reinicia l'aplicació")
    
    return False

if __name__ == "__main__":
    setup_technical_ocr()
