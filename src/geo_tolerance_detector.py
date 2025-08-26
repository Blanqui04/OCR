# src/geo_tolerance_detector.py
import re
import json

# Mapeig de símbols Unicode a tipus de tolerància
SYMBOL_MAP = {
    '⌖': 'posició',
    '⌖': 'planor',
    '⌖': 'circularitat',
    '⌖': 'cilindricitat',
    '⌖': 'paral·lelisme',
    '⌖': 'perpendicularitat',
    '⌖': 'simetria',
    '⌖': 'batiment',
    '⌖': 'batiment_circular'
}

# Expressió regular per detectar patrons de toleràncies
TOLERANCE_PATTERN = r'([' + ''.join(SYMBOL_MAP.keys()) + r'])\s*([0-9.]+)\s*([A-Z])'

def detect_geometric_tolerances(ocr_data):
    tolerances = []
    
    for item in ocr_data:
        text = item['text'].strip()
        # Netegem espais dobles
        text = re.sub(r'\s+', ' ', text)
        
        # Cerquem el patró
        match = re.search(TOLERANCE_PATTERN, text)
        if match:
            symbol, value, datum = match.groups()
            tolerance_type = SYMBOL_MAP.get(symbol, 'desconegut')
            tolerances.append({
                "symbol": symbol,
                "type": tolerance_type,
                "value": value,
                "datum": datum,
                "raw_text": text,
                "confidence": item['confidence'],
                "bbox": item['bbox']
            })
    
    return tolerances

# Exemple d'ús
if __name__ == "__main__":
    with open("C:\\Users\\eceballos\\OneDrive - SOME, S.A\\Desktop\\Projectes\\OCR\\data\\output\\raw\\ocr_output.json", "r", encoding="utf-8") as f:
        ocr_data = json.load(f)
    
    geo_tolerances = detect_geometric_tolerances(ocr_data)

    with open("C:\\Users\\eceballos\\OneDrive - SOME, S.A\\Desktop\\Projectes\\OCR\\data\\geometric_tolerances.json", "w", encoding="utf-8") as f:
        json.dump(geo_tolerances, f, indent=2, ensure_ascii=False)
    
    print(f"✅ S'han detectat {len(geo_tolerances)} toleràncies geomètriques.")
    for t in geo_tolerances:
        print(f"  {t['symbol']} {t['value']} {t['datum']} → {t['type']}")