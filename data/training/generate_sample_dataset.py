# Script per crear imatges d'exemple per entrenar YOLOv8

import cv2
import numpy as np
from pathlib import Path
import random

def create_sample_image_with_annotations():
    """Crea una imatge d'exemple amb elements tècnics simulats"""
    
    # Crear imatge en blanc
    img = np.ones((640, 640, 3), dtype=np.uint8) * 255
    
    # Afegir línies de plànol
    cv2.line(img, (50, 100), (590, 100), (0, 0, 0), 2)
    cv2.line(img, (50, 500), (590, 500), (0, 0, 0), 2)
    cv2.line(img, (100, 50), (100, 550), (0, 0, 0), 2)
    cv2.line(img, (540, 50), (540, 550), (0, 0, 0), 2)
    
    # Afegir cota (dimensions)
    cv2.putText(img, "125.5±0.1", (200, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    cv2.arrowedLine(img, (180, 140), (180, 160), (0, 0, 0), 2)
    cv2.arrowedLine(img, (320, 140), (320, 160), (0, 0, 0), 2)
    
    # Afegir tolerància geomètrica
    cv2.rectangle(img, (400, 200), (500, 240), (0, 0, 0), 2)
    cv2.putText(img, "⌖ 0.05", (410, 225), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    
    # Afegir símbol tècnic
    cv2.circle(img, (150, 350), 30, (0, 0, 0), 2)
    cv2.putText(img, "M8", (135, 360), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    
    return img

def create_sample_annotations():
    """Crea anotacions YOLO per la imatge d'exemple"""
    annotations = []
    
    # Cota: center_x=0.39, center_y=0.20, width=0.22, height=0.08
    annotations.append("0 0.39 0.20 0.22 0.08")
    
    # Tolerància: center_x=0.70, center_y=0.34, width=0.16, height=0.06
    annotations.append("1 0.70 0.34 0.16 0.06")
    
    # Símbol: center_x=0.23, center_y=0.55, width=0.12, height=0.12
    annotations.append("2 0.23 0.55 0.12 0.12")
    
    return annotations

def generate_sample_dataset():
    """Genera un dataset d'exemple per entrenar"""
    
    base_path = Path("data/training")
    
    # Crear diverses variacions de la imatge
    for i in range(20):
        # Crear imatge
        img = create_sample_image_with_annotations()
        
        # Afegir soroll aleatori
        noise = np.random.normal(0, 10, img.shape).astype(np.uint8)
        img = cv2.add(img, noise)
        
        # Determinar split (train/val/test)
        if i < 14:  # 70% train
            split = "train"
        elif i < 18:  # 20% val
            split = "val"
        else:  # 10% test
            split = "test"
        
        # Guardar imatge
        img_path = base_path / "images" / split / f"sample_{i:03d}.jpg"
        cv2.imwrite(str(img_path), img)
        
        # Guardar anotacions
        annotations = create_sample_annotations()
        label_path = base_path / "labels" / split / f"sample_{i:03d}.txt"
        with open(label_path, 'w') as f:
            f.write('\n'.join(annotations))
        
        print(f"Creat: {img_path.name} -> {split}")

if __name__ == "__main__":
    print("🎨 Generant dataset d'exemple...")
    generate_sample_dataset()
    print("✅ Dataset d'exemple generat!")
    print("📁 Fitxers creats a data/training/images/ i data/training/labels/")
    print("🚀 Ja pots entrenar el model amb: python src/ai_model/train_custom_yolo.py")
