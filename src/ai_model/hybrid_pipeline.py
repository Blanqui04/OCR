"""
Integració del model d'IA amb el pipeline existent
Combina la detecció basada en regles amb la detecció amb IA
"""

import os
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

from technical_detector import TechnicalDrawingDetector, SpatialRelationshipAnalyzer


class HybridDetectionPipeline:
    """
    Pipeline híbrid que combina detecció basada en regles amb IA
    """
    
    def __init__(self, project_dir: str, ai_model_path: Optional[str] = None):
        """
        Inicialitza el pipeline híbrid
        
        Args:
            project_dir: Directori del projecte
            ai_model_path: Path al model d'IA entrenat (opcional)
        """
        self.project_dir = Path(project_dir)
        self.logger = logging.getLogger(__name__)
        
        # Inicialitzar detector d'IA
        self.ai_detector = None
        if ai_model_path and os.path.exists(ai_model_path):
            try:
                self.ai_detector = TechnicalDrawingDetector(ai_model_path)
                self.logger.info(f"Model d'IA carregat: {ai_model_path}")
            except Exception as e:
                self.logger.error(f"Error carregant model d'IA: {e}")
        else:
            self.logger.info("Model d'IA no disponible, utilitzant detecció basada en regles")
        
        # Analitzador de relacions espacials
        self.spatial_analyzer = SpatialRelationshipAnalyzer()
        
        # Configuració de confiança
        self.ai_confidence_threshold = 0.7
        self.human_review_threshold = 0.5
    
    def detect_with_ai(self, image_path: str) -> Tuple[List[Dict], List[Dict]]:
        """
        Detecta elements amb IA i separa per confiança
        
        Args:
            image_path: Path a la imatge
            
        Returns:
            Tupla (elements_alta_confiança, elements_baixa_confiança)
        """
        if not self.ai_detector:
            return [], []
        
        try:
            # Detectar tots els elements
            all_elements = self.ai_detector.detect_elements(image_path)
            
            # Separar per confiança
            high_conf, low_conf = self.ai_detector.filter_by_confidence(
                all_elements, self.ai_confidence_threshold
            )
            
            self.logger.info(f"IA: {len(high_conf)} elements alta confiança, {len(low_conf)} baixa confiança")
            return high_conf, low_conf
            
        except Exception as e:
            self.logger.error(f"Error en detecció IA: {e}")
            return [], []
    
    def detect_with_rules(self, ocr_data: List[Dict], image_shape: Tuple[int, int]) -> List[Dict]:
        """
        Detecta elements amb regles tradicionals (sistem actual)
        
        Args:
            ocr_data: Dades d'OCR
            image_shape: Dimensions de la imatge
            
        Returns:
            Elements detectats amb regles
        """
        rule_based_elements = []
        
        # Importar funcions del sistema actual
        try:
            import sys
            sys.path.append(str(self.project_dir / "src"))
            
            from data_extractor import extract_technical_data
            from dimension_linker import detect_lines, link_text_to_lines
            
            # Extreure dades tècniques
            tech_data = extract_technical_data(ocr_data)
            
            # Convertir a format estàndard per compatibilitat
            for dim in tech_data.get("dimensions", []):
                element = {
                    "type": "dimension_text",
                    "bbox": dim.get("bbox", {}),
                    "confidence": dim.get("confidence", 0.8),  # Confiança alta per regles
                    "text": dim.get("text", ""),
                    "source": "rules",
                    "class_id": 0
                }
                rule_based_elements.append(element)
            
            for note in tech_data.get("notes", []):
                element = {
                    "type": "info_text", 
                    "bbox": note.get("bbox", {}),
                    "confidence": 0.7,
                    "text": note.get("text", ""),
                    "source": "rules",
                    "class_id": 4
                }
                rule_based_elements.append(element)
            
            self.logger.info(f"Regles: {len(rule_based_elements)} elements detectats")
            
        except Exception as e:
            self.logger.error(f"Error en detecció amb regles: {e}")
        
        return rule_based_elements
    
    def merge_detections(self, ai_elements: List[Dict], rule_elements: List[Dict]) -> List[Dict]:
        """
        Combina deteccions d'IA i regles, eliminant duplicats
        
        Args:
            ai_elements: Elements detectats per IA
            rule_elements: Elements detectats per regles
            
        Returns:
            Elements combinats sense duplicats
        """
        merged_elements = []
        
        # Afegir elements d'IA (prioritat alta)
        merged_elements.extend(ai_elements)
        
        # Afegir elements de regles si no hi ha solapament amb IA
        for rule_elem in rule_elements:
            has_overlap = False
            
            for ai_elem in ai_elements:
                if self._elements_overlap(rule_elem, ai_elem):
                    has_overlap = True
                    break
            
            if not has_overlap:
                rule_elem["source"] = "rules"
                merged_elements.append(rule_elem)
        
        self.logger.info(f"Combinat: {len(merged_elements)} elements totals")
        return merged_elements
    
    def _elements_overlap(self, elem1: Dict, elem2: Dict, overlap_threshold: float = 0.5) -> bool:
        """
        Comprova si dos elements se superposen significativament
        
        Args:
            elem1, elem2: Elements a comparar
            overlap_threshold: Llindar de solapament (IoU)
            
        Returns:
            True si se superposen
        """
        try:
            bbox1 = elem1.get("bbox", {})
            bbox2 = elem2.get("bbox", {})
            
            # Convertir a format estàndard si cal
            if "x1" in bbox1:
                # Format IA (x1, y1, x2, y2)
                x1_1, y1_1, x2_1, y2_1 = bbox1["x1"], bbox1["y1"], bbox1["x2"], bbox1["y2"]
            else:
                # Format regles (x, y, width, height)
                x1_1 = bbox1.get("x", 0)
                y1_1 = bbox1.get("y", 0)
                x2_1 = x1_1 + bbox1.get("width", 0)
                y2_1 = y1_1 + bbox1.get("height", 0)
            
            if "x1" in bbox2:
                x1_2, y1_2, x2_2, y2_2 = bbox2["x1"], bbox2["y1"], bbox2["x2"], bbox2["y2"]
            else:
                x1_2 = bbox2.get("x", 0)
                y1_2 = bbox2.get("y", 0)
                x2_2 = x1_2 + bbox2.get("width", 0)
                y2_2 = y1_2 + bbox2.get("height", 0)
            
            # Calcular IoU (Intersection over Union)
            x_left = max(x1_1, x1_2)
            y_top = max(y1_1, y1_2)
            x_right = min(x2_1, x2_2)
            y_bottom = min(y2_1, y2_2)
            
            if x_right < x_left or y_bottom < y_top:
                return False
            
            intersection_area = (x_right - x_left) * (y_bottom - y_top)
            area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
            area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
            union_area = area1 + area2 - intersection_area
            
            if union_area == 0:
                return False
                
            iou = intersection_area / union_area
            return iou > overlap_threshold
            
        except Exception as e:
            self.logger.error(f"Error calculant solapament: {e}")
            return False
    
    def analyze_relationships(self, elements: List[Dict]) -> List[Dict]:
        """
        Analitza relacions espacials entre elements detectats
        
        Args:
            elements: Elements detectats
            
        Returns:
            Relacions trobades
        """
        relationships = []
        
        try:
            # Separar elements per tipus
            texts = [e for e in elements if "text" in e["type"]]
            lines = [e for e in elements if "line" in e["type"]]
            
            # Vincular texts amb línies
            text_line_links = self.spatial_analyzer.link_dimension_text_to_line(texts, lines)
            relationships.extend(text_line_links)
            
            # Agrupar elements de taules
            table_groups = self.spatial_analyzer.group_table_elements(elements)
            relationships.extend(table_groups)
            
            self.logger.info(f"Trobades {len(relationships)} relacions")
            
        except Exception as e:
            self.logger.error(f"Error analitzant relacions: {e}")
        
        return relationships
    
    def create_human_review_tasks(self, low_confidence_elements: List[Dict]) -> List[Dict]:
        """
        Crea tasques per revisió humana dels elements de baixa confiança
        
        Args:
            low_confidence_elements: Elements que necessiten revisió
            
        Returns:
            Llista de tasques per l'usuari
        """
        review_tasks = []
        
        for i, element in enumerate(low_confidence_elements):
            task = {
                "task_id": f"review_{i}",
                "element": element,
                "confidence": element.get("confidence", 0),
                "suggested_type": element.get("type", "unknown"),
                "review_question": f"És correcte que aquest element sigui '{element.get('type', 'unknown')}'?",
                "bbox": element.get("bbox", {}),
                "needs_human_input": True
            }
            review_tasks.append(task)
        
        return review_tasks
    
    def process_image_hybrid(self, image_path: str, ocr_data: List[Dict], 
                           image_shape: Tuple[int, int]) -> Dict:
        """
        Processa una imatge amb detecció híbrida (IA + regles)
        
        Args:
            image_path: Path a la imatge
            ocr_data: Dades d'OCR
            image_shape: Dimensions de la imatge
            
        Returns:
            Resultats de la detecció híbrida
        """
        results = {
            "ai_elements": [],
            "rule_elements": [],
            "merged_elements": [],
            "low_confidence_elements": [],
            "relationships": [],
            "human_review_tasks": [],
            "processing_metadata": {
                "ai_available": self.ai_detector is not None,
                "total_detections": 0,
                "high_confidence_ratio": 0.0
            }
        }
        
        try:
            # 1. Detecció amb IA (si disponible)
            if self.ai_detector:
                ai_high_conf, ai_low_conf = self.detect_with_ai(image_path)
                results["ai_elements"] = ai_high_conf
                results["low_confidence_elements"] = ai_low_conf
            
            # 2. Detecció amb regles
            rule_elements = self.detect_with_rules(ocr_data, image_shape)
            results["rule_elements"] = rule_elements
            
            # 3. Combinar deteccions
            merged = self.merge_detections(results["ai_elements"], rule_elements)
            results["merged_elements"] = merged
            
            # 4. Analitzar relacions
            relationships = self.analyze_relationships(merged)
            results["relationships"] = relationships
            
            # 5. Crear tasques de revisió humana
            review_tasks = self.create_human_review_tasks(results["low_confidence_elements"])
            results["human_review_tasks"] = review_tasks
            
            # 6. Actualitzar metadades
            total_detections = len(merged) + len(results["low_confidence_elements"])
            results["processing_metadata"].update({
                "total_detections": total_detections,
                "high_confidence_ratio": len(merged) / max(total_detections, 1),
                "needs_human_review": len(review_tasks) > 0
            })
            
            self.logger.info(f"Processament híbrid completat: {total_detections} elements")
            
        except Exception as e:
            self.logger.error(f"Error en processament híbrid: {e}")
        
        return results


class ContinuousLearningManager:
    """
    Gestor per l'aprenentatge continu del model
    """
    
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.feedback_dir = self.project_dir / "data" / "user_feedback"
        self.feedback_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
    
    def save_user_correction(self, element: Dict, correct_type: str, user_id: str = "default"):
        """
        Guarda una correcció de l'usuari per reentrenament futur
        
        Args:
            element: Element corregit
            correct_type: Tipus correcte segons l'usuari
            user_id: ID de l'usuari que fa la correcció
        """
        correction = {
            "timestamp": str(pd.Timestamp.now().isoformat()),
            "user_id": user_id,
            "original_prediction": element.get("type", "unknown"),
            "original_confidence": element.get("confidence", 0),
            "corrected_type": correct_type,
            "bbox": element.get("bbox", {}),
            "image_info": element.get("image_info", {}),
            "feedback_type": "correction"
        }
        
        # Guardar en fitxer amb timestamp
        feedback_file = self.feedback_dir / f"correction_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(feedback_file, 'w') as f:
            json.dump(correction, f, indent=2)
        
        self.logger.info(f"Correcció guardada: {feedback_file}")
    
    def collect_training_data(self) -> List[Dict]:
        """
        Recopila totes les correccions per crear nou dataset d'entrenament
        
        Returns:
            Llista de correccions per reentrenament
        """
        corrections = []
        
        for feedback_file in self.feedback_dir.glob("correction_*.json"):
            try:
                with open(feedback_file, 'r') as f:
                    correction = json.load(f)
                    corrections.append(correction)
            except Exception as e:
                self.logger.error(f"Error llegint {feedback_file}: {e}")
        
        self.logger.info(f"Recopilades {len(corrections)} correccions per reentrenament")
        return corrections


if __name__ == "__main__":
    # Configurar logging
    import pandas as pd
    logging.basicConfig(level=logging.INFO)
    
    # Exemple d'ús del pipeline híbrid
    project_dir = Path(__file__).parent.parent.parent
    
    # Crear pipeline híbrid
    pipeline = HybridDetectionPipeline(str(project_dir))
    
    # Exemple de processament
    image_path = project_dir / "data" / "images" / "page_1.png"
    if image_path.exists():
        # Simular dades OCR (en un cas real vindrien del processament anterior)
        ocr_data = []
        image_shape = (1683, 2383)  # altura, amplada
        
        # Processar amb detecció híbrida
        results = pipeline.process_image_hybrid(str(image_path), ocr_data, image_shape)
        
        print(f"Resultats de detecció híbrida:")
        print(f"- Elements d'IA: {len(results['ai_elements'])}")
        print(f"- Elements de regles: {len(results['rule_elements'])}")
        print(f"- Elements combinats: {len(results['merged_elements'])}")
        print(f"- Necessita revisió humana: {len(results['human_review_tasks'])}")
    
    print("\nSistema d'IA híbrid configurat!")
    print("El sistema combina detecció amb IA i regles per màxima precisió.")
