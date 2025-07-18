# Fitxers d'exemple

Aquest directori conté fitxers d'exemple per provar l'aplicació Professional OCR Viewer.

## 📄 Fitxers de mostra

### sample.pdf
Un document PDF de mostra per provar la funcionalitat OCR. Aquest fitxer demostra:
- Text i gràfics barrejats
- Diverses mides i estils de lletra
- Dibuixos tècnics (si n'hi ha)
- Dissenys de diverses columnes

## 🧪 Instruccions de prova

1. **Inicia l'OCR Viewer:**
   ```bash
   python launch_ocr_viewer.py
   ```

2. **Obre el fitxer de mostra:**
   - Fes clic a "Obre PDF" o prem Ctrl+O
   - Navega fins a aquesta carpeta d'exemples
   - Selecciona `sample.pdf`

3. **Processa el document:**
   - Fes clic a "Processa Document" o prem Ctrl+P
   - Espera que el processament acabi

4. **Explora els resultats:**
   - Visualitza les caixes delimitadores al PDF
   - Comprova la qualitat de l'extracció de text
   - Prova diferents nivells de zoom
   - Testeja les funcions d'exportació

## 📝 Resultats esperats

En processar el fitxer de mostra, hauràs de veure:
- Caixes verdes per text d'alta confiança
- Caixes taronges per text de confiança mitjana
- Caixes vermelles per àrees de baixa confiança
- Blocs de text clicables per seleccionar

## 🔄 Afegir els teus propis fitxers de prova

Per provar amb els teus propis documents:

1. Copia els fitxers PDF en aquest directori
2. Utilitza l'aplicació per obrir-los
3. Compara els resultats amb diferents tipus de documents:
   - Documents escanejats
   - PDFs basats en text
   - Documents amb imatges
   - Contingut multilingüe

## 📊 Ràtios de rendiment

Utilitza aquests fitxers per provar el rendiment:
- Documents petits (< 1MB): S'haurien de processar en 2-5 segons
- Documents mitjans (1-5MB): S'haurien de processar en 5-15 segons
- Documents grans (> 5MB): Podrien trigar més de 15 segons

Nota: El temps de processament depèn de:
- Complexitat del document
- Qualitat de la imatge
- Velocitat de la xarxa
- Càrrega de processament de Google Cloud
