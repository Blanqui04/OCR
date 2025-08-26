"""
Model personalitzat d'IA per detecció d'elements tècnics en plànols
Utilitza YOLOv8 per detectar i classificar elements com cotes, toleràncies, taules, etc.
"""

import os
import torch
import numpy as np
import cv2
from ultralytics import YOLO
from pathlib import Path
import json
from typing import List, Dict, Tuple, Optional
import logging

class TechnicalDrawingDetector:
    """
    Detector d'elements tècnics en plànols basat en YOLOv8
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Inicialitza el detector
        
        Args:
            model_path: Path al model entrenat. Si és None, utilitza el model preentrenat
        """
        self.logger = logging.getLogger(__name__)
        
        # Categories d'elements tècnics que podem detectar
        self.classes = {
            0: "dimension_text",        # Text de cotes
            1: "dimension_line",        # Línies de cota
            2: "arrow_head",           # Caps de fletxa
            3: "geometric_tolerance",   # Símbols de tolerància geomètrica
            4: "info_table",           # Taules d'informació
            5: "revision_table",       # Taules de revisió
            6: "title_block",          # Bloc de títol
            7: "section_line",         # Línies de secció
            8: "center_line",          # Línies de centre
            9: "construction_line",    # Línies de construcció
            10: "weld_symbol",         # Símbols de soldadura
            11: "surface_finish",      # Acabats superficials
            12: "datum_reference",     # Referències de datum
        }
        
        self.model_path = model_path or "yolov8s.pt"  # Model preentrenat per defecte
        self.confidence_threshold = 0.5
        self.iou_threshold = 0.45
        
        # Inicialitzar model
        try:
            self.model = YOLO(self.model_path)
            self.logger.info(f"Model carregat: {self.model_path}")
        except Exception as e:
            self.logger.error(f"Error carregant model: {e}")
            self.model = None
    
    def detect_elements(self, image_path: str) -> List[Dict]:
        """
        Detecta elements tècnics en una imatge
        
        Args:
            image_path: Path a la imatge del plànol
            
        Returns:
            Lista d'elements detectats amb les seves coordenades i tipus
        """
        if not self.model:
            self.logger.error("Model no disponible")
            return []
        
        try:
            # Executar detecció
            results = self.model(image_path, 
                               conf=self.confidence_threshold,
                               iou=self.iou_threshold)
            
            detected_elements = []
            
            if len(results) > 0 and results[0].boxes is not None:
                boxes = results[0].boxes.xyxy.cpu().numpy()    # Coordenades
                classes = results[0].boxes.cls.cpu().numpy()   # Classes
                confs = results[0].boxes.conf.cpu().numpy()    # Confiança
                
                for box, cls, conf in zip(boxes, classes, confs):
                    element = {
                        "type": self.classes.get(int(cls), "unknown"),
                        "bbox": {
                            "x1": float(box[0]),
                            "y1": float(box[1]), 
                            "x2": float(box[2]),
                            "y2": float(box[3])
                        },
                        "confidence": float(conf),
                        "class_id": int(cls),
                        "center": {
                            "x": float((box[0] + box[2]) / 2),
                            "y": float((box[1] + box[3]) / 2)
                        },
                        "width": float(box[2] - box[0]),
                        "height": float(box[3] - box[1])
                    }
                    detected_elements.append(element)
            
            self.logger.info(f"Detectats {len(detected_elements)} elements")
            return detected_elements
            
        except Exception as e:
            self.logger.error(f"Error en detecció: {e}")
            return []
    
    def filter_by_confidence(self, elements: List[Dict], min_confidence: float) -> Tuple[List[Dict], List[Dict]]:
        """
        Separa elements per confiança
        
        Args:
            elements: Elements detectats
            min_confidence: Llindar mínim de confiança
            
        Returns:
            Tupla (elements_alta_confiança, elements_baixa_confiança)
        """
        high_conf = [e for e in elements if e["confidence"] >= min_confidence]
        low_conf = [e for e in elements if e["confidence"] < min_confidence]
        
        return high_conf, low_conf
    
    def visualize_detections(self, image_path: str, elements: List[Dict], 
                           output_path: Optional[str] = None) -> np.ndarray:
        """
        Visualitza les deteccions sobre la imatge
        
        Args:
            image_path: Path a la imatge original
            elements: Elements detectats
            output_path: Path per guardar la imatge (opcional)
            
        Returns:
            Imatge amb les deteccions dibuixades
        """
        image = cv2.imread(image_path)
        if image is None:
            self.logger.error(f"No es pot carregar la imatge: {image_path}")
            return np.array([])
        
        # Colors per cada classe
        colors = {
            "dimension_text": (0, 255, 0),      # Verd
            "dimension_line": (255, 0, 0),      # Blau
            "arrow_head": (0, 0, 255),          # Vermell
            "geometric_tolerance": (255, 255, 0), # Cian
            "info_table": (255, 0, 255),        # Magenta
            "revision_table": (0, 255, 255),    # Groc
            "title_block": (128, 0, 128),       # Púrpura
            "section_line": (255, 165, 0),      # Taronja
            "center_line": (0, 128, 255),       # Blau clar
            "construction_line": (128, 128, 128), # Gris
            "weld_symbol": (255, 20, 147),      # Rosa fosc
            "surface_finish": (50, 205, 50),    # Verd lima
            "datum_reference": (138, 43, 226),  # Blau violeta
        }
        
        for element in elements:
            bbox = element["bbox"]
            element_type = element["type"]
            confidence = element["confidence"]
            
            # Coordenades de la caja
            x1, y1 = int(bbox["x1"]), int(bbox["y1"])
            x2, y2 = int(bbox["x2"]), int(bbox["y2"])
            
            # Color per la classe
            color = colors.get(element_type, (128, 128, 128))
            
            # Dibuixar rectangle
            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            
            # Etiqueta amb tipus i confiança
            label = f"{element_type}: {confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            
            # Fons per l'etiqueta
            cv2.rectangle(image, (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), color, -1)
            
            # Text de l'etiqueta
            cv2.putText(image, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Guardar si s'especifica output_path
        if output_path:
            cv2.imwrite(output_path, image)
            self.logger.info(f"Imatge amb deteccions guardada: {output_path}")
        
        return image


class SpatialRelationshipAnalyzer:
    """
    Analitzador de relacions espacials entre elements detectats
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_distance(self, element1: Dict, element2: Dict) -> float:
        """Calcula distància entre centres d'elements"""
        center1 = element1["center"]
        center2 = element2["center"]
        
        return np.sqrt((center1["x"] - center2["x"])**2 + 
                      (center1["y"] - center2["y"])**2)
    
    def are_aligned(self, element1: Dict, element2: Dict, tolerance: float = 20) -> Dict[str, bool]:
        """
        Comprova si dos elements estan alineats
        
        Returns:
            Dict amb alineació horizontal, vertical i diagonal
        """
        center1 = element1["center"]
        center2 = element2["center"]
        
        horizontal = abs(center1["y"] - center2["y"]) <= tolerance
        vertical = abs(center1["x"] - center2["x"]) <= tolerance
        
        # Alineació diagonal (45 graus aproximadament)
        dx = abs(center1["x"] - center2["x"])
        dy = abs(center1["y"] - center2["y"])
        diagonal = abs(dx - dy) <= tolerance
        
        return {
            "horizontal": horizontal,
            "vertical": vertical,
            "diagonal": diagonal
        }
    
    def find_nearby_elements(self, target_element: Dict, all_elements: List[Dict], 
                           max_distance: float = 100) -> List[Dict]:
        """Troba elements propers a un element target"""
        nearby = []
        
        for element in all_elements:
            if element == target_element:
                continue
                
            distance = self.calculate_distance(target_element, element)
            if distance <= max_distance:
                element_with_distance = element.copy()
                element_with_distance["distance_to_target"] = distance
                nearby.append(element_with_distance)
        
        # Ordenar per distància
        nearby.sort(key=lambda x: x["distance_to_target"])
        return nearby
    
    def link_dimension_text_to_line(self, texts: List[Dict], lines: List[Dict]) -> List[Dict]:
        """
        Vincula texts de cotes amb les seves línies corresponents
        """
        linked = []
        
        for text in texts:
            if text["type"] != "dimension_text":
                continue
                
            best_line = None
            min_distance = float('inf')
            
            for line in lines:
                if line["type"] != "dimension_line":
                    continue
                
                distance = self.calculate_distance(text, line)
                alignment = self.are_aligned(text, line, tolerance=30)
                
                # Preferir línies alineades i properes
                if (alignment["horizontal"] or alignment["vertical"]) and distance < min_distance:
                    min_distance = distance
                    best_line = line
            
            if best_line and min_distance < 80:  # Distància màxima acceptable
                linked.append({
                    "text_element": text,
                    "line_element": best_line,
                    "distance": min_distance,
                    "relationship": "dimension_pair"
                })
        
        return linked
    
    def group_table_elements(self, elements: List[Dict]) -> List[Dict]:
        """
        Agrupa elements que formen part de taules
        """
        table_elements = [e for e in elements if "table" in e["type"]]
        groups = []
        
        for table in table_elements:
            # Buscar elements de text propers que formin part de la taula
            nearby_texts = self.find_nearby_elements(
                table, 
                [e for e in elements if e["type"] == "dimension_text"],
                max_distance=200
            )
            
            groups.append({
                "table_element": table,
                "related_texts": nearby_texts,
                "group_type": "table_group"
            })
        
        return groups


def create_training_dataset_config():
    """
    Crea el fitxer de configuració per entrenar YOLOv8
    """
    config = {
        "path": "data/training",  # Path relatiu al directori del projecte
        "train": "images/train",
        "val": "images/val",
        "test": "images/test",
        
        "names": {
            0: "dimension_text",
            1: "dimension_line",
            2: "arrow_head",
            3: "geometric_tolerance",
            4: "info_table",
            5: "revision_table",
            6: "title_block",
            7: "section_line",
            8: "center_line",
            9: "construction_line",
            10: "weld_symbol",
            11: "surface_finish",
            12: "datum_reference"
        }
    }
    
    return config


if __name__ == "__main__":
    # Exemple d'ús del detector
    detector = TechnicalDrawingDetector()
    
    # Detectar elements en una imatge
    image_path = "data/images/page_1.png"
    if os.path.exists(image_path):
        elements = detector.detect_elements(image_path)
        
        print(f"Detectats {len(elements)} elements:")
        for element in elements:
            print(f"- {element['type']}: confiança {element['confidence']:.2f}")
        
        # Visualitzar deteccions
        output_path = "data/output/detections_visualized.png"
        detector.visualize_detections(image_path, elements, output_path)
        
        # Analitzar relacions espacials
        analyzer = SpatialRelationshipAnalyzer()
        
        # Vincular texts amb línies
        texts = [e for e in elements if e["type"] == "dimension_text"]
        lines = [e for e in elements if e["type"] == "dimension_line"]
        linked = analyzer.link_dimension_text_to_line(texts, lines)
        
        print(f"\nVinculacions trobades: {len(linked)}")
        for link in linked:
            print(f"- Text-Línia: distància {link['distance']:.1f}px")
