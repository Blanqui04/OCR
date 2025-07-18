# Guia d'Instal·lació

Instruccions detallades pas a pas per configurar l'aplicació Professional OCR Viewer.

## 📋 Prerequisits

Abans de començar la instal·lació, assegura't de tenir:

- **Windows 10 o 11** (es recomana 64 bits)
- **Python 3.7 o superior** instal·lat
- **Connexió a Internet** per descarregar dependències i processar Document AI
- **Compte de Google Cloud** amb Document AI habilitat
- **Privilegis d'administrador** (pot ser necessari per a algunes instal·lacions)

## 🚀 Instal·lació Ràpida (Recomanada)

### Pas 1: Descarrega l'Aplicació

```bash
git clone https://github.com/your-username/professional-ocr-viewer.git
cd professional-ocr-viewer
```

### Pas 2: Executa la Instal·lació Automàtica

Fes doble clic a `setup.bat` o executa des de la línia de comandes:

```bash
setup.bat
```

Això farà:
- Comprovar la instal·lació de Python
- Crear un entorn virtual
- Instal·lar totes les dependències
- Provar la instal·lació

### Pas 3: Configura Google Cloud

1. **Instal·la Google Cloud SDK:**
   - Descarrega des de [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
   - Executa l'instal·lador i segueix les instruccions
   - Reinicia la línia de comandes després de la instal·lació

2. **Autentica't:**
   ```bash
   gcloud auth application-default login
   ```

3. **Configura el teu projecte:**
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

### Pas 4: Configura la Aplicació

Edita `ocr_viewer_app.py` i actualitza aquestes línies:

```python
# Configuració de Google Cloud
self.project_id = "your-project-id"
self.location = "your-location"  # ex: "us", "eu", "asia-northeast1"
self.processor_id = "your-processor-id"
```

### Pas 5: Inicia l'Aplicació

Fes doble clic a `OCR_Viewer.bat` o executa:

```bash
python launch_ocr_viewer.py
```

## 🔧 Instal·lació Manual

Si prefereixes la instal·lació manual o la instal·lació automàtica falla:

### Pas 1: Instal·la Python

1. Descarrega Python 3.7+ des de [python.org](https://www.python.org/downloads/)
2. Durant la instal·lació:
   - ✅ Marca "Add Python to PATH"
   - ✅ Marca "Install for all users" (si ets administrador)
3. Verifica la instal·lació:
   ```bash
   python --version
   pip --version
   ```

### Pas 2: Crea el Directori del Projecte

```bash
mkdir professional-ocr-viewer
cd professional-ocr-viewer
```

### Pas 3: Descarrega els Fitxers de l'Aplicació

Descarrega o copia aquests fitxers al teu directori de projecte:
- `ocr_viewer_app.py`
- `launch_ocr_viewer.py`
- `OCR_Viewer.bat`
- `requirements.txt`
- `README.md`

### Pas 4: Crea l'Entorn Virtual

```bash
python -m venv .venv
```

Activa l'entorn:
```bash
.venv\Scripts\activate
```

### Pas 5: Instal·la les Dependències

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

O instal·la els paquets individualment:
```bash
pip install google-cloud-documentai
pip install Pillow
pip install PyMuPDF
```

### Pas 6: Verifica la Instal·lació

Prova totes les dependències:
```bash
python -c "import tkinter; import fitz; from PIL import Image; from google.cloud import documentai_v1; print('Totes les dependències instal·lades correctament!')"
```

## ☁️ Configuració de Google Cloud

### Pas 1: Crea un Projecte de Google Cloud

1. Ves a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nou projecte o selecciona'n un d'existent
3. Apunta el teu Project ID

### Pas 2: Habilita l'API Document AI

1. Ves a "APIs & Services" > "Library"
2. Busca "Document AI API"
3. Fes clic a "Enable"

### Pas 3: Crea un Processador Document AI

1. Ves a "Document AI" al Console
2. Fes clic a "Create Processor"
3. Tria el tipus de processador (ex: "Document OCR")
4. Selecciona la regió (ex: "us", "eu")
5. Apunta el Processor ID

### Pas 4: Configura l'Autenticació

Tria una d'aquestes opcions:

#### Opció A: Credencials per Defecte de l'Aplicació (Recomanat)

1. Instal·la Google Cloud SDK
2. Executa l'autenticació:
   ```bash
   gcloud auth application-default login
   ```
3. Configura el projecte:
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

#### Opció B: Clau de Compte de Servei

1. Ves a "IAM & Admin" > "Service Accounts"
2. Crea un nou compte de servei
3. Descarrega el fitxer JSON de la clau
4. Configura la variable d'entorn:
   ```bash
   set GOOGLE_APPLICATION_CREDENTIALS=path\to\your\key.json
   ```

## ⚙️ Configuració

### Paràmetres de l'Aplicació

Edita `ocr_viewer_app.py` per configurar:

```python
class OCRViewerApp:
    def __init__(self, root):
        # ... altre codi ...
        
        # Configuració de Google Cloud - ACTUALITZA AIXÒ
        self.project_id = "your-project-id"           # El teu Project ID de Google Cloud
        self.location = "eu"                          # Ubicació del processador: "us", "eu", etc.
        self.processor_id = "your-processor-id"       # El teu Processor ID de Document AI
```

### Camins de Fitxers per Defecte

L'aplicació buscarà PDFs al mateix directori per defecte. Pots canviar-ho modificant la funció `open_pdf()`.

### Personalització de la Interfície

Pots personalitzar la interfície modificant aquests paràmetres a `ocr_viewer_app.py`:

```python
# Mida de la finestra
self.root.geometry("1400x900")

# Colors per als nivells de confiança
color = "green"    # Alta confiança (>90%)
color = "orange"   # Confiança mitjana (70-90%)
color = "red"      # Baixa confiança (<70%)
color = "blue"     # Bloc seleccionat
```

## 🧪 Prova de la Instal·lació

### Pas 1: Prova la Funcionalitat Bàsica

Executa l'script de prova:
```bash
python test_ocr.py
```

Això verificarà:
- Connexió amb Google Cloud
- Processament Document AI
- Lectura de fitxers PDF

### Pas 2: Prova l'Aplicació Gràfica

1. Inicia l'aplicació:
   ```bash
   python launch_ocr_viewer.py
   ```

2. Prova d'obrir un PDF de mostra
3. Processa amb Document AI
4. Verifica que apareguin les caixes delimitadores

### Pas 3: Prova les Funcions d'Exportació

1. Processa un document
2. Prova d'exportar a format TXT
3. Prova d'exportar a format JSON

## 📁 Estructura de Directoris Després de la Instal·lació

```
professional-ocr-viewer/
├── .venv/                     # Entorn virtual (creat per la instal·lació)
│   ├── Scripts/
│   │   ├── python.exe
│   │   └── pip.exe
│   └── Lib/
├── docs/                      # Documentació
│   ├── setup-guide.md
│   └── troubleshooting.md
├── OCR_Viewer.bat            # Llançador principal
├── launch_ocr_viewer.py      # Llançador Python
├── ocr_viewer_app.py         # Aplicació principal
├── test_ocr.py              # Script de prova
├── requirements.txt          # Dependències
├── setup.bat                # Script d'instal·lació
├── README.md                # Documentació principal
└── LICENSE                  # Fitxer de llicència
```

## 🔄 Actualització de l'Aplicació

Per actualitzar a una versió més nova:

1. **Fes una còpia de seguretat de la configuració:**
   - Copia els paràmetres modificats de `ocr_viewer_app.py`

2. **Descarrega la nova versió:**
   ```bash
   git pull origin main
   ```

3. **Actualitza les dependències:**
   ```bash
   .venv\Scripts\activate
   pip install --upgrade -r requirements.txt
   ```

4. **Restaura la configuració:**
   - Actualitza el nou `ocr_viewer_app.py` amb els teus paràmetres

## 🚨 Problemes Comuns d'Instal·lació

### Python No Trobat
- Assegura't que Python està al PATH
- Prova la comanda `py` en lloc de `python`
- Reinstal·la Python amb l'opció "Add to PATH"

### Problemes amb l'Entorn Virtual
- Elimina la carpeta `.venv` i torna-la a crear
- Assegura espai suficient al disc
- Executa com a administrador si cal

### Autenticació Google Cloud
- Verifica la connexió a Internet
- Comprova la configuració del tallafoc/antivirus
- Assegura't de tenir permisos correctes al projecte

### Errors de Permís
- Executa la línia de comandes com a administrador
- Comprova els permisos de fitxer/carpeta
- Desactiva temporalment l'antivirus

Per a més detalls de resolució de problemes, consulta [troubleshooting.md](troubleshooting.md).

## ✅ Llista de Verificació

Abans d'utilitzar l'aplicació, verifica:

- [ ] Python 3.7+ instal·lat i al PATH
- [ ] Entorn virtual creat correctament
- [ ] Totes les dependències instal·lades sense errors
- [ ] Google Cloud SDK instal·lat i autenticat
- [ ] Project ID, ubicació i processor ID configurats
- [ ] Script de prova executat correctament
- [ ] L'aplicació gràfica s'inicia sense errors
- [ ] Es pot carregar i processar un PDF de mostra
- [ ] Les caixes delimitadores són visibles als documents processats
- [ ] Les funcions d'exportació funcionen correctament

## 📞 Suport

Si tens problemes durant la instal·lació:

1. Consulta [troubleshooting.md](troubleshooting.md)
2. Cerca incidències a GitHub
3. Crea una nova incidència amb els detalls de la instal·lació

Inclou aquesta informació quan informis de problemes:
- Versió del sistema operatiu
- Versió de Python
- Missatges d'error (text complet)
- Passos seguits fins a l'error
