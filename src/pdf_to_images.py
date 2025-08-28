# src/pdf_to_images.py
from pdf2image import convert_from_path
import os
import tempfile

def pdf_to_images(pdf_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    images = convert_from_path(pdf_path, dpi=300)  
    image_paths = []
    for i, image in enumerate(images):
        path = os.path.join(output_folder, f"page_{i+1}.png")
        image.save(path, "PNG")
        image_paths.append(path)
        print(f"Pàgina {i+1} guardada com a {path}")
    return image_paths

def convert_pdf_to_images(pdf_path, output_folder=None):
    """
    Convert PDF to images - alias for compatibility with web pipeline
    """
    if output_folder is None:
        # Create temporary directory for images
        output_folder = tempfile.mkdtemp(prefix="ocr_images_")
    
    return pdf_to_images(pdf_path, output_folder)

# Exemple d'ús
if __name__ == "__main__":
    pdf_path = "C:\\Users\\eceballos\\OneDrive - SOME, S.A\\Desktop\\Projectes\\OCR\\data\\exemples\\6555945_003.pdf"
    output_folder = "C:\\Users\\eceballos\\OneDrive - SOME, S.A\\Desktop\\Projectes\\OCR\\data\\images"
    pdf_to_images(pdf_path, output_folder)