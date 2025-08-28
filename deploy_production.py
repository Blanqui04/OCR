"""
Sistema de Desplegament en Producció
Configura i llança el sistema OCR millorat per producció
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from loguru import logger
import subprocess

class ProductionDeployment:
    """Gestor de desplegament en producció"""
    
    def __init__(self, base_dir=None):
        if base_dir is None:
            self.base_dir = Path(__file__).parent
        else:
            self.base_dir = Path(base_dir)
        
        self.production_dir = self.base_dir / "production"
        self.logs_dir = self.production_dir / "logs"
        self.config_dir = self.production_dir / "config"
        self.data_dir = self.production_dir / "data"
        
        self.deployment_info = {
            "version": "1.0.0",
            "deployed_at": datetime.now().isoformat(),
            "components": [],
            "status": "initializing"
        }
    
    def create_production_structure(self):
        """Crea l'estructura de directoris de producció"""
        logger.info("🏗️ Creant estructura de producció...")
        
        directories = [
            self.production_dir,
            self.logs_dir,
            self.config_dir,
            self.data_dir,
            self.data_dir / "input",
            self.data_dir / "output",
            self.data_dir / "processed",
            self.data_dir / "backup",
            self.production_dir / "models",
            self.production_dir / "static",
            self.production_dir / "templates"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"  📁 {directory}")
        
        self.deployment_info["components"].append("directory_structure")
        return True
    
    def copy_production_files(self):
        """Copia els fitxers necessaris per producció"""
        logger.info("📋 Copiant fitxers de producció...")
        
        # Fitxers principals
        files_to_copy = [
            ("src/technical_element_detector.py", "technical_element_detector.py"),
            ("src/enhanced_pipeline.py", "enhanced_pipeline.py"),
            ("src/pipeline.py", "pipeline.py"),
            ("src/ocr_processor.py", "ocr_processor.py"),
            ("src/pdf_to_images.py", "pdf_to_images.py"),
            ("src/data_extractor.py", "data_extractor.py"),
            ("src/dimension_linker.py", "dimension_linker.py"),
            ("requirements.txt", "requirements.txt"),
            ("README.md", "README.md")
        ]
        
        for src, dst in files_to_copy:
            src_path = self.base_dir / src
            dst_path = self.production_dir / dst
            
            if src_path.exists():
                shutil.copy2(src_path, dst_path)
                logger.info(f"  ✅ {src} → {dst}")
            else:
                logger.warning(f"  ⚠️ No trobat: {src}")
        
        # Copiar models
        models_src = self.base_dir / "src" / "ai_model"
        models_dst = self.production_dir / "ai_model"
        
        if models_src.exists():
            shutil.copytree(models_src, models_dst, dirs_exist_ok=True)
            logger.info(f"  ✅ Models copiats a {models_dst}")
        
        # Copiar UI
        ui_src = self.base_dir / "src" / "ui"
        ui_dst = self.production_dir / "ui"
        
        if ui_src.exists():
            shutil.copytree(ui_src, ui_dst, dirs_exist_ok=True)
            logger.info(f"  ✅ UI copiada a {ui_dst}")
        
        self.deployment_info["components"].append("files_copied")
        return True
    
    def create_production_config(self):
        """Crea configuració de producció"""
        logger.info("⚙️ Creant configuració de producció...")
        
        config = {
            "system": {
                "name": "OCR Technical Analyzer - Production",
                "version": self.deployment_info["version"],
                "environment": "production",
                "debug": False,
                "log_level": "INFO"
            },
            "ocr": {
                "tesseract_config": "--psm 6 -l eng+spa",
                "technical_mode": True,
                "dpi": 300,
                "preprocessing": True
            },
            "yolo": {
                "model_name": "technical_detector",
                "confidence_threshold": 0.3,
                "iou_threshold": 0.45,
                "save_annotated": True
            },
            "processing": {
                "max_file_size_mb": 50,
                "supported_formats": [".pdf", ".png", ".jpg", ".jpeg"],
                "parallel_processing": True,
                "max_workers": 4
            },
            "storage": {
                "input_dir": "data/input",
                "output_dir": "data/output",
                "processed_dir": "data/processed",
                "backup_dir": "data/backup",
                "auto_cleanup_days": 30
            },
            "monitoring": {
                "enable_metrics": True,
                "log_requests": True,
                "performance_tracking": True,
                "error_reporting": True
            },
            "security": {
                "max_requests_per_minute": 60,
                "allowed_extensions": [".pdf", ".png", ".jpg", ".jpeg"],
                "scan_uploads": True
            }
        }
        
        config_file = self.config_dir / "production_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"  ✅ Configuració guardada: {config_file}")
        self.deployment_info["components"].append("configuration")
        return config
    
    def setup_logging(self):
        """Configura el sistema de logs de producció"""
        logger.info("📝 Configurant sistema de logs...")
        
        # Configuració de loguru per producció
        log_config = {
            "handlers": [
                {
                    "sink": str(self.logs_dir / "application.log"),
                    "rotation": "10 MB",
                    "retention": "30 days",
                    "level": "INFO",
                    "format": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} - {message}"
                },
                {
                    "sink": str(self.logs_dir / "errors.log"),
                    "rotation": "5 MB",
                    "retention": "60 days",
                    "level": "ERROR",
                    "format": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} - {message}"
                },
                {
                    "sink": str(self.logs_dir / "performance.log"),
                    "rotation": "20 MB",
                    "retention": "15 days",
                    "level": "DEBUG",
                    "filter": "lambda record: 'performance' in record.get('extra', {})",
                    "format": "{time:YYYY-MM-DD HH:mm:ss} | PERF | {extra[performance]} - {message}"
                }
            ]
        }
        
        log_config_file = self.config_dir / "logging_config.json"
        with open(log_config_file, 'w', encoding='utf-8') as f:
            json.dump(log_config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"  ✅ Logs configurats: {self.logs_dir}")
        self.deployment_info["components"].append("logging")
        return True
    
    def create_startup_scripts(self):
        """Crea scripts d'inici per producció"""
        logger.info("🚀 Creant scripts d'inici...")
        
        # Script principal de producció
        main_script = """#!/usr/bin/env python3
\"\"\"
Script Principal de Producció - OCR Technical Analyzer
\"\"\"

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
        \"\"\"Funció principal de producció\"\"\"
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
"""
        
        main_script_file = self.production_dir / "start_production.py"
        with open(main_script_file, 'w', encoding='utf-8') as f:
            f.write(main_script)
        
        # Script de test de producció
        test_script = """#!/usr/bin/env python3
\"\"\"
Test de Producció - Verifica que tot funcioni correctament
\"\"\"

import sys
import os
from pathlib import Path
import time
import json
from loguru import logger

sys.path.append(str(Path(__file__).parent))

def test_production_system():
    \"\"\"Test complet del sistema de producció\"\"\"
    
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
"""
        
        test_script_file = self.production_dir / "test_production.py"
        with open(test_script_file, 'w', encoding='utf-8') as f:
            f.write(test_script)
        
        logger.info(f"  ✅ Script principal: {main_script_file}")
        logger.info(f"  ✅ Script de test: {test_script_file}")
        
        self.deployment_info["components"].append("startup_scripts")
        return True
    
    def create_deployment_info(self):
        """Crea fitxer d'informació del desplegament"""
        self.deployment_info["status"] = "deployed"
        self.deployment_info["deployed_at"] = datetime.now().isoformat()
        
        deployment_file = self.production_dir / "deployment_info.json"
        with open(deployment_file, 'w', encoding='utf-8') as f:
            json.dump(self.deployment_info, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📋 Informació de desplegament: {deployment_file}")
        return True
    
    def deploy(self):
        """Executa el desplegament complet"""
        logger.info("🚀 Iniciant desplegament en producció...")
        
        try:
            # Pas 1: Crear estructura
            self.create_production_structure()
            
            # Pas 2: Copiar fitxers
            self.copy_production_files()
            
            # Pas 3: Configuració
            config = self.create_production_config()
            
            # Pas 4: Logging
            self.setup_logging()
            
            # Pas 5: Scripts
            self.create_startup_scripts()
            
            # Pas 6: Info desplegament
            self.create_deployment_info()
            
            logger.info("✅ Desplegament completat amb èxit!")
            logger.info(f"📁 Directori de producció: {self.production_dir}")
            logger.info("🚀 Per iniciar el sistema, executa: python production/start_production.py")
            logger.info("🧪 Per fer tests, executa: python production/test_production.py")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en desplegament: {e}")
            return False


def main():
    """Funció principal de desplegament"""
    deployer = ProductionDeployment()
    success = deployer.deploy()
    
    if success:
        print("🎉 Sistema desplegat correctament en producció!")
        print(f"📁 Ubicació: {deployer.production_dir}")
        print("\n📋 Següents passos:")
        print("1. cd production")
        print("2. python test_production.py  # Verificar funcionament")
        print("3. python start_production.py  # Iniciar sistema")
    else:
        print("❌ Error en el desplegament")
        sys.exit(1)


if __name__ == "__main__":
    main()
