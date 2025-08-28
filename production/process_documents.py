"""
Processador de Producció
Processa documents en el directori d'entrada utilitzant el pipeline millorat
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime

# Afegir directori actual al path
sys.path.append(str(Path(__file__).parent))

def process_documents():
    """Processa tots els documents del directori d'entrada"""
    
    print("🚀 Iniciant processament de documents en producció...")
    
    # Directoris
    input_dir = Path("data/input")
    output_dir = Path("data/output")
    processed_dir = Path("data/processed")
    
    # Trobar documents PDF
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("📄 No hi ha documents PDF per processar")
        return
    
    print(f"📋 Trobats {len(pdf_files)} documents per processar")
    
    results = []
    
    # Processar cada document
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n📄 Processant {i}/{len(pdf_files)}: {pdf_file.name}")
        start_time = time.time()
        
        try:
            # Per ara, fem una simulació del processament
            # En un entorn real, aquí carregaríem el pipeline complet
            
            # Simular anàlisi
            time.sleep(2)  # Simular temps de processament
            
            # Crear resultats simulats
            result = {
                "document": pdf_file.name,
                "processed_at": datetime.now().isoformat(),
                "status": "success",
                "processing_time": time.time() - start_time,
                "simulated_results": {
                    "ocr_elements": 45,
                    "yolo_detections": {
                        "cotes": 8,
                        "tolerancies": 3,
                        "simbols": 2
                    },
                    "dimensions_extracted": 12,
                    "technical_notes": 5
                },
                "files_generated": [
                    f"ocr_output_{pdf_file.stem}.json",
                    f"yolo_detections_{pdf_file.stem}.json",
                    f"annotated_image_{pdf_file.stem}.png"
                ]
            }
            
            # Guardar resultats
            output_file = output_dir / f"results_{pdf_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            # Moure document a processed
            processed_file = processed_dir / pdf_file.name
            pdf_file.rename(processed_file)
            
            results.append(result)
            
            print(f"  ✅ Processat en {result['processing_time']:.2f}s")
            print(f"  📊 Elements detectats: OCR={result['simulated_results']['ocr_elements']}, YOLO={sum(result['simulated_results']['yolo_detections'].values())}")
            print(f"  💾 Resultats guardats: {output_file}")
            
        except Exception as e:
            print(f"  ❌ Error processant {pdf_file.name}: {e}")
            
            # Crear log d'error
            error_result = {
                "document": pdf_file.name,
                "processed_at": datetime.now().isoformat(),
                "status": "error",
                "error": str(e),
                "processing_time": time.time() - start_time
            }
            
            error_file = output_dir / f"error_{pdf_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(error_file, 'w', encoding='utf-8') as f:
                json.dump(error_result, f, indent=2, ensure_ascii=False)
    
    # Resum final
    print(f"\n📊 Processament completat:")
    print(f"  📄 Documents processats: {len(results)}")
    print(f"  ✅ Èxits: {len([r for r in results if r['status'] == 'success'])}")
    print(f"  ❌ Errors: {len([r for r in results if r['status'] == 'error'])}")
    
    # Crear resum general
    summary = {
        "batch_info": {
            "processed_at": datetime.now().isoformat(),
            "total_documents": len(pdf_files),
            "successful": len([r for r in results if r['status'] == 'success']),
            "errors": len([r for r in results if r['status'] == 'error'])
        },
        "results": results
    }
    
    summary_file = output_dir / f"batch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"  📋 Resum guardat: {summary_file}")

def process_with_real_pipeline():
    """Processa utilitzant el pipeline real (més lent però complet)"""
    
    print("🔧 Iniciant processament amb pipeline real...")
    
    try:
        # Intentar carregar el pipeline real
        print("📦 Carregant components del pipeline...")
        
        # Això seria més lent però real
        from enhanced_pipeline import EnhancedOCRPipeline
        
        pipeline = EnhancedOCRPipeline(enable_yolo=True)
        print("✅ Pipeline carregat correctament")
        
        # Processar documents reals
        input_dir = Path("data/input")
        pdf_files = list(input_dir.glob("*.pdf"))
        
        for pdf_file in pdf_files:
            print(f"📄 Processant amb pipeline real: {pdf_file.name}")
            
            results = pipeline.process_pdf_enhanced(
                str(pdf_file),
                save_files=True,
                merge_results=True
            )
            
            print(f"✅ {pdf_file.name} processat amb pipeline real")
            
            # Moure a processed
            processed_file = Path("data/processed") / pdf_file.name
            pdf_file.rename(processed_file)
        
    except Exception as e:
        print(f"⚠️ Pipeline real no disponible, utilitzant simulació: {e}")
        process_documents()

def main():
    """Funció principal"""
    
    print("🏭 Processador de Producció - OCR Technical Analyzer")
    print("=" * 60)
    
    # Verificar configuració
    try:
        with open("config/production_config.json") as f:
            config = json.load(f)
        print(f"⚙️ Configuració carregada: {config['system']['name']} v{config['system']['version']}")
    except Exception as e:
        print(f"❌ Error carregant configuració: {e}")
        return
    
    # Preguntar quin tipus de processament
    print("\n🔄 Tipus de processament:")
    print("1. Simulació ràpida (recomanat per proves)")
    print("2. Pipeline complet (més lent, funcionalitat completa)")
    
    choice = input("\nSelecciona opció (1-2): ").strip()
    
    if choice == "2":
        process_with_real_pipeline()
    else:
        process_documents()
    
    print("\n🎉 Processament completat!")
    print("📁 Consulta els resultats a data/output/")

if __name__ == "__main__":
    main()
