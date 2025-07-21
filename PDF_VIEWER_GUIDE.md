# 📄 Visualitzador PDF amb Marcatge de Text OCR

## Descripció

El nou visualitzador PDF integra funcionalitats avançades similars a la demo de Google Document AI, permetent visualitzar documents PDF amb marques de text reconegut superposades de manera interactiva.

## ✨ Funcionalitats Principals

### 📋 Visualització de PDF
- **Renderització d'alta qualitat**: Utilitza PyMuPDF per renderitzar pàgines PDF amb qualitat òptima
- **Zoom dinàmic**: Control de zoom de 0.5x a 3.0x amb botons o roda del ratolí
- **Navegació fluida**: Botons de navegació i suport per tecles de fletxa
- **Desplaçament**: Barres de desplaçament automàtiques per documents grans

### 🎯 Marques de Text OCR
- **Caixes de delimitació**: Quadres colorits al voltant de cada bloc de text detectat
- **Colors per confiança**: 
  - 🟢 **Verd**: Confiança alta (>90%)
  - 🟡 **Groc**: Confiança mitjana (70-90%)
  - 🔴 **Vermell**: Confiança baixa (<70%)
- **Transparència ajustable**: Marques semi-transparents per no ocultar el text original

### 🔢 Ordre de Lectura
- **Números visibles**: Cada bloc de text mostra el seu número d'ordre de lectura
- **Font llegible**: Text blanc amb contorn negre per màxima visibilitat
- **Posició intel·ligent**: Números posicionats a la cantonada superior esquerra de cada bloc

### 🖱️ Interactivitat
- **Selecció de blocs**: Clic sobre un bloc per seleccionar-lo i destacar-lo
- **Informació detallada**: Mostra confiança i text del bloc seleccionat
- **Zoom amb roda**: Control intuïtiu del zoom amb la roda del ratolí
- **Navegació per teclat**: Tecles de fletxa per canviar de pàgina

## 🎮 Controls i Navegació

### Botons de Navegació
```
[◀ Anterior] [Pàgina X de Y] [Següent ▶]
```

### Controls de Zoom
```
[🔍-] [100%] [🔍+] [Ajustar a la finestra]
```

### Tecles de Drecera
- **←/→**: Pàgina anterior/següent
- **Roda del ratolí**: Zoom in/out
- **Clic**: Seleccionar bloc de text

## 🔧 Integració amb OCR

### Flux de Treball
1. **Càrrega del PDF**: L'usuari selecciona un document PDF
2. **Visualització inicial**: El PDF es mostra sense marques
3. **Processament OCR**: L'usuari inicia el processament amb Google Cloud Document AI
4. **Actualització automàtica**: Les marques de text apareixen automàticament després del processament
5. **Navegació millorada**: L'usuari pot navegar i explorar els resultats visualment

### Sincronització
- **Actualització en temps real**: Les marques s'actualitzen automàticament després del processament OCR
- **Conservació de l'estat**: Zoom i posició es mantenen durant l'actualització
- **Canvi de pestanya automàtic**: L'aplicació canvia automàticament a la pestanya del visualitzador quan es carrega un PDF

## 📊 Informació Visual

### Colors de Confiança
```
🟢 Verde  (>90%):  Confiança molt alta - Text segur
🟡 Groc   (70-90%): Confiança mitjana - Revisar si cal
🔴 Vermell (<70%):  Confiança baixa - Necessita validació
```

### Estil de Marques
- **Contorn**: Línia de 2px de gruix
- **Farciment**: Semi-transparent (alpha=0.3)
- **Text**: Font Arial de 12px amb contorn per llegibilitat

## 🏗️ Arquitectura Tècnica

### Components Principals
- **`create_pdf_viewer()`**: Crea la interfície del visualitzador
- **`display_current_page()`**: Renderitza la pàgina actual amb marques
- **`draw_text_overlays()`**: Dibuixa les marques de text sobre la imatge
- **`update_pdf_controls()`**: Actualitza l'estat dels controls de navegació

### Dependències
- **PyMuPDF (fitz)**: Renderització de PDF
- **PIL/Pillow**: Processament d'imatges i dibuix de marques
- **tkinter**: Interfície gràfica i controls

### Gestió de Memòria
- **Càrrega per pàgina**: Només es renderitza la pàgina actual
- **Neteja automàtica**: Imatges anteriors es netegen automàticament
- **Optimització**: Renderitzat eficient amb matrius de transformació

## 🚀 Ús Pràctic

### Exemple d'Ús
1. Obre l'aplicació OCR Viewer
2. Selecciona un document PDF des del botó "📂 Obrir PDF"
3. El PDF es carrega i es mostra a la pestanya "📄 Visualitzador PDF"
4. Navega per les pàgines amb els controls o tecles de fletxa
5. Ajusta el zoom segons necessitis
6. Processa el document amb "🚀 Processar Document"
7. Observa com apareixen les marques de text amb colors de confiança
8. Fes clic sobre qualsevol bloc per veure'n els detalls

### Casos d'Ús Ideals
- **Validació visual d'OCR**: Verificar que el text s'ha detectat correctament
- **Anàlisi de qualitat**: Identificar zones amb baixa confiança
- **Documentació tècnica**: Revisar plànols i documents d'enginyeria
- **Control de qualitat**: Assegurar precisió abans de l'exportació de dades

## 🔄 Integració amb el Sistema

El visualitzador PDF està completament integrat amb les altres funcionalitats de l'aplicació:

- **Pestanya de Text**: Sincronitzada amb la selecció visual
- **Validació de Dades**: Els blocs seleccionats es poden editar directament
- **Exportació**: Les dades visuals i estructurades es mantenen coherents
- **Processament**: Actualització automàtica després de cada processament OCR

Aquest visualitzador proporciona una experiència similar a Google Document AI Demo, amb la comoditat d'estar integrat directament en l'aplicació d'escriptori.
