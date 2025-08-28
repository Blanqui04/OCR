# Models Personalitzats

## Estructura:
- `detection/`: Models de detecció d'objectes (YOLO, etc.)
- `classification/`: Models de classificació de text/imatges
- `segmentation/`: Models de segmentació d'imatges

## Com afegir un model personalitzat:
1. Entrenar el model amb les teves dades
2. Guardar el model en el directori apropiat
3. Actualitzar la configuració amb `ModelManager.register_custom_model()`

## Exemples d'ús:
- Detecció de símbols tècnics específics
- Classificació de tipus de plànol
- Segmentació de zones de text vs dibuix
