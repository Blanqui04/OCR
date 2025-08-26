# main.py
from src.pdf_to_images import pdf_to_images
from src.ocr_processor import ocr_with_boxes
from src.data_extractor import extract_technical_data
import json

def process_pla(pdf_path):
    # 1. PDF → Imatges
    image_paths = pdf_to_images(pdf_path, "C:\\Users\\eceballos\\OneDrive - SOME, S.A\\Desktop\\Projectes\\OCR\\data\\images")

    # 2. OCR
    ocr_data, shape = ocr_with_boxes(image_paths[0])  # Només pàgina 1 ara
    with open("C:\\Users\\eceballos\\OneDrive - SOME, S.A\\Desktop\\Projectes\\OCR\\data\\output\\raw\\ocr_output.json", "w") as f:
        json.dump(ocr_data, f)

    # 3. Extracció
    tech_data = extract_technical_data(ocr_data)
    with open("C:\\Users\\eceballos\\OneDrive - SOME, S.A\\Desktop\\Projectes\\OCR\\data\\output\\structured\\structured_output.json", "w") as f:
        json.dump(tech_data, f, indent=2)

    print("✅ Procés complet!")

if __name__ == "__main__":
    process_pla("C:\\Users\\eceballos\\OneDrive - SOME, S.A\\Desktop\\Projectes\\OCR\\data\\exemples\\6555945_003.pdf")