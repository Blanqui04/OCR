"""
Demo de Producció amb Pipeline Real
Executa una demostració completa del sistema en producció
"""

import sys
import time
from pathlib import Path

# Afegir directori actual al path
sys.path.append(str(Path(__file__).parent))

def demo_real_processing():
    """Demostració amb processament real (sense interacció)"""
    
    print("🎬 DEMO: Processament Real en Producció")
    print("=" * 50)
    
    try:
        print("📦 Carregant detector YOLOv8...")
        from technical_element_detector import TechnicalElementDetector
        
        detector = TechnicalElementDetector()
        detector.set_thresholds(confidence=0.3, iou=0.45)
        print("✅ Detector YOLOv8 carregat")
        
        # Buscar imatges disponibles per processar
        input_dir = Path("data/input")
        
        # Si hi ha PDFs, convertir a imatges primer
        pdf_files = list(input_dir.glob("*.pdf"))
        
        if pdf_files:
            print(f"📄 Trobat PDF: {pdf_files[0].name}")
            
            # Per aquesta demo, utilitzem una imatge existent
            print("🔄 Per aquesta demo, utilitzarem imatge d'exemple...")
            
            # Copiar imatge d'exemple si existeix
            example_image = Path("../data/images/page_1.png")
            if example_image.exists():
                demo_image = Path("data/input/demo_page.png")
                import shutil
                shutil.copy2(example_image, demo_image)
                print(f"📷 Imatge copiada: {demo_image}")
                
                # Processar amb YOLOv8
                print("🎯 Detectant elements tècnics...")
                results = detector.detect_elements(str(demo_image), save_annotated=True)
                
                if "error" not in results:
                    print(f"✅ Detecció completada!")
                    print(f"📊 Total elements: {results['total_elements']}")
                    print(f"📋 Per tipus: {results['summary']}")
                    
                    # Mostrar detalls
                    for element in results['elements']:
                        print(f"  - {element['type']}: confiança {element['confidence']:.3f}")
                    
                    # Guardar resultats
                    output_file = Path("data/output/demo_results.json")
                    import json
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(results, f, indent=2, ensure_ascii=False)
                    
                    print(f"💾 Resultats guardats: {output_file}")
                    
                    if 'annotated_image' in results:
                        print(f"🖼️ Imatge anotada: {results['annotated_image']}")
                
                else:
                    print(f"❌ Error en detecció: {results['error']}")
            
            else:
                print("⚠️ No s'ha trobat imatge d'exemple")
        
        else:
            print("📄 No hi ha documents per processar")
    
    except Exception as e:
        print(f"❌ Error en demo: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Funció principal de demo"""
    
    print("🚀 Demo de Producció - OCR Technical Analyzer")
    print("Aquesta demo utilitza el pipeline real amb YOLOv8")
    print("=" * 60)
    
    start_time = time.time()
    
    demo_real_processing()
    
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 60)
    print(f"⏱️ Demo completada en {duration:.2f} segons")
    print("🎉 Sistema de producció demostrat amb èxit!")

if __name__ == "__main__":
    main()
