# src/pipeline.py
import os
import json
from pathlib import Path

# Import absolute para evitar problemas con relative imports
try:
    from pdf_to_images import pdf_to_images
    from ocr_processor import ocr_with_boxes
    from data_extractor import extract_technical_data
    from dimension_linker import detect_lines, link_text_to_lines
except ImportError:
    # Fallback con relative imports
    from .pdf_to_images import pdf_to_images
    from .ocr_processor import ocr_with_boxes
    from .data_extractor import extract_technical_data
    from .dimension_linker import detect_lines, link_text_to_lines

class OCRPipeline:
    def __init__(self, base_dir=None):
        if base_dir is None:
            self.base_dir = str(Path(__file__).parent.parent)
        else:
            self.base_dir = base_dir
            
        # Crear directoris necessaris
        self.ensure_directories()
    
    def ensure_directories(self):
        """Crear tots els directoris necessaris"""
        dirs = [
            "data/images",
            "data/output/raw",
            "data/output/structured", 
            "data/lines",
            "data/dimensions"
        ]
        
        for dir_path in dirs:
            full_path = os.path.join(self.base_dir, dir_path)
            os.makedirs(full_path, exist_ok=True)
    
    def process_pdf(self, pdf_path, save_files=True):
        """
        Processa un PDF complet amb tot el pipeline
        
        Args:
            pdf_path: Camí al fitxer PDF
            save_files: Si True, guarda tots els fitxers intermedis
            
        Returns:
            dict: Diccionari amb tots els resultats
        """
        results = {}
        
        # 1. PDF → Imatges
        images_dir = os.path.join(self.base_dir, "data", "images")
        image_paths = pdf_to_images(pdf_path, images_dir)
        image_path = image_paths[0]  # Traballem amb la primera pàgina
        results['image_path'] = image_path
        
        # 2. OCR amb mode tècnic
        ocr_data, img_shape = ocr_with_boxes(image_path, use_technical_mode=True)
        results['ocr_data'] = ocr_data
        results['image_shape'] = img_shape
        
        if save_files:
            with open(os.path.join(self.base_dir, "data/output/raw/ocr_output.json"), "w", encoding="utf-8") as f:
                json.dump(ocr_data, f, ensure_ascii=False, indent=2)
        
        # 3. Detectar línies
        line_boxes, _ = detect_lines(image_path, threshold=100)
        results['line_boxes'] = line_boxes
        
        if save_files:
            with open(os.path.join(self.base_dir, "data/lines/lines.json"), "w", encoding="utf-8") as f:
                json.dump(line_boxes, f, ensure_ascii=False, indent=2)
        
        # 4. Vincular textos amb línies
        linked_data = link_text_to_lines(ocr_data, line_boxes, max_distance=150)
        results['linked_data'] = linked_data
        
        if save_files:
            with open(os.path.join(self.base_dir, "data/dimensions/dimensions_linked.json"), "w", encoding="utf-8") as f:
                json.dump(linked_data, f, indent=2, ensure_ascii=False)
        
        # 5. Extracció tècnica
        tech_data = extract_technical_data(ocr_data)
        results['tech_data'] = tech_data
        
        if save_files:
            with open(os.path.join(self.base_dir, "data/output/structured/structured_output.json"), "w", encoding="utf-8") as f:
                json.dump(tech_data, f, indent=2, ensure_ascii=False)
        
        return results
    
    def get_stats(self, results):
        """Genera estadístiques del processament"""
        stats = {
            'total_text_elements': len(results.get('ocr_data', [])),
            'detected_lines': len(results.get('line_boxes', [])),
            'linked_elements': len(results.get('linked_data', [])),
            'dimensions': len(results.get('tech_data', {}).get('dimensions', [])),
            'notes': len(results.get('tech_data', {}).get('notes', []))
        }
        return stats

def main():
    """Funció principal per executar el pipeline com a script"""
    pipeline = OCRPipeline()
    pdf_path = os.path.join(pipeline.base_dir, "data", "exemples", "6555945_003.pdf")
    
    print("🚀 Iniciant pipeline OCR...")
    results = pipeline.process_pdf(pdf_path)
    
    stats = pipeline.get_stats(results)
    print(f"📊 Estadístiques:")
    print(f"  - Elements de text: {stats['total_text_elements']}")
    print(f"  - Línies detectades: {stats['detected_lines']}")
    print(f"  - Elements vinculats: {stats['linked_elements']}")
    print(f"  - Cotes: {stats['dimensions']}")
    print(f"  - Anotacions: {stats['notes']}")
    print("✅ Pipeline completat!")

if __name__ == "__main__":
    main()
