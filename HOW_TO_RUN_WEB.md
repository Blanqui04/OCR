# 🌐 COM EXECUTAR LA VERSIÓ WEB OCR

## 🚀 Execució Ràpida (1 minut)

```bash
# Activar entorn virtual
.venv\Scripts\Activate.ps1

# Executar servidor web
python src\ui\app_production.py
```

**📱 Obrir navegador:** http://localhost:5000

---

## 📋 Opcions de Servidor Web

### 1️⃣ **Producció** (Recomanat)
```bash
python src\ui\app_production.py
```
- ✅ Servidor estable i optimitzat
- ✅ Logs detallats
- ✅ Gestió d'errors robusta
- 🌐 **URL:** http://localhost:5000

### 2️⃣ **Debug** (Desenvolupament)
```bash
python src\ui\app_debug.py
```
- 🔧 Mode debug activat
- 🔄 Auto-reload en canvis
- 📊 Informació de debug
- 🌐 **URL:** http://127.0.0.1:5000

### 3️⃣ **Aplicació Base**
```bash
python src\ui\app.py
```
- 🏗️ Versió bàsica
- 🌐 **URL:** http://localhost:5000

---

## 🎯 Scripts d'Execució Ràpida

### Script PowerShell
```powershell
# Crear run_web.ps1
cd OCR
.venv\Scripts\Activate.ps1
echo "🌐 Iniciant servidor web OCR..."
python src\ui\app_production.py
```

### Script Batch
```batch
# Crear run_web.bat
@echo off
cd /d "C:\Users\eceballos\OneDrive - SOME, S.A\Desktop\Projectes\OCR"
call .venv\Scripts\Activate.bat
echo 🌐 Iniciant servidor web OCR...
python src\ui\app_production.py
pause
```

---

## 📱 Ús de la Interfície Web

### 1. **Pujar Fitxers**
- 📤 Arrossegar fitxers a la zona de pujada
- 📂 O clicar per seleccionar
- ✅ Formats: PDF, PNG, JPG, JPEG, TIFF, BMP
- 📏 Mida màxima: 16MB per fitxer

### 2. **Configurar Opcions**
- 🗣️ **Idioma:** Català, Espanyol, Anglès
- ⚡ **Mode:** Ràpid / Precís
- 📊 **Format sortida:** JSON / TXT
- 📋 **Detecció taules:** Sí/No

### 3. **Processar Documents**
- ▶️ Clicar "Processar"
- ⏱️ Veure progrés en temps real
- 📥 Descarregar resultats automàticament

### 4. **Consultar Resultats**
- 📊 Veure resum de processament
- 📄 Text extret per document
- 🎯 Confiança de detecció
- 📈 Estadístiques detallades

---

## 🔧 Configuració del Servidor

### Variables d'Entorn
```bash
# Port personalitzat
export PORT=8080
python src\ui\app_production.py

# Mode debug
export FLASK_ENV=development
export FLASK_DEBUG=1
```

### Configuració Avançada
```python
# Al fitxer app_production.py (línia 25-27):
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB
app.config['UPLOAD_FOLDER'] = 'custom/upload/path'
app.config['OUTPUT_FOLDER'] = 'custom/output/path'
```

---

## 🌐 Accés de Xarxa

### Accés Local
- **URL Principal:** http://localhost:5000
- **Health Check:** http://localhost:5000/health
- **API Upload:** http://localhost:5000/upload

### Accés per Xarxa Local
```bash
# El servidor escolta a 0.0.0.0:5000
# Accés des d'altres dispositius:
http://[IP_DEL_ORDINADOR]:5000

# Exemple:
http://192.168.1.100:5000
```

### Trobar IP Local
```powershell
ipconfig | findstr "IPv4"
```

---

## 📁 Estructura de Fitxers Web

```
src/ui/
├── app_production.py      # Servidor principal
├── app_debug.py          # Servidor debug
├── app.py               # Servidor bàsic
├── templates/
│   ├── index.html       # Interfície principal
│   └── index_debug.html # Interfície debug
├── static/
│   └── style.css        # Estils CSS
└── ocr_app.log         # Logs del servidor
```

---

## 🔍 Endpoints API

### **POST /upload**
Pujar fitxers al servidor
```javascript
// Exemple JavaScript
const formData = new FormData();
formData.append('files', file);
fetch('/upload', {method: 'POST', body: formData})
```

### **POST /process**
Processar fitxers amb OCR
```javascript
fetch('/process', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    files: uploadedFiles,
    options: {language: 'cat', ocr_mode: 'fast'}
  })
})
```

### **GET /download/[filename]**
Descarregar resultats processats
```
http://localhost:5000/download/ocr_results_1234567890.json
```

### **GET /health**
Comprovar estat del servidor
```json
{
  "status": "healthy",
  "timestamp": "2025-08-28T10:30:00"
}
```

---

## 🛠️ Solució de Problemes

### Error: "Port 5000 en ús"
```bash
# Usar port alternatiu
python -c "
import sys
sys.path.append('src/ui')
from app_production import app
app.run(port=8080)
"
```

### Error: "Template no trobat"
```bash
# Verificar que estem al directori correcte
cd "C:\Users\eceballos\OneDrive - SOME, S.A\Desktop\Projectes\OCR"
python src\ui\app_production.py
```

### Error: "Modules no trobats"
```bash
# Reinstal·lar dependències
pip install flask werkzeug
```

---

## 📊 Monitorització

### Logs en Temps Real
```bash
# Veure logs del servidor
Get-Content src\ui\ocr_app.log -Wait -Tail 20
```

### Logs d'Accés
```
[2025-08-28 10:30:15] INFO - File uploaded: document.pdf (2.5MB)
[2025-08-28 10:30:20] INFO - Processing started for 1 files
[2025-08-28 10:30:25] INFO - OCR completed: 95.2% confidence
```

---

## ⚡ EXECUCIÓ EXPRESS WEB

```bash
# Tot en 30 segons
cd OCR
.venv\Scripts\Activate.ps1
python src\ui\app_production.py

# Obrir: http://localhost:5000
# Arrossegar PDF → Processar → Descarregar
```

**🎉 La interfície web està llesta per utilitzar!**
