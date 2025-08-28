"""
Script d'entrenament de model YOLOv8 personalitzat per OCR tècnic
"""

import os
from ultralytics import YOLO
from pathlib import Path
from loguru import logger

# Configuració
DATASET_PATH = Path("data/training/custom_dataset.yaml")  # YAML amb rutes d'imatges i anotacions
MODEL_OUTPUT = Path("src/ai_model/models/custom/technical.pt")
EPOCHS = 50
IMG_SIZE = 640

# Entrenament
if __name__ == "__main__":
    logger.info(f"🚀 Iniciant entrenament YOLOv8...")
    if not DATASET_PATH.exists():
        logger.error(f"❌ Dataset no trobat: {DATASET_PATH}")
        exit(1)
    
    # Inicialitzar model base
    model = YOLO('yolov8s.pt')  # Es pot canviar per yolov8n.pt si es vol més ràpid
    
    # Entrenar
    results = model.train(
        data=str(DATASET_PATH),
        epochs=EPOCHS,
        imgsz=IMG_SIZE,
        project=str(MODEL_OUTPUT.parent),
        name=MODEL_OUTPUT.stem,
        exist_ok=True
    )
    
    # Guardar model
    trained_model_path = MODEL_OUTPUT.parent / f"{MODEL_OUTPUT.stem}.pt"
    if trained_model_path.exists():
        logger.success(f"✅ Model entrenat guardat a: {trained_model_path}")
    else:
        logger.error("❌ Error guardant el model entrenat")
    
    # Registrar al sistema
    try:
        from model_manager import ModelManager
        manager = ModelManager(MODEL_OUTPUT.parent)
        manager.register_custom_model(
            name="technical_detector",
            path=str(trained_model_path),
            description="Detector de símbols tècnics personalitzat",
            model_type="detection"
        )
        logger.info("📋 Model personalitzat registrat al sistema")
    except Exception as e:
        logger.error(f"❌ Error registrant el model: {e}")
