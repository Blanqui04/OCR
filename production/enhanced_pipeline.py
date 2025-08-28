"""
Pipeline OCR Millorat amb Integració YOLOv8
Combina OCR tradicional amb detecció d'elements tècnics
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger

try:
    from pipeline import OCRPipeline
    from technical_element_detector import TechnicalElementDetector
except ImportError:
    from .pipeline import OCRPipeline
    from .technical_element_detector import TechnicalElementDetector


class EnhancedOCRPipeline(OCRPipeline):
    """Pipeline OCR millorat amb detecció YOLOv8 integrada"""
    
    def __init__(self, base_dir=None, enable_yolo=True):
        """
        Inicialitza el pipeline millorat
        
        Args:
            base_dir: Directori base del projecte
            enable_yolo: Si activar la detecció YOLOv8
        """
        super().__init__(base_dir)
        
        self.enable_yolo = enable_yolo
        self.yolo_detector = None
        
        if enable_yolo:
            try:
                self.yolo_detector = TechnicalElementDetector()
                logger.info("✅ Detector YOLOv8 inicialitzat correctament")
            except Exception as e:
                logger.warning(f"⚠️ No es pot inicialitzar YOLOv8: {e}")
                self.enable_yolo = False
    
    def process_pdf_enhanced(self, pdf_path: str, save_files: bool = True, 
                           merge_results: bool = True) -> Dict:
        """
        Processa un PDF amb pipeline millorat (OCR + YOLOv8)
        
        Args:
            pdf_path: Camí al fitxer PDF
            save_files: Si guardar fitxers intermedis
            merge_results: Si combinar resultats OCR i YOLOv8
            
        Returns:
            Dict amb resultats combinats
        """
        logger.info(f"🚀 Iniciant pipeline millorat per: {Path(pdf_path).name}")
        
        # 1. Executar pipeline OCR tradicional
        ocr_results = self.process_pdf(pdf_path, save_files)
        
        # 2. Afegir detecció YOLOv8 si està disponible
        yolo_results = {}
        if self.enable_yolo and self.yolo_detector:
            try:
                image_path = ocr_results.get('image_path')
                if image_path:
                    yolo_results = self.yolo_detector.detect_elements(
                        image_path, 
                        save_annotated=True
                    )
                    
                    # Guardar resultats YOLOv8
                    if save_files and "error" not in yolo_results:
                        yolo_path = os.path.join(
                            self.base_dir, 
                            "data/technical_elements/yolo_detections.json"
                        )
                        with open(yolo_path, "w", encoding="utf-8") as f:
                            json.dump(yolo_results, f, ensure_ascii=False, indent=2)
                        
                        logger.info(f"💾 Resultats YOLOv8 guardats: {yolo_path}")
                
            except Exception as e:
                logger.error(f"❌ Error en detecció YOLOv8: {e}")
                yolo_results = {"error": str(e)}
        
        # 3. Combinar resultats si es demana
        enhanced_results = {
            "metadata": {
                "pdf_path": pdf_path,
                "processed_at": datetime.now().isoformat(),
                "pipeline_version": "enhanced_v1.0",
                "yolo_enabled": self.enable_yolo
            },
            "ocr_results": ocr_results,
            "yolo_results": yolo_results
        }
        
        if merge_results:
            enhanced_results["merged_analysis"] = self._merge_ocr_yolo_results(
                ocr_results, yolo_results
            )
        
        # 4. Guardar resultats combinats
        if save_files:
            combined_path = os.path.join(
                self.base_dir, 
                "data/output/final",
                f"enhanced_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            os.makedirs(os.path.dirname(combined_path), exist_ok=True)
            
            with open(combined_path, "w", encoding="utf-8") as f:
                json.dump(enhanced_results, f, ensure_ascii=False, indent=2)
            
            logger.info(f"📁 Resultats combinats guardats: {combined_path}")
        
        return enhanced_results
    
    def _merge_ocr_yolo_results(self, ocr_results: Dict, yolo_results: Dict) -> Dict:
        """
        Combina i analitza resultats d'OCR i YOLOv8
        
        Args:
            ocr_results: Resultats del pipeline OCR
            yolo_results: Resultats de la detecció YOLOv8
            
        Returns:
            Dict amb anàlisi combinada
        """
        if "error" in yolo_results:
            return {
                "status": "ocr_only",
                "reason": yolo_results.get("error", "YOLOv8 error"),
                "ocr_elements": len(ocr_results.get('ocr_data', [])),
                "yolo_elements": 0
            }
        
        merged = {
            "status": "success",
            "detection_methods": ["ocr", "yolo"],
            "summary": {
                "total_ocr_elements": len(ocr_results.get('ocr_data', [])),
                "total_yolo_elements": yolo_results.get('total_elements', 0),
                "yolo_by_type": yolo_results.get('summary', {}),
                "ocr_dimensions": len(ocr_results.get('tech_data', {}).get('dimensions', [])),
                "ocr_notes": len(ocr_results.get('tech_data', {}).get('notes', []))
            },
            "confidence_analysis": self._analyze_detection_confidence(yolo_results),
            "spatial_analysis": self._analyze_spatial_distribution(yolo_results),
            "validation": self._validate_detections(ocr_results, yolo_results)
        }
        
        return merged
    
    def _analyze_detection_confidence(self, yolo_results: Dict) -> Dict:
        """Analitza la confiança de les deteccions YOLOv8"""
        if "elements" not in yolo_results:
            return {"status": "no_data"}
        
        elements = yolo_results["elements"]
        if not elements:
            return {"status": "no_elements"}
        
        confidences = [elem["confidence"] for elem in elements]
        
        return {
            "total_detections": len(elements),
            "avg_confidence": sum(confidences) / len(confidences),
            "min_confidence": min(confidences),
            "max_confidence": max(confidences),
            "high_confidence_count": len([c for c in confidences if c > 0.8]),
            "medium_confidence_count": len([c for c in confidences if 0.5 <= c <= 0.8]),
            "low_confidence_count": len([c for c in confidences if c < 0.5])
        }
    
    def _analyze_spatial_distribution(self, yolo_results: Dict) -> Dict:
        """Analitza la distribució espacial de les deteccions"""
        if "elements" not in yolo_results:
            return {"status": "no_data"}
        
        elements = yolo_results["elements"]
        if not elements:
            return {"status": "no_elements"}
        
        # Calcular centres de les deteccions
        centers = [(elem["center"]["x"], elem["center"]["y"]) for elem in elements]
        
        # Estadístiques espacials bàsiques
        x_coords = [c[0] for c in centers]
        y_coords = [c[1] for c in centers]
        
        return {
            "total_elements": len(elements),
            "bounding_box": {
                "min_x": min(x_coords),
                "max_x": max(x_coords),
                "min_y": min(y_coords),
                "max_y": max(y_coords)
            },
            "center_of_mass": {
                "x": sum(x_coords) / len(x_coords),
                "y": sum(y_coords) / len(y_coords)
            },
            "distribution_by_type": self._get_type_distribution(elements)
        }
    
    def _get_type_distribution(self, elements: List[Dict]) -> Dict:
        """Calcula la distribució per tipus d'element"""
        type_positions = {}
        
        for elem in elements:
            elem_type = elem["type"]
            if elem_type not in type_positions:
                type_positions[elem_type] = []
            
            type_positions[elem_type].append({
                "x": elem["center"]["x"],
                "y": elem["center"]["y"],
                "confidence": elem["confidence"]
            })
        
        return type_positions
    
    def _validate_detections(self, ocr_results: Dict, yolo_results: Dict) -> Dict:
        """Valida la coherència entre OCR i YOLOv8"""
        validation = {
            "status": "completed",
            "checks": {}
        }
        
        # Verificar si YOLOv8 ha detectat elements on OCR ha trobat text
        ocr_elements = len(ocr_results.get('ocr_data', []))
        yolo_elements = yolo_results.get('total_elements', 0)
        
        validation["checks"]["element_count_ratio"] = {
            "ocr_count": ocr_elements,
            "yolo_count": yolo_elements,
            "ratio": yolo_elements / ocr_elements if ocr_elements > 0 else 0
        }
        
        # Verificar coherència de dimensions
        ocr_dimensions = len(ocr_results.get('tech_data', {}).get('dimensions', []))
        yolo_dimensions = yolo_results.get('summary', {}).get('cota', 0)
        
        validation["checks"]["dimension_coherence"] = {
            "ocr_dimensions": ocr_dimensions,
            "yolo_dimensions": yolo_dimensions,
            "coherent": abs(ocr_dimensions - yolo_dimensions) <= 2  # Tolerància de 2 elements
        }
        
        return validation
    
    def get_enhanced_stats(self, enhanced_results: Dict) -> Dict:
        """Genera estadístiques del pipeline millorat"""
        ocr_results = enhanced_results.get("ocr_results", {})
        yolo_results = enhanced_results.get("yolo_results", {})
        merged = enhanced_results.get("merged_analysis", {})
        
        stats = {
            "pipeline_info": {
                "version": enhanced_results.get("metadata", {}).get("pipeline_version", "unknown"),
                "yolo_enabled": enhanced_results.get("metadata", {}).get("yolo_enabled", False),
                "processed_at": enhanced_results.get("metadata", {}).get("processed_at", "unknown")
            },
            "ocr_stats": self.get_stats(ocr_results),
            "yolo_stats": {
                "total_elements": yolo_results.get("total_elements", 0),
                "by_type": yolo_results.get("summary", {}),
                "avg_confidence": merged.get("confidence_analysis", {}).get("avg_confidence", 0)
            },
            "merged_stats": merged.get("summary", {}),
            "validation": merged.get("validation", {})
        }
        
        return stats


def main():
    """Funció principal per testejar el pipeline millorat"""
    pipeline = EnhancedOCRPipeline(enable_yolo=True)
    pdf_path = os.path.join(pipeline.base_dir, "data", "exemples", "6555945_003.pdf")
    
    logger.info("🚀 Iniciant pipeline OCR millorat...")
    
    results = pipeline.process_pdf_enhanced(pdf_path, save_files=True, merge_results=True)
    
    stats = pipeline.get_enhanced_stats(results)
    
    logger.info("📊 Estadístiques del Pipeline Millorat:")
    logger.info(f"  📝 OCR - Elements de text: {stats['ocr_stats']['total_text_elements']}")
    logger.info(f"  📐 OCR - Cotes detectades: {stats['ocr_stats']['dimensions']}")
    logger.info(f"  🎯 YOLO - Elements detectats: {stats['yolo_stats']['total_elements']}")
    logger.info(f"  🎯 YOLO - Per tipus: {stats['yolo_stats']['by_type']}")
    logger.info(f"  📈 Confiança mitjana YOLO: {stats['yolo_stats']['avg_confidence']:.3f}")
    
    validation = stats.get('validation', {})
    if validation:
        logger.info("✅ Validació:")
        for check_name, check_result in validation.get('checks', {}).items():
            logger.info(f"  - {check_name}: {check_result}")
    
    logger.info("🎉 Pipeline millorat completat!")
    return results


if __name__ == "__main__":
    main()
