#!/usr/bin/env python3
"""
PDF Handler for OCR Viewer Application
Handles PDF loading, rendering, and page management
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
import io
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

logger = logging.getLogger(__name__)

class PDFHandler:
    """Handles PDF operations for the OCR Viewer"""
    
    def __init__(self):
        """Initialize PDF handler"""
        self.document = None
        self.current_page = 0
        self.total_pages = 0
        self.file_path = None
        self.zoom_level = 1.0
        self.page_cache = {}  # Cache for rendered pages
        
    def open_pdf(self, file_path: str) -> bool:
        """
        Open a PDF file
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not fitz:
                logger.error("PyMuPDF (fitz) not installed. Cannot open PDF files.")
                return False
                
            # Close existing document
            self.close_pdf()
            
            # Open new document
            self.document = fitz.open(file_path)
            self.file_path = file_path
            self.total_pages = len(self.document)
            self.current_page = 0
            self.page_cache = {}
            
            logger.info(f"PDF opened successfully: {file_path}")
            logger.info(f"Total pages: {self.total_pages}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error opening PDF {file_path}: {str(e)}")
            return False
            
    def close_pdf(self):
        """Close the current PDF document"""
        try:
            if self.document:
                self.document.close()
                self.document = None
                
            self.file_path = None
            self.current_page = 0
            self.total_pages = 0
            self.page_cache = {}
            
            logger.info("PDF closed")
            
        except Exception as e:
            logger.error(f"Error closing PDF: {str(e)}")
            
    def get_page_count(self) -> int:
        """Get the total number of pages"""
        return self.total_pages
        
    def set_current_page(self, page_num: int) -> bool:
        """
        Set the current page number
        
        Args:
            page_num: Page number (0-based)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.document:
                return False
                
            if 0 <= page_num < self.total_pages:
                self.current_page = page_num
                return True
            else:
                logger.warning(f"Invalid page number: {page_num}")
                return False
                
        except Exception as e:
            logger.error(f"Error setting current page: {str(e)}")
            return False
            
    def get_current_page(self) -> int:
        """Get the current page number"""
        return self.current_page
        
    def next_page(self) -> bool:
        """Go to the next page"""
        return self.set_current_page(self.current_page + 1)
        
    def prev_page(self) -> bool:
        """Go to the previous page"""
        return self.set_current_page(self.current_page - 1)
        
    def set_zoom_level(self, zoom: float):
        """
        Set the zoom level
        
        Args:
            zoom: Zoom level (1.0 = 100%)
        """
        if zoom > 0:
            self.zoom_level = zoom
            # Clear cache when zoom changes
            self.page_cache = {}
            
    def get_zoom_level(self) -> float:
        """Get the current zoom level"""
        return self.zoom_level
        
    def render_page(self, page_num: int = None, zoom: float = None) -> Optional[Image.Image]:
        """
        Render a page as an image
        
        Args:
            page_num: Page number to render (default: current page)
            zoom: Zoom level (default: current zoom level)
            
        Returns:
            PIL.Image: Rendered page image or None if failed
        """
        try:
            if not self.document or not Image:
                return None
                
            if page_num is None:
                page_num = self.current_page
                
            if zoom is None:
                zoom = self.zoom_level
                
            # Check if page is already cached
            cache_key = f"{page_num}_{zoom:.2f}"
            if cache_key in self.page_cache:
                return self.page_cache[cache_key]
                
            if not (0 <= page_num < self.total_pages):
                logger.warning(f"Invalid page number for rendering: {page_num}")
                return None
                
            # Get the page
            page = self.document[page_num]
            
            # Create transformation matrix for zoom
            mat = fitz.Matrix(zoom, zoom)
            
            # Render page to pixmap
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # Convert to PIL Image
            img_data = pix.tobytes("ppm")
            img = Image.open(io.BytesIO(img_data))
            
            # Cache the image
            self.page_cache[cache_key] = img
            
            logger.debug(f"Page {page_num + 1} rendered at {zoom:.2f}x zoom")
            
            return img
            
        except Exception as e:
            logger.error(f"Error rendering page {page_num}: {str(e)}")
            return None
            
    def get_page_size(self, page_num: int = None) -> Tuple[float, float]:
        """
        Get the size of a page in points
        
        Args:
            page_num: Page number (default: current page)
            
        Returns:
            Tuple[float, float]: (width, height) in points
        """
        try:
            if not self.document:
                return (0, 0)
                
            if page_num is None:
                page_num = self.current_page
                
            if not (0 <= page_num < self.total_pages):
                return (0, 0)
                
            page = self.document[page_num]
            rect = page.rect
            
            return (rect.width, rect.height)
            
        except Exception as e:
            logger.error(f"Error getting page size: {str(e)}")
            return (0, 0)
            
    def get_page_text(self, page_num: int = None) -> str:
        """
        Extract text from a page
        
        Args:
            page_num: Page number (default: current page)
            
        Returns:
            str: Extracted text
        """
        try:
            if not self.document:
                return ""
                
            if page_num is None:
                page_num = self.current_page
                
            if not (0 <= page_num < self.total_pages):
                return ""
                
            page = self.document[page_num]
            return page.get_text()
            
        except Exception as e:
            logger.error(f"Error extracting text from page {page_num}: {str(e)}")
            return ""
            
    def search_text(self, text: str, page_num: int = None) -> List[Dict]:
        """
        Search for text in a page
        
        Args:
            text: Text to search for
            page_num: Page number (default: current page)
            
        Returns:
            List[Dict]: List of found text instances with coordinates
        """
        try:
            if not self.document or not text:
                return []
                
            if page_num is None:
                page_num = self.current_page
                
            if not (0 <= page_num < self.total_pages):
                return []
                
            page = self.document[page_num]
            text_instances = page.search_for(text)
            
            results = []
            for i, rect in enumerate(text_instances):
                results.append({
                    'index': i,
                    'text': text,
                    'bbox': {
                        'x': rect.x0,
                        'y': rect.y0,
                        'width': rect.x1 - rect.x0,
                        'height': rect.y1 - rect.y0
                    }
                })
                
            return results
            
        except Exception as e:
            logger.error(f"Error searching text: {str(e)}")
            return []
            
    def get_document_info(self) -> Dict:
        """
        Get document metadata
        
        Returns:
            Dict: Document information
        """
        try:
            if not self.document:
                return {}
                
            metadata = self.document.metadata
            
            info = {
                'title': metadata.get('title', ''),
                'author': metadata.get('author', ''),
                'subject': metadata.get('subject', ''),
                'creator': metadata.get('creator', ''),
                'producer': metadata.get('producer', ''),
                'creation_date': metadata.get('creationDate', ''),
                'modification_date': metadata.get('modDate', ''),
                'page_count': self.total_pages,
                'file_path': self.file_path,
                'encrypted': self.document.needs_pass,
                'file_size': Path(self.file_path).stat().st_size if self.file_path else 0
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting document info: {str(e)}")
            return {}
            
    def convert_coordinates(self, bbox: Dict, from_page_size: Tuple[float, float], 
                          to_page_size: Tuple[float, float]) -> Dict:
        """
        Convert coordinates between different page sizes (for zoom)
        
        Args:
            bbox: Bounding box dictionary with x, y, width, height
            from_page_size: Source page size (width, height)
            to_page_size: Target page size (width, height)
            
        Returns:
            Dict: Converted bounding box
        """
        try:
            if not all([from_page_size[0], from_page_size[1], to_page_size[0], to_page_size[1]]):
                return bbox
                
            scale_x = to_page_size[0] / from_page_size[0]
            scale_y = to_page_size[1] / from_page_size[1]
            
            return {
                'x': bbox['x'] * scale_x,
                'y': bbox['y'] * scale_y,
                'width': bbox['width'] * scale_x,
                'height': bbox['height'] * scale_y
            }
            
        except Exception as e:
            logger.error(f"Error converting coordinates: {str(e)}")
            return bbox
            
    def clear_cache(self):
        """Clear the page rendering cache"""
        self.page_cache = {}
        logger.debug("Page cache cleared")
