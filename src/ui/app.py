# src/ui/app.py (actualitzat)
import streamlit as st
import json
import pandas as pd
import os
import tempfile
import sys
from pathlib import Path
from io import BytesIO

# Afegir el directori src al path per importar els mòduls
sys.path.append(str(Path(__file__).parent.parent))

try:
    from pipeline import OCRPipeline
except ImportError as e:
    st.error(f"Error important OCRPipeline: {e}")
    # Fallback a importacions individuals
    try:
        from pdf_to_images import pdf_to_images
        from ocr_processor import ocr_with_boxes
        from data_extractor import extract_technical_data
        from dimension_linker import detect_lines, link_text_to_lines
        OCRPipeline = None
    except ImportError as e2:
        st.error(f"Error important mòduls individuals: {e2}")
        OCRPipeline = None

st.set_page_config(page_title="Validador de Plànols Tècnics", layout="wide")
st.title("📐 Validador de Plànols Tècnics")

# Funcions d'exportació
def create_excel_export(data):
    """Crea un fitxer Excel amb les dades processades"""
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Full 1: Informació de la peça
        part_info_df = pd.DataFrame([data.get("part_info", {})])
        part_info_df.to_excel(writer, sheet_name='Informació_Peça', index=False)
        
        # Full 2: Cotes
        if data.get("dimensions"):
            dimensions_df = pd.DataFrame(data["dimensions"])
            dimensions_df.to_excel(writer, sheet_name='Cotes', index=False)
        
        # Full 3: Toleràncies Geomètriques
        if data.get("geometric_tolerances"):
            tolerances_df = pd.DataFrame(data["geometric_tolerances"])
            tolerances_df.to_excel(writer, sheet_name='Toleràncies', index=False)
        
        # Full 4: Taules Extretes
        if data.get("raw_tables"):
            for i, table in enumerate(data["raw_tables"]):
                table_data = table.get("data", [])
                if table_data:
                    try:
                        table_df = pd.DataFrame(table_data)
                        sheet_name = f'Taula_{i+1}'
                        table_df.to_excel(writer, sheet_name=sheet_name, index=False)
                    except:
                        # Si no es pot convertir a DataFrame, crear un full amb info
                        info_df = pd.DataFrame([{
                            'Taula': i+1,
                            'Tipus': table.get('name', 'Desconeguda'),
                            'Dades': str(table_data)[:1000]  # Limitar text
                        }])
                        info_df.to_excel(writer, sheet_name=f'Taula_{i+1}_Info', index=False)
    
    output.seek(0)
    return output.getvalue()

def create_json_schema_export(data):
    """Crea un JSON amb esquema validat"""
    export_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "Validació de Plànols Tècnics",
        "type": "object",
        "properties": {
            "metadata": {
                "type": "object",
                "properties": {
                    "export_timestamp": {"type": "string"},
                    "validation_completed": {"type": "boolean"},
                    "total_elements": {"type": "integer"}
                }
            },
            "part_info": {"type": "object"},
            "dimensions": {"type": "array"},
            "geometric_tolerances": {"type": "array"},
            "raw_tables": {"type": "array"}
        },
        "required": ["metadata", "part_info"]
    }
    
    # Crear dades amb esquema
    schema_data = {
        "schema": export_schema,
        "data": {
            "metadata": {
                "export_timestamp": str(pd.Timestamp.now().isoformat()),
                "validation_completed": True,
                "total_elements": (len(data.get("dimensions", [])) + 
                                 len(data.get("geometric_tolerances", [])) + 
                                 len(data.get("raw_tables", [])))
            },
            "part_info": data.get("part_info", {}),
            "dimensions": data.get("dimensions", []),
            "geometric_tolerances": data.get("geometric_tolerances", []),
            "raw_tables": data.get("raw_tables", [])
        }
    }
    
    return json.dumps(schema_data, indent=2, ensure_ascii=False)

# Carregar dades integrades
@st.cache_data
def load_integrated_data():
    """Carrega les dades del fitxer final_output.json"""
    try:
        base_dir = str(Path(__file__).parent.parent.parent)
        data_path = os.path.join(base_dir, "data", "final_output.json")
        
        if os.path.exists(data_path):
            with open(data_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return None
    except Exception as e:
        st.error(f"Error carregant les dades: {e}")
        return None

# Intentar carregar dades existents
data = load_integrated_data()

if data is None:
    st.warning("⚠️ No s'han trobat dades processades.")
    st.info("💡 Pots:")
    st.write("1. Executar `main.py` primer per processar un PDF")
    st.write("2. O carregar un nou PDF aquí:")
    
    # Opció per carregar i processar un nou PDF
    uploaded_file = st.file_uploader("Selecciona un PDF", type=['pdf'])
    
    if uploaded_file is not None:
        if st.button("🚀 Processar PDF", type="primary"):
            if OCRPipeline is None:
                st.error("❌ OCRPipeline no està disponible. Revisa les importacions.")
                st.stop()
                
            with st.spinner("Processant el PDF..."):
                # Guardar el fitxer carregat temporalment
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                try:
                    # Utilitzar el pipeline integrat
                    base_dir = str(Path(__file__).parent.parent.parent)
                    
                    # Crear pipeline
                    pipeline = OCRPipeline(base_dir)
                    
                    # Processar PDF
                    st.info("⚙️ Executant pipeline complet...")
                    results = pipeline.process_pdf(tmp_path, save_files=True)
                    
                    st.success("✅ Processament completat!")
                    st.info("🔄 Recarrega la pàgina per veure els resultats.")
                    
                except Exception as e:
                    st.error(f"❌ Error durant el processament: {str(e)}")
                    st.exception(e)
                finally:
                    # Netejar fitxer temporal
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
    
    st.stop()

# Informació general
st.sidebar.header("📄 Informació de la Peça")
part = data.get("part_info", {})
st.sidebar.write(f"**Número:** {part.get('part_number', 'N/A')}")
st.sidebar.write(f"**Material:** {part.get('material', 'N/A')}")
st.sidebar.write(f"**Revisió:** {part.get('revision', 'N/A')}")

# Estadístiques ràpides
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📏 Cotes", len(data.get("dimensions", [])))
with col2:
    st.metric("⚙️ Toleràncies", len(data.get("geometric_tolerances", [])))
with col3:
    st.metric("📊 Taules", len(data.get("raw_tables", [])))
with col4:
    total_elements = (len(data.get("dimensions", [])) + 
                     len(data.get("geometric_tolerances", [])) + 
                     len(data.get("raw_tables", [])))
    st.metric("🔍 Total Elements", total_elements)

# Pestanyes
tab1, tab2, tab3 = st.tabs(["📏 Cotes", "⚙️ Toleràncies Geomètriques", "📊 Taules"])

with tab1:
    st.subheader("📏 Cotes Detectades")
    
    if data.get("dimensions"):
        for i, dim in enumerate(data["dimensions"]):
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                desc = dim.get("description", dim.get("text", "Sense descripció"))
                confidence = dim.get("confidence", "N/A")
                if isinstance(confidence, (int, float)):
                    st.text(f"• {desc} (confiança: {confidence:.1f})")
                else:
                    st.text(f"• {desc}")
            with col2:
                is_correct = st.checkbox("Correcte?", True, key=f"dim_{i}")
            with col3:
                if st.button("📝", key=f"edit_dim_{i}", help="Editar"):
                    st.session_state[f'editing_dim_{i}'] = True
            
            # Edició inline
            if st.session_state.get(f'editing_dim_{i}', False):
                new_desc = st.text_input(f"Corregir descripció {i+1}:", value=desc, key=f"new_desc_{i}")
                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.button("💾 Guardar", key=f"save_dim_{i}"):
                        data["dimensions"][i]['description'] = new_desc
                        st.session_state[f'editing_dim_{i}'] = False
                        st.rerun()
                with col_cancel:
                    if st.button("❌ Cancel·lar", key=f"cancel_dim_{i}"):
                        st.session_state[f'editing_dim_{i}'] = False
                        st.rerun()
    else:
        st.info("No s'han detectat cotes en aquest document.")

with tab2:
    st.subheader("⚙️ Toleràncies Geomètriques")
    
    if data.get("geometric_tolerances"):
        for i, tol in enumerate(data["geometric_tolerances"]):
            col1, col2 = st.columns([4, 1])
            with col1:
                symbol = tol.get('symbol', 'N/A')
                value = tol.get('value', 'N/A')
                datum = tol.get('datum', '')
                tol_type = tol.get('type', 'N/A')
                
                if datum:
                    st.text(f"{symbol} {value} {datum} → {tol_type}")
                else:
                    st.text(f"{symbol} {value} → {tol_type}")
            with col2:
                st.checkbox("Correcte?", True, key=f"tol_{i}")
    else:
        st.info("No s'han detectat toleràncies geomètriques en aquest document.")

with tab3:
    st.subheader("📊 Taules Extretes")
    
    if data.get("raw_tables"):
        for i, table in enumerate(data["raw_tables"]):
            with st.expander(f"Taula {i+1} - {table.get('type', 'Desconeguda')}"):
                if table.get("type") == "info_table":
                    st.json(table.get("data", {}))
                else:
                    table_data = table.get("data", [])
                    if isinstance(table_data, list) and table_data:
                        # Convertir a DataFrame si és possible
                        try:
                            df = pd.DataFrame(table_data)
                            st.dataframe(df, use_container_width=True)
                        except:
                            # Si no es pot convertir, mostrar com JSON
                            st.json(table_data)
                    else:
                        st.write("Taula buida o dades no vàlides")
    else:
        st.info("No s'han extret taules d'aquest document.")

# Secció de finalització i exportació
st.divider()
st.subheader("💾 Finalització i Exportació")

col1, col2 = st.columns(2)
with col1:
    if st.button("✅ Finalitzar Validació", type="primary"):
        st.success("✅ Validació completada. Dades preparades per a exportar.")

with col2:
    st.write("**Opcions d'exportació:**")

# Secció d'exportació millorada
st.subheader("📤 Exportar Resultats")

# Crear les dades d'exportació amb correccions de l'usuari
export_data = data.copy()

# Aplicar correccions de l'usuari
for i in range(len(data.get("dimensions", []))):
    if st.session_state.get(f'editing_dim_{i}', False):
        new_desc = st.session_state.get(f'new_desc_{i}', '')
        if new_desc and 'dimensions' in export_data:
            export_data["dimensions"][i]['description'] = new_desc
            export_data["dimensions"][i]['user_corrected'] = True

# Opcions d'exportació en columnes
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**📊 Exportar a Excel**")
    st.write("Full de càlcul amb pestanyes separades per cada tipus de dada")
    
    try:
        excel_data = create_excel_export(export_data)
        st.download_button(
            label="⬇️ Descarregar Excel",
            data=excel_data,
            file_name=f"validacio_planols_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="excel_download"
        )
    except Exception as e:
        st.error(f"Error creant Excel: {e}")

with col2:
    st.markdown("**📄 JSON Schema Validat**")
    st.write("Fitxer JSON amb esquema de validació incorporat")
    
    json_schema_data = create_json_schema_export(export_data)
    st.download_button(
        label="⬇️ Descarregar JSON Schema",
        data=json_schema_data,
        file_name=f"schema_validacio_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        key="json_schema_download"
    )

with col3:
    st.markdown("**📋 JSON Simple**")
    st.write("Format JSON estàndard per integració")
    
    # JSON simple amb metadades
    simple_json_data = {
        "validation_completed": True,
        "export_timestamp": str(pd.Timestamp.now().isoformat()),
        "data": export_data,
        "user_corrections": {
            "total_corrections": sum(1 for i in range(len(data.get("dimensions", []))) 
                                   if st.session_state.get(f'editing_dim_{i}', False))
        }
    }
    
    st.download_button(
        label="⬇️ Descarregar JSON",
        data=json.dumps(simple_json_data, indent=2, ensure_ascii=False),
        file_name=f"validacio_simple_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        key="json_simple_download"
    )

# Informació addicional sobre exportació
with st.expander("ℹ️ Informació sobre formats d'exportació"):
    st.markdown("""
    **📊 Format Excel (.xlsx):**
    - Conté pestanyes separades per: Informació de Peça, Cotes, Toleràncies, Taules
    - Ideal per anàlisi i edició manual
    - Compatible amb Microsoft Excel, LibreOffice Calc, Google Sheets
    
    **📄 JSON Schema:**
    - Inclou esquema de validació JSON Schema v7
    - Estructura de dades validada automàticament
    - Ideal per integració amb sistemes externos
    
    **📋 JSON Simple:**
    - Format JSON estàndard sense esquema
    - Inclou metadades de validació i correccions
    - Ideal per processament programàtic simple
    """)
