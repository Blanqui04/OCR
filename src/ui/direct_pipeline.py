#!/usr/bin/env python3
"""
Pipeline OCR directe per la interfície web
Utilitza els mòduls existents directament
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

class DirectWebPipeline:
    """Pipeline OCR directe utilitzant funcions existents"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.yolo_available = False
        self.ocr_available = False
        self._setup_components()
    
    def _setup_components(self):
        """Configurar components del pipeline"""
        # Add project paths to sys.path
        project_root_str = str(self.project_root)
        src_path = str(self.project_root / 'src')
        
        for path in [project_root_str, src_path]:
            if path not in sys.path:
                sys.path.insert(0, path)
        
        # Test YOLOv8 detector
        try:
            from src.technical_element_detector import TechnicalElementDetector
            self.yolo_detector = TechnicalElementDetector()
            self.yolo_available = True
            logger.info("YOLOv8 detector initialized successfully")
        except Exception as e:
            logger.warning(f"YOLOv8 detector not available: {e}")
            self.yolo_detector = None
        
        # Test OCR processor
        try:
            from src.ocr_processor import ocr_with_boxes
            self.ocr_function = ocr_with_boxes
            self.ocr_available = True
            logger.info("OCR function loaded successfully")
        except Exception as e:
            logger.warning(f"OCR function not available: {e}")
            self.ocr_function = None
    
    def process_document(self, file_path: str, options: Dict = None) -> Dict[str, Any]:
        """
        Processar document amb OCR i YOLOv8
        """
        if options is None:
            options = {}
        
        result = {
            'file_path': file_path,
            'timestamp': time.time(),
            'processing_method': 'direct_web_pipeline',
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
                if self.ocr_available and self.ocr_function:
                    try:
                        ocr_data, img_shape = self.ocr_function(image_path)
                        # Extract text and confidence
                        page_text = ' '.join([item['text'] for item in ocr_data if item['text'].strip()])
                        page_confidence = sum([item['confidence'] for item in ocr_data]) / len(ocr_data) if ocr_data else 0
                        
                        all_text.append(page_text)
                        all_confidences.append(page_confidence)
                        
                        logger.info(f"OCR processed {len(ocr_data)} text elements from {image_path}")
                    except Exception as e:
                        logger.error(f"OCR processing error: {e}")
                
                # Process with YOLOv8
                if self.yolo_available and self.yolo_detector:
                    try:
                        # Set confidence threshold on the detector instance
                        original_threshold = self.yolo_detector.confidence_threshold
                        confidence_threshold = options.get('yolo_confidence', 0.3)
                        self.yolo_detector.confidence_threshold = confidence_threshold
                        
                        detections = self.yolo_detector.detect_elements(image_path)
                        
                        # Restore original threshold
                        self.yolo_detector.confidence_threshold = original_threshold
                        
                        if 'elements' in detections:
                            all_detections.extend(detections['elements'])
                            logger.info(f"YOLOv8 detected {len(detections['elements'])} elements from {image_path}")
                        else:
                            logger.info(f"YOLOv8 processed {image_path} but found no elements")
                    except Exception as e:
                        logger.error(f"YOLOv8 processing error: {e}")
            
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
        import os
        try:
            if file_path.lower().endswith('.pdf'):
                # Try to convert PDF to images
                try:
                    from src.pdf_to_images import convert_pdf_to_images
                    images_folder = str(self.project_root / 'data' / 'images')
                    os.makedirs(images_folder, exist_ok=True)
                    return convert_pdf_to_images(file_path, images_folder)
                except Exception as e:
                    logger.warning(f"PDF conversion failed: {e}")
                    return [file_path]
            else:
                # Already an image
                return [file_path]
        except Exception as e:
            logger.error(f"Error preparing images: {e}")
            return [file_path]
    
    def _format_technical_elements(self, detections: List[Dict]) -> List[Dict]:
        """Formatar elements tècnics trobats"""
        elements = []
        for detection in detections:
            elements.append({
                'type': detection.get('type', 'unknown'),
                'confidence': detection.get('confidence', 0),
                'bbox': detection.get('bbox', {}),
                'center': detection.get('center', {}),
                'id': detection.get('id', 'unknown'),
                'area': detection.get('bbox', {}).get('width', 0) * detection.get('bbox', {}).get('height', 0)
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
        return self.yolo_available or self.ocr_available
    
    def get_capabilities(self) -> Dict[str, bool]:
        """Obtenir capacitats disponibles"""
        return {
            'yolo_detection': self.yolo_available,
            'ocr_processing': self.ocr_available,
            'pdf_conversion': True,
            'combined_analysis': True
        }

def create_direct_pipeline() -> Optional[DirectWebPipeline]:
    """Factory function per crear pipeline directe"""
    try:
        pipeline = DirectWebPipeline()
        if pipeline.is_available():
            return pipeline
        else:
            logger.warning("No OCR/YOLOv8 components available")
            return None
    except Exception as e:
        logger.error(f"Failed to create direct pipeline: {e}")
        return None

# Export for web app
__all__ = ['DirectWebPipeline', 'create_direct_pipeline']
