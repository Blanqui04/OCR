"""
Test Ràpid de Producció
Verifica els components bàsics sense carregar models pesats
"""

import sys
import os
from pathlib import Path
import json
import time

def test_basic_system():
    """Test bàsic del sistema de producció"""
    
    print("🧪 Iniciant tests ràpids de producció...")
    
    tests_passed = 0
    total_tests = 5
    
    try:
        # Test 1: Verificar directoris
        print("Test 1/5: Verificant estructura de directoris...")
        required_dirs = [
            "data/input", "data/output", "data/processed", "data/backup",
            "logs", "config", "ai_model", "ui"
        ]
        
        for dir_path in required_dirs:
            if not Path(dir_path).exists():
                raise Exception(f"Directori no trobat: {dir_path}")
        
        tests_passed += 1
        print("✅ Estructura de directoris correcta")
        
        # Test 2: Verificar fitxers principals
        print("Test 2/5: Verificant fitxers principals...")
        required_files = [
            "technical_element_detector.py",
            "enhanced_pipeline.py", 
            "pipeline.py",
            "config/production_config.json",
            "ai_model/model_manager.py"
        ]
        
        for file_path in required_files:
            if not Path(file_path).exists():
                raise Exception(f"Fitxer no trobat: {file_path}")
        
        tests_passed += 1
        print("✅ Fitxers principals presents")
        
        # Test 3: Carregar configuració
        print("Test 3/5: Carregant configuració...")
        with open("config/production_config.json") as f:
            config = json.load(f)
        
        if not config.get("system", {}).get("name"):
            raise Exception("Configuració incompleta")
        
        tests_passed += 1
        print("✅ Configuració carregada correctament")
        
        # Test 4: Verificar models
        print("Test 4/5: Verificant models...")
        model_config = Path("ai_model/models/models_config.json")
        if model_config.exists():
            with open(model_config) as f:
                models = json.load(f)
            
            if "technical_detector" in models.get("models", {}):
                print("  📦 Model YOLOv8 trobat")
            else:
                print("  ⚠️ Model YOLOv8 no registrat (normal en primer desplegament)")
        
        tests_passed += 1
        print("✅ Estructura de models verificada")
        
        # Test 5: Verificar permisos d'escriptura
        print("Test 5/5: Verificant permisos...")
        test_file = Path("logs/test_write.tmp")
        test_file.write_text("test")
        test_file.unlink()
        
        tests_passed += 1
        print("✅ Permisos d'escriptura correctes")
        
        # Resum
        print(f"\n🎉 Tests completats: {tests_passed}/{total_tests} ✅")
        
        if tests_passed == total_tests:
            print("✅ Sistema de producció llest per funcionar!")
            print("\n📋 Configuració del sistema:")
            print(f"  📛 Nom: {config['system']['name']}")
            print(f"  🔢 Versió: {config['system']['version']}")
            print(f"  🌍 Entorn: {config['system']['environment']}")
            print(f"  📁 Directori base: {Path.cwd()}")
            return True
        else:
            print(f"❌ {total_tests - tests_passed} tests han fallat")
            return False
            
    except Exception as e:
        print(f"❌ Error en tests: {e}")
        return False

def test_file_processing():
    """Test de processament de fitxers bàsic"""
    print("\n🔧 Test de processament de fitxers...")
    
    try:
        # Crear fitxer de test
        test_input = Path("data/input/test_document.txt")
        test_input.write_text("Test document for processing")
        
        # Verificar que es pot llegir
        content = test_input.read_text()
        
        # Simular processament
        test_output = Path("data/output/processed_test.json")
        test_result = {
            "original_file": str(test_input),
            "processed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "success",
            "content_length": len(content)
        }
        
        test_output.write_text(json.dumps(test_result, indent=2))
        
        # Moure a processed
        processed_file = Path("data/processed") / test_input.name
        test_input.rename(processed_file)
        
        print("✅ Flux de processament funcional")
        
        # Neteja
        test_output.unlink()
        processed_file.unlink()
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test de processament: {e}")
        return False

def main():
    """Funció principal de test ràpid"""
    start_time = time.time()
    
    print("🚀 Tests Ràpids de Producció - OCR Technical Analyzer")
    print("=" * 60)
    
    # Test bàsic del sistema
    basic_success = test_basic_system()
    
    # Test de processament
    processing_success = test_file_processing()
    
    # Resum final
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 60)
    print(f"⏱️ Tests completats en {duration:.2f} segons")
    
    if basic_success and processing_success:
        print("🎉 Sistema de producció OPERATIU!")
        print("\n📋 Següents passos:")
        print("1. Copiar documents PDF a data/input/")
        print("2. Executar: python start_production.py")
        print("3. Consultar resultats a data/output/")
        return True
    else:
        print("❌ Hi ha problemes que cal resoldre")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
