"""
Component de visualització interactiva per Streamlit
Proporciona eines avançades per visualitzar i interactuar amb elements detectats
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from PIL import Image
import cv2
from typing import Dict, List, Optional, Tuple


class InteractiveVisualization:
    """Classe per crear visualitzacions interactives dels resultats OCR+IA"""
    
    def __init__(self):
        self.colors = {
            "dimension_text": "#00FF00",      # Verd
            "dimension_line": "#FF0000",      # Vermell
            "arrow_head": "#0000FF",          # Blau
            "geometric_tolerance": "#FFFF00", # Groc
            "info_table": "#FF00FF",          # Magenta
            "revision_table": "#00FFFF",      # Cian
            "title_block": "#800080",         # Púrpura
            "section_line": "#FFA500",        # Taronja
            "center_line": "#0080FF",         # Blau clar
            "construction_line": "#808080",   # Gris
            "weld_symbol": "#FF1493",         # Rosa fosc
            "surface_finish": "#32CD32",      # Verd lima
            "datum_reference": "#8A2BE2",     # Blau violeta
        }
    
    def create_confidence_histogram(self, elements: List[Dict]) -> go.Figure:
        """Crea histograma de distribució de confiança"""
        confidences = [elem.get('confidence', 0.5) for elem in elements]
        
        fig = px.histogram(
            x=confidences,
            nbins=20,
            title="Distribució de Confiança dels Elements",
            labels={'x': 'Confiança', 'y': 'Nombre d\'Elements'},
            color_discrete_sequence=['#1f77b4']
        )
        
        # Afegir línies verticals per als llindars
        fig.add_vline(x=0.8, line_dash="dash", line_color="green", 
                     annotation_text="Confiança Alta")
        fig.add_vline(x=0.5, line_dash="dash", line_color="orange", 
                     annotation_text="Confiança Mitjana")
        
        fig.update_layout(
            xaxis_title="Confiança",
            yaxis_title="Nombre d'Elements",
            showlegend=False
        )
        
        return fig
    
    def create_elements_scatter_plot(self, elements: List[Dict], image_width: int, image_height: int) -> go.Figure:
        """Crea gràfic de dispersió dels elements sobre la imatge"""
        if not elements:
            return go.Figure()
        
        # Preparar dades amb error handling
        x_coords = [elem.get('center', {}).get('x', 0) for elem in elements]
        y_coords = [image_height - elem.get('center', {}).get('y', 0) for elem in elements]  # Invertir Y per coordenades d'imatge
        types = [elem.get('type', 'unknown') for elem in elements]
        confidences = [elem.get('confidence', 0.5) for elem in elements]
        texts = [elem.get('text', '')[:30] + '...' if len(elem.get('text', '')) > 30 else elem.get('text', '') for elem in elements]
        
        # Crear figura
        fig = go.Figure()
        
        # Afegir punt per cada tipus d'element
        for element_type in set(types):
            mask = [t == element_type for t in types]
            fig.add_trace(go.Scatter(
                x=[x for x, m in zip(x_coords, mask) if m],
                y=[y for y, m in zip(y_coords, mask) if m],
                mode='markers',
                name=element_type,
                text=[f"Tipus: {element_type}<br>Confiança: {c:.2f}<br>Text: {txt}" 
                      for c, txt, m in zip(confidences, texts, mask) if m],
                textposition="top center",
                marker=dict(
                    size=[c*20 + 5 for c, m in zip(confidences, mask) if m],  # Mida segons confiança
                    color=self.colors.get(element_type, '#808080'),
                    opacity=0.7,
                    line=dict(width=2, color='white')
                ),
                hovertemplate="<b>%{text}</b><extra></extra>"
            ))
        
        fig.update_layout(
            title="Posició dels Elements Detectats",
            xaxis_title="Coordenada X (pixels)",
            yaxis_title="Coordenada Y (pixels)",
            width=800,
            height=600,
            xaxis=dict(range=[0, image_width]),
            yaxis=dict(range=[0, image_height]),
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.01
            )
        )
        
        return fig
    
    def create_type_distribution_chart(self, elements: List[Dict]) -> go.Figure:
        """Crea gràfic de distribució per tipus d'element"""
        type_counts = {}
        for elem in elements:
            element_type = elem['type']
            type_counts[element_type] = type_counts.get(element_type, 0) + 1
        
        if not type_counts:
            return go.Figure()
        
        # Ordenar per frequència
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        types, counts = zip(*sorted_types)
        
        colors = [self.colors.get(t, '#808080') for t in types]
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(types),
                y=list(counts),
                marker_color=colors,
                text=list(counts),
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title="Distribució d'Elements per Tipus",
            xaxis_title="Tipus d'Element",
            yaxis_title="Nombre d'Elements",
            xaxis_tickangle=-45
        )
        
        return fig
    
    def create_confidence_by_type_chart(self, elements: List[Dict]) -> go.Figure:
        """Crea box plot de confiança per tipus d'element"""
        if not elements:
            return go.Figure()
        
        # Preparar dades per plotly amb error handling
        data_for_box = []
        for elem in elements:
            data_for_box.append({
                'type': elem.get('type', 'unknown'),
                'confidence': elem.get('confidence', 0.5)
            })
        
        df = pd.DataFrame(data_for_box)
        
        # Crear box plot
        fig = px.box(
            df, 
            x='type', 
            y='confidence',
            title="Distribució de Confiança per Tipus d'Element",
            color='type',
            color_discrete_map=self.colors
        )
        
        fig.update_layout(
            xaxis_title="Tipus d'Element",
            yaxis_title="Confiança",
            xaxis_tickangle=-45,
            showlegend=False
        )
        
        return fig
    
    def create_size_analysis_chart(self, elements: List[Dict]) -> go.Figure:
        """Crea anàlisi de mides dels elements detectats"""
        if not elements:
            return go.Figure()
        
        # Preparar dades amb error handling
        areas = [elem.get('area', 1) for elem in elements]
        types = [elem.get('type', 'unknown') for elem in elements]
        confidences = [elem.get('confidence', 0.5) for elem in elements]
        
        # Crear scatter plot amb àrea vs confiança
        fig = go.Figure()
        
        for element_type in set(types):
            mask = [t == element_type for t in types]
            fig.add_trace(go.Scatter(
                x=[a for a, m in zip(areas, mask) if m],
                y=[c for c, m in zip(confidences, mask) if m],
                mode='markers',
                name=element_type,
                marker=dict(
                    color=self.colors.get(element_type, '#808080'),
                    size=8,
                    opacity=0.7
                ),
                hovertemplate=f"<b>{element_type}</b><br>" +
                             "Àrea: %{x} px²<br>" +
                             "Confiança: %{y:.3f}<extra></extra>"
            ))
        
        fig.update_layout(
            title="Relació entre Àrea i Confiança dels Elements",
            xaxis_title="Àrea (pixels²)",
            yaxis_title="Confiança",
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.01
            )
        )
        
        return fig
    
    def create_processing_performance_chart(self, pages_data: List[Dict]) -> go.Figure:
        """Crea gràfic de rendiment del processament per pàgina"""
        if not pages_data:
            return go.Figure()
        
        page_numbers = []
        total_elements = []
        high_conf_ratios = []
        processing_methods = []
        
        for page in pages_data:
            page_numbers.append(page['page_number'])
            total_elements.append(len(page.get('elements', [])))
            
            if 'ai_metadata' in page:
                high_conf_ratios.append(page['ai_metadata'].get('high_confidence_ratio', 0))
            else:
                high_conf_ratios.append(0)
            
            processing_methods.append(page.get('processing_method', 'unknown'))
        
        # Crear subplot amb dues mètriques
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Elements Detectats per Pàgina', 'Ratio de Confiança Alta per Pàgina'),
            vertical_spacing=0.1
        )
        
        # Gràfic d'elements detectats
        fig.add_trace(
            go.Bar(
                x=page_numbers,
                y=total_elements,
                name="Elements Detectats",
                marker_color='lightblue'
            ),
            row=1, col=1
        )
        
        # Gràfic de ratio de confiança
        fig.add_trace(
            go.Bar(
                x=page_numbers,
                y=[r * 100 for r in high_conf_ratios],  # Convertir a percentatge
                name="Confiança Alta (%)",
                marker_color='lightgreen'
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title="Rendiment del Processament per Pàgina",
            showlegend=False,
            height=600
        )
        
        fig.update_xaxes(title_text="Número de Pàgina", row=2, col=1)
        fig.update_yaxes(title_text="Nombre d'Elements", row=1, col=1)
        fig.update_yaxes(title_text="Percentatge (%)", row=2, col=1)
        
        return fig
    
    def create_summary_dashboard(self, processing_results: Dict):
        """Crea un dashboard complet amb totes les visualitzacions"""
        st.subheader("📊 Dashboard de Visualització")
        
        if not processing_results or not processing_results.get('pages'):
            st.warning("No hi ha dades per visualitzar")
            return
        
        # Recopilar tots els elements
        all_elements = []
        for page in processing_results['pages']:
            for elem in page.get('elements', []):
                elem_with_page = elem.copy()
                elem_with_page['page_number'] = page['page_number']
                all_elements.append(elem_with_page)
        
        if not all_elements:
            st.warning("No s'han detectat elements per visualitzar")
            return
        
        # Layout del dashboard
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribució de confiança
            conf_fig = self.create_confidence_histogram(all_elements)
            st.plotly_chart(conf_fig, use_container_width=True, key="dashboard_confidence_hist")
            
            # Distribució per tipus
            type_fig = self.create_type_distribution_chart(all_elements)
            st.plotly_chart(type_fig, use_container_width=True, key="dashboard_type_dist")
        
        with col2:
            # Confiança per tipus
            conf_type_fig = self.create_confidence_by_type_chart(all_elements)
            st.plotly_chart(conf_type_fig, use_container_width=True, key="dashboard_conf_by_type")
            
            # Anàlisi de mides
            size_fig = self.create_size_analysis_chart(all_elements)
            st.plotly_chart(size_fig, use_container_width=True, key="dashboard_size_analysis")
        
        # Gràfics de pàgina completa
        st.subheader("📈 Anàlisi de Rendiment")
        
        # Rendiment per pàgina
        perf_fig = self.create_processing_performance_chart(processing_results['pages'])
        st.plotly_chart(perf_fig, use_container_width=True, key="dashboard_performance")
        
        # Posició dels elements (només per la primera pàgina amb elements)
        page_with_elements = None
        for page in processing_results['pages']:
            if page.get('elements'):
                page_with_elements = page
                break
        
        if page_with_elements:
            st.subheader(f"🗺️ Mapa d'Elements - Pàgina {page_with_elements['page_number']}")
            
            # Estimar dimensions de la imatge amb error handling
            elements = page_with_elements['elements']
            if elements:
                max_x = max([elem.get('coordinates', {}).get('x1', 0) + elem.get('coordinates', {}).get('width', 0) for elem in elements] + [1000])
                max_y = max([elem.get('coordinates', {}).get('y1', 0) + elem.get('coordinates', {}).get('height', 0) for elem in elements] + [1000])
            else:
                max_x, max_y = 1000, 1000
            
            scatter_fig = self.create_elements_scatter_plot(elements, max_x, max_y)
            st.plotly_chart(scatter_fig, use_container_width=True, key="dashboard_elements_scatter")


def show_interactive_element_details(element: Dict, element_id: str):
    """Mostra detalls interactius d'un element específic"""
    st.subheader(f"🔍 Element {element_id} - {element['type']}")
    
    # Informació en columnes
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Confiança", f"{element.get('confidence', 0):.3f}")
        st.metric("Tipus", element.get('type', 'unknown'))
    
    with col2:
        st.metric("Àrea", f"{element.get('area', 0)} px²")
        st.metric("Font", element.get('source', 'unknown'))
    
    with col3:
        center = element.get('center', {})
        center_x = center.get('x', 0)
        center_y = center.get('y', 0)
        st.metric("Centre X", center_x)
        st.metric("Centre Y", center_y)
    
    # Text detectat
    if element.get('text', '').strip():
        st.subheader("📝 Text Detectat")
        st.text_area("Contingut:", element.get('text', ''), height=100, disabled=True, key=f"text_content_{element_id}")
    
    # Coordenades detallades
    with st.expander("📐 Coordenades detallades"):
        coords = element.get('coordinates', {})
        center = element.get('center', {})
        
        # Calcular coordenades de la cantonada inferior dreta
        x1 = coords.get('x1', 0)
        y1 = coords.get('y1', 0)
        width = coords.get('width', 0)
        height = coords.get('height', 0)
        x2 = x1 + width
        y2 = y1 + height
        
        st.json({
            "Cantonada superior esquerra": f"({x1}, {y1})",
            "Cantonada inferior dreta": f"({x2}, {y2})",
            "Amplada": f"{width} px",
            "Altura": f"{height} px",
            "Centre": f"({center.get('x', 0)}, {center.get('y', 0)})",
            "Àrea": f"{element.get('area', 0)} px²"
        })


if __name__ == "__main__":
    # Exemple d'ús
    st.title("🎨 Component de Visualització Interactiva")
    
    # Dades d'exemple
    example_elements = [
        {
            'id': 1, 'type': 'dimension_text', 'confidence': 0.95, 'text': '50mm',
            'coordinates': {'x1': 100, 'y1': 100, 'x2': 150, 'y2': 120},
            'center': {'x': 125, 'y': 110}, 'area': 1000, 'source': 'ai'
        },
        {
            'id': 2, 'type': 'arrow_head', 'confidence': 0.88, 'text': '',
            'coordinates': {'x1': 200, 'y1': 200, 'x2': 220, 'y2': 220},
            'center': {'x': 210, 'y': 210}, 'area': 400, 'source': 'ai'
        }
    ]
    
    viz = InteractiveVisualization()
    
    # Mostrar gràfics d'exemple
    fig1 = viz.create_confidence_histogram(example_elements)
    st.plotly_chart(fig1, key="example_confidence_hist")
    
    fig2 = viz.create_type_distribution_chart(example_elements)
    st.plotly_chart(fig2, key="example_type_dist")
