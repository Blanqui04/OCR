#!/usr/bin/env python3
"""
OCR Viewer Application - Main Entry Point
Professional OCR visualization tool with Google Cloud Document AI integration
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ocr_viewer.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'google.cloud.documentai',
        'PIL',
        'fitz',  # PyMuPDF
        'reportlab'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('.', '/').split('/')[0])
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        error_msg = f"Missing required packages: {', '.join(missing_packages)}\n"
        error_msg += "Please install them using: pip install -r requirements.txt"
        logger.error(error_msg)
        messagebox.showerror("Missing Dependencies", error_msg)
        return False
    
    return True

def check_credentials():
    """Check if Google Cloud credentials are properly configured"""
    try:
        credentials_path = os.path.join(os.path.dirname(__file__), 'docs', 'natural-bison-465607-b6-a638a05f2638.json')
        if os.path.exists(credentials_path):
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
            logger.info(f"Google Cloud credentials found: {credentials_path}")
            return True
        else:
            logger.warning("Google Cloud credentials file not found")
            return False
    except Exception as e:
        logger.error(f"Error checking credentials: {str(e)}")
        return False

def main():
    """Main application entry point"""
    try:
        logger.info("Starting OCR Viewer Application")
        
        # Check dependencies
        if not check_dependencies():
            sys.exit(1)
        
        # Check credentials
        check_credentials()
        
        # Import and start the main application
        from ocr_viewer import OCRViewerApp
        
        # Create main window
        root = tk.Tk()
        app = OCRViewerApp(root)
        
        # Start the application
        logger.info("Application started successfully")
        root.mainloop()
        
    except Exception as e:
        logger.error(f"Application startup failed: {str(e)}")
        messagebox.showerror("Application Error", f"Failed to start application:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
