# 🚀 Guia d'Execució - OCR Technical Analyzer

## 📋 Requisits Previs

### 1. Entorn Python
```bash
# Assegurar-se que Python 3.13+ està instal·lat
python --version

# Activar l'entorn virtual
.venv\Scripts\Activate.ps1  # Windows PowerShell
# o
source .venv/bin/activate   # Linux/Mac
```

### 2. Dependències
```bash
# Instal·lar paquets necessaris
pip install -r requirements.txt
pip install ultralytics opencv-python loguru
```

### 3. Tesseract OCR
- Assegurar-se que Tesseract està instal·lat i configurat
- El sistema detectarà automàticament la instal·lació

---

## 🏭 Execució en Producció

### Opció 1: Execució Completa Automàtica

```bash
# 1. Anar al directori de producció
cd production

# 2. Verificar sistema
python quick_test.py

# 3. Processar documents
python process_documents.py
```

### Opció 2: Execució Pas a Pas

```bash
# 1. Preparar documents
# Copiar PDFs al directori d'entrada
cp /camí/als/documents/*.pdf production/data/input/

# 2. Executar detecció YOLOv8 individual
cd production
python -c "
from technical_element_detector import TechnicalElementDetector
detector = TechnicalElementDetector()
detector.set_thresholds(confidence=0.3, iou=0.45)
results = detector.detect_in_directory('data/input', 'data/output/yolo_results')
print(f'Elements detectats: {results[\"summary\"][\"total_elements\"]}')
"

# 3. Executar pipeline complet
python -c "
from enhanced_pipeline import EnhancedOCRPipeline
pipeline = EnhancedOCRPipeline(enable_yolo=True)
results = pipeline.process_pdf_enhanced('data/input/document.pdf')
print('Processament completat!')
"
```

---

## 🎯 Scripts d'Execució Ràpida

### Script 1: Processament Individual
```bash
# Processar un document específic
python ../src/technical_element_detector.py --input data/input/document.pdf --confidence 0.3
```

### Script 2: Processament en Batch
```bash
# Processar tots els documents del directori
python ../src/technical_element_detector.py --input data/input --output data/output --confidence 0.3
```

### Script 3: Demo Interactiva
```bash
# Executar demo amb interfície
python demo_production.py
```

---

## 📊 Monitorització i Resultats

### Consultar Logs
```bash
# Logs generals
tail -f production/logs/application.log

# Logs d'errors
tail -f production/logs/errors.log

# Logs de rendiment
tail -f production/logs/performance.log
```

### Consultar Resultats
```bash
# Llistar resultats processats
ls -la production/data/output/

# Veure últim resultat
cat production/data/output/results_*.json | jq '.'
```

---

## 🔧 Configuració Avançada

### Ajustar Paràmetres YOLOv8
```bash
# Editar configuració
nano production/config/production_config.json

# Modificar:
"yolo": {
  "confidence_threshold": 0.3,  # Ajustar segons necessitat
  "iou_threshold": 0.45,
  "save_annotated": true
}
```

### Personalitzar Processament
```bash
# Modificar configuració OCR
"ocr": {
  "tesseract_config": "--psm 6 -l eng+spa",
  "technical_mode": true,
  "dpi": 300
}
```

---

## 🚨 Solució de Problemes

### Error: Model no trobat
```bash
# Verificar models registrats
python -c "
from ai_model.model_manager import ModelManager
manager = ModelManager()
models = manager.list_models()
"

# Re-registrar model si cal
python src/register_model.py
```

### Error: Tesseract no trobat
```bash
# Verificar Tesseract
tesseract --version

# Si no està instal·lat
python src/install_tesseract.py
```

### Error: Dependències
```bash
# Reinstal·lar dependències
pip install --force-reinstall -r requirements.txt
pip install ultralytics opencv-python loguru
```

---

## 📈 Optimització de Rendiment

### Processament Paral·lel
```bash
# Activar processament paral·lel
python -c "
import json
config = json.load(open('production/config/production_config.json'))
config['processing']['parallel_processing'] = True
config['processing']['max_workers'] = 4
json.dump(config, open('production/config/production_config.json', 'w'), indent=2)
"
```

### Memòria i GPU
```bash
# Verificar ús de GPU (si disponible)
python -c "
import torch
print(f'CUDA disponible: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name(0)}')
"
```

---

## 🎬 Exemples d'Execució

### Exemple 1: Document Individual
```bash
cd production
echo "📄 Processant document individual..."
cp ../data/exemples/6555945_003.pdf data/input/
python demo_production.py
echo "✅ Consulta resultats a data/output/"
```

### Exemple 2: Batch de Documents
```bash
cd production
echo "📄 Processant múltiples documents..."
cp ../data/exemples/*.pdf data/input/
python process_documents.py
echo "✅ Tots els documents processats"
```

### Exemple 3: Només YOLOv8
```bash
cd production
echo "🎯 Només detecció d'elements..."
python ../src/technical_element_detector.py --input data/input --confidence 0.2
echo "✅ Elements detectats i anotats"
```

---

## 📋 Checklist de Verificació

- [ ] Python 3.13+ instal·lat
- [ ] Entorn virtual activat
- [ ] Dependències instal·lades
- [ ] Tesseract configurat
- [ ] Model YOLOv8 registrat
- [ ] Directori de producció creat
- [ ] Tests ràpids superats
- [ ] Documents copiats a data/input/
- [ ] Configuració verificada

---

## 🎯 Execució Recomanada (Pas a Pas)

```bash
# 1. Preparació
cd OCR
.venv\Scripts\Activate.ps1

# 2. Verificar sistema
cd production
python quick_test.py

# 3. Afegir documents
cp ../data/exemples/6555945_003.pdf data/input/

# 4. Executar processament
python demo_production.py

# 5. Consultar resultats
ls data/output/
cat data/output/demo_results.json
```

**🎉 Sistema llest per utilitzar en producció!**
