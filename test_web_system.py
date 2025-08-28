#!/usr/bin/env python3
"""
Test script per verificar que la versió web té accés al pipeline YOLOv8
"""

import os
import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_enhanced_pipeline_import():
    """Test que podem importar el pipeline millorat"""
    try:
        # Test production pipeline
        sys.path.append(str(project_root / 'production'))
        from enhanced_pipeline import EnhancedOCRPipeline
        print("✅ Enhanced Pipeline import successful")
        return True
    except ImportError as e:
        print(f"❌ Enhanced Pipeline import failed: {e}")
        try:
            # Fallback to basic components
            from src.ocr_processor import OCRProcessor
            from src.technical_element_detector import TechnicalElementDetector
            print("⚠️ Fallback to basic components successful")
            return False
        except ImportError as e2:
            print(f"❌ All imports failed: {e2}")
            return False

def test_yolo_model():
    """Test que el model YOLOv8 està disponible"""
    try:
        from src.technical_element_detector import TechnicalElementDetector
        detector = TechnicalElementDetector()
        print("✅ YOLOv8 detector initialized successfully")
        
        # Check model file
        model_path = project_root / 'models' / 'best.pt'
        if model_path.exists():
            print(f"✅ YOLOv8 model found: {model_path}")
            return True
        else:
            print(f"⚠️ YOLOv8 model not found at: {model_path}")
            return False
    except Exception as e:
        print(f"❌ YOLOv8 detector test failed: {e}")
        return False

def test_sample_processing():
    """Test processament d'exemple"""
    try:
        sample_pdf = project_root / 'data' / 'exemples' / '6555945_003.pdf'
        if not sample_pdf.exists():
            print(f"⚠️ Sample PDF not found: {sample_pdf}")
            return False
        
        # Try enhanced pipeline first
        try:
            sys.path.append(str(project_root / 'production'))
            from enhanced_pipeline import EnhancedOCRPipeline
            
            pipeline = EnhancedOCRPipeline()
            result = pipeline.process_document(str(sample_pdf))
            
            # Check results
            technical_elements = len(result.get('yolo_detections', []))
            ocr_text_length = len(result.get('ocr_text', ''))
            
            print(f"✅ Enhanced processing successful:")
            print(f"   - Technical elements found: {technical_elements}")
            print(f"   - OCR text length: {ocr_text_length} characters")
            
            return True
            
        except Exception as e:
            print(f"❌ Enhanced processing failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Sample processing test failed: {e}")
        return False

def test_web_compatibility():
    """Test compatibilitat amb l'aplicació web"""
    try:
        # Test web app imports
        sys.path.append(str(project_root / 'src' / 'ui'))
        
        # Test paths that web app uses
        upload_folder = project_root / 'data' / 'uploads'
        output_folder = project_root / 'data' / 'output'
        
        print(f"✅ Upload folder exists: {upload_folder.exists()}")
        print(f"✅ Output folder exists: {output_folder.exists()}")
        
        # Test write permissions
        test_file = output_folder / 'test_write.txt'
        try:
            test_file.write_text('test')
            test_file.unlink()
            print("✅ Output folder is writable")
        except Exception as e:
            print(f"❌ Output folder not writable: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Web compatibility test failed: {e}")
        return False

def main():
    """Executar tots els tests"""
    print("=" * 60)
    print("🧪 TESTING WEB OCR SYSTEM COMPATIBILITY")
    print("=" * 60)
    
    tests = [
        ("Enhanced Pipeline Import", test_enhanced_pipeline_import),
        ("YOLOv8 Model Availability", test_yolo_model),
        ("Sample Processing", test_sample_processing),
        ("Web Compatibility", test_web_compatibility)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\nTests passed: {passed}/{len(tests)}")
    
    if passed == len(tests):
        print("\n🎉 ALL TESTS PASSED - Web system ready for YOLOv8 processing!")
    elif passed >= len(tests) - 1:
        print("\n⚠️ MOSTLY WORKING - Minor issues may exist")
    else:
        print("\n❌ MULTIPLE FAILURES - System needs attention")
    
    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
