"""
Test del Pipeline OCR Millorat
Executa el pipeline complet amb OCR + YOLOv8
"""

import sys
from pathlib import Path
import json

# Afegir src al path
sys.path.append(str(Path(__file__).parent / "src"))

# Importar directament
from technical_element_detector import TechnicalElementDetector

def test_yolo_detector():
    """Test del detector YOLOv8"""
    print("🎯 Testejant detector YOLOv8...")
    
    detector = TechnicalElementDetector()
    detector.set_thresholds(confidence=0.3, iou=0.45)
    
    # Test amb imatge disponible
    image_path = "data/images/page_1.png"
    
    if not Path(image_path).exists():
        print(f"❌ Imatge no trobada: {image_path}")
        return
    
    print(f"📷 Analitzant: {image_path}")
    
    results = detector.detect_elements(image_path, save_annotated=True)
    
    if "error" in results:
        print(f"❌ Error: {results['error']}")
        return
    
    # Mostrar resultats
    print(f"✅ Detecció completada!")
    print(f"📊 Total elements: {results['total_elements']}")
    print(f"📋 Per tipus: {results['summary']}")
    
    # Detalls per element
    print(f"\n🔍 Detalls per element:")
    for element in results['elements']:
        print(f"  - {element['type']}: {element['confidence']:.3f} confiança")
    
    # Imatge anotada
    if 'annotated_image' in results:
        print(f"🖼️ Imatge anotada: {results['annotated_image']}")
    
    return results

def test_directory_processing():
    """Test de processament de directori"""
    print("\n📁 Testejant processament de directori...")
    
    detector = TechnicalElementDetector()
    detector.set_thresholds(confidence=0.2, iou=0.45)
    
    # Processar directori d'imatges d'entrenament
    input_dir = "data/training/images/train"
    output_dir = "data/training/test_results"
    
    if not Path(input_dir).exists():
        print(f"❌ Directori no trobat: {input_dir}")
        return
    
    print(f"📂 Processant directori: {input_dir}")
    
    results = detector.detect_in_directory(input_dir, output_dir)
    
    if "error" in results:
        print(f"❌ Error: {results['error']}")
        return
    
    print(f"✅ Processament completat!")
    print(f"📊 Imatges processades: {results['batch_info']['total_images']}")
    print(f"🎯 Total elements: {results['summary']['total_elements']}")
    print(f"📋 Per tipus: {results['summary']['by_type']}")
    
    return results

def main():
    """Funció principal de test"""
    print("🚀 Iniciant tests del Pipeline OCR Millorat")
    print("=" * 50)
    
    # Test 1: Detector individual
    yolo_results = test_yolo_detector()
    
    # Test 2: Processament de directori
    batch_results = test_directory_processing()
    
    print("\n" + "=" * 50)
    print("✅ Tests completats!")
    
    if yolo_results:
        print(f"🎯 Test individual: {yolo_results['total_elements']} elements detectats")
    
    if batch_results:
        print(f"📁 Test directori: {batch_results['summary']['total_elements']} elements en total")

if __name__ == "__main__":
    main()
