# src/ui/app.py (actualitzat)
import streamlit as st
import json
import pandas as pd
import os
import tempfile
import sys
from pathlib import Path

# Afegir el directori src al path per importar els mòduls
sys.path.append(str(Path(__file__).parent.parent))

try:
    from pipeline import OCRPipeline
except ImportError:
    # Fallback a importacions individuals
    from pdf_to_images import pdf_to_images
    from ocr_processor import ocr_with_boxes
    from data_extractor import extract_technical_data
    from dimension_linker import detect_lines, link_text_to_lines

st.set_page_config(page_title="Validador de Plànols Tècnics", layout="wide")
st.title("� Validador de Plànols Tècnics")

# Sidebar per càrrega de fitxers
with st.sidebar:
    st.header("📂 Càrrega de fitxer")
    uploaded_file = st.file_uploader("Selecciona un PDF", type=['pdf'])
    
    if uploaded_file is not None:
        if st.button("🚀 Processar PDF", type="primary"):
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
                    st.info("� Executant pipeline complet...")
                    results = pipeline.process_pdf(tmp_path, save_files=True)
                    
                    # Generar estadístiques
                    stats = pipeline.get_stats(results)
                    
                    # Guardar resultats a la sessió
                    st.session_state['processed_data'] = results['tech_data']
                    st.session_state['linked_data'] = results['linked_data']
                    st.session_state['image_path'] = results['image_path']
                    st.session_state['stats'] = stats
                    
                    st.success("✅ Processament completat!")
                    
                    # Mostrar estadístiques ràpides
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📏 Cotes", stats['dimensions'])
                    with col2:
                        st.metric("📝 Anotacions", stats['notes'])
                    with col3:
                        st.metric("🔗 Vinculats", stats['linked_elements'])
                    
                except Exception as e:
                    st.error(f"❌ Error durant el processament: {str(e)}")
                    st.exception(e)  # Per debug
                finally:
                    # Netejar fitxer temporal
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)

# Mostrar resultats si existeixen
if 'processed_data' in st.session_state:
    data = st.session_state['processed_data']
    
    # Mostrar imatge processada
    if 'image_path' in st.session_state:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("📸 Imatge processada")
            st.image(st.session_state['image_path'], caption="Plànol tècnic", use_column_width=True)
        
        with col2:
            st.subheader("📊 Resum")
            st.metric("Cotes detectades", len(data.get("dimensions", [])))
            st.metric("Anotacions", len(data.get("notes", [])))
            if 'linked_data' in st.session_state:
                st.metric("Elements vinculats", len(st.session_state['linked_data']))
    
    # Validació de cotes
    st.subheader("📏 Cotes detectades")
    if data.get("dimensions"):
        for i, dim in enumerate(data["dimensions"]):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.text(f"🔍 {dim['text']} (conf: {dim['confidence']:.1f})")
            with col2:
                is_ok = st.checkbox("Correcte?", value=True, key=f"dim_{i}")
            with col3:
                if st.button("📝", key=f"edit_{i}", help="Editar"):
                    st.session_state[f'editing_{i}'] = True
            
            # Edició inline
            if st.session_state.get(f'editing_{i}', False):
                new_text = st.text_input(f"Corregir cota {i+1}:", value=dim['text'], key=f"new_text_{i}")
                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.button("💾 Guardar", key=f"save_{i}"):
                        data["dimensions"][i]['text'] = new_text
                        st.session_state[f'editing_{i}'] = False
                        st.rerun()
                with col_cancel:
                    if st.button("❌ Cancel·lar", key=f"cancel_{i}"):
                        st.session_state[f'editing_{i}'] = False
                        st.rerun()
    else:
        st.info("No s'han detectat cotes en aquest document.")
    
    # Anotacions
    st.subheader("📝 Anotacions")
    if data.get("notes"):
        for i, note in enumerate(data["notes"]):
            st.text(f"📝 {note['text']}")
    else:
        st.info("No s'han detectat anotacions en aquest document.")
    
    # Dades vinculades (si existeixen)
    if 'linked_data' in st.session_state and st.session_state['linked_data']:
        with st.expander("🔗 Dades vinculades a línies"):
            for i, item in enumerate(st.session_state['linked_data']):
                st.write(f"**Text:** {item['text']}")
                st.write(f"**Orientació:** {item['orientation']}")
                st.write(f"**Distància a línia:** {item['distance']:.1f}px")
                st.divider()
    
    # Finalització
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Finalitzar Validació", type="primary"):
            st.success("✅ Validació completada. Dades preparades per a exportar.")
    
    with col2:
        if st.button("📤 Exportar resultats", type="secondary"):
            # Crear JSON per exportar
            export_data = {
                "validation_completed": True,
                "processed_data": data,
                "linked_data": st.session_state.get('linked_data', []),
                "user_corrections": {}
            }
            
            st.download_button(
                label="⬇️ Descarregar JSON",
                data=json.dumps(export_data, indent=2, ensure_ascii=False),
                file_name="resultats_validacio.json",
                mime="application/json"
            )

else:
    # Fallback: carregar dades existents si no hi ha res processat
    try:
        base_dir = str(Path(__file__).parent.parent.parent)
        structured_path = os.path.join(base_dir, "data", "output", "structured", "structured_output.json")
        
        if os.path.exists(structured_path):
            st.info("📂 Carregant dades de l'últim processament...")
            with open(structured_path, "r", encoding="utf-8") as f:
                st.session_state['processed_data'] = json.load(f)
            st.rerun()
        else:
            st.info("👆 Carrega un PDF per començar el processament.")
    except Exception as e:
        st.warning("⚠️ No s'han trobat dades processades anteriorment. Carrega un PDF per començar.")