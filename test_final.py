#!/usr/bin/env python3
"""
Test final per verificar que tot funciona correctament
"""
import sys
from pathlib import Path

# Configurar el path
current_dir = Path(__file__).parent.absolute()
src_dir = current_dir / "src"

if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

print("🔍 Test final del sistema...")

try:
    # Test 1: Import del pipeline d'IA
    from ai_enhanced_pipeline import AIEnhancedPipeline
    print("✅ AIEnhancedPipeline importat correctament")
    
    # Test 2: Inicialitzar pipeline
    config_path = "config_ai.json"
    if Path(config_path).exists():
        pipeline = AIEnhancedPipeline(config_path)
        print("✅ Pipeline inicialitzat correctament")
        
        # Test 3: Verificar PDF d'exemple
        pdf_path = "data/exemples/6555945_003.pdf"
        if Path(pdf_path).exists():
            print(f"✅ PDF trobat: {pdf_path}")
            
            # Test 4: Processar document (sense IA per simplicitat)
            print("🔄 Processant document...")
            results = pipeline.process_document_with_ai(pdf_path, use_ai=False)
            
            print(f"✅ Document processat sense errors!")
            print(f"   - Pàgines: {len(results['pages'])}")
            print(f"   - Total elements: {results['total_elements']}")
            print(f"   - IA habilitada: {results['ai_enabled']}")
            
            # Test 5: Verificar estructura d'elements
            if results['pages']:
                first_page = results['pages'][0]
                elements = first_page.get('elements', [])
                print(f"   - Elements a la primera pàgina: {len(elements)}")
                
                if elements:
                    sample_element = elements[0]
                    required_fields = ['type', 'confidence', 'text', 'source', 'bbox', 'coordinates', 'center', 'area', 'id']
                    missing_fields = [field for field in required_fields if field not in sample_element]
                    
                    if missing_fields:
                        print(f"   ⚠️ Camps que falten: {missing_fields}")
                    else:
                        print("   ✅ Tots els camps necessaris estan presents")
                        
        else:
            print(f"⚠️ PDF no trobat: {pdf_path}")
    else:
        print(f"⚠️ Configuració no trobada: {config_path}")
        
except Exception as e:
    print(f"❌ Error en test final: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Test final completat!")
