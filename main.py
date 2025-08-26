# main.py (actualitzat)
import os
import json
from camelot_example import extract_tables_from_pdf
from integrator import integrate_all_data
from src.pdf_to_images import pdf_to_images
from src.ocr_processor import ocr_with_boxes
from src.data_extractor import extract_technical_data
from src.dimension_linker import detect_lines, link_text_to_lines, distance_box_to_box

def process_pla(pdf_path):
    # 1. PDF → Imatges
    image_paths = pdf_to_images(pdf_path, "C:\\Users\\eceballos\\OneDrive - SOME, S.A\\Desktop\\Projectes\\OCR\\data\\images")
    image_path = image_paths[0]  # Traballem amb la primera pàgina

    # 2. OCR amb mode tècnic millorat
    ocr_data, img_shape = ocr_with_boxes(image_path, use_technical_mode=True)
    with open("C:\\Users\\eceballos\\OneDrive - SOME, S.A\\Desktop\\Projectes\\OCR\\data\\output\\raw\\ocr_output.json", "w", encoding="utf-8") as f:
        json.dump(ocr_data, f, ensure_ascii=False, indent=2)

    # 3. Detectar línies
    line_boxes, _ = detect_lines(image_path, threshold=100)
    with open("C:\\Users\\eceballos\\OneDrive - SOME, S.A\\Desktop\\Projectes\\OCR\\data\\lines\\lines.json", "w", encoding="utf-8") as f:
        json.dump(line_boxes, f, ensure_ascii=False, indent=2)

    # 4. Vincular textos amb línies
    linked_data = link_text_to_lines(ocr_data, line_boxes, max_distance=150)
    with open("C:\\Users\\eceballos\\OneDrive - SOME, S.A\\Desktop\\Projectes\\OCR\\data\\dimensions\\dimensions_linked.json", "w", encoding="utf-8") as f:
        json.dump(linked_data, f, indent=2, ensure_ascii=False)

    # 5. Extracció bàsica (ja no és necessària si fem linking, però la deixem)
    tech_data = extract_technical_data(ocr_data)
    with open("C:\\Users\\eceballos\\OneDrive - SOME, S.A\\Desktop\\Projectes\\OCR\\data\\output\\structured\\structured_output.json", "w", encoding="utf-8") as f:
        json.dump(tech_data, f, indent=2, ensure_ascii=False)

    print("📊 Extraient taules...")
    tables = extract_tables_from_pdf(pdf_path)
    
    # Convertir DataFrames a format serializable
    tables_data = []
    for i, table_df in enumerate(tables):
        table_info = {
            "table_id": i + 1,
            "name": getattr(table_df, 'name', f'table_{i+1}'),
            "shape": table_df.shape,
            "data": table_df.values.tolist(),
            "columns": table_df.columns.tolist()
        }
        tables_data.append(table_info)
    
    os.makedirs("C:\\Users\\eceballos\\OneDrive - SOME, S.A\\Desktop\\Projectes\\OCR\\data\\tables", exist_ok=True)
    with open("C:\\Users\\eceballos\\OneDrive - SOME, S.A\\Desktop\\Projectes\\OCR\\data\\tables\\extracted_tables.json", "w") as f:
        json.dump(tables_data, f, indent=2)

    print("✅ Integrant totes les dades...")
    integrate_all_data()

    print("🎉 Procés complet! Obre la UI amb: streamlit run C:\\Users\\eceballos\\OneDrive - SOME, S.A\\Desktop\\Projectes\\OCR\\src\\ui\\app.py")

if __name__ == "__main__":
    process_pla("C:\\Users\\eceballos\\OneDrive - SOME, S.A\\Desktop\\Projectes\\OCR\\data\\exemples\\6555945_003.pdf")