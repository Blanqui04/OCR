"""
Sistema de gestió de models d'IA per OCR tècnic
Inclou descàrrega, entrenament i gestió de models
"""

import os
import json
import urllib.request
from pathlib import Path
from loguru import logger
import torch
import torchvision
from typing import Dict, List, Optional

class ModelManager:
    """Gestor de models d'IA"""
    
    def __init__(self, models_dir: str = None):
        if models_dir is None:
            self.models_dir = Path(__file__).parent / "models"
        else:
            self.models_dir = Path(models_dir)
        
        self.models_dir.mkdir(exist_ok=True, parents=True)
        self.config_file = self.models_dir / "models_config.json"
        self.config = self.load_config()
    
    def load_config(self) -> Dict:
        """Carrega la configuració de models"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            default_config = {
                "models": {},
                "default_model": None,
                "last_updated": None
            }
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config: Dict):
        """Guarda la configuració de models"""
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        self.config = config
    
    def download_pretrained_models(self):
        """Descarrega models pre-entrenats per OCR tècnic"""
        logger.info("📥 Descarregant models pre-entrenats...")
        
        models_to_download = {
            "yolov8n": {
                "url": "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt",
                "description": "YOLO v8 Nano - Detecció d'objectes ràpida",
                "size": "~6MB",
                "use_case": "Detecció general d'elements"
            },
            "yolov8s": {
                "url": "https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8s.pt", 
                "description": "YOLO v8 Small - Equilibri velocitat/precisió",
                "size": "~21MB",
                "use_case": "Detecció precisa d'elements tècnics"
            }
        }
        
        for model_name, model_info in models_to_download.items():
            self.download_model(model_name, model_info)
    
    def download_model(self, model_name: str, model_info: Dict):
        """Descarrega un model específic"""
        model_path = self.models_dir / f"{model_name}.pt"
        
        if model_path.exists():
            logger.info(f"✅ {model_name} ja existeix")
            return
        
        try:
            logger.info(f"⬇️ Descarregant {model_name} ({model_info['size']})...")
            urllib.request.urlretrieve(model_info["url"], model_path)
            
            # Actualitzar configuració
            self.config["models"][model_name] = {
                "path": str(model_path),
                "description": model_info["description"],
                "use_case": model_info["use_case"],
                "downloaded": True
            }
            self.save_config(self.config)
            
            logger.success(f"✅ {model_name} descarregat correctament")
            
        except Exception as e:
            logger.error(f"❌ Error descarregant {model_name}: {e}")
    
    def create_custom_model_structure(self):
        """Crea l'estructura per models personalitzats"""
        custom_dir = self.models_dir / "custom"
        custom_dir.mkdir(exist_ok=True)
        
        # Crear directoris per tipus de model
        (custom_dir / "detection").mkdir(exist_ok=True)
        (custom_dir / "classification").mkdir(exist_ok=True)
        (custom_dir / "segmentation").mkdir(exist_ok=True)
        
        # Crear fitxer README
        readme_content = """# Models Personalitzats

## Estructura:
- `detection/`: Models de detecció d'objectes (YOLO, etc.)
- `classification/`: Models de classificació de text/imatges
- `segmentation/`: Models de segmentació d'imatges

## Com afegir un model personalitzat:
1. Entrenar el model amb les teves dades
2. Guardar el model en el directori apropiat
3. Actualitzar la configuració amb `ModelManager.register_custom_model()`

## Exemples d'ús:
- Detecció de símbols tècnics específics
- Classificació de tipus de plànol
- Segmentació de zones de text vs dibuix
"""
        
        with open(custom_dir / "README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)
        
        logger.info(f"📁 Estructura de models personalitzats creada: {custom_dir}")
    
    def register_custom_model(self, name: str, path: str, description: str, model_type: str):
        """Registra un model personalitzat"""
        self.config["models"][name] = {
            "path": path,
            "description": description,
            "type": model_type,
            "custom": True
        }
        self.save_config(self.config)
        logger.info(f"✅ Model personalitzat '{name}' registrat")
    
    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Obté informació d'un model registrat"""
        return self.config["models"].get(model_name, None)
    
    def list_models(self) -> Dict:
        """Llista tots els models disponibles"""
        return self.config["models"]
    
    def model_exists(self, model_name: str) -> bool:
        """Verifica si un model existeix"""
        return model_name in self.config["models"]
    
    def list_models(self):
        """Llista tots els models disponibles"""
        logger.info("📋 Models disponibles:")
        
        if not self.config["models"]:
            logger.warning("No hi ha models configurats")
            return {}
        
        for name, info in self.config["models"].items():
            status = "✅" if Path(info["path"]).exists() else "❌"
            model_type = info.get("type", "detection")
            custom = "🔧" if info.get("custom", False) else "📦"
            
            logger.info(f"  {status} {custom} {name} ({model_type})")
            logger.info(f"    📝 {info['description']}")
            logger.info(f"    📁 {info['path']}")
        
        return self.config["models"]
    
    def get_model_path(self, model_name: str) -> Optional[str]:
        """Obté el path d'un model"""
        if model_name in self.config["models"]:
            path = self.config["models"][model_name]["path"]
            if Path(path).exists():
                return path
            else:
                logger.warning(f"Model {model_name} no trobat a {path}")
                return None
        else:
            logger.warning(f"Model {model_name} no està registrat")
            return None
    
    def setup_all(self):
        """Configuració completa del sistema de models"""
        logger.info("🏗️ Configurant sistema de models d'IA...")
        
        # Crear estructura
        self.create_custom_model_structure()
        
        # Descarregar models base
        self.download_pretrained_models()
        
        # Configurar model per defecte
        if "yolov8n" in self.config["models"]:
            self.config["default_model"] = "yolov8n"
            self.save_config(self.config)
        
        logger.success("✅ Sistema de models configurat!")
        self.list_models()

# Instància global
model_manager = ModelManager()

def setup_models():
    """Funció d'entrada per configurar models"""
    return model_manager.setup_all()

def get_model(name: str = None):
    """Obté un model (per defecte si no s'especifica)"""
    if name is None:
        name = model_manager.config.get("default_model", "yolov8n")
    
    return model_manager.get_model_path(name)

if __name__ == "__main__":
    setup_models()
