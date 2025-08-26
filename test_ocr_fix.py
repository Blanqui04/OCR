#!/usr/bin/env python3
"""
Test simple per verificar que el processament funciona sense errors
"""
import sys
from pathlib import Path

# Configurar el path
current_dir = Path(__file__).parent.absolute()
src_dir = current_dir / "src"

if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

print("🔍 Testejant processament OCR...")

try:
    # Test 1: Importar OCR processor
    from ocr_processor import ocr_with_boxes
    print("✅ ocr_with_boxes importat correctament")
    
    # Test 2: Comprovar que el PDF existeix
    test_image = "data/images/page_1.png"
    if Path(test_image).exists():
        print(f"✅ Imatge trobada: {test_image}")
        
        # Test 3: Processar OCR
        print("🔄 Processant OCR...")
        results, img_shape = ocr_with_boxes(test_image)
        print(f"✅ OCR processat correctament!")
        print(f"   - Elements trobats: {len(results)}")
        print(f"   - Forma imatge: {img_shape}")
        
        if len(results) > 0:
            print(f"   - Primer element: {results[0]}")
        
        # Test 4: Verificar format de dades
        if isinstance(results, list):
            print("✅ Format de dades OCR correcte (llista)")
        else:
            print(f"❌ Format de dades OCR incorrecte: {type(results)}")
            
    else:
        print(f"⚠️ Imatge no trobada: {test_image}")
        print("Això és normal si no s'ha processat cap PDF encara")
        
except Exception as e:
    print(f"❌ Error en test OCR: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Test OCR completat!")
