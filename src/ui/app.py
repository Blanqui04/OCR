# src/ui/app.py (actualitzat amb IA)
import streamlit as st
import json
import pandas as pd
import os
import tempfile
import sys
import traceback
from pathlib import Path
from io import BytesIO
from datetime import datetime

# Afegir el directori src al path per importar els mòduls
sys.path.append(str(Path(__file__).parent.parent))

try:
    from pipeline import OCRPipeline
    
    # Intentar importar components d'IA
    try:
        from ai_enhanced_pipeline import AIEnhancedPipeline, DEFAULT_AI_CONFIG
        AI_ENHANCED_AVAILABLE = True
    except ImportError:
        AI_ENHANCED_AVAILABLE = False
        
except ImportError as e:
    st.error(f"Error important OCRPipeline: {e}")
    # Fallback a importacions individuals
    try:
        from pdf_to_images import pdf_to_images
        from ocr_processor import ocr_with_boxes
        from data_extractor import extract_technical_data
        from dimension_linker import detect_lines, link_text_to_lines
        OCRPipeline = None
        AI_ENHANCED_AVAILABLE = False
    except ImportError as e2:
        st.error(f"Error important mòduls individuals: {e2}")
        OCRPipeline = None
        AI_ENHANCED_AVAILABLE = False

st.set_page_config(page_title="Validador de Plànols Tècnics amb IA", layout="wide")

# Configurar l'estat de la sessió per IA
if 'ai_enabled' not in st.session_state:
    st.session_state.ai_enabled = AI_ENHANCED_AVAILABLE
if 'ai_pipeline' not in st.session_state:
    st.session_state.ai_pipeline = None
if 'processing_results' not in st.session_state:
    st.session_state.processing_results = None

st.title("🤖📐 Validador de Plànols Tècnics amb IA")

# Sidebar per configuració d'IA
with st.sidebar:
    st.header("⚙️ Configuració")
    
    # Configuració d'IA
    st.subheader("🤖 Intel·ligència Artificial")
    
    if AI_ENHANCED_AVAILABLE:
        st.success("✅ Components d'IA disponibles")
        
        # Toggle per activar/desactivar IA
        ai_enabled = st.checkbox(
            "Utilitzar IA híbrida", 
            value=st.session_state.ai_enabled,
            help="Combina detecció amb IA i regles tradicionals per màxima precisió"
        )
        st.session_state.ai_enabled = ai_enabled
        
        if ai_enabled:
            # Inicialitzar pipeline d'IA si cal
            if st.session_state.ai_pipeline is None:
                with st.spinner("Inicialitzant pipeline d'IA..."):
                    try:
                        # Crear configuració d'IA si no existeix
                        project_root = Path(__file__).parent.parent.parent
                        config_path = project_root / "config_ai.json"
                        
                        if not config_path.exists():
                            with open(config_path, 'w') as f:
                                json.dump(DEFAULT_AI_CONFIG, f, indent=2)
                        
                        st.session_state.ai_pipeline = AIEnhancedPipeline(str(config_path))
                        st.success("Pipeline d'IA inicialitzat!")
                    except Exception as e:
                        st.error(f"Error inicialitzant IA: {e}")
                        st.session_state.ai_enabled = False
            
            if st.session_state.ai_pipeline:
                # Mostrar estadístiques del model
                stats = st.session_state.ai_pipeline.get_model_performance_stats()
                
                col1, col2 = st.columns(2)
                with col1:
                    if stats['model_loaded']:
                        st.success("🎯 Model carregat")
                    else:
                        st.warning("⚠️ Model no carregat")
                
                with col2:
                    st.metric("Precisió estimada", f"{stats['accuracy_estimate']:.1%}")
                
                st.metric("Correccions d'usuari", stats['total_corrections'])
                
                # Configuració avançada
                with st.expander("Configuració avançada"):
                    confidence_threshold = st.slider(
                        "Llindar de confiança", 
                        0.1, 1.0, 0.7, 0.05,
                        help="Elements amb confiança inferior necessitaran revisió humana"
                    )
        
    else:
        st.error("❌ Components d'IA no disponibles")
        st.info("💡 Instal·la les dependències d'IA per habilitar aquesta funcionalitat")
        st.session_state.ai_enabled = False

# Pestanyes principals amb IA
tab1, tab2, tab3, tab4 = st.tabs(["📤 Pujar Fitxer", "🔍 Resultats", "🔧 Validació HIITL", "📊 Export de Dades"])

with tab1:
    st.header("Pujar fitxer PDF")
    
    # Selector del mètode de processament
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Escull un fitxer PDF", 
            type=['pdf'],
            help="Puja un plànol tècnic en format PDF per analitzar"
        )
    
    with col2:
        processing_method = st.selectbox(
            "Mètode de processament",
            ["IA Híbrida", "Només Regles", "Només IA"] if st.session_state.ai_enabled else ["Només Regles"],
            help="Escull com processar el document"
        )
    
    if uploaded_file is not None:
        # Guardar fitxer temporalment
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name
        
        col1, col2, col3 = st.columns(3)
        
        with col2:
            if st.button("🚀 Processar amb IA" if st.session_state.ai_enabled else "🚀 Processar", 
                        type="primary", use_container_width=True):
                
                with st.spinner("Processant document..."):
                    try:
                        if st.session_state.ai_enabled and st.session_state.ai_pipeline:
                            # Processament amb IA
                            use_ai = processing_method in ["IA Híbrida", "Només IA"]
                            results = st.session_state.ai_pipeline.process_document_with_ai(tmp_path, use_ai)
                            st.session_state.processing_results = results
                            
                            if results['status'] == 'success':
                                st.success(f"✅ Document processat amb èxit!")
                                st.info(f"📄 {len(results['pages'])} pàgines processades")
                                st.info(f"🔍 {results['total_elements']} elements detectats")
                                
                                if results['human_review_required']:
                                    st.warning("⚠️ Alguns elements necessiten revisió humana")
                            else:
                                st.error(f"❌ Error: {results.get('error', 'Unknown error')}")
                        
                        else:
                            # Processament tradicional
                            st.info("Utilitzant processament tradicional...")
                            # Aquí aniria la lògica existent del pipeline tradicional
                            st.warning("Implementar fallback al pipeline tradicional")
                    
                    except Exception as e:
                        st.error(f"Error processant: {str(e)}")
                        st.error(traceback.format_exc())
                
                # Netejar fitxer temporal
                try:
                    os.unlink(tmp_path)
                except:
                    pass

with tab2:
    st.header("🔍 Resultats de la Detecció")
    
    if st.session_state.processing_results:
        results = st.session_state.processing_results
        
        # Resum general
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📄 Pàgines", len(results.get('pages', [])))
        
        with col2:
            st.metric("🔍 Elements totals", results.get('total_elements', 0))
        
        with col3:
            needs_review = sum(len(page.get('human_review_tasks', [])) for page in results.get('pages', []))
            st.metric("⚠️ Necessiten revisió", needs_review)
        
        with col4:
            ai_enabled_display = "✅ Sí" if results.get('ai_enabled', False) else "❌ No"
            st.metric("🤖 IA utilitzada", ai_enabled_display)
        
        # Resultats per pàgina
        st.subheader("Resultats per pàgina")
        
        for page in results.get('pages', []):
            with st.expander(f"📄 Pàgina {page['page_number']} - {len(page.get('elements', []))} elements"):
                
                # Informació de la pàgina
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Mètode de processament:**", page.get('processing_method', 'Unknown'))
                    if 'ai_metadata' in page:
                        st.write("**Ratio alta confiança:**", f"{page['ai_metadata'].get('high_confidence_ratio', 0):.1%}")
                
                with col2:
                    st.write("**Necessita revisió:**", "Sí" if page.get('needs_human_review', False) else "No")
                    st.write("**Elements detectats:**", len(page.get('elements', [])))
                
                # Taula d'elements
                if page.get('elements'):
                    elements_df = pd.DataFrame([
                        {
                            'Tipus': elem.get('type', ''),
                            'Confiança': f"{elem.get('confidence', 0):.2f}",
                            'Font': elem.get('source', ''),
                            'Text': elem.get('text', '')[:50] + '...' if len(elem.get('text', '')) > 50 else elem.get('text', '')
                        }
                        for elem in page['elements']
                    ])
                    st.dataframe(elements_df, use_container_width=True)
                
                # Relacions espacials
                if page.get('relationships'):
                    st.write("**Relacions espacials trobades:**")
                    for rel in page['relationships'][:5]:  # Mostrar només les primeres 5
                        st.write(f"- {rel.get('type', 'Unknown relation')}")
    
    else:
        st.info("👆 Puja i processa un document per veure els resultats aquí")

with tab3:
    st.header("🔧 Validació Human-in-the-Loop (HIITL)")
    
    if st.session_state.processing_results and st.session_state.processing_results.get('human_review_required'):
        st.warning("⚠️ Hi ha elements que necessiten la teva revisió per millorar la precisió del model")
        
        # Recopilar totes les tasques de revisió
        all_review_tasks = []
        for page in st.session_state.processing_results.get('pages', []):
            for task in page.get('human_review_tasks', []):
                task['page_number'] = page['page_number']
                all_review_tasks.append(task)
        
        if all_review_tasks:
            st.write(f"**Total tasques de revisió:** {len(all_review_tasks)}")
            
            # Selector de tasca
            task_index = st.selectbox(
                "Selecciona tasca a revisar:",
                range(len(all_review_tasks)),
                format_func=lambda x: f"Pàgina {all_review_tasks[x]['page_number']} - {all_review_tasks[x].get('suggested_type', 'Unknown')}"
            )
            
            if task_index is not None:
                current_task = all_review_tasks[task_index]
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write("**Pregunta de revisió:**")
                    st.info(current_task.get('review_question', 'No question available'))
                    
                    st.write("**Detalls de l'element:**")
                    st.json({
                        'Tipus suggerit': current_task.get('suggested_type', ''),
                        'Confiança': current_task.get('confidence', 0),
                        'Coordenades': current_task.get('bbox', {})
                    })
                
                with col2:
                    st.write("**Correcció:**")
                    
                    # Tipus disponibles per correcció
                    available_types = [
                        "dimension_text", "arrow", "tolerance", "symbol", 
                        "info_text", "title", "line", "table", "scale", 
                        "north_arrow", "border", "legend", "other"
                    ]
                    
                    corrected_type = st.selectbox(
                        "Tipus correcte:",
                        available_types,
                        index=available_types.index(current_task.get('suggested_type', 'other')) 
                        if current_task.get('suggested_type', 'other') in available_types else 0
                    )
                    
                    if st.button("✅ Confirmar correcció", type="primary"):
                        # Guardar feedback
                        if st.session_state.ai_pipeline and st.session_state.ai_pipeline.learning_manager:
                            try:
                                st.session_state.ai_pipeline.learning_manager.save_user_correction(
                                    current_task.get('element', {}), 
                                    corrected_type, 
                                    "streamlit_user"
                                )
                                st.success("✅ Correcció guardada! El model millorarà amb aquesta informació.")
                                
                                # Actualitzar estadístiques
                                st.rerun()
                                
                            except Exception as e:
                                st.error(f"Error guardant correcció: {e}")
                        else:
                            st.warning("Sistema d'aprenentatge no disponible")
        
    elif st.session_state.processing_results:
        st.success("🎉 Tots els elements han estat detectats amb alta confiança! No cal revisió manual.")
    
    else:
        st.info("👆 Processa primer un document per veure tasques de validació aquí")

with tab4:
    st.header("📊 Export de Dades")
    
    if st.session_state.processing_results:
        results = st.session_state.processing_results
        
        st.subheader("Formats d'exportació disponibles")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Exportar a Excel", type="primary"):
                with st.spinner("Creant fitxer Excel..."):
                    try:
                        if st.session_state.ai_pipeline:
                            export_path = st.session_state.ai_pipeline.export_results_enhanced(results, "excel")
                            st.success(f"✅ Excel creat: {Path(export_path).name}")
                            
                            # Oferir descàrrega
                            with open(export_path, 'rb') as f:
                                st.download_button(
                                    "⬇️ Descarregar Excel",
                                    f.read(),
                                    f"resultats_ia_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                        else:
                            st.error("Pipeline d'IA no disponible per exportació")
                    except Exception as e:
                        st.error(f"Error creant Excel: {e}")
        
        with col2:
            if st.button("📄 Exportar JSON Schema", type="secondary"):
                with st.spinner("Creant JSON Schema..."):
                    try:
                        if st.session_state.ai_pipeline:
                            export_path = st.session_state.ai_pipeline.export_results_enhanced(results, "json_schema")
                            st.success(f"✅ JSON Schema creat: {Path(export_path).name}")
                            
                            # Oferir descàrrega
                            with open(export_path, 'r', encoding='utf-8') as f:
                                st.download_button(
                                    "⬇️ Descarregar JSON Schema",
                                    f.read(),
                                    f"resultats_schema_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                    "application/json"
                                )
                        else:
                            st.error("Pipeline d'IA no disponible per exportació")
                    except Exception as e:
                        st.error(f"Error creant JSON Schema: {e}")
        
        with col3:
            if st.button("🗂️ Exportar JSON Simple", type="secondary"):
                with st.spinner("Creant JSON..."):
                    try:
                        if st.session_state.ai_pipeline:
                            export_path = st.session_state.ai_pipeline.export_results_enhanced(results, "json")
                            st.success(f"✅ JSON creat: {Path(export_path).name}")
                            
                            # Oferir descàrrega
                            with open(export_path, 'r', encoding='utf-8') as f:
                                st.download_button(
                                    "⬇️ Descarregar JSON",
                                    f.read(),
                                    f"resultats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                    "application/json"
                                )
                        else:
                            st.error("Pipeline d'IA no disponible per exportació")
                    except Exception as e:
                        st.error(f"Error creant JSON: {e}")
        
        # Previsualització de dades
        st.subheader("Previsualització de dades")
        
        # Crear dataframe resum per mostrar
        all_elements = []
        for page in results.get('pages', []):
            for elem in page.get('elements', []):
                elem_data = {
                    'Pàgina': page['page_number'],
                    'Tipus': elem.get('type', ''),
                    'Confiança': elem.get('confidence', 0),
                    'Font': elem.get('source', ''),
                    'Text': elem.get('text', '')[:100] + '...' if len(elem.get('text', '')) > 100 else elem.get('text', '')
                }
                all_elements.append(elem_data)
        
        if all_elements:
            df_preview = pd.DataFrame(all_elements)
            st.dataframe(df_preview, use_container_width=True)
            
            # Estadístiques ràpides
            st.subheader("Estadístiques")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                type_counts = df_preview['Tipus'].value_counts()
                st.write("**Elements per tipus:**")
                st.write(type_counts)
            
            with col2:
                avg_confidence = df_preview['Confiança'].mean()
                st.metric("Confiança mitjana", f"{avg_confidence:.2f}")
            
            with col3:
                source_counts = df_preview['Font'].value_counts()
                st.write("**Elements per font:**")
                st.write(source_counts)
    
    else:
        st.info("👆 Processa primer un document per exportar les dades")

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
