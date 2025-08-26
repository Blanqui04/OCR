# src/data_extractor.py
import re
import json

def is_dimension(text):
    # Ex: "50", "Ø25", "R10", "15±0.1", "0.05 A"
    patterns = [
        r'^\d+\.?\d*\s*[±±]\s*\d+\.?\d*',  # 15±0.1
        r'^Ø?\d+\.?\d*',                   # 25 o Ø25
        r'^R\d+\.?\d*',                    # R10
        r'^\d+\.?\d*\s*[A-Z]'              # 0.05 A (tolerància)
    ]
    return any(re.match(p, text) for p in patterns)

def extract_technical_data(ocr_data):
    dimensions = []
    tolerances = []
    notes = []

    for item in ocr_data:
        text = item['text']
        if is_dimension(text):
            dimensions.append(item)
        elif "tolerància" in text.lower() or "tolerancia" in text.lower():
            tolerances.append(item)
        else:
            notes.append(item)

    return {
        "dimensions": dimensions,
        "tolerances": tolerances,
        "notes": notes
    }

# Exemple
if __name__ == "__main__":
    with open("C:\\Users\\eceballos\\OneDrive - SOME, S.A\\Desktop\\Projectes\\OCR\\data\\output\\raw\\ocr_output.json", "r", encoding="utf-8") as f:
        ocr_data = json.load(f)
    
    tech_data = extract_technical_data(ocr_data)
    with open("C:\\Users\\eceballos\\OneDrive - SOME, S.A\\Desktop\\Projectes\\OCR\\data\\output\\structured\\structured_output.json", "w", encoding="utf-8") as f:
        json.dump(tech_data, f, indent=2, ensure_ascii=False)
    print("Dades tècniques extretes.")