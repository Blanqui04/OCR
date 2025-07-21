#!/usr/bin/env python3
"""
Test del visualitzador de PDF
"""

import tkinter as tk
from ocr_viewer_app import OCRViewerApp
import os

def test_pdf_viewer():
    """Test del visualitzador PDF"""
    print("Iniciant test del visualitzador PDF...")
    
    # Create main window
    root = tk.Tk()
    app = OCRViewerApp(root)
    
    # Check if there's a sample PDF in the current directory
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    if pdf_files:
        sample_pdf = pdf_files[0]
        print(f"Trobat PDF de mostra: {sample_pdf}")
        print("\nFuncionalitats del visualitzador:")
        print("• 📄 Visualització de PDF amb zoom")
        print("• 🎯 Marques de text reconegut amb colors segons confiança")
        print("• 🔢 Números d'ordre de lectura")
        print("• 🖱️ Selecció interactiva de blocs de text")
        print("• ⚡ Navegació per pàgines amb tecles de fletxa")
        print("• 🔍 Zoom amb roda del ratolí o botons")
        
        # Load the PDF automatically for demonstration
        if hasattr(app, 'load_pdf'):
            root.after(1000, lambda: app.load_pdf(os.path.abspath(sample_pdf)))
            print(f"\nCarregant automàticament: {sample_pdf}")
    else:
        print("No s'ha trobat cap PDF de mostra al directori actual")
        print("Pots obrir manualment un PDF des de l'aplicació")
    
    print("\n🚀 Aplicació OCR Viewer iniciada!")
    print("Tanca la finestra per sortir...")
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    test_pdf_viewer()
