# 🚀 COM EXECUTAR EL SISTEMA OCR

## Execució Ràpida (Recomanada)

### Opció 1: Script Automàtic
```bash
# Executar directament
python run_ocr.py

# O amb el script batch (Windows)
run.bat
```

### Opció 2: Comandes Directes

#### 1️⃣ Test Ràpid del Sistema
```bash
cd production
python quick_test.py
```

#### 2️⃣ Demo amb Exemple
```bash
cd production
python demo_production.py
```

#### 3️⃣ Processar Documents Reals
```bash
# Primer: copiar documents a production/data/input/
cp documents/*.pdf production/data/input/

# Després: processar
cd production
python process_documents.py
```

#### 4️⃣ Només Detecció YOLOv8
```bash
python src/technical_element_detector.py --input production/data/input --confidence 0.3
```

---

## Flux de Treball Complet

### Pas 1: Preparació
```bash
# Activar entorn virtual
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate   # Linux/Mac

# Verificar sistema
cd production
python quick_test.py
```

### Pas 2: Afegir Documents
```bash
# Copiar documents PDF al directori d'entrada
cp /camí/documents/*.pdf production/data/input/

# Verificar que s'han copiat
ls production/data/input/
```

### Pas 3: Executar Processament
```bash
# Opció A: Demo ràpida
python production/demo_production.py

# Opció B: Processament complet
python production/process_documents.py

# Opció C: Només YOLOv8
python src/technical_element_detector.py --input production/data/input
```

### Pas 4: Consultar Resultats
```bash
# Veure fitxers generats
ls production/data/output/

# Llegir resultats JSON
cat production/data/output/demo_results.json

# Veure imatges anotades
ls production/data/input/annotated/
```

---

## Exemples Pràctics

### Exemple 1: Primera Execució
```bash
# 1. Test del sistema
python run_ocr.py
# Seleccionar opció 1: Test ràpid

# 2. Demo amb exemple
python run_ocr.py  
# Seleccionar opció 2: Demo
```

### Exemple 2: Processar Document Nou
```bash
# 1. Copiar document
cp nou_document.pdf production/data/input/

# 2. Processar
cd production
python demo_production.py

# 3. Ver resultats
cat data/output/demo_results.json
```

### Exemple 3: Processament en Batch
```bash
# 1. Copiar múltiples documents
cp *.pdf production/data/input/

# 2. Processar tots
cd production
echo "1" | python process_documents.py

# 3. Consultar resum
ls data/output/batch_summary_*.json
```

---

## Solució de Problemes

### Error: "Model no trobat"
```bash
# Re-registrar model
python src/register_model.py
```

### Error: "Tesseract no trobat"
```bash
# Instal·lar Tesseract
python src/install_tesseract.py
```

### Error: "Dependències"
```bash
# Reinstal·lar paquets
pip install -r requirements.txt
```

---

## Resultats i Sortides

### Fitxers Generats
- `data/output/demo_results.json` - Resultats de detecció
- `data/input/annotated/detected_*.png` - Imatges amb anotacions
- `data/output/batch_summary_*.json` - Resum de processament
- `logs/application.log` - Logs del sistema

### Format de Resultats
```json
{
  "total_elements": 2,
  "summary": {
    "cota": 2,
    "tolerancia": 0,
    "simbol": 0
  },
  "elements": [
    {
      "type": "cota",
      "confidence": 0.440,
      "bbox": {...}
    }
  ]
}
```

---

## ⚡ Execució EXPRESS (1 Minut)

```bash
# Executar tot en 1 minut
cd OCR
.venv\Scripts\Activate.ps1
python run_ocr.py
# Opció 2: Demo
# ✅ Resultat: 2 elements detectats en 8 segons
```

**🎯 El sistema està llest per utilitzar!**
