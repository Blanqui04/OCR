"""
Script per registrar el model YOLOv8 entrenat al ModelManager
"""

import sys
from pathlib import Path

# Afegir el directori src al path
sys.path.append(str(Path(__file__).parent))

from ai_model.model_manager import ModelManager

def register_trained_model():
    """Registra el model YOLOv8 entrenat"""
    
    model_manager = ModelManager()
    
    # Path al model entrenat (millor model)
    model_path = Path(__file__).parent / "ai_model" / "models" / "custom" / "technical" / "weights" / "best.pt"
    
    if not model_path.exists():
        print(f"❌ Model no trobat: {model_path}")
        return False
    
    # Registrar el model
    model_manager.register_custom_model(
        name="technical_detector",
        path=str(model_path),
        description="YOLOv8 personalitzat per detectar elements tècnics (cotes, toleràncies, símbols)",
        model_type="yolov8_detection"
    )
    
    print(f"✅ Model 'technical_detector' registrat correctament")
    print(f"📁 Path: {model_path}")
    
    # Llistar tots els models
    models = model_manager.list_models()
    print(f"\n📋 Models disponibles:")
    for name, info in models.items():
        print(f"  - {name}: {info.get('description', 'No description')}")
    
    return True

if __name__ == "__main__":
    register_trained_model()
