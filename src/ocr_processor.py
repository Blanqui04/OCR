# src/ocr_processor.py
import cv2
import pytesseract
import json
import os
import platform

# Configurar el path de Tesseract segons el sistema operatiu
if platform.system() == "Windows":
    # Possible paths per Windows
    possible_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe".format(os.getenv('USERNAME')),
        r"C:\tesseract\tesseract.exe"
    ]
    
    tesseract_path = None
    for path in possible_paths:
        if os.path.exists(path):
            tesseract_path = path
            break
    
    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        print(f"Tesseract trobat a: {tesseract_path}")
    else:
        print("ERROR: Tesseract no trobat en cap dels paths habituals.")
        print("Paths cercats:")
        for path in possible_paths:
            print(f"  - {path}")
        print("\nSi Tesseract està instal·lat en un altre lloc, actualitza el path a aquest fitxer.")

def ocr_with_boxes(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Millora d'imatge
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # Configuració per a text tècnic (sense diccionari)
    custom_config = r'--oem 3 --psm 6'
    data = pytesseract.image_to_data(gray, config=custom_config, output_type=pytesseract.Output.DICT)

    results = []
    for i in range(len(data['text'])):
        if int(data['conf'][i]) > 30:  # Només text amb confiança >30%
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            text = data['text'][i].strip()
            if text:
                results.append({
                    "text": text,
                    "bbox": [x, y, w, h],
                    "confidence": data['conf'][i]
                })

    return results, img.shape  # Retornem també la mida de la imatge

# Exemple
if __name__ == "__main__":
    text_data, img_shape = ocr_with_boxes("C:\\Users\\eceballos\\OneDrive - SOME, S.A\\Desktop\\Projectes\\OCR\\data\\images\\page_1.png")
    with open("C:\\Users\\eceballos\\OneDrive - SOME, S.A\\Desktop\\Projectes\\OCR\\data\\output\\raw\\ocr_output.json", "w", encoding="utf-8") as f:
        json.dump(text_data, f, indent=2, ensure_ascii=False)
    print(f"OCR fet: {len(text_data)} elements trobats.")