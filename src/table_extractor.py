# src/table_extractor.py
import camelot
import json
import pandas as pd

def extract_tables_from_pdf(pdf_path, page=1):
    # Utilitzem el mètode 'lattice' per a taules amb línies
    tables = camelot.read_pdf(pdf_path, pages=str(page), flavor='lattice')
    
    table_data = []
    
    for i, table in enumerate(tables):
        df: pd.DataFrame = table.df
        # Netegem espais dobles i cel·les buides
        df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
        df = df.replace('', None).dropna(how='all').dropna(axis=1, how='all')
        
        # Convertim a llista de diccionaris (clau: valor)
        # Sovint les taules són 2-columnes: Propietat | Valor
        if df.shape[1] == 2:
            table_dict = {}
            for _, row in df.iterrows():
                key = row[0] if pd.notna(row[0]) else "Desconegut"
                value = row[1] if pd.notna(row[1]) else ""
                table_dict[key.strip()] = value.strip()
            table_data.append({
                "type": "info_table",
                "data": table_dict
            })
        else:
            # Si no és 2-columnes, guardem com a matriu
            table_data.append({
                "type": "generic_table",
                "data": df.values.tolist()
            })
    
    return table_data

# Exemple d'ús
if __name__ == "__main__":
    tables = extract_tables_from_pdf("C:\\Users\\eceballos\\OneDrive - SOME, S.A\\Desktop\\Projectes\\OCR\\data\\exemples\\6555945_003.pdf", page=1)
    with open("C:\\Users\\eceballos\\OneDrive - SOME, S.A\\Desktop\\Projectes\\OCR\\data\\tables.json", "w", encoding="utf-8") as f:
        json.dump(tables, f, indent=2, ensure_ascii=False)
    print(f"✅ S'han extret {len(tables)} taules.")
    for t in tables:
        if t["type"] == "info_table":
            print("Taula d'informació:", t["data"])