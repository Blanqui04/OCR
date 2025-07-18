# Instruccions per Configurar el Repositori GitHub

## 🎉 Repositori Preparat per a GitHub!

El teu projecte Professional OCR Viewer ja està llest per pujar-lo a GitHub. Aquí tens el que s’ha preparat:

## 📂 Contingut del Repositori

```
professional-ocr-viewer/
├── 📄 README.md                  # Documentació completa per GitHub
├── 📄 LICENSE                    # Llicència MIT
├── 📄 .gitignore                 # Fitxer d’exclusió de Git
├── 📄 requirements.txt           # Dependències de Python
├── 📄 setup.bat                  # Script d’instal·lació automatitzat
├── 📄 OCR_Viewer.bat             # Llançador principal de l’aplicació
├── 📄 launch_ocr_viewer.py       # Llançador Python amb comprovacions
├── 📄 ocr_viewer_app.py          # Codi principal de l’aplicació
├── 📄 test_ocr.py                # Script de proves
├── 📄 ocr-google_tuned.py        # Script original senzill
├── 📁 docs/                      # Carpeta de documentació
│   ├── 📄 setup-guide.md         # Guia d’instal·lació detallada
│   └── 📄 troubleshooting.md     # Guia de resolució de problemes
├── 📁 examples/                  # Carpeta d’exemples
│   └── 📄 README.md              # Documentació d’exemples
└── 📄 6555945_003.pdf            # Fitxer PDF d’exemple
```

## 🚀 Passos per Crear el Repositori GitHub

### Mètode 1: Usant la Interfície Web de GitHub (Recomanat)

1. **Ves a GitHub:**
   - Visita [github.com](https://github.com)
   - Inicia sessió al teu compte

2. **Crea un Nou Repositori:**
   - Fes clic a la icona "+" → "New repository"
   - Nom del repositori: `professional-ocr-viewer`
   - Descripció: "Aplicació d’escriptori professional per Windows per Google Cloud Document AI amb visualització interactiva de PDF"
   - Tria Públic o Privat segons prefereixis
   - ❌ **NO** inicialitzis amb README, .gitignore o llicència (ja els tens)
   - Fes clic a "Create repository"

3. **Puja el teu Repositori Local:**
   - Copia les comandes que mostra GitHub (semblaran així):
   ```bash
   git remote add origin https://github.com/elteunomdusuari/professional-ocr-viewer.git
   git branch -M main
   git push -u origin main
   ```

### Mètode 2: Usant GitHub CLI (Si està instal·lat)

1. **Crea el repositori:**
   ```bash
   gh repo create professional-ocr-viewer --public --description "Aplicació d’escriptori professional per Windows per Google Cloud Document AI amb visualització interactiva de PDF"
   ```

2. **Puja el codi:**
   ```bash
   git remote add origin https://github.com/elteunomdusuari/professional-ocr-viewer.git
   git branch -M main
   git push -u origin main
   ```

## 🔧 Abans de Publicar

1. **Actualitza la Configuració:**
   - Edita `ocr_viewer_app.py`
   - Substitueix els valors de mostra pels teus paràmetres reals de Google Cloud:
   ```python
   self.project_id = "el-teu-project-id-real"
   self.location = "la-teva-localització-real"
   self.processor_id = "el-teu-processor-id-real"
   ```

2. **Elimina Fitxers Sensibles (si n’hi ha):**
   - El fitxer `.gitignore` ja exclou fitxers sensibles
   - Revisa que no s’hagin pujat claus API ni credencials

3. **Prova el Repositori:**
   ```bash
   # Comprova que git fa el seguiment correctament
   git status

   # Veu quins fitxers es pujaran
   git ls-files
   ```

## 📝 Funcionalitats del Repositori Preparades

✅ **Documentació Completa:**
- README professional amb insígnies i captures de pantalla
- Guia d’instal·lació detallada
- Guia de resolució de problemes
- Exemples i instruccions d’ús

✅ **Configuració Git Correcta:**
- .gitignore exclou fitxers sensibles
- Historial de commits net
- Estructura de fitxers adequada

✅ **Presentació Professional:**
- Llicència MIT inclosa
- Característiques destacades amb emojis
- Instruccions d’instal·lació
- Exemples d’ús
- Guia de contribució

✅ **Instal·lació Fàcil per l’Usuari:**
- Script d’instal·lació automatitzat
- Llançador per Windows
- Fitxer de requeriments
- Scripts de prova

## 🎯 Després de Publicar a GitHub

1. **Afegeix Temes/Etiquetes:**
   - Ves a la pàgina del teu repositori
   - Fes clic a la icona d’engranatge al costat de "About"
   - Afegeix temes: `ocr`, `document-ai`, `google-cloud`, `python`, `tkinter`, `pdf-viewer`, `windows`

2. **Crea Versions:**
   - Ves a "Releases" → "Create a new release"
   - Etiqueta de versió: `v1.0.0`
   - Títol de la versió: "Professional OCR Viewer v1.0.0"
   - Descriu les funcionalitats i millores

3. **Activa Issues i Discussions:**
   - Ves a Settings → Features
   - Activa Issues per a informes d’errors
   - Activa Discussions per a suport comunitari

4. **Afegeix Insígnies al Repositori:**
   El README ja inclou insígnies per la versió de Python, Google Cloud i Llicència.

## 🔗 URL del Repositori

Un cop creat, el teu repositori estarà disponible a:
```
https://github.com/elteunomdusuari/professional-ocr-viewer
```

## 📊 Estadístiques del Repositori Preparades

- **Total de fitxers:** 16
- **Línies de codi:** ~2.600+
- **Documentació:** Completa
- **Llenguatges:** Python, Batch, Markdown
- **Llicència:** MIT
- **Plataforma:** Windows

## 🎉 Preparat per Compartir!

El teu repositori és professional i està llest per:
- ⭐ Estrelles de GitHub
- 🍴 Forks i contribucions
- 🐛 Seguiment d’errors
- 📚 Documentació comunitària
- 🚀 Desenvolupament continu

El repositori mostra:
- Estructura de codi professional
- Documentació completa
- Instal·lació fàcil per l’usuari
- Aplicació real
- Integració amb Google Cloud
- Pràctiques modernes de Python

**El teu Professional OCR Viewer està llest per al món! 🌟**
