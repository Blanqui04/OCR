"""
Detector d'Elements Tècnics integrat amb YOLOv8
Detecta cotes, toleràncies i símbols en plànols tècnics
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from loguru import logger
import json
from datetime import datetime

try:
    from ultralytics import YOLO
except ImportError:
    logger.error("ultralytics no està instal·lat. Executa: pip install ultralytics")
    YOLO = None

try:
    from ai_model.model_manager import ModelManager
except ImportError:
    from .ai_model.model_manager import ModelManager


class TechnicalElementDetector:
    """Detector d'elements tècnics utilitzant YOLOv8 personalitzat"""
    
    def __init__(self, model_name: str = "technical_detector"):
        """
        Inicialitza el detector d'elements tècnics
        
        Args:
            model_name: Nom del model registrat al ModelManager
        """
        self.model_name = model_name
        self.model = None
        self.model_manager = ModelManager()
        self.class_names = ["cota", "tolerancia", "simbol"]
        self.confidence_threshold = 0.5
        self.iou_threshold = 0.45
        
        self._load_model()
    
    def _load_model(self) -> bool:
        """Carrega el model YOLOv8 personalitzat"""
        try:
            if YOLO is None:
                logger.error("YOLO no disponible")
                return False
            
            # Obtenir el path del model del ModelManager
            model_info = self.model_manager.get_model_info(self.model_name)
            if not model_info:
                logger.error(f"Model '{self.model_name}' no trobat al registre")
                return False
            
            model_path = model_info.get('path')
            if not model_path or not Path(model_path).exists():
                logger.error(f"Fitxer del model no trobat: {model_path}")
                return False
            
            # Carregar el model YOLOv8
            self.model = YOLO(model_path)
            logger.info(f"✅ Model '{self.model_name}' carregat des de: {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error carregant el model: {e}")
            return False
    
    def detect_elements(self, image_path: str, save_annotated: bool = True) -> Dict:
        """
        Detecta elements tècnics en una imatge
        
        Args:
            image_path: Path a la imatge a processar
            save_annotated: Si guardar la imatge amb anotacions
            
        Returns:
            Dict amb els resultats de la detecció
        """
        if not self.model:
            logger.error("Model no carregat")
            return {"error": "Model no disponible"}
        
        try:
            # Carregar imatge
            image_path = Path(image_path)
            if not image_path.exists():
                logger.error(f"Imatge no trobada: {image_path}")
                return {"error": f"Imatge no trobada: {image_path}"}
            
            # Executar detecció
            results = self.model(
                str(image_path),
                conf=self.confidence_threshold,
                iou=self.iou_threshold,
                save=False,
                verbose=False
            )
            
            # Processar resultats
            detections = self._process_results(results[0], str(image_path))
            
            # Guardar imatge anotada si es demana
            if save_annotated and detections['elements']:
                annotated_path = self._save_annotated_image(
                    str(image_path), 
                    results[0], 
                    detections
                )
                detections['annotated_image'] = annotated_path
            
            logger.info(f"🔍 Detectats {len(detections['elements'])} elements a {image_path.name}")
            return detections
            
        except Exception as e:
            logger.error(f"Error en la detecció: {e}")
            return {"error": str(e)}
    
    def _process_results(self, result, image_path: str) -> Dict:
        """Processa els resultats de YOLO en un format estructurat"""
        elements = []
        summary = {"cota": 0, "tolerancia": 0, "simbol": 0}
        
        if result.boxes is not None:
            boxes = result.boxes.xyxy.cpu().numpy()  # Coordenades x1, y1, x2, y2
            confidences = result.boxes.conf.cpu().numpy()
            classes = result.boxes.cls.cpu().numpy()
            
            for i, (box, conf, cls) in enumerate(zip(boxes, confidences, classes)):
                class_name = self.class_names[int(cls)]
                
                element = {
                    "id": f"{class_name}_{i+1}",
                    "type": class_name,
                    "confidence": float(conf),
                    "bbox": {
                        "x1": float(box[0]),
                        "y1": float(box[1]),
                        "x2": float(box[2]),
                        "y2": float(box[3]),
                        "width": float(box[2] - box[0]),
                        "height": float(box[3] - box[1])
                    },
                    "center": {
                        "x": float((box[0] + box[2]) / 2),
                        "y": float((box[1] + box[3]) / 2)
                    }
                }
                
                elements.append(element)
                summary[class_name] += 1
        
        return {
            "image_path": image_path,
            "timestamp": datetime.now().isoformat(),
            "model_used": self.model_name,
            "total_elements": len(elements),
            "summary": summary,
            "elements": elements,
            "detection_params": {
                "confidence_threshold": self.confidence_threshold,
                "iou_threshold": self.iou_threshold
            }
        }
    
    def _save_annotated_image(self, image_path: str, result, detections: Dict) -> str:
        """Guarda la imatge amb les deteccions anotades"""
        try:
            # Carregar imatge original
            image = cv2.imread(image_path)
            if image is None:
                return ""
            
            # Colors per cada classe
            colors = {
                "cota": (0, 255, 0),      # Verd
                "tolerancia": (255, 0, 0), # Blau
                "simbol": (0, 0, 255)     # Vermell
            }
            
            # Dibuixar deteccions
            for element in detections['elements']:
                bbox = element['bbox']
                color = colors.get(element['type'], (255, 255, 255))
                
                # Rectangle
                cv2.rectangle(
                    image,
                    (int(bbox['x1']), int(bbox['y1'])),
                    (int(bbox['x2']), int(bbox['y2'])),
                    color,
                    2
                )
                
                # Etiqueta
                label = f"{element['type']} {element['confidence']:.2f}"
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                
                cv2.rectangle(
                    image,
                    (int(bbox['x1']), int(bbox['y1']) - label_size[1] - 10),
                    (int(bbox['x1']) + label_size[0], int(bbox['y1'])),
                    color,
                    -1
                )
                
                cv2.putText(
                    image,
                    label,
                    (int(bbox['x1']), int(bbox['y1']) - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2
                )
            
            # Guardar imatge anotada
            image_path_obj = Path(image_path)
            annotated_path = image_path_obj.parent / "annotated" / f"detected_{image_path_obj.name}"
            annotated_path.parent.mkdir(exist_ok=True)
            
            cv2.imwrite(str(annotated_path), image)
            logger.info(f"💾 Imatge anotada guardada: {annotated_path}")
            
            return str(annotated_path)
            
        except Exception as e:
            logger.error(f"Error guardant imatge anotada: {e}")
            return ""
    
    def detect_in_directory(self, input_dir: str, output_dir: str = None) -> Dict:
        """
        Detecta elements tècnics en totes les imatges d'un directori
        
        Args:
            input_dir: Directori amb imatges a processar
            output_dir: Directori per guardar resultats
            
        Returns:
            Dict amb resultats de totes les deteccions
        """
        input_path = Path(input_dir)
        if not input_path.exists():
            return {"error": f"Directori no trobat: {input_dir}"}
        
        if output_dir is None:
            output_dir = input_path / "detection_results"
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Extensions d'imatge suportades
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        image_files = [
            f for f in input_path.iterdir() 
            if f.is_file() and f.suffix.lower() in image_extensions
        ]
        
        if not image_files:
            return {"error": "No s'han trobat imatges al directori"}
        
        all_results = {
            "batch_info": {
                "input_directory": str(input_path),
                "output_directory": str(output_path),
                "total_images": len(image_files),
                "processed_at": datetime.now().isoformat(),
                "model_used": self.model_name
            },
            "results": [],
            "summary": {
                "total_elements": 0,
                "by_type": {"cota": 0, "tolerancia": 0, "simbol": 0},
                "by_image": {}
            }
        }
        
        # Processar cada imatge
        for i, image_file in enumerate(image_files, 1):
            logger.info(f"📷 Processant {i}/{len(image_files)}: {image_file.name}")
            
            detection_result = self.detect_elements(str(image_file), save_annotated=True)
            
            if "error" not in detection_result:
                all_results["results"].append(detection_result)
                
                # Actualitzar resum
                all_results["summary"]["total_elements"] += detection_result["total_elements"]
                
                for element_type, count in detection_result["summary"].items():
                    all_results["summary"]["by_type"][element_type] += count
                
                all_results["summary"]["by_image"][image_file.name] = detection_result["total_elements"]
        
        # Guardar resultats en JSON
        results_file = output_path / f"detection_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📊 Resultats guardats a: {results_file}")
        logger.info(f"🎯 Total elements detectats: {all_results['summary']['total_elements']}")
        
        return all_results
    
    def set_thresholds(self, confidence: float = 0.5, iou: float = 0.45):
        """Configura els llindars de confiança i IoU"""
        self.confidence_threshold = confidence
        self.iou_threshold = iou
        logger.info(f"🎛️ Llindars actualitzats - Confidence: {confidence}, IoU: {iou}")


def main():
    """Funció principal per testejar el detector"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Detector d'Elements Tècnics YOLOv8")
    parser.add_argument("--input", required=True, help="Imatge o directori d'entrada")
    parser.add_argument("--output", help="Directori de sortida")
    parser.add_argument("--confidence", type=float, default=0.5, help="Llindar de confiança")
    parser.add_argument("--iou", type=float, default=0.45, help="Llindar IoU")
    parser.add_argument("--model", default="technical_detector", help="Nom del model")
    
    args = parser.parse_args()
    
    # Crear detector
    detector = TechnicalElementDetector(model_name=args.model)
    detector.set_thresholds(args.confidence, args.iou)
    
    input_path = Path(args.input)
    
    if input_path.is_file():
        # Processar una sola imatge
        result = detector.detect_elements(str(input_path))
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif input_path.is_dir():
        # Processar directori
        results = detector.detect_in_directory(str(input_path), args.output)
        print(f"Processades {results.get('batch_info', {}).get('total_images', 0)} imatges")
        print(f"Total elements: {results.get('summary', {}).get('total_elements', 0)}")
    
    else:
        logger.error(f"Path no vàlid: {input_path}")


if __name__ == "__main__":
    main()
