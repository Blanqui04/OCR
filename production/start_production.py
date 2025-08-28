#!/usr/bin/env python3
"""
Script Principal de Producció - OCR Technical Analyzer
"""

import sys
import os
from pathlib import Path
import json
from loguru import logger

# Afegir directori actual al path
sys.path.append(str(Path(__file__).parent))

# Configurar logs
logger.add("logs/production.log", rotation="10 MB", retention="30 days")

try:
    from enhanced_pipeline import EnhancedOCRPipeline
    from technical_element_detector import TechnicalElementDetector
    
    def main():
        """Funció principal de producció"""
        logger.info("🚀 Iniciant OCR Technical Analyzer - Producció")
        
        # Carregar configuració
        with open("config/production_config.json") as f:
            config = json.load(f)
        
        logger.info(f"📋 Configuració carregada: {config['system']['name']} v{config['system']['version']}")
        
        # Inicialitzar pipeline
        pipeline = EnhancedOCRPipeline(enable_yolo=True)
        
        logger.info("✅ Sistema llest per processar documents")
        return pipeline
    
    if __name__ == "__main__":
        pipeline = main()
        print("Sistema OCR en funcionament. Consulta els logs per més detalls.")

except Exception as e:
    logger.error(f"❌ Error iniciant sistema: {e}")
    sys.exit(1)
