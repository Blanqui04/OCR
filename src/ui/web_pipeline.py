#!/usr/bin/env python3
"""
Pipeline OCR simplificat per la interfície web
Combina OCR tradicional amb detecció YOLOv8
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

class WebOCRPipeline:
    """Pipeline OCR optimitzat per la interfície web"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.yolo_detector = None
        self.ocr_processor = None
        self._setup_components()
    
    def _setup_components(self):
        """Configurar components del pipeline"""
        # Add project paths to sys.path
        project_root_str = str(self.project_root)
        src_path = str(self.project_root / 'src')
        production_path = str(self.project_root / 'production')
        
        for path in [project_root_str, src_path, production_path]:
            if path not in sys.path:
                sys.path.insert(0, path)
        
        try:
            # Try different import paths for YOLOv8 detector
            self.yolo_detector = None
            import_attempts = [
                'src.technical_element_detector',
                'technical_element_detector',
                'production.technical_element_detector'
            ]
            
            for module_name in import_attempts:
                try:
                    module = __import__(module_name, fromlist=['TechnicalElementDetector'])
                    TechnicalElementDetector = getattr(module, 'TechnicalElementDetector')
                    self.yolo_detector = TechnicalElementDetector()
                    logger.info(f"YOLOv8 detector initialized successfully from {module_name}")
                    break
                except (ImportError, AttributeError) as e:
                    logger.debug(f"Failed to import from {module_name}: {e}")
                    continue
            
            if not self.yolo_detector:
                logger.warning("YOLOv8 detector not available from any source")
                
        except Exception as e:
            logger.warning(f"YOLOv8 detector setup failed: {e}")
        
        try:
            # Try different import paths for OCR processor
            self.ocr_processor = None
            import_attempts = [
                'src.ocr_processor',
                'ocr_processor',
                'production.ocr_processor'
            ]
            
            for module_name in import_attempts:
                try:
                    module = __import__(module_name, fromlist=['OCRProcessor'])
                    OCRProcessor = getattr(module, 'OCRProcessor')
                    self.ocr_processor = OCRProcessor()
                    logger.info(f"OCR processor initialized successfully from {module_name}")
                    break
                except (ImportError, AttributeError) as e:
                    logger.debug(f"Failed to import from {module_name}: {e}")
                    continue
            
            if not self.ocr_processor:
                logger.warning("OCR processor not available from any source")
                
        except Exception as e:
            logger.warning(f"OCR processor setup failed: {e}")
    
    def process_document(self, file_path: str, options: Dict = None) -> Dict[str, Any]:
        """
        Processar document amb OCR i YOLOv8
        
        Args:
            file_path: Camí al fitxer a processar
            options: Opcions de processament
        
        Returns:
            Dict amb resultats del processament
        """
        if options is None:
            options = {}
        
        result = {
            'file_path': file_path,
            'timestamp': time.time(),
            'processing_method': 'web_pipeline',
            'ocr_text': '',
            'ocr_confidence': 0,
            'yolo_detections': [],
            'technical_elements': [],
            'combined_analysis': {},
            'error': None
        }
        
        try:
            # Convert PDF to image if needed
            image_paths = self._prepare_images(file_path)
            
            all_text = []
            all_confidences = []
            all_detections = []
            
            for image_path in image_paths:
                # Process with OCR
                if self.ocr_processor:
                    ocr_result = self._process_ocr(image_path, options)
                    all_text.append(ocr_result.get('text', ''))
                    all_confidences.append(ocr_result.get('confidence', 0))
                
                # Process with YOLOv8
                if self.yolo_detector:
                    yolo_result = self._process_yolo(image_path, options)
                    all_detections.extend(yolo_result.get('detections', []))
            
            # Combine results
            result['ocr_text'] = '\n\n'.join(filter(None, all_text))
            result['ocr_confidence'] = sum(all_confidences) / len(all_confidences) if all_confidences else 0
            result['yolo_detections'] = all_detections
            result['technical_elements'] = self._format_technical_elements(all_detections)
            result['combined_analysis'] = self._analyze_combined_results(result)
            
            logger.info(f"Document processed successfully: {len(all_detections)} technical elements found")
            
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            result['error'] = str(e)
        
        return result
    
    def _prepare_images(self, file_path: str) -> List[str]:
        """Preparar imatges per processar"""
        try:
            if file_path.lower().endswith('.pdf'):
                # Try different import paths for PDF conversion
                import_attempts = [
                    'src.pdf_to_images',
                    'pdf_to_images',
                    'production.pdf_to_images'
                ]
                
                for module_name in import_attempts:
                    try:
                        module = __import__(module_name, fromlist=['convert_pdf_to_images'])
                        convert_pdf_to_images = getattr(module, 'convert_pdf_to_images')
                        return convert_pdf_to_images(file_path)
                    except (ImportError, AttributeError) as e:
                        logger.debug(f"Failed to import PDF converter from {module_name}: {e}")
                        continue
                
                # If all imports fail, return original path
                logger.warning("PDF to images conversion not available")
                return [file_path]
            else:
                # Already an image
                return [file_path]
        except Exception as e:
            logger.error(f"Error preparing images: {e}")
            return [file_path]  # Return original path as fallback
    
    def _process_ocr(self, image_path: str, options: Dict) -> Dict[str, Any]:
        """Processar imatge amb OCR"""
        try:
            language = options.get('language', 'eng')
            mode = options.get('ocr_mode', 'fast')
            
            return self.ocr_processor.process_image(
                image_path,
                language=language,
                mode=mode
            )
        except Exception as e:
            logger.error(f"OCR processing error: {e}")
            return {'text': '', 'confidence': 0, 'error': str(e)}
    
    def _process_yolo(self, image_path: str, options: Dict) -> Dict[str, Any]:
        """Processar imatge amb YOLOv8"""
        try:
            confidence_threshold = options.get('yolo_confidence', 0.3)
            
            detections = self.yolo_detector.detect_elements(
                image_path,
                confidence_threshold=confidence_threshold
            )
            
            return {'detections': detections}
        except Exception as e:
            logger.error(f"YOLOv8 processing error: {e}")
            return {'detections': [], 'error': str(e)}
    
    def _format_technical_elements(self, detections: List[Dict]) -> List[Dict]:
        """Formatar elements tècnics trobats"""
        elements = []
        for detection in detections:
            elements.append({
                'type': detection.get('class', 'unknown'),
                'confidence': detection.get('confidence', 0),
                'bbox': detection.get('bbox', []),
                'text_nearby': detection.get('text_nearby', ''),
                'area': detection.get('area', 0)
            })
        return elements
    
    def _analyze_combined_results(self, result: Dict) -> Dict[str, Any]:
        """Analitzar resultats combinats"""
        analysis = {
            'total_elements': len(result['technical_elements']),
            'element_types': {},
            'confidence_stats': {},
            'text_quality': 'unknown'
        }
        
        # Count element types
        for element in result['technical_elements']:
            element_type = element['type']
            if element_type not in analysis['element_types']:
                analysis['element_types'][element_type] = 0
            analysis['element_types'][element_type] += 1
        
        # Calculate confidence statistics
        if result['technical_elements']:
            confidences = [e['confidence'] for e in result['technical_elements']]
            analysis['confidence_stats'] = {
                'min': min(confidences),
                'max': max(confidences),
                'avg': sum(confidences) / len(confidences)
            }
        
        # Analyze text quality
        if result['ocr_text']:
            word_count = len(result['ocr_text'].split())
            if word_count > 100:
                analysis['text_quality'] = 'good'
            elif word_count > 20:
                analysis['text_quality'] = 'fair'
            else:
                analysis['text_quality'] = 'limited'
        
        return analysis
    
    def is_available(self) -> bool:
        """Verificar si el pipeline està disponible"""
        return self.yolo_detector is not None or self.ocr_processor is not None
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Obtenir capacitats disponibles"""
        return {
            'yolo_detection': self.yolo_detector is not None,
            'ocr_processing': self.ocr_processor is not None,
            'pdf_conversion': True,  # pdf2image should be available
            'combined_analysis': True
        }

def create_web_pipeline() -> Optional[WebOCRPipeline]:
    """Factory function per crear pipeline web"""
    try:
        pipeline = WebOCRPipeline()
        if pipeline.is_available():
            return pipeline
        else:
            logger.warning("No OCR/YOLOv8 components available")
            return None
    except Exception as e:
        logger.error(f"Failed to create web pipeline: {e}")
        return None

# Export for web app
__all__ = ['WebOCRPipeline', 'create_web_pipeline']
