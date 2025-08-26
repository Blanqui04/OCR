# src/integrator.py
import json
import re

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def integrate_all_data():
    # Carreguem totes les dades
    dimensions = load_json("C:\\Users\\eceballos\\OneDrive - SOME, S.A\\Desktop\\Projectes\\OCR\\data\\dimensions\\dimensions_linked.json")
    geo_tolerances = load_json("C:\\Users\\eceballos\\OneDrive - SOME, S.A\\Desktop\\Projectes\\OCR\\data\\geometric\\geometric_tolerances.json")
    tables = load_json("C:\\Users\\eceballos\\OneDrive - SOME, S.A\\Desktop\\Projectes\\OCR\\data\\tables\\extracted_tables.json")

    # Busquem info clau a les taules
    part_info = {}
    for table in tables:
        # Nova estructura de taules des de camelot
        table_data = table.get("data", [])
        if table_data and len(table_data) > 0:
            # Buscar informació de la peça a la primera fila/columna
            first_row = table_data[0] if table_data else []
            for row in table_data:
                for i, cell in enumerate(row):
                    if isinstance(cell, str):
                        if "part" in cell.lower() or "número" in cell.lower():
                            if i + 1 < len(row):
                                part_info["part_number"] = row[i + 1]
                        elif "material" in cell.lower():
                            if i + 1 < len(row):
                                part_info["material"] = row[i + 1]
                        elif "rev" in cell.lower():
                            if i + 1 < len(row):
                                part_info["revision"] = row[i + 1]
    
    # Si no trobem info específica, usar valors per defecte
    if not part_info:
        part_info = {
            "part_number": "N/A",
            "material": "N/A", 
            "revision": "N/A",
            "drawing_title": "Plànol Tècnic"
        }
    
    # Preparem dimensions
    parsed_dimensions = []
    for dim in dimensions:
        value = dim["text"]
        tolerance_match = re.search(r'([0-9.]+)\s*[±±]\s*([0-9.]+)', value)
        if tolerance_match:
            nominal, tol = tolerance_match.groups()
            parsed_dimensions.append({
                "type": "linear",
                "nominal": float(nominal),
                "tolerance": float(tol),
                "description": value,
                "orientation": dim["orientation"],
                "bbox": dim["bbox"]
            })
        else:
            parsed_dimensions.append({
                "type": "nominal",
                "value": value,
                "description": value,
                "orientation": dim["orientation"],
                "bbox": dim["bbox"]
            })

    # Resultat final
    final_data = {
        "part_info": part_info,
        "dimensions": parsed_dimensions,
        "geometric_tolerances": geo_tolerances,
        "raw_tables": tables
    }

    # Crear directori si no existeix
    import os
    output_dir = os.path.dirname("C:\\Users\\eceballos\\OneDrive - SOME, S.A\\Desktop\\Projectes\\OCR\\data\\final_output.json")
    os.makedirs(output_dir, exist_ok=True)

    with open("C:\\Users\\eceballos\\OneDrive - SOME, S.A\\Desktop\\Projectes\\OCR\\data\\final_output.json", "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
    
    return final_data

# Exemple
if __name__ == "__main__":
    data = integrate_all_data()
    print("✅ Integració completada. Mira C:\\Users\\eceballos\\OneDrive - SOME, S.A\\Desktop\\Projectes\\OCR\\data\\output\\final")