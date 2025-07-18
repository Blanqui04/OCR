# Guia de resolució de problemes

Aquesta guia t'ajuda a resoldre problemes comuns amb l'aplicació Professional OCR Viewer.

## 🔧 Problemes d'instal·lació

### Python no trobat
**Error:** `'python' no es reconeix com a comandament intern o extern`

**Solució:**
1. Instal·la Python 3.7+ des de [python.org](https://www.python.org/downloads/)
2. Durant la instal·lació, marca "Add Python to PATH"
3. Reinicia el terminal o la línia de comandes
4. Verifica amb: `python --version`

### Error en la creació de l'entorn virtual
**Error:** `Failed to create virtual environment`

**Solució:**
1. Assegura't que tens prou espai en disc
2. Executa com a administrador si cal
3. Prova manualment: `python -m venv .venv`
4. Comprova la integritat de la instal·lació de Python

### Errors d'instal·lació de dependències
**Error:** `Failed to install dependencies`

**Solucions:**
1. **Actualitza pip primer:**
   ```bash
   python -m pip install --upgrade pip
   ```

2. **Instal·la els paquets individualment:**
   ```bash
   pip install google-cloud-documentai
   pip install Pillow
   pip install PyMuPDF
   ```

3. **Utilitza un índex alternatiu (si estàs darrere d'un tallafoc):**
   ```bash
   pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt
   ```

## 🔐 Problemes d'autenticació

### Credencials per defecte no trobades
**Error:** `Your default credentials were not found`

**Solució:**
1. **Instal·la Google Cloud SDK:**
   - Descarrega des de [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
   - Segueix les instruccions d'instal·lació per a Windows

2. **Autentica't:**
   ```bash
   gcloud auth application-default login
   ```

3. **Configura el projecte:**
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

4. **Verifica l'autenticació:**
   ```bash
   gcloud auth list
   ```

### ID de projecte invàlid
**Error:** `Project not found` o `Permission denied`

**Solució:**
1. Verifica l'ID del projecte a Google Cloud Console
2. Assegura't que tens accés al projecte
3. Actualitza l'ID del projecte a `ocr_viewer_app.py`:
   ```python
   self.project_id = "your-correct-project-id"
   ```

### Processador no trobat
**Error:** `Processor not found` o `Invalid processor ID`

**Solució:**
1. Ves a Google Cloud Console > Document AI
2. Troba el teu processador i copia l'ID
3. Actualitza l'ID del processador a `ocr_viewer_app.py`:
   ```python
   self.processor_id = "your-processor-id"
   ```

### Quota excedida
**Error:** `Quota exceeded` o `Rate limit exceeded`

**Solucions:**
1. Comprova les quotes a Google Cloud Console
2. Sol·licita un augment de quota si cal
3. Espera abans de tornar a intentar-ho (els límits es reinicien)
4. Considera utilitzar un altre projecte

## 📄 Problemes amb el processament de PDF

### El PDF no es carrega
**Error:** `Failed to load PDF`

**Solucions:**
1. **Comprova el format del fitxer:**
   - Assegura't que el fitxer és realment un PDF
   - Prova amb un altre fitxer PDF

2. **Permisos del fitxer:**
   - Assegura't que el fitxer no està obert en un altre programa
   - Comprova els permisos de lectura del fitxer
   - Prova de copiar el fitxer a una altra ubicació

3. **Corruptió del fitxer:**
   - Prova d'obrir el PDF amb Adobe Reader
   - Utilitza un altre PDF si l'original està corrupte

### Text en blanc o absent
**Error:** El PDF es carrega però no s'extreu cap text

**Solucions:**
1. **PDFs escanejats:**
   - El document pot ser basat en imatge
   - El processament OCR hauria de funcionar igualment amb Document AI

2. **Problemes de fonts:**
   - Algunes fonts poden no ser reconegudes correctament
   - Prova amb un PDF estàndard amb fonts comunes

3. **Configuració d'idioma:**
   - Assegura't que el processador Document AI suporta l'idioma del document

## 🖥️ Problemes d'interfície

### L'aplicació no s'inicia
**Error:** L'aplicació es tanca immediatament o no s'obre

**Solucions:**
1. **Comprova els missatges d'error:**
   - Executa des de la línia de comandes per veure errors:
     ```bash
     python launch_ocr_viewer.py
     ```

2. **Problemes gràfics:**
   - Actualitza els controladors gràfics
   - Prova d'executar en una pantalla diferent

3. **Dependències:**
   - Verifica que tots els paquets estan instal·lats:
     ```bash
     python -c "import tkinter, fitz, PIL, google.cloud.documentai_v1"
     ```

### No es veuen les caixes delimitadores
**Problema:** El PDF es mostra però no apareixen les caixes superposades

**Solucions:**
1. **Processa el document primer:**
   - Fes clic al botó "Processa Document"
   - Espera que el processament acabi

2. **Nivell de zoom:**
   - Prova diferents nivells de zoom
   - Utilitza l'opció "Ajusta a la finestra"

3. **Visibilitat del color:**
   - Les caixes poden tenir el mateix color que el fons
   - Prova de seleccionar blocs de text des del panell dret

### Baix rendiment
**Problema:** L'aplicació és lenta o no respon

**Solucions:**
1. **Fitxers grans:**
   - Prova primer amb fitxers PDF més petits
   - Considera dividir documents grans

2. **Problemes de memòria:**
   - Tanca altres aplicacions
   - Reinicia l'OCR Viewer

3. **Velocitat de xarxa:**
   - El processament amb Document AI requereix internet
   - Comprova la velocitat de la connexió

## 🌐 Problemes de xarxa

### Temps d'espera excedit
**Error:** `Connection timeout` o `Network error`

**Solucions:**
1. **Comprova la connexió a internet**
2. **Tallafoc/antivirus:**
   - Desactiva temporalment per fer proves
   - Afegeix excepcions per a Python i l'aplicació

3. **Configuració de proxy:**
   - Configura el proxy si estàs darrere d'un tallafoc corporatiu
   - Defineix variables d'entorn si cal

4. **Problemes amb VPN:**
   - Prova de desconnectar la VPN
   - Algunes VPN poden bloquejar serveis de Google

## 📊 Problemes d'exportació de dades

### Error d'exportació
**Error:** `Failed to export` o errors de permisos

**Solucions:**
1. **Permisos de fitxer:**
   - Tria una ubicació d'exportació diferent
   - Assegura't que tens permisos d'escriptura a la carpeta de destinació

2. **Fitxer en ús:**
   - Tanca el fitxer exportat si està obert en un altre programa
   - Tria un nom de fitxer diferent

3. **Espai en disc:**
   - Assegura't que tens prou espai en disc
   - Neteja fitxers temporals

## 🔄 Passos generals de resolució de problemes

### Reinicia l'aplicació
1. Tanca completament l'aplicació
2. Elimina la carpeta `.venv`
3. Executa `setup.bat` de nou
4. Reconfigura la configuració de Google Cloud

### Instal·lació neta
1. Elimina tots els fitxers de l'aplicació
2. Descarrega una còpia nova des de GitHub
3. Segueix la guia d'instal·lació pas a pas
4. Prova amb un PDF de mostra

### Comprova els requisits del sistema
- **SO:** Windows 10/11
- **Python:** 3.7 o superior
- **RAM:** mínim 4GB, recomanat 8GB
- **Disc:** mínim 500MB d'espai lliure
- **Internet:** Necessari per al processament amb Document AI

## 📞 Obtenir ajuda addicional

Si encara tens problemes:

1. **Comprova els Issues de GitHub:**
   - Cerca problemes similars
   - Consulta els issues tancats per solucions

2. **Crea un nou Issue:**
   - Inclou els missatges d'error
   - Descriu els passos per reproduir el problema
   - Inclou informació del sistema
   - Adjunta fitxers rellevants si és possible

3. **Informació de diagnòstic:**
   Quan informis de problemes, inclou:
   - Versió del sistema operatiu
   - Versió de Python (`python --version`)
   - Missatges d'error (text complet)
   - Passos que han portat a l'error
   - Característiques del fitxer PDF (si és rellevant)

## 📝 Comandes de diagnòstic

Executa aquestes comandes per obtenir informació del sistema:

```bash
# Versió de Python
python --version

# Paquets instal·lats
pip list

# Estat d'autenticació de Google Cloud
gcloud auth list

# Informació del sistema
systeminfo | findstr "OS"
```

Recorda no compartir mai informació sensible com claus API o tokens d'autenticació quan informis de problemes.
