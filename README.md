# Visualitzador OCR Professional

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Document%20AI-4285F4.svg)](https://cloud.google.com/document-ai)
[![Llicència](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Aplicació d'escriptori professional per a Windows per visualitzar els resultats de Google Cloud Document AI amb renderització de PDF i superposició interactiva de caixes de text, similar a la interfície de demostració de Google Cloud Document AI.

![Captura de pantalla OCR Viewer](docs/screenshot.png)

## 🚀 Funcionalitats

### 📄 Visualització de PDF
- Renderització de PDF d'alta qualitat amb PyMuPDF
- Controls de zoom (ampliar, reduir, ajustar a la finestra)
- Navegació multipàgina
- Llenç interactiu amb desplaçament suau

### 🤖 Integració amb Document AI
- Processament amb Google Cloud Document AI
- Extracció de text en temps real
- Puntuació de confiança pel text extret
- Gestió robusta d'errors i mètodes alternatius
- **Processament per lots** de múltiples PDFs

### 🎯 Anàlisi de text interactiu
- **Superposició de caixes** sobre el PDF (igual que la demo de Google!)
- **Nivells de confiança amb colors:**
   - 🟢 Verd: Alta confiança (>90%)
   - 🟠 Taronja: Confiança mitjana (70-90%)
   - 🔴 Vermell: Baixa confiança (<70%)
   - 🔵 Blau: Bloc de text seleccionat
- **Mode mapa de calor de confiança** amb superposicions transparents
- **Visualització de l'ordre de lectura** amb seqüència numerada
- Selecció de blocs de text amb clic
- Efectes de pas del cursor i canvis de cursor

### 📊 Vistes d'anàlisi completes
- **Pestanya de text complet:** Text extret amb cerca
- **Pestanya de blocs de text:** Llista detallada amb puntuacions de confiança i coordenades
- **Pestanya d'estadístiques:** Mètriques i anàlisi del document
- **Detecció de llengua:** Identificació automàtica de l'idioma del text
- **Extracció de taules:** Detecció intel·ligent d'estructures tabulars
- **Estadístiques avançades:** Freqüència de paraules, mètriques detallades i analítica

### 💾 Capacitats d'exportació
- Exportació de text complet a fitxers .txt
- Exportació de dades estructurades a JSON amb coordenades i puntuacions de confiança
- **Exportació a CSV** amb mètriques detallades (coordenades, confiança, dimensions)
- **Exportació d'informes PDF** amb taules, estadístiques i anàlisi professional
- Diàlegs de fitxers professionals

### 🎨 Interfície professional
- GUI moderna amb tkinter per a Windows
- Organització de contingut per pestanyes
- Barra d'eines amb controls intuïtius
- **Barres de progrés** per a feedback visual
- **Menú d'arxius recents** (últims 10 fitxers)
- Barra d'estat amb actualitzacions de progrés
- **Dreceres de teclat completes**
- Sistema d'ajuda integrat

### ⚡ Funcionalitats avançades
- **Processament per lots:** Processa múltiples PDFs simultàniament
- **Modes visuals:** Alterna entre normal, mapa de calor i ordre de lectura
- **Anàlisi intel·ligent:** Detecció de llengua i reconeixement de taules
- **Eines de productivitat:** Fitxers recents, dreceres de teclat, seguiment de progrés
- **Sistema d'ajuda:** Guia de dreceres i documentació completa

## ⌨️ Dreceres de teclat

### Operacions de fitxer
- `Ctrl + O` - Obre fitxer PDF
- `Ctrl + P` - Processa document amb Document AI  
- `Ctrl + B` - Processa per lots múltiples fitxers

### Controls de vista
- `Ctrl + +` - Ampliar
- `Ctrl + -` - Reduir
- `Ctrl + 0` - Ajustar a la finestra
- `Ctrl + H` - Alterna mapa de calor de confiança
- `Ctrl + R` - Alterna visualització de l'ordre de lectura

### Navegació
- `Page Up/Down` - Navega entre pàgines
- `Home/End` - Salta a la primera/última pàgina
- `Fletxes` - Mou la vista del PDF

### Ajuda i utilitats
- `F1` - Mostra ajuda de dreceres de teclat
- `Escape` - Neteja la selecció actual
- `Ctrl + Q` - Surt de l'aplicació

### Controls de ratolí
- **Clic** - Selecciona bloc de text
- **Arrossega** - Mou la vista del PDF  
- **Desplaça** - Ampliar/reduir
- **Doble clic** - Ajusta el bloc seleccionat a la vista

## 📋 Requisits

- **Sistema operatiu:** Windows 10/11
- **Python:** 3.7 o superior
- **Google Cloud:** Autenticació configurada
- **Internet:** Necessari per al processament amb Document AI

## 🛠️ Instal·lació

### Opció 1: Instal·lació ràpida (Recomanada)

1. **Clona el repositori:**
    ```bash
    git clone https://github.com/your-username/professional-ocr-viewer.git
    cd professional-ocr-viewer
    ```

2. **Executa l'script d'instal·lació:**
    ```bash
    setup.bat
    ```

3. **Configura Google Cloud:**
    - Instal·la [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
    - Executa: `gcloud auth application-default login`
    - Estableix el projecte: `gcloud config set project YOUR_PROJECT_ID`

4. **Llança l'aplicació:**
    ```bash
    OCR_Viewer.bat
    ```

### Opció 2: Instal·lació manual

1. **Crea un entorn virtual:**
    ```bash
    python -m venv .venv
    .venv\Scripts\activate
    ```

2. **Instal·la les dependències:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Configura els paràmetres del projecte** a `ocr_viewer_app.py`:
    ```python
    self.project_id = "your-project-id"
    self.location = "your-location"  # p. ex., "us" o "eu"
    self.processor_id = "your-processor-id"
    ```

4. **Executa l'aplicació:**
    ```bash
    python launch_ocr_viewer.py
    ```

## 🎯 Inici ràpid

1. **Llança l'aplicació** amb `OCR_Viewer.bat`

2. **Obre un fitxer PDF:**
    - Fes clic al botó "Obre PDF" o usa `Ctrl+O`
    - Selecciona el fitxer PDF al diàleg

3. **Processa amb Document AI:**
    - Fes clic al botó "Processa document" o usa `Ctrl+P`
    - Espera que acabi el processament a Google Cloud

4. **Explora els resultats:**
    - Visualitza les superposicions de text al PDF
    - Selecciona blocs de text amb clic
    - Navega per les diferents pestanyes d'anàlisi
    - Cerca dins el text extret
    - Exporta els resultats segons necessitis

## 🖥️ Vista general de la interfície

### Disposició de la finestra principal

- **Panell esquerre**: Visualitzador de PDF amb superposició interactiva
- **Panell dret**: Vista d'anàlisi per pestanyes
   - **Text complet**: Text extret amb cerca
   - **Blocs de text**: Llista detallada amb puntuacions de confiança
   - **Estadístiques**: Mètriques i anàlisi del document

### Controls de la barra d'eines

- **Obre PDF**: Carrega un fitxer PDF per processar
- **Processa document**: Envia a Google Cloud Document AI
- **Ampliar/reduir**: Ajusta la mida del PDF
- **Ajusta a la finestra**: Autoajusta el PDF a la mida de la finestra
- **Navegació de pàgines**: Navega per documents multipàgina

### Sistema de codificació de colors

- **🟢 Verd**: Text d'alta confiança (>90%)
- **🟠 Taronja**: Text de confiança mitjana (70-90%)
- **🔴 Vermell**: Text de baixa confiança (<70%)
- **🔵 Blau**: Bloc de text seleccionat

## ⌨️ Dreceres de teclat

| Drecera    | Acció                  |
|------------|------------------------|
| `Ctrl+O`   | Obre fitxer PDF        |
| `Ctrl+P`   | Processa document      |
| `Ctrl++`   | Ampliar                |
| `Ctrl+-`   | Reduir                 |
| `Ctrl+0`   | Ajusta a la finestra   |

## 📂 Estructura del projecte

```
professional-ocr-viewer/
├── 📄 OCR_Viewer.bat          # Llançador principal de l'aplicació
├── 📄 launch_ocr_viewer.py    # Llançador amb comprovacions
├── 📄 ocr_viewer_app.py       # Codi principal de l'aplicació
├── 📄 test_ocr.py             # Script de proves
├── 📄 requirements.txt        # Dependències Python
├── 📄 setup.bat               # Script d'instal·lació automatitzada
├── 📄 README.md               # Aquest fitxer
├── 📄 LICENSE                 # Llicència MIT
├── 📁 docs/                   # Documentació
│   ├── 📄 setup-guide.md      # Guia d'instal·lació detallada
│   ├── 📄 troubleshooting.md  # Problemes comuns i solucions
│   └── 🖼️ screenshot.png      # Captura de pantalla de l'aplicació
└── 📁 examples/               # Fitxers d'exemple
      └── 📄 sample.pdf          # PDF d'exemple per a proves
```

## 🔧 Configuració

### Paràmetres de Google Cloud

Edita la configuració a `ocr_viewer_app.py`:

```python
# Paràmetres de Google Cloud
self.project_id = "your-project-id"
self.location = "eu"  # o "us", "asia-northeast1", etc.
self.processor_id = "your-processor-id"
```

### Tipus de documents suportats

- Fitxers PDF (`.pdf`)
- Imatges (`.png`, `.jpg`, `.jpeg`, `.tiff`, `.bmp`)
- Altres formats suportats per Google Cloud Document AI

## 💾 Opcions d'exportació

### Exportació de text
- **Format**: Text pla (`.txt`)
- **Contingut**: Tot el text extret organitzat per pàgines
- **Ús**: Anàlisi simple de text, operacions de copiar i enganxar

### Exportació JSON
- **Format**: JSON estructurat (`.json`)
- **Contingut**: Dades completes incloent:
   - Contingut de text per cada bloc
   - Puntuacions de confiança
   - Coordenades de les caixes
   - Número de pàgina
- **Ús**: Processament addicional, integració amb altres eines

## 🔍 Resolució de problemes

### Problemes comuns

1. **Errors d'autenticació**
    - Assegura't que Google Cloud SDK està instal·lat
    - Executa `gcloud auth application-default login`
    - Verifica que l'ID de projecte sigui correcte

2. **Errors d'importació**
    - Comprova que l'entorn virtual estigui activat
    - Instal·la les dependències: `pip install -r requirements.txt`

3. **Problemes de càrrega de PDF**
    - Verifica permisos de fitxer
    - Comprova que el format sigui suportat
    - Assegura't que el fitxer no estigui corrupte

4. **Errors de processament**
    - Comprova la connexió a Internet
    - Verifica les quotes de Google Cloud
    - Assegura't que l'API Document AI estigui activada

Consulta [docs/troubleshooting.md](docs/troubleshooting.md) per a solucions detallades.

## 🤝 Contribució

Les contribucions són benvingudes! Pots enviar un Pull Request. Per a canvis importants, obre primer una issue per discutir la proposta.

### Entorn de desenvolupament

1. Fes un fork del repositori
2. Crea una branca de funcionalitat: `git checkout -b feature-name`
3. Fes els canvis
4. Prova exhaustivament
5. Envia un pull request

## 📜 Llicència

Aquest projecte està sota llicència MIT - consulta el fitxer [LICENSE](LICENSE) per a més detalls.

## 🙏 Agraïments

- **Google Cloud Document AI** per les capacitats OCR
- **PyMuPDF** per la renderització de PDF
- **tkinter** pel framework GUI multiplataforma
- **Pillow** per les capacitats de processament d'imatges

## 📞 Suport

Si tens problemes o preguntes:

1. Consulta la [guia de resolució de problemes](docs/troubleshooting.md)
2. Cerca issues existents a [GitHub](https://github.com/your-username/professional-ocr-viewer/issues)
3. Crea una nova issue amb informació detallada

## 🔄 Canvis

### v1.0.0 (2025-01-17)
- Llançament inicial
- Visualització de PDF amb zoom i navegació
- Integració amb Google Cloud Document AI
- Visualització interactiva de blocs de text
- Interfície professional per a Windows
- Capacitats d'exportació (TXT, JSON)
- Gestió d'errors completa

---

**Professional OCR Viewer v1.0**  
*Impulsat per Google Cloud Document AI*
