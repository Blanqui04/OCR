#!/usr/bin/env python3
"""
Test de Producció - Verifica que tot funcioni correctament
"""

import sys
import os
from pathlib import Path
import time
import json
from loguru import logger

sys.path.append(str(Path(__file__).parent))

def test_production_system():
    """Test complet del sistema de producció"""
    
    logger.info("🧪 Iniciant tests de producció...")
    
    tests_passed = 0
    total_tests = 5
    
    try:
        # Test 1: Importar mòduls
        logger.info("Test 1/5: Important mòduls...")
        from technical_element_detector import TechnicalElementDetector
        from enhanced_pipeline import EnhancedOCRPipeline
        tests_passed += 1
        logger.info("✅ Mòduls importats correctament")
        
        # Test 2: Carregar configuració
        logger.info("Test 2/5: Carregant configuració...")
        with open("config/production_config.json") as f:
            config = json.load(f)
        tests_passed += 1
        logger.info("✅ Configuració carregada")
        
        # Test 3: Inicialitzar detector
        logger.info("Test 3/5: Inicialitzant detector YOLOv8...")
        detector = TechnicalElementDetector()
        tests_passed += 1
        logger.info("✅ Detector inicialitzat")
        
        # Test 4: Inicialitzar pipeline
        logger.info("Test 4/5: Inicialitzant pipeline...")
        pipeline = EnhancedOCRPipeline(enable_yolo=True)
        tests_passed += 1
        logger.info("✅ Pipeline inicialitzat")
        
        # Test 5: Verificar directoris
        logger.info("Test 5/5: Verificant directoris...")
        required_dirs = ["data/input", "data/output", "logs", "config"]
        for dir_path in required_dirs:
            if not Path(dir_path).exists():
                raise Exception(f"Directori no trobat: {dir_path}")
        tests_passed += 1
        logger.info("✅ Directoris verificats")
        
        # Resum
        logger.info(f"🎉 Tests completats: {tests_passed}/{total_tests} ✅")
        
        if tests_passed == total_tests:
            logger.info("✅ Sistema de producció llest!")
            return True
        else:
            logger.error(f"❌ {total_tests - tests_passed} tests han fallat")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error en tests: {e}")
        return False

if __name__ == "__main__":
    success = test_production_system()
    sys.exit(0 if success else 1)
