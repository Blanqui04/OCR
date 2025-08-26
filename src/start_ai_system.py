#!/usr/bin/env python3
"""
Script d'inici del sistema OCR amb IA
Facilita l'inici de l'aplicació Streamlit amb totes les funcionalitats d'IA
"""

import os
import sys
import json
import subprocess
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Comprova si totes les dependències estan instal·lades"""
    logger.info("Comprovant dependències...")
    
    required_packages = [
        'streamlit', 'pandas', 'pillow', 'opencv-python',
        'pytesseract', 'camelot-py[cv]', 'ultralytics', 
        'torch', 'torchvision', 'openpyxl', 'jsonschema'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'camelot-py[cv]':
                import camelot
            elif package == 'opencv-python':
                import cv2
            elif package == 'pillow':
                import PIL
            elif package == 'pytesseract':
                import pytesseract
            elif package == 'ultralytics':
                import ultralytics
            elif package == 'torch':
                import torch
            elif package == 'torchvision':
                import torchvision
            elif package == 'openpyxl':
                import openpyxl
            elif package == 'jsonschema':
                import jsonschema
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Dependències no trobades: {missing_packages}")
        return False
    
    logger.info("✅ Totes les dependències estan instal·lades")
    return True

def create_config_files():
    """Crea fitxers de configuració si no existeixen"""
    logger.info("Creant fitxers de configuració...")
    
    project_root = Path(__file__).parent
    
    # Configuració d'IA
    ai_config_path = project_root / "config_ai.json"
    if not ai_config_path.exists():
        ai_config = {
            "ai_model_path": "src/ai_model/models/best.pt",
            "confidence_threshold": 0.7,
            "human_review_threshold": 0.5,
            "enable_continuous_learning": True,
            "auto_retrain_after_corrections": 50,
            "model_classes": [
                "dimension_text", "arrow", "tolerance", "symbol", 
                "info_text", "title", "line", "table", "scale", 
                "north_arrow", "border", "legend", "other"
            ]
        }
        
        with open(ai_config_path, 'w') as f:
            json.dump(ai_config, f, indent=2)
        logger.info(f"✅ Configuració d'IA creada: {ai_config_path}")
    
    # Crear directoris necessaris
    dirs_to_create = [
        "data/images",
        "data/output/raw", 
        "data/output/structured",
        "data/output/ai_enhanced",
        "data/user_feedback",
        "src/ai_model/models",
        "src/ai_model/datasets"
    ]
    
    for dir_path in dirs_to_create:
        full_path = project_root / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Directori creat: {dir_path}")

def check_ai_model():
    """Comprova si hi ha un model d'IA entrenat disponible"""
    project_root = Path(__file__).parent
    model_path = project_root / "src/ai_model/models/best.pt"
    
    if model_path.exists():
        logger.info(f"✅ Model d'IA trobat: {model_path}")
        return True
    else:
        logger.warning("⚠️ Model d'IA no trobat - el sistema funcionarà amb detecció basada en regles")
        logger.info("💡 Per entrenar un model personalitzat, utilitza model_trainer.py")
        return False

def start_streamlit_app():
    """Inicia l'aplicació Streamlit"""
    logger.info("Iniciant aplicació Streamlit...")
    
    project_root = Path(__file__).parent
    app_path = project_root / "src/ui/app.py"
    
    if not app_path.exists():
        logger.error(f"❌ Aplicació no trobada: {app_path}")
        return False
    
    try:
        # Canviar al directori del projecte
        os.chdir(project_root)
        
        # Executar Streamlit
        cmd = [sys.executable, "-m", "streamlit", "run", str(app_path), "--server.port=8501"]
        
        logger.info("🚀 Iniciant Streamlit a http://localhost:8501")
        logger.info("💡 Prem Ctrl+C per aturar l'aplicació")
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        logger.info("👋 Aplicació aturada per l'usuari")
    except Exception as e:
        logger.error(f"❌ Error iniciant Streamlit: {e}")
        return False
    
    return True

def main():
    """Funció principal"""
    print("🤖📐 Sistema OCR amb Intel·ligència Artificial")
    print("=" * 50)
    
    # 1. Comprovar dependències
    if not check_dependencies():
        print("\n❌ Dependències no trobades. Executa:")
        print("pip install -r requirements.txt")
        return 1
    
    # 2. Crear fitxers de configuració
    create_config_files()
    
    # 3. Comprovar model d'IA
    has_ai_model = check_ai_model()
    
    # 4. Mostrar estat del sistema
    print(f"\n📊 Estat del sistema:")
    print(f"  ✅ Dependències: Instal·lades")
    print(f"  ✅ Configuració: Creada")
    print(f"  {'✅' if has_ai_model else '⚠️'} Model d'IA: {'Disponible' if has_ai_model else 'No disponible'}")
    
    # 5. Iniciar aplicació
    print(f"\n🚀 Iniciant aplicació web...")
    if not start_streamlit_app():
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
