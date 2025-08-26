#!/usr/bin/env python3
"""
Google Cloud Document AI OCR Processor
Handles OCR processing using Google Cloud Document AI
"""

import os
import logging
from typing import Dict, List, Optional, Tuple, Any
import json
from pathlib import Path

try:
    from google.cloud import documentai
    from google.api_core.client_options import ClientOptions
except ImportError:
    documentai = None

logger = logging.getLogger(__name__)

class GoogleCloudOCR:
    """Google Cloud Document AI OCR processor"""
    
    def __init__(self, project_id: str = "natural-bison-465607-b6", location: str = "eu", processor_id: str = "4369d16f70cb0a26"):
        """
        Initialize Google Cloud Document AI client
        
        Args:
            project_id: Google Cloud project ID
            location: Processing location (default: eu)
            processor_id: Document AI processor ID
        """
        self.project_id = project_id
        self.location = location
        self.processor_id = processor_id
        self.client = None
        self.processor_path = None
        
        # Try to get credentials from environment or config
        self._setup_credentials()
        
    def _setup_credentials(self):
        """Setup Google Cloud credentials"""
        try:
            # Check if credentials file exists in docs folder
            credentials_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), 
                'docs', 
                'natural-bison-465607-b6-a638a05f2638.json'
            )
            
            if os.path.exists(credentials_path):
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
                logger.info(f"Using credentials from: {credentials_path}")
            
            # Try to load project settings from config file
            self._load_config()
            
        except Exception as e:
            logger.error(f"Error setting up credentials: {str(e)}")
            
    def _load_config(self):
        """Load configuration from config file"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    
                self.project_id = config.get('project_id', self.project_id)
                self.location = config.get('location', self.location)
                self.processor_id = config.get('processor_id', self.processor_id)
                
                logger.info("Configuration loaded from config.json")
                
        except Exception as e:
            logger.warning(f"Could not load config: {str(e)}")
            
    def save_config(self):
        """Save current configuration to config file"""
        try:
            config = {
                'project_id': self.project_id,
                'location': self.location,
                'processor_id': self.processor_id
            }
            
            config_path = os.path.join(os.path.dirname(__file__), 'config.json')
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
                
            logger.info("Configuration saved to config.json")
            
        except Exception as e:
            logger.error(f"Error saving config: {str(e)}")
            
    def initialize_client(self) -> bool:
        """
        Initialize the Document AI client
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            if not documentai:
                logger.error("Google Cloud Document AI library not installed")
                return False
                
            if not all([self.project_id, self.location, self.processor_id]):
                logger.error("Missing required configuration: project_id, location, or processor_id")
                return False
                
            # Create client options with API endpoint
            opts = ClientOptions(api_endpoint=f"{self.location}-documentai.googleapis.com")
            
            # Initialize the client
            self.client = documentai.DocumentProcessorServiceClient(client_options=opts)
            
            # Create processor path
            self.processor_path = self.client.processor_path(
                self.project_id, self.location, self.processor_id
            )
            
            logger.info(f"Google Cloud Document AI client initialized successfully")
            logger.info(f"Processor path: {self.processor_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error initializing Google Cloud client: {str(e)}")
            return False
            
    def test_connection(self) -> Tuple[bool, str]:
        """
        Test the connection to Google Cloud Document AI
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            if not self.initialize_client():
                return False, "Failed to initialize client"
                
            # Try to get processor info
            processor = self.client.get_processor(name=self.processor_path)
            
            return True, f"Connection successful. Processor: {processor.display_name}"
            
        except Exception as e:
            error_msg = f"Connection failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
            
    def process_document(self, file_path: str, mime_type: str = "application/pdf") -> Optional[Dict]:
        """
        Process a document using Google Cloud Document AI
        
        Args:
            file_path: Path to the document file
            mime_type: MIME type of the document
            
        Returns:
            Dict: Processing results or None if failed
        """
        try:
            if not self.client:
                if not self.initialize_client():
                    return None
                    
            # Read the file
            with open(file_path, "rb") as file:
                file_content = file.read()
                
            # Create the document object
            raw_document = documentai.RawDocument(
                content=file_content,
                mime_type=mime_type
            )
            
            # Create the request
            request = documentai.ProcessRequest(
                name=self.processor_path,
                raw_document=raw_document
            )
            
            logger.info(f"Processing document: {file_path}")
            
            # Process the document
            result = self.client.process_document(request=request)
            document = result.document
            
            # Extract and structure the results
            ocr_results = self._extract_ocr_results(document)
            
            logger.info(f"Document processed successfully. Found {len(ocr_results.get('blocks', []))} text blocks")
            
            return ocr_results
            
        except Exception as e:
            error_msg = f"Error processing document: {str(e)}"
            logger.error(error_msg)
            return None
            
    def _extract_ocr_results(self, document) -> Dict:
        """
        Extract OCR results from Document AI response
        
        Args:
            document: Document AI document object
            
        Returns:
            Dict: Structured OCR results
        """
        results = {
            'text': document.text,
            'blocks': [],
            'pages': [],
            'statistics': {
                'total_blocks': 0,
                'avg_confidence': 0.0,
                'languages': [],
                'page_count': len(document.pages)
            }
        }
        
        total_confidence = 0.0
        block_count = 0
        
        # Process each page
        for page_num, page in enumerate(document.pages):
            page_info = {
                'page_number': page_num + 1,
                'width': page.dimension.width,
                'height': page.dimension.height,
                'blocks': []
            }
            
            # Process text blocks
            for block_num, block in enumerate(page.blocks):
                block_text = self._get_text_from_layout(document.text, block.layout)
                confidence = block.layout.confidence if hasattr(block.layout, 'confidence') else 0.0
                
                # Get bounding box
                bbox = self._get_bounding_box(block.layout.bounding_poly, page.dimension)
                
                block_info = {
                    'block_id': f"page_{page_num + 1}_block_{block_num + 1}",
                    'text': block_text.strip(),
                    'confidence': confidence,
                    'page': page_num + 1,
                    'bbox': bbox,
                    'x': bbox['x'],
                    'y': bbox['y'],
                    'width': bbox['width'],
                    'height': bbox['height']
                }
                
                results['blocks'].append(block_info)
                page_info['blocks'].append(block_info)
                
                total_confidence += confidence
                block_count += 1
                
            results['pages'].append(page_info)
            
        # Calculate statistics
        if block_count > 0:
            results['statistics']['total_blocks'] = block_count
            results['statistics']['avg_confidence'] = total_confidence / block_count
            
        # Detect languages
        if hasattr(document, 'pages') and document.pages:
            for page in document.pages:
                if hasattr(page, 'detected_languages'):
                    for lang in page.detected_languages:
                        if lang.language_code not in results['statistics']['languages']:
                            results['statistics']['languages'].append(lang.language_code)
                            
        return results
        
    def _get_text_from_layout(self, document_text: str, layout) -> str:
        """Extract text from layout object"""
        try:
            if not layout.text_anchor:
                return ""
                
            text_segments = []
            for segment in layout.text_anchor.text_segments:
                start_index = int(segment.start_index) if segment.start_index else 0
                end_index = int(segment.end_index) if segment.end_index else len(document_text)
                text_segments.append(document_text[start_index:end_index])
                
            return "".join(text_segments)
            
        except Exception as e:
            logger.warning(f"Error extracting text from layout: {str(e)}")
            return ""
            
    def _get_bounding_box(self, bounding_poly, page_dimension) -> Dict[str, float]:
        """Extract bounding box coordinates"""
        try:
            if not bounding_poly or not bounding_poly.vertices:
                return {'x': 0, 'y': 0, 'width': 0, 'height': 0}
                
            vertices = bounding_poly.vertices
            
            # Get min/max coordinates
            x_coords = [v.x for v in vertices if hasattr(v, 'x')]
            y_coords = [v.y for v in vertices if hasattr(v, 'y')]
            
            if not x_coords or not y_coords:
                return {'x': 0, 'y': 0, 'width': 0, 'height': 0}
                
            x = min(x_coords)
            y = min(y_coords)
            width = max(x_coords) - x
            height = max(y_coords) - y
            
            # Normalize coordinates (0-1 range)
            if page_dimension:
                x = x / page_dimension.width
                y = y / page_dimension.height
                width = width / page_dimension.width
                height = height / page_dimension.height
                
            return {
                'x': x,
                'y': y,
                'width': width,
                'height': height
            }
            
        except Exception as e:
            logger.warning(f"Error extracting bounding box: {str(e)}")
            return {'x': 0, 'y': 0, 'width': 0, 'height': 0}
