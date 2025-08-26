"""
Sistema d'entrenament per al model personalitzat de detecció d'elements tècnics
"""

import os
import yaml
import shutil
from pathlib import Path
from ultralytics import YOLO
import logging
from typing import Dict, List, Optional
import json

class ModelTrainer:
    """
    Entrenador per al model personalitzat de detecció d'elements tècnics
    """
    
    def __init__(self, project_dir: str):
        """
        Inicialitza l'entrenador
        
        Args:
            project_dir: Directori arrel del projecte
        """
        self.project_dir = Path(project_dir)
        self.training_dir = self.project_dir / "data" / "training"
        self.models_dir = self.project_dir / "models"
        self.logger = logging.getLogger(__name__)
        
        # Crear directoris necessaris
        self.setup_directories()
    
    def setup_directories(self):
        """Crea l'estructura de directoris per l'entrenament"""
        dirs_to_create = [
            self.training_dir / "images" / "train",
            self.training_dir / "images" / "val", 
            self.training_dir / "images" / "test",
            self.training_dir / "labels" / "train",
            self.training_dir / "labels" / "val",
            self.training_dir / "labels" / "test",
            self.models_dir
        ]
        
        for dir_path in dirs_to_create:
            dir_path.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Directori creat: {dir_path}")
    
    def create_dataset_config(self) -> str:
        """
        Crea el fitxer YAML de configuració del dataset per YOLOv8
        
        Returns:
            Path al fitxer de configuració creat
        """
        config = {
            'path': str(self.training_dir.absolute()),
            'train': 'images/train',
            'val': 'images/val',
            'test': 'images/test',
            
            'names': {
                0: 'dimension_text',
                1: 'dimension_line', 
                2: 'arrow_head',
                3: 'geometric_tolerance',
                4: 'info_table',
                5: 'revision_table',
                6: 'title_block',
                7: 'section_line',
                8: 'center_line',
                9: 'construction_line',
                10: 'weld_symbol',
                11: 'surface_finish',
                12: 'datum_reference'
            }
        }
        
        config_path = self.training_dir / "dataset.yaml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        self.logger.info(f"Configuració del dataset creada: {config_path}")
        return str(config_path)
    
    def train_model(self, 
                   epochs: int = 100,
                   batch_size: int = 16,
                   img_size: int = 640,
                   model_size: str = 'yolov8s.pt',
                   device: str = 'auto') -> str:
        """
        Entrena el model YOLOv8 personalitzat
        
        Args:
            epochs: Nombre d'èpoques d'entrenament
            batch_size: Mida del batch
            img_size: Mida de les imatges d'entrenament
            model_size: Model base (yolov8n.pt, yolov8s.pt, yolov8m.pt, yolov8l.pt, yolov8x.pt)
            device: Dispositiu ('cpu', 'cuda', 'auto')
            
        Returns:
            Path al model entrenat
        """
        try:
            # Crear configuració del dataset
            dataset_config = self.create_dataset_config()
            
            # Inicialitzar model base
            model = YOLO(model_size)
            
            # Entrenar
            self.logger.info("Iniciant entrenament del model...")
            results = model.train(
                data=dataset_config,
                epochs=epochs,
                batch=batch_size,
                imgsz=img_size,
                device=device,
                project=str(self.models_dir),
                name='technical_drawing_detector',
                save_period=10,  # Guardar checkpoint cada 10 èpoques
                patience=20,     # Early stopping si no millora en 20 èpoques
                workers=4,
                verbose=True
            )
            
            # Path al millor model entrenat
            best_model_path = self.models_dir / "technical_drawing_detector" / "weights" / "best.pt"
            
            self.logger.info(f"Entrenament completat. Millor model: {best_model_path}")
            return str(best_model_path)
            
        except Exception as e:
            self.logger.error(f"Error durant l'entrenament: {e}")
            raise
    
    def validate_model(self, model_path: str) -> Dict:
        """
        Valida el model entrenat
        
        Args:
            model_path: Path al model entrenat
            
        Returns:
            Mètriques de validació
        """
        try:
            model = YOLO(model_path)
            
            # Executar validació
            self.logger.info("Validant model...")
            results = model.val(
                data=self.create_dataset_config(),
                device='auto'
            )
            
            # Extreure mètriques
            metrics = {
                'mAP50': float(results.box.map50),
                'mAP50-95': float(results.box.map),
                'precision': float(results.box.mp),
                'recall': float(results.box.mr),
                'fitness': float(results.fitness)
            }
            
            self.logger.info(f"Mètriques de validació: {metrics}")
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error durant la validació: {e}")
            return {}
    
    def export_model(self, model_path: str, formats: List[str] = None) -> List[str]:
        """
        Exporta el model a diferents formats
        
        Args:
            model_path: Path al model entrenat
            formats: Llista de formats ('onnx', 'torchscript', 'openvino', etc.)
            
        Returns:
            Llista de paths als models exportats
        """
        if formats is None:
            formats = ['onnx', 'torchscript']
        
        exported_models = []
        
        try:
            model = YOLO(model_path)
            
            for format_type in formats:
                self.logger.info(f"Exportant model a format {format_type}...")
                exported_path = model.export(format=format_type)
                exported_models.append(str(exported_path))
                self.logger.info(f"Model exportat: {exported_path}")
                
        except Exception as e:
            self.logger.error(f"Error durant l'exportació: {e}")
        
        return exported_models


class DatasetManager:
    """
    Gestor per preparar i organitzar el dataset d'entrenament
    """
    
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.training_dir = self.project_dir / "data" / "training"
        self.logger = logging.getLogger(__name__)
    
    def convert_labelimg_to_yolo(self, labelimg_dir: str, output_dir: str):
        """
        Converteix anotacions de LabelImg (XML) a format YOLO (TXT)
        
        Args:
            labelimg_dir: Directori amb anotacions XML de LabelImg
            output_dir: Directori de sortida per les anotacions YOLO
        """
        import xml.etree.ElementTree as ET
        
        labelimg_path = Path(labelimg_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Mapatge de noms de classes a IDs
        class_mapping = {
            'dimension_text': 0,
            'dimension_line': 1,
            'arrow_head': 2,
            'geometric_tolerance': 3,
            'info_table': 4,
            'revision_table': 5,
            'title_block': 6,
            'section_line': 7,
            'center_line': 8,
            'construction_line': 9,
            'weld_symbol': 10,
            'surface_finish': 11,
            'datum_reference': 12
        }
        
        for xml_file in labelimg_path.glob("*.xml"):
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Obtenir dimensions de la imatge
            size = root.find('size')
            img_width = int(size.find('width').text)
            img_height = int(size.find('height').text)
            
            # Convertir cada objecte anotat
            yolo_annotations = []
            
            for obj in root.findall('object'):
                class_name = obj.find('name').text
                if class_name not in class_mapping:
                    self.logger.warning(f"Classe desconeguda: {class_name}")
                    continue
                
                class_id = class_mapping[class_name]
                
                # Coordenades del bounding box
                bbox = obj.find('bndbox')
                xmin = int(bbox.find('xmin').text)
                ymin = int(bbox.find('ymin').text)
                xmax = int(bbox.find('xmax').text)
                ymax = int(bbox.find('ymax').text)
                
                # Convertir a format YOLO (normalitzat)
                x_center = (xmin + xmax) / 2.0 / img_width
                y_center = (ymin + ymax) / 2.0 / img_height
                width = (xmax - xmin) / img_width
                height = (ymax - ymin) / img_height
                
                yolo_annotations.append(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")
            
            # Guardar anotacions YOLO
            txt_file = output_path / f"{xml_file.stem}.txt"
            with open(txt_file, 'w') as f:
                f.write('\n'.join(yolo_annotations))
            
            self.logger.info(f"Convertit: {xml_file} -> {txt_file}")
    
    def split_dataset(self, images_dir: str, labels_dir: str, 
                     train_ratio: float = 0.7, val_ratio: float = 0.2):
        """
        Divideix el dataset en train/validation/test
        
        Args:
            images_dir: Directori amb imatges
            labels_dir: Directori amb etiquetes
            train_ratio: Proporció per entrenament
            val_ratio: Proporció per validació (la resta serà test)
        """
        import random
        
        images_path = Path(images_dir)
        labels_path = Path(labels_dir)
        
        # Obtenir llista d'imatges
        image_files = list(images_path.glob("*.png")) + list(images_path.glob("*.jpg"))
        random.shuffle(image_files)
        
        total_images = len(image_files)
        train_count = int(total_images * train_ratio)
        val_count = int(total_images * val_ratio)
        
        # Dividir en conjunts
        train_files = image_files[:train_count]
        val_files = image_files[train_count:train_count + val_count]
        test_files = image_files[train_count + val_count:]
        
        # Copiar fitxers als directoris corresponents
        for split_name, file_list in [("train", train_files), ("val", val_files), ("test", test_files)]:
            img_split_dir = self.training_dir / "images" / split_name
            lbl_split_dir = self.training_dir / "labels" / split_name
            
            for img_file in file_list:
                # Copiar imatge
                shutil.copy2(img_file, img_split_dir / img_file.name)
                
                # Copiar etiqueta corresponent
                lbl_file = labels_path / f"{img_file.stem}.txt"
                if lbl_file.exists():
                    shutil.copy2(lbl_file, lbl_split_dir / lbl_file.name)
                else:
                    # Crear fitxer d'etiqueta buit si no existeix
                    (lbl_split_dir / lbl_file.name).touch()
        
        self.logger.info(f"Dataset dividit: {len(train_files)} train, {len(val_files)} val, {len(test_files)} test")


def create_annotation_guide():
    """
    Crea una guia per anotar elements tècnics
    """
    guide = """
# Guia d'Anotació per Elements Tècnics

## Classes d'Elements a Anotar:

### 1. dimension_text (Text de Cotes)
- Números i text que indiquen mesures
- Exemples: "25.0", "Ø12", "R5", "45°"
- Incloure el text complet dins la caixa

### 2. dimension_line (Línies de Cota)
- Línies que delimiten les mesures
- Línies amb fletxes als extrems
- Línies d'extensió

### 3. arrow_head (Caps de Fletxa)
- Fletxes al final de línies de cota
- Fletxes indicadores de direcció

### 4. geometric_tolerance (Toleràncies Geomètriques)
- Símbols com ⌖, ⊥, ∥, ○, etc.
- Caixes amb toleràncies de forma

### 5. info_table (Taules d'Informació)
- Taules amb dades de la peça
- Blocs d'informació general

### 6. revision_table (Taules de Revisió)
- Historial de revisions del plànol
- Taules amb dates i canvis

### 7. title_block (Bloc de Títol)
- Capcera principal del plànol
- Informació del projecte i empresa

### 8. section_line (Línies de Secció)
- Línies que indiquen talls o seccions
- Marcades amb lletres (A-A, B-B)

### 9. center_line (Línies de Centre)
- Línies discontinues que marquen centres
- Eixos de simetria

### 10. construction_line (Línies de Construcció)
- Línies auxiliars de dibuix
- Línies de projecció

### 11. weld_symbol (Símbols de Soldadura)
- Símbols de tipus de soldadura
- Indicacions de processos de soldadura

### 12. surface_finish (Acabats Superficials)
- Símbol de rugositat (Ra, Rz)
- Indicacions de tractaments superficials

### 13. datum_reference (Referències de Datum)
- Lletres o símbols de referència (A, B, C)
- Sistemes de coordenades

## Consells d'Anotació:

1. **Precisió**: Les caixes han de ser ajustades però no massa petites
2. **Consistència**: Utilitza sempre la mateixa classe per elements similars
3. **Completesa**: Anota tots els elements visibles d'una classe
4. **Qualitat**: Revisa les anotacions abans de passar a la següent imatge

## Eines Recomanades:

- **LabelImg**: Per anotacions ràpides amb interfície gràfica
- **LabelMe**: Per anotacions més complexes
- **Roboflow**: Plataforma online amb col·laboració
"""
    return guide


if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Exemple d'ús del sistema d'entrenament
    project_dir = Path(__file__).parent.parent.parent
    
    # Crear entrenador
    trainer = ModelTrainer(str(project_dir))
    
    # Crear gestor de dataset
    dataset_manager = DatasetManager(str(project_dir))
    
    print("Sistema d'entrenament del model personalitzat configurat!")
    print("\nPassos següents:")
    print("1. Recopilar i anotar imatges de plànols")
    print("2. Convertir anotacions a format YOLO")
    print("3. Dividir dataset en train/val/test")
    print("4. Executar entrenament")
    
    # Crear guia d'anotació
    guide = create_annotation_guide()
    guide_path = project_dir / "ANNOTATION_GUIDE.md"
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide)
    
    print(f"\nGuia d'anotació creada: {guide_path}")
