"""
Google Document AI OCR Integration
Provides advanced OCR capabilities for technical drawings and blueprints
"""

import os
import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any, Tuple

try:
    from google.cloud import documentai
    from google.oauth2 import service_account
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    print("Warning: Google Cloud libraries not available")

@dataclass
class DetectedElement:
    """Represents a detected element from Google Document AI"""
    element_type: str
    value: str
    description: str
    confidence: float
    coordinates: Tuple[float, float, float, float]  # x1, y1, x2, y2
    page_number: int
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

class GoogleDocumentAIOCR:
    """Google Document AI OCR processor for technical drawings"""
    
    def __init__(self, project_id: str, location: str, processor_id: str, credentials_path: str):
        """
        Initialize Google Document AI OCR
        
        Args:
            project_id: Google Cloud project ID
            location: Google Cloud location (e.g., 'us' or 'eu')
            processor_id: Document AI processor ID
            credentials_path: Path to service account key JSON file
        """
        if not GOOGLE_CLOUD_AVAILABLE:
            raise ImportError("Google Cloud libraries are not installed")
            
        self.project_id = project_id
        self.location = location
        self.processor_id = processor_id
        self.credentials_path = credentials_path
        
        # Initialize client
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Document AI client with credentials"""
        try:
            # Load credentials
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            
            # Initialize client
            self.client = documentai.DocumentProcessorServiceClient(credentials=credentials)
            
            # Create processor resource name
            self.processor_name = self.client.processor_path(
                self.project_id, 
                self.location, 
                self.processor_id
            )
            
            print(f"✅ Document AI client initialized successfully")
            print(f"📍 Processor: {self.processor_name}")
            
        except Exception as e:
            print(f"❌ Error initializing Document AI client: {e}")
            raise
    
    def process_document(self, file_path: str) -> Dict[str, Any]:
        """
        Process a PDF document with Google Document AI
        
        Args:
            file_path: Path to the PDF file to process
            
        Returns:
            Dictionary containing processed results and detected elements
        """
        try:
            print(f"📄 Processing document: {os.path.basename(file_path)}")
            
            # Read document file
            with open(file_path, 'rb') as document_file:
                document_content = document_file.read()
            
            # Configure request
            raw_document = documentai.RawDocument(
                content=document_content,
                mime_type='application/pdf'
            )
            
            request = documentai.ProcessRequest(
                name=self.processor_name,
                raw_document=raw_document
            )
            
            # Process document
            print("🤖 Sending request to Google Document AI...")
            result = self.client.process_document(request=request)
            document = result.document
            
            print(f"✅ Document processed successfully")
            print(f"📊 Pages: {len(document.pages)}")
            print(f"📝 Text length: {len(document.text)} characters")
            
            # Extract structured elements
            elements = self._extract_elements(document)
            
            # Prepare results
            results = {
                'success': True,
                'document_text': document.text,
                'pages': len(document.pages),
                'elements': elements,
                'raw_document': document,  # Keep reference for advanced processing
                'statistics': self._calculate_statistics(elements)
            }
            
            print(f"🔍 Extracted {len(elements)} structured elements")
            
            return results
            
        except Exception as e:
            print(f"❌ Error processing document: {e}")
            return {
                'success': False,
                'error': str(e),
                'elements': [],
                'document_text': '',
                'pages': 0
            }
    
    def _extract_elements(self, document) -> List[DetectedElement]:
        """
        Extract structured elements from Document AI response
        
        Args:
            document: Document AI document object
            
        Returns:
            List of DetectedElement objects
        """
        elements = []
        
        try:
            # Process each page
            for page_num, page in enumerate(document.pages):
                page_elements = []
                
                # Extract from form fields (if available)
                if hasattr(page, 'form_fields'):
                    page_elements.extend(self._extract_form_fields(page.form_fields, page_num, document.text))
                
                # Extract from tables (if available)
                if hasattr(page, 'tables'):
                    page_elements.extend(self._extract_table_data(page.tables, page_num, document.text))
                
                # Extract from paragraphs
                if hasattr(page, 'paragraphs'):
                    page_elements.extend(self._extract_paragraph_data(page.paragraphs, page_num, document.text))
                
                # Extract from lines (fallback)
                if not page_elements and hasattr(page, 'lines'):
                    page_elements.extend(self._extract_line_data(page.lines, page_num, document.text))
                
                elements.extend(page_elements)
            
            # Post-process elements to classify types
            elements = self._classify_elements(elements)
            
        except Exception as e:
            print(f"Warning: Error extracting elements: {e}")
            # Fallback: extract basic text blocks
            elements = self._extract_basic_text_blocks(document)
        
        return elements
    
    def _extract_form_fields(self, form_fields, page_num: int, document_text: str) -> List[DetectedElement]:
        """Extract elements from form fields"""
        elements = []
        
        for field in form_fields:
            try:
                # Get field name
                field_name = ""
                if field.field_name:
                    field_name = self._get_text_from_layout(document_text, field.field_name)
                
                # Get field value
                field_value = ""
                if field.field_value:
                    field_value = self._get_text_from_layout(document_text, field.field_value)
                
                # Get bounding box
                bbox = self._get_bounding_box(field.field_value, page_num) if field.field_value else (0, 0, 100, 20)
                
                # Determine confidence
                confidence = field.field_value.confidence if hasattr(field.field_value, 'confidence') else 0.8
                
                if field_value.strip():
                    element = DetectedElement(
                        element_type='form_field',
                        value=field_value.strip(),
                        description=field_name.strip(),
                        confidence=confidence,
                        coordinates=bbox,
                        page_number=page_num
                    )
                    elements.append(element)
                    
            except Exception as e:
                print(f"Warning: Error processing form field: {e}")
                continue
        
        return elements
    
    def _extract_table_data(self, tables, page_num: int, document_text: str) -> List[DetectedElement]:
        """Extract elements from table data"""
        elements = []
        
        for table in tables:
            try:
                for row in table.body_rows:
                    for cell in row.cells:
                        cell_text = self._get_text_from_layout(document_text, cell.layout)
                        
                        if cell_text.strip():
                            bbox = self._get_bounding_box(cell.layout, page_num)
                            confidence = cell.layout.confidence if hasattr(cell.layout, 'confidence') else 0.7
                            
                            element = DetectedElement(
                                element_type='table_cell',
                                value=cell_text.strip(),
                                description='Table cell data',
                                confidence=confidence,
                                coordinates=bbox,
                                page_number=page_num
                            )
                            elements.append(element)
                            
            except Exception as e:
                print(f"Warning: Error processing table: {e}")
                continue
        
        return elements
    
    def _extract_paragraph_data(self, paragraphs, page_num: int, document_text: str) -> List[DetectedElement]:
        """Extract elements from paragraph data"""
        elements = []
        
        for paragraph in paragraphs:
            try:
                para_text = self._get_text_from_layout(document_text, paragraph.layout)
                
                if para_text.strip():
                    bbox = self._get_bounding_box(paragraph.layout, page_num)
                    confidence = paragraph.layout.confidence if hasattr(paragraph.layout, 'confidence') else 0.8
                    
                    element = DetectedElement(
                        element_type='paragraph',
                        value=para_text.strip(),
                        description='Paragraph text',
                        confidence=confidence,
                        coordinates=bbox,
                        page_number=page_num
                    )
                    elements.append(element)
                    
            except Exception as e:
                print(f"Warning: Error processing paragraph: {e}")
                continue
        
        return elements
    
    def _extract_line_data(self, lines, page_num: int, document_text: str) -> List[DetectedElement]:
        """Extract elements from line data (fallback)"""
        elements = []
        
        for line in lines:
            try:
                line_text = self._get_text_from_layout(document_text, line.layout)
                
                if line_text.strip():
                    bbox = self._get_bounding_box(line.layout, page_num)
                    confidence = line.layout.confidence if hasattr(line.layout, 'confidence') else 0.6
                    
                    element = DetectedElement(
                        element_type='text_line',
                        value=line_text.strip(),
                        description='Text line',
                        confidence=confidence,
                        coordinates=bbox,
                        page_number=page_num
                    )
                    elements.append(element)
                    
            except Exception as e:
                print(f"Warning: Error processing line: {e}")
                continue
        
        return elements
    
    def _extract_basic_text_blocks(self, document) -> List[DetectedElement]:
        """Fallback method for basic text extraction"""
        elements = []
        
        try:
            # Simple text extraction as fallback
            full_text = document.text
            if full_text:
                lines = full_text.split('\n')
                for i, line in enumerate(lines):
                    if line.strip():
                        element = DetectedElement(
                            element_type='text_block',
                            value=line.strip(),
                            description='Basic text block',
                            confidence=0.5,
                            coordinates=(10, i*20, 500, (i+1)*20),
                            page_number=0
                        )
                        elements.append(element)
        except Exception as e:
            print(f"Error in basic text extraction: {e}")
        
        return elements
    
    def _get_text_from_layout(self, document_text: str, layout) -> str:
        """Extract text from layout using text segments"""
        try:
            if hasattr(layout, 'text_anchor') and layout.text_anchor:
                text_content = ""
                for segment in layout.text_anchor.text_segments:
                    start_index = int(segment.start_index) if hasattr(segment, 'start_index') else 0
                    end_index = int(segment.end_index) if hasattr(segment, 'end_index') else len(document_text)
                    text_content += document_text[start_index:end_index]
                return text_content
        except Exception as e:
            print(f"Warning: Error extracting text from layout: {e}")
        
        return ""
    
    def _get_bounding_box(self, layout, page_num: int) -> Tuple[float, float, float, float]:
        """Get bounding box coordinates from layout"""
        try:
            if hasattr(layout, 'bounding_poly') and layout.bounding_poly:
                if hasattr(layout.bounding_poly, 'normalized_vertices') and layout.bounding_poly.normalized_vertices:
                    # Normalized coordinates (0-1)
                    vertices = layout.bounding_poly.normalized_vertices
                    if len(vertices) >= 2:
                        x1 = min(v.x for v in vertices if hasattr(v, 'x')) * 1000  # Scale to typical PDF coordinates
                        y1 = min(v.y for v in vertices if hasattr(v, 'y')) * 1000
                        x2 = max(v.x for v in vertices if hasattr(v, 'x')) * 1000
                        y2 = max(v.y for v in vertices if hasattr(v, 'y')) * 1000
                        return (x1, y1, x2, y2)
                
                elif hasattr(layout.bounding_poly, 'vertices') and layout.bounding_poly.vertices:
                    # Absolute coordinates
                    vertices = layout.bounding_poly.vertices
                    if len(vertices) >= 2:
                        x1 = min(v.x for v in vertices if hasattr(v, 'x'))
                        y1 = min(v.y for v in vertices if hasattr(v, 'y'))
                        x2 = max(v.x for v in vertices if hasattr(v, 'x'))
                        y2 = max(v.y for v in vertices if hasattr(v, 'y'))
                        return (x1, y1, x2, y2)
        
        except Exception as e:
            print(f"Warning: Error extracting bounding box: {e}")
        
        # Return default coordinates
        return (10, 10, 100, 30)
    
    def _classify_elements(self, elements: List[DetectedElement]) -> List[DetectedElement]:
        """
        Classify elements based on content patterns for technical drawings
        """
        import re
        
        for element in elements:
            text = element.value.lower()
            
            # Dimension patterns
            if re.search(r'\d+[\.,]?\d*\s*(mm|cm|m|in|"|\'|±)', text):
                element.element_type = 'dimension'
                element.description = 'Dimensional measurement'
            
            # Tolerance patterns
            elif re.search(r'[±∓]\s*\d+[\.,]?\d*', text):
                element.element_type = 'tolerance'
                element.description = 'Tolerance specification'
            
            # Material specifications
            elif re.search(r'(steel|aluminum|iron|brass|copper|plastic|wood)', text):
                element.element_type = 'material'
                element.description = 'Material specification'
            
            # Part numbers
            elif re.search(r'^[A-Z]{1,3}[-_]?\d{2,6}[A-Z]?$', text):
                element.element_type = 'part_number'
                element.description = 'Part identification number'
            
            # Scale indicators
            elif re.search(r'(scale|escala)\s*[:\-]?\s*\d+:\d+', text):
                element.element_type = 'scale'
                element.description = 'Drawing scale'
            
            # Annotations and notes
            elif any(keyword in text for keyword in ['note', 'nota', 'see', 'veure', 'detail', 'detall']):
                element.element_type = 'annotation'
                element.description = 'Drawing annotation'
            
            # Default classification based on original type
            elif element.element_type in ['paragraph', 'text_line', 'text_block']:
                element.element_type = 'annotation'
                element.description = 'General text annotation'
        
        return elements
    
    def _calculate_statistics(self, elements: List[DetectedElement]) -> Dict[str, Any]:
        """Calculate statistics about detected elements"""
        if not elements:
            return {}
        
        stats = {
            'total_elements': len(elements),
            'average_confidence': sum(e.confidence for e in elements) / len(elements),
            'element_types': {},
            'pages_processed': len(set(e.page_number for e in elements)),
            'confidence_distribution': {
                'high': len([e for e in elements if e.confidence > 0.8]),
                'medium': len([e for e in elements if 0.5 <= e.confidence <= 0.8]),
                'low': len([e for e in elements if e.confidence < 0.5])
            }
        }
        
        # Count by element type
        for element in elements:
            element_type = element.element_type
            if element_type not in stats['element_types']:
                stats['element_types'][element_type] = 0
            stats['element_types'][element_type] += 1
        
        return stats

def test_google_document_ai():
    """Test function for Google Document AI integration"""
    print("🧪 Testing Google Document AI integration...")
    
    # Test configuration
    test_config = {
        'project_id': 'natural-bison-465607-b6',
        'location': 'us',
        'processor_id': 'your-processor-id',  # Replace with actual processor ID
        'credentials_path': r'C:\Users\eceballos\keys\natural-bison-465607-b6-a638a05f2638.json'
    }
    
    try:
        # Initialize OCR
        ocr = GoogleDocumentAIOCR(**test_config)
        print("✅ Google Document AI OCR initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_google_document_ai()
