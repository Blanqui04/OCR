# src/dimension_linker.py
import json
import cv2
import numpy as np

def detect_lines(image_path, threshold=100):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    
    # Detectar línies amb Hough
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=threshold,
                            minLineLength=50, maxLineGap=10)
    
    line_boxes = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            # Calcular bounding box de la línia (amb marge)
            margin = 10
            lx = int(min(x1, x2) - margin)  # Convert to Python int
            ly = int(min(y1, y2) - margin)  # Convert to Python int
            lw = int(abs(x2 - x1) + 2 * margin)  # Convert to Python int
            lh = int(abs(y2 - y1) + 2 * margin)  # Convert to Python int
            line_boxes.append([lx, ly, lw, lh])
            # (Opcional) dibuixar per debug
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
    return line_boxes, img.shape

def distance_box_to_box(box1, box2):
    # box = [x, y, w, h]
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    # Centre
    cx1, cy1 = x1 + w1/2, y1 + h1/2
    cx2, cy2 = x2 + w2/2, y2 + h2/2
    return np.sqrt((cx1 - cx2)**2 + (cy1 - cy2)**2)

def link_text_to_lines(ocr_data, line_boxes, max_distance=100):
    linked = []
    for text_item in ocr_data:
        text_box = text_item['bbox']  # [x, y, w, h]
        distances = [distance_box_to_box(text_box, line_box) for line_box in line_boxes]
        if distances and min(distances) < max_distance:
            nearest_line_idx = int(np.argmin(distances))  # Convert to Python int
            min_distance = float(min(distances))  # Convert to Python float
            linked.append({
                "text": text_item['text'],
                "bbox": text_item['bbox'],
                "line_index": nearest_line_idx,
                "distance": min_distance,
                "orientation": "horizontal" if abs(line_boxes[nearest_line_idx][3]) < 20 else "vertical"
            })
    return linked

# Exemple d'ús
if __name__ == "__main__":
    image_path = "C:\\Users\\eceballos\\OneDrive - SOME, S.A\\Desktop\\Projectes\\OCR\\data\\images\\page_1.png"
    line_boxes, img_shape = detect_lines(image_path, threshold=100)
    print(f"S'han detectat {len(line_boxes)} línies.")

    with open("C:\\Users\\eceballos\\OneDrive - SOME, S.A\\Desktop\\Projectes\\OCR\\data\\output\\raw\\ocr_output.json", "r", encoding="utf-8") as f:
        ocr_data = json.load(f)

    linked_data = link_text_to_lines(ocr_data, line_boxes, max_distance=150)

    # Filtrar només els textos que són possibles cotes
    dimensions_linked = [item for item in linked_data if any(p in item["text"] for p in ["±", "Ø", "R", "±"])]

    with open("C:\\Users\\eceballos\\OneDrive - SOME, S.A\\Desktop\\Projectes\\OCR\\data\\dimensions\\dimensions_linked.json", "w", encoding="utf-8") as f:
        json.dump(dimensions_linked, f, indent=2, ensure_ascii=False)

    print(f"Cotes vinculades a línies: {len(dimensions_linked)}")