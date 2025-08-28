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
        
        self.model_path = model_path
        self.confidence_threshold = 0.5
        self.iou_threshold = 0.45
        self.is_custom_model = False
        
        # Inicialitzar model
        try:
            if model_path and os.path.exists(model_path):
                # Utilitzar model personalitzat
                self.model = YOLO(model_path)
                self.is_custom_model = True
                self.logger.info(f"Model personalitzat carregat: {model_path}")
            else:
                # Utilitzar model per defecte de YOLO per detecció general
                self.model = YOLO("yolov8s.pt")
                self.is_custom_model = False
                self.logger.info("Utilitzant model YOLO per defecte (detecció general)")
                
                # Ajustar classes per model per defecte (COCO dataset)
                self.coco_classes = {
                    0: "person", 14: "bird", 15: "cat", 16: "dog",
                    # Afegim algunes classes que poden ser útils per plànols
                    73: "book", 74: "clock", 75: "scissors"
                }
                
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
                    # Determinar el tipus d'element basat en el model utilitzat
                    if self.is_custom_model:
                        element_type = self.classes.get(int(cls), "unknown")
                    else:
                        # Per model per defecte, interpretar com a elements generals
                        element_type = f"general_object_{int(cls)}"
                        # Assignar confiança menor per elements no específics
                        conf = conf * 0.6  # Reduir confiança per model genèric
                    
                    element = {
                        "type": element_type,
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
                        "model_type": "custom" if self.is_custom_model else "default"
                    }
                    
                    detected_elements.append(element)
            
            self.logger.info(f"Detectats {len(detected_elements)} elements amb model {'personalitzat' if self.is_custom_model else 'per defecte'}")
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
                           output_path: Optional[str] = None, show_labels: bool = True,
                           show_confidence: bool = True, interactive: bool = False) -> np.ndarray:
        """
        Visualitza les deteccions sobre la imatge
        
        Args:
            image_path: Path a la imatge original
            elements: Elements detectats
            output_path: Path per guardar la imatge (opcional)
            show_labels: Mostrar etiquetes dels tipus
            show_confidence: Mostrar valors de confiança
            interactive: Preparar per visualització interactiva
            
        Returns:
            Imatge amb les deteccions dibuixades
        """
        image = cv2.imread(image_path)
        if image is None:
            self.logger.error(f"No es pot carregar la imatge: {image_path}")
            return np.array([])
        
        # Colors per cada classe (BGR format per OpenCV)
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
        
        for i, element in enumerate(elements):
            bbox = element["bbox"]
            element_type = element["type"]
            confidence = element["confidence"]
            text_content = element.get("text", "")
            
            # Coordenades de la caja
            x1, y1 = int(bbox["x1"]), int(bbox["y1"])
            x2, y2 = int(bbox["x2"]), int(bbox["y2"])
            
            # Color per la classe
            color = colors.get(element_type, (128, 128, 128))
            
            # Grossor segons confiança
            thickness = max(1, int(confidence * 4))
            
            # Dibuixar rectangle
            cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)
            
            # Dibuixar punt central
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            cv2.circle(image, (center_x, center_y), 4, color, -1)
            
            # Preparar etiqueta
            label_parts = []
            if show_labels:
                label_parts.append(f"{element_type}")
            if show_confidence:
                label_parts.append(f"{confidence:.2f}")
            if text_content and len(text_content) > 0:
                # Truncar text llarg
                display_text = text_content[:25] + "..." if len(text_content) > 25 else text_content
                label_parts.append(f'"{display_text}"')
            
            if label_parts:
                label = " | ".join(label_parts)
                
                # Calcular mida de l'etiqueta
                font_scale = 0.5
                font_thickness = 1
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)[0]
                
                # Posició de l'etiqueta (evitar sortir de la imatge)
                label_x = max(5, min(x1, image.shape[1] - label_size[0] - 5))
                label_y = max(label_size[1] + 10, y1 - 5)
                
                # Fons semi-transparent per l'etiqueta
                overlay = image.copy()
                cv2.rectangle(overlay, (label_x - 3, label_y - label_size[1] - 5), 
                             (label_x + label_size[0] + 3, label_y + 5), color, -1)
                cv2.addWeighted(overlay, 0.8, image, 0.2, 0, image)
                
                # Text de l'etiqueta
                cv2.putText(image, label, (label_x, label_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), font_thickness)
                
                # Número d'element a la cantonada superior esquerra
                cv2.putText(image, str(i+1), (x1 + 2, y1 + 15), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Afegir llegenda si hi ha elements
        if elements:
            self._add_legend_to_image(image, colors, elements)
        
        # Afegir informació general
        self._add_image_info(image, elements)
        
        # Guardar si s'especifica path
        if output_path:
            cv2.imwrite(output_path, image)
        
        return image
    
    def _add_legend_to_image(self, image: np.ndarray, colors: Dict, elements: List[Dict]):
        """Afegeix una llegenda amb els tipus d'elements detectats"""
        # Obtenir tipus únics detectats
        detected_types = {}
        for element in elements:
            element_type = element["type"]
            if element_type not in detected_types:
                detected_types[element_type] = {'color': colors.get(element_type, (128, 128, 128)), 'count': 0}
            detected_types[element_type]['count'] += 1
        
        if not detected_types:
            return
        
        # Configuració de la llegenda
        legend_y_start = 30
        legend_x = max(10, image.shape[1] - 250)  # Assegurar que la llegenda sigui visible
        line_height = 22
        
        # Calcular dimensions de la llegenda
        max_text_width = 0
        for element_type, info in detected_types.items():
            text = f"{element_type} ({info['count']})"
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
            max_text_width = max(max_text_width, text_size[0])
        
        legend_width = max_text_width + 40
        legend_height = len(detected_types) * line_height + 30
        
        # Fons de la llegenda
        overlay = image.copy()
        cv2.rectangle(overlay, (legend_x - 15, legend_y_start - 20), 
                     (legend_x + legend_width, legend_y_start + legend_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.8, image, 0.2, 0, image)
        
        # Vora de la llegenda
        cv2.rectangle(image, (legend_x - 15, legend_y_start - 20), 
                     (legend_x + legend_width, legend_y_start + legend_height), (255, 255, 255), 2)
        
        # Títol de la llegenda
        cv2.putText(image, "Elements Detectats:", (legend_x - 10, legend_y_start), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Entrades de la llegenda
        y_pos = legend_y_start + 25
        for element_type, info in sorted(detected_types.items()):
            color = info['color']
            count = info['count']
            
            # Rectangle de color
            cv2.rectangle(image, (legend_x - 10, y_pos - 10), (legend_x + 10, y_pos), color, -1)
            cv2.rectangle(image, (legend_x - 10, y_pos - 10), (legend_x + 10, y_pos), (255, 255, 255), 1)
            
            # Text
            text = f"{element_type} ({count})"
            cv2.putText(image, text, (legend_x + 15, y_pos - 2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            
            y_pos += line_height
    
    def _add_image_info(self, image: np.ndarray, elements: List[Dict]):
        """Afegeix informació general de la imatge"""
        # Informació a mostrar
        total_elements = len(elements)
        avg_confidence = sum(elem["confidence"] for elem in elements) / total_elements if total_elements > 0 else 0
        
        # Configuració del panell d'informació
        info_y_start = image.shape[0] - 80
        info_x = 20
        
        # Fons del panell
        overlay = image.copy()
        cv2.rectangle(overlay, (info_x - 10, info_y_start - 10), 
                     (info_x + 300, info_y_start + 70), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.8, image, 0.2, 0, image)
        
        # Vora del panell
        cv2.rectangle(image, (info_x - 10, info_y_start - 10), 
                     (info_x + 300, info_y_start + 70), (255, 255, 255), 2)
        
        # Informació
        cv2.putText(image, f"Total elements: {total_elements}", (info_x, info_y_start + 15), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(image, f"Confiança mitjana: {avg_confidence:.2f}", (info_x, info_y_start + 35), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(image, f"Dimensions: {image.shape[1]}x{image.shape[0]}", (info_x, info_y_start + 55), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def create_interactive_visualization_data(self, image_path: str, elements: List[Dict]) -> Dict:
        """
        Crea dades per visualització interactiva en Streamlit
        
        Args:
            image_path: Path a la imatge
            elements: Elements detectats
            
        Returns:
            Diccionari amb dades per visualització interactiva
        """
        # Carregar imatge original
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"No es pot carregar la imatge: {image_path}")
        
        # Convertir BGR a RGB per Streamlit
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Crear imatge amb visualitzacions
        visualized_image = self.visualize_detections(image_path, elements, show_labels=True, show_confidence=True)
        visualized_image_rgb = cv2.cvtColor(visualized_image, cv2.COLOR_BGR2RGB)
        
        # Preparar dades d'elements per interactivitat
        interactive_elements = []
        for i, element in enumerate(elements):
            bbox = element["bbox"]
            
            interactive_element = {
                'id': i + 1,
                'type': element["type"],
                'confidence': element["confidence"],
                'text': element.get("text", ""),
                'source': element.get("source", "unknown"),
                'bbox': bbox,
                'coordinates': {
                    'x1': int(bbox["x1"]),
                    'y1': int(bbox["y1"]),
                    'x2': int(bbox["x2"]),
                    'y2': int(bbox["y2"]),
                    'width': int(bbox["x2"] - bbox["x1"]),
                    'height': int(bbox["y2"] - bbox["y1"])
                },
                'center': {
                    'x': int((bbox["x1"] + bbox["x2"]) / 2),
                    'y': int((bbox["y1"] + bbox["y2"]) / 2)
                },
                'area': int((bbox["x2"] - bbox["x1"]) * (bbox["y2"] - bbox["y1"])),
            }
            interactive_elements.append(interactive_element)
        
        # Estadístiques de la imatge
        image_stats = {
            'width': image.shape[1],
            'height': image.shape[0],
            'channels': image.shape[2] if len(image.shape) > 2 else 1,
            'total_elements': len(elements),
            'element_types': list(set(elem["type"] for elem in elements)),
            'avg_confidence': sum(elem["confidence"] for elem in elements) / len(elements) if elements else 0,
            'confidence_distribution': {
                'high': len([e for e in elements if e["confidence"] >= 0.8]),
                'medium': len([e for e in elements if 0.5 <= e["confidence"] < 0.8]),
                'low': len([e for e in elements if e["confidence"] < 0.5])
            }
        }
        
        return {
            'original_image': image_rgb,
            'visualized_image': visualized_image_rgb,
            'image_stats': image_stats,
            'elements': interactive_elements,
            'visualization_ready': True
        }
        
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
