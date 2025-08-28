# Dataset d'Entrenament YOLOv8

Aquest directori conté l'estructura del dataset per entrenar models YOLOv8 personalitzats per detectar elements tècnics en plànols.

## Estructura del Dataset

```
data/training/
├── custom_dataset.yaml          # Configuració del dataset
├── images/
│   ├── train/                   # Imatges d'entrenament
│   ├── val/                     # Imatges de validació
│   └── test/                    # Imatges de test
├── labels/
│   ├── train/                   # Etiquetes d'entrenament (format YOLO)
│   ├── val/                     # Etiquetes de validació
│   └── test/                    # Etiquetes de test
└── README_dataset.md           # Aquest fitxer
```

## Classes Definides

1. **cota** (0): Dimensions i mesures
2. **tolerancia** (1): Toleràncies geomètriques
3. **simbol** (2): Símbols tècnics

## Format de les Etiquetes

Les etiquetes segueixen el format YOLO:
```
class_id center_x center_y width height
```

On tots els valors són normalitzats (0-1).

## Instruccions d'Ús

1. **Afegir Imatges:**
   - Col·loca les imatges `.jpg`, `.png` a les carpetes corresponents
   - Distribueix: 70% train, 20% val, 10% test

2. **Afegir Etiquetes:**
   - Crea fitxers `.txt` amb el mateix nom que les imatges
   - Una línia per objecte detectat
   - Format: `class_id x_center y_center width height`

3. **Entrenar Model:**
   ```bash
   python src/ai_model/train_custom_yolo.py --data data/training/custom_dataset.yaml --epochs 100
   ```

## Eines d'Anotació Recomanades

- **Labelme**: Per crear anotacions i convertir a format YOLO
- **CVAT**: Per projectes d'anotació col·laboratius
- **LabelImg**: Eina simple per anotació d'objectes

## Exemples d'Anotació

### Exemple de fitxer d'etiqueta (exemple.txt):
```
0 0.5 0.3 0.2 0.1    # Cota al centre-esquerra
1 0.8 0.7 0.15 0.08  # Tolerància a la dreta-baix
2 0.2 0.2 0.1 0.1    # Símbol a l'esquerra-dalt
```

## Validació del Dataset

Abans d'entrenar, assegura't que:
- [ ] Totes les imatges tenen les etiquetes corresponents
- [ ] Les coordenades estan normalitzades (0-1)
- [ ] Les classes estan correctament assignades (0, 1, 2)
- [ ] La distribució train/val/test és adequada
