"""
Aplicació Professional de Visualització OCR
Una aplicació d'escriptori per a Windows per visualitzar els resultats de Google Cloud Document AI
amb renderització de PDF i superposició de caixes delimitadores de text.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import tkinter.font as tkFont
from PIL import Image, ImageTk, ImageDraw
import fitz 
from google.cloud import documentai_v1 as documentai
from google.api_core.client_options import ClientOptions
import os
import io
import threading
from dataclasses import dataclass
from typing import List, Optional
import json
import warnings
import csv
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from drawing_postprocessor import DrawingPostProcessor
from modern_ui_theme import ModernUITheme

# Suprimeix els avisos d'autenticació de Google Cloud
warnings.filterwarnings("ignore", message="La vostra aplicació s'ha autenticat utilitzant credencials d'usuari final")

@dataclass
class TextBlock:
    """Representa un bloc de text amb el seu contingut i caixa delimitadora"""
    text: str
    confidence: float
    bbox: tuple  # (x1, y1, x2, y2)
    page_num: int

class OCRViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📄 Visor OCR Professional - Google Cloud Document AI")
        self.root.geometry("1600x1000")
        
        # Initialize modern UI theme
        self.theme = ModernUITheme()
        self.root.configure(bg=self.theme.colors['bg_primary'])

        # Estat de l'aplicació
        self.current_pdf_path = None
        self.pdf_document = None
        self.text_blocks = []
        self.current_page = 0
        self.zoom_factor = 1.0
        self.selected_block = None
        self.recent_files = self.load_recent_files()
        self.heatmap_mode = False
        self.show_reading_order_mode = False
        
        # Post-processor for technical drawings
        self.post_processor = DrawingPostProcessor()
        self.structured_data = None
        
        # Google Cloud configuració
        self.project_id = "natural-bison-465607-b6"
        self.location = "eu"
        self.processor_id = "4369d16f70cb0a26"
        
        # Set up Google Cloud credentials
        self._setup_google_credentials()
        
        self.setup_main_interface()
        self.setup_styles()
        
    def _setup_google_credentials(self):
        """Setup Google Cloud credentials"""
        # Check if credentials are already set
        if 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
            creds_path = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
            if os.path.exists(creds_path):
                print(f"✅ Utilitzant credencials de: {creds_path}")
                return
        
        # Try to find the expected credentials file
        keys_dir = r"C:\Users\eceballos\keys"
        expected_key_file = "natural-bison-465607-b6-a638a05f2638.json"
        key_path = os.path.join(keys_dir, expected_key_file)
        
        if os.path.exists(key_path):
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = key_path
            print(f"✅ Credencials configurades: {key_path}")
        else:
            print(f"⚠️ Fitxer de credencials no trobat: {key_path}")
            print("💡 Utilitza setup_google_auth.py per configurar l'autenticació")
        
    def setup_styles(self):
        """Configurar estil de l'UI"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Esquema de colors blau i blanc
        colors = {
            'primary_blue': '#2563eb',      # Blau modern
            'light_blue': '#3b82f6',       # Blau més clar
            'accent_blue': '#1d4ed8',      # Blau més fosc
            'white': '#ffffff',            # Blanc pur
            'light_gray': '#f8fafc',       # Blau gris molt clar
            'medium_gray': '#e2e8f0',      # Blau gris clar
            'dark_gray': '#475569',        # Blau gris fosc
            'text_dark': '#1e293b'         # Text blau gris fosc
        }
        
        # Configurar estils de botons moderns
        style.configure('Modern.TButton', 
                       padding=(12, 8), 
                       font=('Segoe UI', 9),
                       background=colors['primary_blue'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none')
        
        style.map('Modern.TButton',
                 background=[('active', colors['light_blue']),
                           ('pressed', colors['accent_blue'])])
        
        # Botó d'exportació amb estil modern
        style.configure('Export.TButton', 
                       padding=(12, 8), 
                       font=('Segoe UI', 9),
                       background='white',
                       foreground=colors['primary_blue'],
                       borderwidth=1,
                       bordercolor=colors['primary_blue'],
                       focuscolor='none')
        
        style.map('Export.TButton',
                 background=[('active', colors['light_gray']),
                           ('pressed', colors['medium_gray'])])
        
        # Estil de les etiquetes
        style.configure('Modern.TLabelFrame',
                       background=colors['white'],
                       foreground=colors['text_dark'],
                       borderwidth=1,
                       relief='solid',
                       bordercolor=colors['medium_gray'])
        
        style.configure('Modern.TLabelFrame.Label',
                       background=colors['white'],
                       foreground=colors['primary_blue'],
                       font=('Segoe UI', 10, 'bold'))
        
        # Estil de la capçalera
        style.configure('Header.TLabel', 
                       font=('Segoe UI', 12, 'bold'),
                       background=colors['white'],
                       foreground=colors['primary_blue'])
        
        # Estil de les pestanyes
        style.configure('Modern.TNotebook',
                       background=colors['white'],
                       borderwidth=0)
        
        style.configure('Modern.TNotebook.Tab',
                       padding=(12, 8),
                       background=colors['light_gray'],
                       foreground=colors['text_dark'],
                       borderwidth=1,
                       bordercolor=colors['medium_gray'])
        
        style.map('Modern.TNotebook.Tab',
                 background=[('selected', colors['white']),
                           ('active', colors['medium_gray'])])
        
        # Estil de la taula
        style.configure('Modern.Treeview',
                       background=colors['white'],
                       foreground=colors['text_dark'],
                       fieldbackground=colors['white'],
                       borderwidth=1,
                       bordercolor=colors['medium_gray'])
        
        style.configure('Modern.Treeview.Heading',
                       background=colors['primary_blue'],
                       foreground='white',
                       font=('Segoe UI', 9, 'bold'))
        
        # Estil de la barra de progrés
        style.configure('Modern.Horizontal.TProgressbar',
                       background=colors['primary_blue'],
                       troughcolor=colors['light_gray'],
                       borderwidth=0)
        
    def setup_main_interface(self):
        """Configuració de la interfície principal amb modern UI"""
        # Configure the root window
        self.root.configure(bg=self.theme.colors['bg_primary'])
        
        # Apply modern styles to ttk widgets
        self.theme.apply_style()
        
        # Main title frame with modern styling
        self.setup_title_frame()
        
        # File selection frame with modern buttons
        self.setup_file_frame()
        
        # Main content area with cards
        self.setup_content_area()
        
        # Status bar with modern notifications
        self.setup_status_bar()
    
    def setup_title_frame(self):
        """Configuració del frame del títol amb estil modern"""
        title_frame = self.theme.create_card_frame(self.root, has_shadow=True)
        title_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        # Title with modern typography
        title_label = tk.Label(
            title_frame, 
            text="📄 Visor OCR Professional",
            font=self.theme.fonts['heading_large'],
            fg=self.theme.colors['text_primary'],
            bg=self.theme.colors['bg_secondary']
        )
        title_label.pack(pady=20)
        
        # Subtitle
        subtitle_label = tk.Label(
            title_frame,
            text="Processament intel·ligent de documents tècnics amb Google Cloud Document AI",
            font=self.theme.fonts['body_large'],
            fg=self.theme.colors['text_secondary'],
            bg=self.theme.colors['bg_secondary']
        )
        subtitle_label.pack(pady=(0, 10))
    
    def setup_file_frame(self):
        """Configuració del frame de selecció de fitxers amb botons moderns"""
        file_frame = self.theme.create_card_frame(self.root)
        file_frame.pack(fill='x', padx=20, pady=10)
        
        # File info section
        info_frame = tk.Frame(file_frame, bg=self.theme.colors['bg_secondary'])
        info_frame.pack(fill='x', padx=20, pady=20)
        
        self.file_label = tk.Label(
            info_frame, 
            text="📂 Cap fitxer seleccionat",
            font=self.theme.fonts['body_medium'],
            fg=self.theme.colors['text_secondary'],
            bg=self.theme.colors['bg_secondary']
        )
        self.file_label.pack(side='left')
        
        # Modern button container
        button_frame = tk.Frame(info_frame, bg=self.theme.colors['bg_secondary'])
        button_frame.pack(side='right')
        
        # Modern styled buttons
        self.select_button = self.theme.create_modern_button(
            button_frame, 
            text="📁 Seleccionar PDF",
            command=self.open_pdf,
            style='primary'
        )
        self.select_button.pack(side='left', padx=(0, 10))
        
        self.process_button = self.theme.create_modern_button(
            button_frame,
            text="🚀 Processar Document",
            command=self.process_document,
            style='primary',
            state='disabled'
        )
        self.process_button.pack(side='left')
    
    def setup_content_area(self):
        """Configuració de l'àrea de contingut principal amb cards"""
        # Main content frame with modern styling
        content_frame = tk.Frame(self.root, bg=self.theme.colors['bg_primary'])
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create notebook with modern tabs
        self.notebook = self.theme.create_modern_notebook(content_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Setup tabs with modern styling
        self.setup_text_tab()
        self.setup_structured_tab()
        self.setup_validation_tab()
    
    def setup_text_tab(self):
        """Tab de text amb scroll i estil modern"""
        text_frame = self.theme.create_card_frame(self.notebook, padding=0)
        
        # Text area with modern styling
        text_container = tk.Frame(text_frame, bg=self.theme.colors['bg_secondary'])
        text_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Text widget with scrollbar
        self.text_widget = tk.Text(
            text_container,
            wrap=tk.WORD,
            font=self.theme.fonts['code'],
            bg=self.theme.colors['bg_primary'],
            fg=self.theme.colors['text_primary'],
            relief='flat',
            borderwidth=0,
            padx=15,
            pady=15
        )
        
        scrollbar = ttk.Scrollbar(text_container, orient="vertical", command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        
        self.text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.notebook.add(text_frame, text="📝 Text Extret")
    
    def setup_structured_tab(self):
        """Tab de dades estructurades amb treeview modern"""
        structured_frame = self.theme.create_card_frame(self.notebook, padding=0)
        
        # Controls frame
        controls_frame = tk.Frame(structured_frame, bg=self.theme.colors['bg_secondary'])
        controls_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        # Export button with format selector
        self.export_button = self.theme.create_modern_button(
            controls_frame,
            text="📦 Exportar Dades",
            command=self.export_structured_data,
            style='secondary',
            state='disabled'
        )
        self.export_button.pack(side='right')
        
        # Treeview container
        tree_container = tk.Frame(structured_frame, bg=self.theme.colors['bg_secondary'])
        tree_container.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Modern treeview
        self.tree = self.theme.create_modern_treeview(tree_container)
        self.tree.pack(fill='both', expand=True)
        
        self.notebook.add(structured_frame, text="📋 Dades Estructurades")
    
    def setup_validation_tab(self):
        """Tab de validació amb editor modern"""
        validation_frame = self.theme.create_card_frame(self.notebook, padding=0)
        
        # Header frame
        header_frame = tk.Frame(validation_frame, bg=self.theme.colors['bg_secondary'])
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        header_label = tk.Label(
            header_frame,
            text="✅ Validació i Edició de Dades",
            font=self.theme.fonts['heading_medium'],
            fg=self.theme.colors['text_primary'],
            bg=self.theme.colors['bg_secondary']
        )
        header_label.pack(side='left')
        
        # Validation button
        self.validate_button = self.theme.create_modern_button(
            header_frame,
            text="🔍 Obrir Editor",
            command=self.validate_structured_data,
            style='primary',
            state='disabled'
        )
        self.validate_button.pack(side='right')
        
        # Validation status
        self.validation_status_frame = tk.Frame(validation_frame, bg=self.theme.colors['bg_secondary'])
        self.validation_status_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        self.validation_label = tk.Label(
            self.validation_status_frame,
            text="📋 Processa un document primer per accedir a la validació",
            font=self.theme.fonts['body_medium'],
            fg=self.theme.colors['text_secondary'],
            bg=self.theme.colors['bg_secondary'],
            wraplength=800,
            justify='center'
        )
        self.validation_label.pack(expand=True)
        
        self.notebook.add(validation_frame, text="✅ Validació")
    
    def setup_status_bar(self):
        """Barra d'estat amb notificacions modernes"""
        self.status_frame = tk.Frame(self.root, bg=self.theme.colors['bg_secondary'], height=40)
        self.status_frame.pack(fill='x', padx=20, pady=(0, 20))
        self.status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            self.status_frame,
            text="📋 Llest per processar documents",
            font=self.theme.fonts['body_small'],
            fg=self.theme.colors['text_secondary'],
            bg=self.theme.colors['bg_secondary']
        )
        self.status_label.pack(side='left', padx=20, pady=10)
        
        # Progress indicator
        self.progress_var = tk.StringVar(value="")
        self.progress_label = tk.Label(
            self.status_frame,
            textvariable=self.progress_var,
            font=self.theme.fonts['body_small'],
            fg=self.theme.colors['primary_blue'],
            bg=self.theme.colors['bg_secondary']
        )
        self.progress_label.pack(side='right', padx=20, pady=10)
        
    def create_menu(self):
        """Creació del menú de l'aplicació"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu de fitxers
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fitxer", menu=file_menu)
        file_menu.add_command(label="Obrir PDF...", command=self.open_pdf, accelerator="Ctrl+O")

        # Submenú de fitxers recents
        self.recent_files_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Fitxers Recents", menu=self.recent_files_menu)
        self.update_recent_files_menu()

        file_menu.add_command(label="Processar Document", command=self.process_document, accelerator="Ctrl+P")
        file_menu.add_command(label="Processament per Lotes...", command=self.batch_process, accelerator="Ctrl+B")
        file_menu.add_separator()
        file_menu.add_command(label="Exportar Text...", command=self.export_text)
        file_menu.add_command(label="Exportar JSON...", command=self.export_json)
        file_menu.add_command(label="Exportar CSV...", command=self.export_csv)
        file_menu.add_command(label="Exportar PDF Report...", command=self.export_pdf_report)
        file_menu.add_separator()
        file_menu.add_command(label="Sortir", command=self.root.quit)

        # Menu de visualització
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Visualització", menu=view_menu)
        view_menu.add_command(label="Zoom In", command=self.zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="Zoom Out", command=self.zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="Ajustar a la finestra", command=self.fit_to_window, accelerator="Ctrl+0")
        view_menu.add_separator()
        view_menu.add_command(label="Activar mapa de calor de confiança", command=self.toggle_heatmap, accelerator="Ctrl+H")
        view_menu.add_command(label="Mostrar ordre de lectura", command=self.show_reading_order, accelerator="Ctrl+R")

        # Menu d'eines
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Eines", menu=tools_menu)
        tools_menu.add_command(label="Verificar Autenticació Google Cloud", command=self.check_google_auth)
        tools_menu.add_separator()
        tools_menu.add_command(label="Processar Dades Estructurades", command=self.process_structured_data)
        tools_menu.add_command(label="Validar i Editar Dades Estructurades", command=self.validate_structured_data)
        tools_menu.add_command(label="Exportar Dades Estructurades...", command=self.export_structured_data)
        tools_menu.add_separator()
        tools_menu.add_command(label="Detecció d'idioma", command=self.detect_language)
        tools_menu.add_command(label="Extracció de taules", command=self.extract_tables)
        tools_menu.add_command(label="Estadístiques de Text", command=self.show_detailed_stats)

        # Menu d'ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Dreceres de teclat", command=self.show_shortcuts)
        help_menu.add_command(label="Quant a", command=self.show_about)
        
        # Dreceres de teclat
        self.root.bind('<Control-o>', lambda e: self.open_pdf())
        self.root.bind('<Control-p>', lambda e: self.process_document())
        self.root.bind('<Control-b>', lambda e: self.batch_process())
        self.root.bind('<Control-plus>', lambda e: self.zoom_in())
        self.root.bind('<Control-minus>', lambda e: self.zoom_out())
        self.root.bind('<Control-0>', lambda e: self.fit_to_window())
        self.root.bind('<Control-h>', lambda e: self.toggle_heatmap())
        self.root.bind('<Control-r>', lambda e: self.show_reading_order())
        self.root.bind('<F1>', lambda e: self.show_shortcuts())
        
    def create_toolbar(self):
        """Creació de la barra d'eines principal amb estil modern"""
        # Barra d'eines principal 
        toolbar_frame = ttk.Frame(self.root)
        toolbar_frame.pack(fill=tk.X, padx=8, pady=(8, 4))
        
        # Secció de botons de la barra d'eines
        left_frame = ttk.Frame(toolbar_frame)
        left_frame.pack(side=tk.LEFT, padx=8, pady=8)

        ttk.Button(left_frame, text="📁 Obrir PDF", command=self.open_pdf,
                  style='Modern.TButton').pack(side=tk.LEFT, padx=(0, 8))

        ttk.Button(left_frame, text="🤖 Processar Document", command=self.process_document,
                  style='Modern.TButton').pack(side=tk.LEFT, padx=(0, 8))
        
        ttk.Button(left_frame, text="🏗️ Dades Estructurades", command=self.process_structured_data,
                  style='Modern.TButton').pack(side=tk.LEFT, padx=(0, 8))
        
        ttk.Button(left_frame, text="🔍 Validar Dades", command=self.validate_structured_data,
                  style='Modern.TButton').pack(side=tk.LEFT, padx=(0, 8))
        
        separator1 = ttk.Frame(toolbar_frame, width=2)
        separator1.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=8)

        view_frame = ttk.Frame(toolbar_frame)
        view_frame.pack(side=tk.LEFT, padx=8, pady=8)
        
        ttk.Button(view_frame, text="🔍 Zoom In", command=self.zoom_in,
                  style='Modern.TButton').pack(side=tk.LEFT, padx=(0, 4))
        
        ttk.Button(view_frame, text="🔍 Zoom Out", command=self.zoom_out,
                  style='Modern.TButton').pack(side=tk.LEFT, padx=(0, 4))

        ttk.Button(view_frame, text="📱 Ajustar a la finestra", command=self.fit_to_window,
                  style='Modern.TButton').pack(side=tk.LEFT, padx=(0, 8))
        
        separator2 = ttk.Frame(toolbar_frame, width=2)
        separator2.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=8)

        # Secció d'exportació
        export_frame = ttk.Frame(toolbar_frame)
        export_frame.pack(side=tk.LEFT, padx=8, pady=8)
        
        ttk.Button(export_frame, text="📊 Exportar CSV", command=self.export_csv,
                  style='Export.TButton').pack(side=tk.LEFT, padx=(0, 4))
        
        ttk.Button(export_frame, text="📄 Exportar PDF", command=self.export_pdf_report,
                  style='Export.TButton').pack(side=tk.LEFT, padx=(0, 8))
        
        # Separador per a la navegació de pàgines
        separator3 = ttk.Frame(toolbar_frame, width=2)
        separator3.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=8)

        # Navegació de pàgines amb estil modern
        nav_frame = ttk.Frame(toolbar_frame)
        nav_frame.pack(side=tk.LEFT, padx=8, pady=8)

        ttk.Label(nav_frame, text="Pàgina:", 
                 font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=(0, 4))
        
        self.page_var = tk.StringVar(value="0")
        page_spinbox = ttk.Spinbox(nav_frame, from_=0, to=0, width=6, 
                                  textvariable=self.page_var, command=self.change_page,
                                  font=('Segoe UI', 9))
        page_spinbox.pack(side=tk.LEFT, padx=(0, 4))
        
        self.page_label = ttk.Label(nav_frame, text="of 0",
                                   font=('Segoe UI', 9))
        self.page_label.pack(side=tk.LEFT, padx=(0, 8))
        
        # Separador per a la barra de progrés
        separator4 = ttk.Frame(toolbar_frame, width=2)
        separator4.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=8)
        
        progress_frame = ttk.Frame(toolbar_frame)
        progress_frame.pack(side=tk.LEFT, padx=8, pady=8)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                          length=180, mode='determinate',
                                          style='Modern.Horizontal.TProgressbar')
        self.progress_label = ttk.Label(progress_frame, text="",
                                       font=('Segoe UI', 9))
        
        # Inicialment ocultem la barra de progrés
        self.hide_progress()
        
    def create_pdf_viewer(self, parent):
        """Creació del visualitzador de PDF"""
        pdf_frame = ttk.LabelFrame(parent, text="📄 Visualitzador de PDF", padding=15)
        parent.add(pdf_frame, weight=2)
        
        # Creació del canvas amb scrollbars
        canvas_frame = ttk.Frame(pdf_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.pdf_canvas = tk.Canvas(canvas_frame, bg='white', cursor='hand2',
                                   highlightthickness=0, relief='flat')
        
        # Scrollbars per al canvas
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.pdf_canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.pdf_canvas.xview)
        
        self.pdf_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Scrollbars i canvas
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.pdf_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Draceres d'esdeveniments per a la selecció de blocs de text
        self.pdf_canvas.bind("<Button-1>", self.on_canvas_click)
        self.pdf_canvas.bind("<Motion>", self.on_canvas_motion)
        
    def create_text_panel(self, parent):
        """Creació del panell d'anàlisi de text"""
        text_frame = ttk.LabelFrame(parent, text="📊 Anàlisi de Text", padding=15)
        parent.add(text_frame, weight=1)
        
        # Create notebook for different views
        notebook = ttk.Notebook(text_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Full text tab
        self.create_full_text_tab(notebook)
        
        # Text blocks tab
        self.create_text_blocks_tab(notebook)
        
        # Structured data tab for technical drawings
        self.create_structured_data_tab(notebook)
        
        # Statistics tab
        self.create_statistics_tab(notebook)
        
    def create_full_text_tab(self, notebook):
        """Creació de la pestanya de visualització de text complet"""
        text_tab = ttk.Frame(notebook)
        notebook.add(text_tab, text="📝 Text Complet")
        
        # Search frame with modern styling
        search_frame = ttk.Frame(text_tab)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        search_label = ttk.Label(search_frame, text="🔍 Cerca:", 
                                font=('Segoe UI', 10),
                                foreground='#475569')
        search_label.pack(side=tk.LEFT, padx=(0, 8))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var,
                               font=('Segoe UI', 10))
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        search_entry.bind('<KeyRelease>', self.search_text)
        
        # Text widget with modern styling
        self.full_text_widget = scrolledtext.ScrolledText(text_tab, 
                                                         wrap=tk.WORD, 
                                                         font=('Segoe UI', 10),
                                                         state=tk.DISABLED,
                                                         bg='white',
                                                         fg='#1e293b',
                                                         selectbackground='#dbeafe',
                                                         selectforeground='#1e40af',
                                                         relief='flat',
                                                         borderwidth=1)
        self.full_text_widget.pack(fill=tk.BOTH, expand=True)
        
    def create_text_blocks_tab(self, notebook):
        """Creació de la pestanya de blocs de text"""
        blocks_tab = ttk.Frame(notebook)
        notebook.add(blocks_tab, text="📋 Text Blocs")

        # Treeview for text blocks with modern styling
        columns = ('Pagina', 'Text', 'Confiança')
        self.blocks_tree = ttk.Treeview(blocks_tab, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.blocks_tree.heading('Pagina', text='Pàgina')
        self.blocks_tree.heading('Text', text='Contingut del Text')
        self.blocks_tree.heading('Confiança', text='Confiança %')

        self.blocks_tree.column('Pagina', width=80, anchor='center')
        self.blocks_tree.column('Text', width=300)
        self.blocks_tree.column('Confiança', width=100, anchor='center')

        # Scrollbar for treeview
        tree_scroll = ttk.Scrollbar(blocks_tab, orient=tk.VERTICAL, command=self.blocks_tree.yview)
        self.blocks_tree.configure(yscrollcommand=tree_scroll.set)
        
        # Pack treeview and scrollbar
        self.blocks_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.blocks_tree.bind('<<TreeviewSelect>>', self.on_block_select)
        
    def create_structured_data_tab(self, notebook):
        """Creació de la pestanya de dades estructurades per a plànols tècnics"""
        structured_tab = ttk.Frame(notebook)
        notebook.add(structured_tab, text="🏗️ Dades Estructurades")
        
        # Top frame for controls
        control_frame = ttk.Frame(structured_tab)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Button to process structured data
        ttk.Button(control_frame, text="⚙️ Processar Dades Estructurades", 
                  command=self.process_structured_data,
                  style='Modern.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        # Button to validate and edit structured data
        ttk.Button(control_frame, text="🔍 Validar i Editar Dades", 
                  command=self.validate_structured_data,
                  style='Modern.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        # Export structured data button
        ttk.Button(control_frame, text="📤 Exportar Dades", 
                  command=self.export_structured_data,
                  style='Export.TButton').pack(side=tk.LEFT)
        
        # Sub-notebook for different structured views
        sub_notebook = ttk.Notebook(structured_tab)
        sub_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Parts list tab
        self.create_parts_list_tab(sub_notebook)
        
        # Dimensions tab
        self.create_dimensions_tab(sub_notebook)
        
        # Annotations tab
        self.create_annotations_tab(sub_notebook)
        
        # Block overview tab
        self.create_block_overview_tab(sub_notebook)
        
    def create_parts_list_tab(self, notebook):
        """Creació de la pestanya de llista de peces"""
        parts_tab = ttk.Frame(notebook)
        notebook.add(parts_tab, text="📋 Llista de Peces")
        
        # Treeview for parts list
        columns = ('Núm. Element', 'Descripció', 'Valor', 'Tolerància', 'Confiança')
        self.parts_tree = ttk.Treeview(parts_tab, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.parts_tree.heading('Núm. Element', text='Núm. Element')
        self.parts_tree.heading('Descripció', text='Descripció')
        self.parts_tree.heading('Valor', text='Valor')
        self.parts_tree.heading('Tolerància', text='Tolerància')
        self.parts_tree.heading('Confiança', text='Confiança %')
        
        self.parts_tree.column('Núm. Element', width=100, anchor='center')
        self.parts_tree.column('Descripció', width=250)
        self.parts_tree.column('Valor', width=100, anchor='center')
        self.parts_tree.column('Tolerància', width=100, anchor='center')
        self.parts_tree.column('Confiança', width=100, anchor='center')
        
        # Scrollbar for parts treeview
        parts_scroll = ttk.Scrollbar(parts_tab, orient=tk.VERTICAL, command=self.parts_tree.yview)
        self.parts_tree.configure(yscrollcommand=parts_scroll.set)
        
        self.parts_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        parts_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_dimensions_tab(self, notebook):
        """Creació de la pestanya de dimensions"""
        dimensions_tab = ttk.Frame(notebook)
        notebook.add(dimensions_tab, text="📏 Dimensions")
        
        # Treeview for dimensions
        columns = ('Núm. Element', 'Descripció', 'Valor', 'Tolerància', 'Confiança')
        self.dimensions_tree = ttk.Treeview(dimensions_tab, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.dimensions_tree.heading('Núm. Element', text='Núm. Element')
        self.dimensions_tree.heading('Descripció', text='Descripció')
        self.dimensions_tree.heading('Valor', text='Valor')
        self.dimensions_tree.heading('Tolerància', text='Tolerància')
        self.dimensions_tree.heading('Confiança', text='Confiança %')
        
        self.dimensions_tree.column('Núm. Element', width=100, anchor='center')
        self.dimensions_tree.column('Descripció', width=250)
        self.dimensions_tree.column('Valor', width=100, anchor='center')
        self.dimensions_tree.column('Tolerància', width=100, anchor='center')
        self.dimensions_tree.column('Confiança', width=100, anchor='center')
        
        # Scrollbar for dimensions treeview
        dimensions_scroll = ttk.Scrollbar(dimensions_tab, orient=tk.VERTICAL, command=self.dimensions_tree.yview)
        self.dimensions_tree.configure(yscrollcommand=dimensions_scroll.set)
        
        self.dimensions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        dimensions_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_annotations_tab(self, notebook):
        """Creació de la pestanya d'anotacions"""
        annotations_tab = ttk.Frame(notebook)
        notebook.add(annotations_tab, text="📝 Anotacions")
        
        # Treeview for annotations
        columns = ('Núm. Element', 'Descripció', 'Valor', 'Tolerància', 'Confiança')
        self.annotations_tree = ttk.Treeview(annotations_tab, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.annotations_tree.heading('Núm. Element', text='Núm. Element')
        self.annotations_tree.heading('Descripció', text='Descripció')
        self.annotations_tree.heading('Valor', text='Valor')
        self.annotations_tree.heading('Tolerància', text='Tolerància')
        self.annotations_tree.heading('Confiança', text='Confiança %')
        
        self.annotations_tree.column('Núm. Element', width=100, anchor='center')
        self.annotations_tree.column('Descripció', width=250)
        self.annotations_tree.column('Valor', width=100, anchor='center')
        self.annotations_tree.column('Tolerància', width=100, anchor='center')
        self.annotations_tree.column('Confiança', width=100, anchor='center')
        
        # Scrollbar for annotations treeview
        annotations_scroll = ttk.Scrollbar(annotations_tab, orient=tk.VERTICAL, command=self.annotations_tree.yview)
        self.annotations_tree.configure(yscrollcommand=annotations_scroll.set)
        
        self.annotations_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        annotations_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
    def create_block_overview_tab(self, notebook):
        """Creació de la pestanya de resum de blocs"""
        overview_tab = ttk.Frame(notebook)
        notebook.add(overview_tab, text="🔍 Resum de Blocs")
        
        # Text widget for block overview
        self.block_overview_text = scrolledtext.ScrolledText(overview_tab,
                                                            wrap=tk.WORD,
                                                            font=('Consolas', 9),
                                                            state=tk.DISABLED,
                                                            bg='white',
                                                            fg='#1e293b',
                                                            selectbackground='#dbeafe',
                                                            selectforeground='#1e40af',
                                                            relief='flat',
                                                            borderwidth=1)
        self.block_overview_text.pack(fill=tk.BOTH, expand=True)
        
    def create_statistics_tab(self, notebook):
        """Create statistics view tab"""
        stats_tab = ttk.Frame(notebook)
        notebook.add(stats_tab, text="📈 Estadístiques")

        self.stats_text = scrolledtext.ScrolledText(stats_tab,
                                                   wrap=tk.WORD,
                                                   font=('Segoe UI', 10),
                                                   state=tk.DISABLED,
                                                   bg='white',
                                                   fg='#1e293b',
                                                   selectbackground='#dbeafe',
                                                   selectforeground='#1e40af',
                                                   relief='flat',
                                                   borderwidth=1)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
    def create_status_bar(self):
        """Create status bar"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=(4, 8))
        
        self.status_bar = ttk.Label(status_frame, text="✅ L'aplicació està llesta", 
                                   font=('Segoe UI', 9),
                                   padding=(12, 8))
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
    def update_status(self, message):
        """Update status bar message"""
        # Add emoji indicators for different message types
        if "error" in message.lower() or "failed" in message.lower():
            status_message = f"❌ {message}"
        elif "success" in message.lower() or "complete" in message.lower():
            status_message = f"✅ {message}"
        elif "processing" in message.lower() or "loading" in message.lower():
            status_message = f"⏳ {message}"
        else:
            status_message = f"ℹ️ {message}"
            
        if hasattr(self, 'status_label'):
            self.status_label.config(text=status_message)
        self.root.update_idletasks()
        
    def open_pdf(self):
        """Open PDF file dialog"""
        file_path = filedialog.askopenfilename(
            title="Selecciona un fitxer PDF",
            filetypes=[("Fitxers PDF", "*.pdf"), ("Tots els fitxers", "*.*")]
        )
        
        if file_path:
            self.load_pdf(file_path)
            
    def load_pdf(self, file_path):
        """Load PDF file"""
        try:
            self.update_status("Carregant PDF...")
            
            if self.pdf_document:
                self.pdf_document.close()
                
            self.pdf_document = fitz.open(file_path)
            self.current_pdf_path = file_path
            self.current_page = 0
            self.text_blocks = []
            
            self.add_recent_file(file_path)
            
            page_count = len(self.pdf_document)
            
            # Update file label
            filename = os.path.basename(file_path)
            self.file_label.config(text=f"📂 {filename} ({page_count} pàgines)")
            
            # Enable process button
            if hasattr(self, 'process_button'):
                self.process_button.config(state='normal')
            
            self.update_status(f"Carregat: {filename} ({page_count} pàgines)")
            
        except Exception as e:
            messagebox.showerror("Error", f"Carregant PDF: {str(e)}")
            self.update_status("Error carregant PDF")

    def display_current_page(self):
        """Display current PDF page"""
        if not self.pdf_document:
            return
            
        try:
            page = self.pdf_document[self.current_page]
            
            # Render page to image
            mat = fitz.Matrix(self.zoom_factor, self.zoom_factor)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("ppm")
            
            # Convert to PIL Image
            pil_image = Image.open(io.BytesIO(img_data))
            
            # Draw text block overlays if available
            if self.text_blocks:
                self.draw_text_overlays(pil_image)
            
            # Convert to PhotoImage for tkinter
            self.pdf_image = ImageTk.PhotoImage(pil_image)
            
            # Update canvas
            self.pdf_canvas.delete("all")
            self.pdf_canvas.create_image(0, 0, anchor=tk.NW, image=self.pdf_image)
            self.pdf_canvas.configure(scrollregion=self.pdf_canvas.bbox("all"))
            
        except Exception as e:
            messagebox.showerror("Error", f"Error mostrant la pàgina: {str(e)}")

    def draw_text_overlays(self, image):
        """Draw text block bounding boxes on image"""
        draw = ImageDraw.Draw(image)
        
        # Get font for reading order numbers
        try:
            from PIL import ImageFont
            font = ImageFont.truetype("arial.ttf", 12)
        except:
            font = None
        
        for i, block in enumerate(self.text_blocks):
            if block.page_num != self.current_page:
                continue
                
            x1, y1, x2, y2 = block.bbox
            
            # Scale coordinates by zoom factor
            x1 *= self.zoom_factor
            y1 *= self.zoom_factor
            x2 *= self.zoom_factor
            y2 *= self.zoom_factor
            
            # Fix coordinate order to ensure x1 <= x2 and y1 <= y2
            x1, x2 = min(x1, x2), max(x1, x2)
            y1, y2 = min(y1, y2), max(y1, y2)
            
            # Ensure minimum size for very small boxes
            if abs(x2 - x1) < 2:
                x2 = x1 + 2
            if abs(y2 - y1) < 2:
                y2 = y1 + 2
            
            # Ensure coordinates are within image bounds
            img_width, img_height = image.size
            x1 = max(0, min(x1, img_width - 1))
            y1 = max(0, min(y1, img_height - 1))
            x2 = max(x1 + 1, min(x2, img_width))
            y2 = max(y1 + 1, min(y2, img_height))
            
            try:
                if self.heatmap_mode:
                    # Heatmap mode: fill boxes with confidence-based colors (modern blue theme)
                    if block.confidence > 0.9:
                        fill_color = (37, 99, 235, 80)  # Modern blue with transparency
                    elif block.confidence > 0.7:
                        fill_color = (59, 130, 246, 80)  # Light blue with transparency
                    else:
                        fill_color = (147, 197, 253, 80)  # Very light blue with transparency
                    
                    # Create a temporary image for transparency
                    overlay = Image.new('RGBA', image.size, (255, 255, 255, 0))
                    overlay_draw = ImageDraw.Draw(overlay)
                    overlay_draw.rectangle([x1, y1, x2, y2], fill=fill_color)
                    
                    # Composite with main image
                    image_rgba = image.convert('RGBA')
                    image_rgba = Image.alpha_composite(image_rgba, overlay)
                    image.paste(image_rgba.convert('RGB'))
                    
                    # Still draw border
                    border_color = "#2563eb" if block.confidence > 0.9 else "#3b82f6" if block.confidence > 0.7 else "#93c5fd"
                    draw.rectangle([x1, y1, x2, y2], outline=border_color, width=2)
                else:
                    # Normal mode: modern blue theme outlines
                    if block.confidence > 0.9:
                        color = "#2563eb"  # Modern blue
                    elif block.confidence > 0.7:
                        color = "#3b82f6"  # Light blue
                    else:
                        color = "#93c5fd"  # Very light blue
                        
                    # Draw rectangle
                    if block == self.selected_block:
                        draw.rectangle([x1, y1, x2, y2], outline="#1d4ed8", width=3)  # Accent blue for selection
                    else:
                        draw.rectangle([x1, y1, x2, y2], outline=color, width=2)
                
                # Reading order mode: add numbers
                if self.show_reading_order_mode:
                    # Calculate reading order based on top-to-bottom, left-to-right
                    page_blocks = [b for b in self.text_blocks if b.page_num == self.current_page]
                    page_blocks.sort(key=lambda b: (b.bbox[1], b.bbox[0]))  # Sort by Y then X
                    
                    if block in page_blocks:
                        order_num = page_blocks.index(block) + 1
                        
                        # Draw background circle for number (modern blue theme)
                        center_x = x1 + 15
                        center_y = y1 + 15
                        draw.ellipse([center_x-12, center_y-12, center_x+12, center_y+12], 
                                   fill="#ffffff", outline="#2563eb", width=2)
                        
                        # Draw number
                        if font:
                            bbox = draw.textbbox((0, 0), str(order_num), font=font)
                            text_width = bbox[2] - bbox[0]
                            text_height = bbox[3] - bbox[1]
                        else:
                            text_width, text_height = 8, 12  # Estimate
                        
                        text_x = center_x - text_width // 2
                        text_y = center_y - text_height // 2
                        
                        draw.text((text_x, text_y), str(order_num), fill="#2563eb", font=font)
                        
            except Exception as e:
                print(f"Avís: No s'ha pogut dibuixar la caixa delimitadora pel bloc {i}: {e}")
                # Skip this block if drawing fails
                continue
                
    def process_document(self):
        """Process document with Google Cloud Document AI"""
        if not self.current_pdf_path:
            messagebox.showwarning("Avís", "Si us plau, obre primer un fitxer PDF")
            return
            
        # Run processing in separate thread to avoid UI freeze
        threading.Thread(target=self._process_document_thread, daemon=True).start()
        
    def _process_document_thread(self):
        """Process document in background thread"""
        try:
            # Check credentials before starting
            if 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
                self._setup_google_credentials()
            
            self.root.after(0, lambda: self.show_progress("Connexió a Google Cloud..."))
            self.root.after(0, lambda: self.update_progress(10))
            
            # Set up Document AI client
            opts = ClientOptions(api_endpoint=f"{self.location}-documentai.googleapis.com")
            client = documentai.DocumentProcessorServiceClient(client_options=opts)

            self.root.after(0, lambda: self.update_progress(20, "Llegint fitxer PDF..."))

            # Read file
            with open(self.current_pdf_path, "rb") as pdf_file:
                content = pdf_file.read()

            self.root.after(0, lambda: self.update_progress(30, "Preparant sol·licitud..."))
                
            # Create request
            raw_document = documentai.RawDocument(content=content, mime_type="application/pdf")
            name = f"projects/{self.project_id}/locations/{self.location}/processors/{self.processor_id}"
            request = documentai.ProcessRequest(name=name, raw_document=raw_document)
            
            # Process document
            self.root.after(0, lambda: self.update_progress(50, "Processant amb Document AI..."))
            result = client.process_document(request=request)
            document = result.document

            self.root.after(0, lambda: self.update_progress(80, "Extracció de blocs de text..."))

            # Extract text blocks with error handling
            try:
                self._extract_text_blocks(document)
                self.root.after(0, lambda: self.update_progress(90, "Finalitzant..."))
            except Exception as extract_error:
                print(f"Error extraient blocs de text: {extract_error}")
                # Fallback: extract basic text
                self._extract_basic_text(document)
                self.root.after(0, lambda: self.update_progress(90, "Extracció bàsica completa..."))

            self.root.after(0, lambda: self.update_progress(100, "Completa!"))

            # Update UI on main thread
            self.root.after(0, self._update_ui_after_processing)
            self.root.after(2000, self.hide_progress)  # Hide after 2 seconds
            
        except Exception as e:
            error_msg = f"Error en el processat: {str(e)}"
            print(f"Error complert: {e}")
            
            # Check if it's an authentication error
            if "not found" in str(e).lower() and ".json" in str(e):
                auth_error_msg = ("Error d'autenticació de Google Cloud.\n\n"
                                "Solucions:\n"
                                "1. Executa 'python setup_google_auth.py' per configurar l'autenticació\n"
                                "2. O utilitza: gcloud auth application-default login\n"
                                "3. Assegura't que tens el fitxer de credencials al directori correcte")
                self.root.after(0, lambda: messagebox.showerror("Error d'Autenticació", auth_error_msg))
            else:
                self.root.after(0, lambda: messagebox.showerror("Error en el processat", error_msg))
            
            self.root.after(0, lambda: self.update_status("El processament ha fallat"))
            self.root.after(0, self.hide_progress)
    
    def _extract_basic_text(self, document):
        """Fallback method for basic text extraction"""
        self.text_blocks = []
        
        try:
            # Simple extraction using document text
            full_text = document.text
            if full_text:
                # Split text into chunks for basic visualization
                lines = [line.strip() for line in full_text.split('\n') if line.strip()]
                
                for page_num in range(len(self.pdf_document)):
                    page_height = self.pdf_document[page_num].rect.height
                    page_width = self.pdf_document[page_num].rect.width
                    
                    lines_per_page = max(1, len(lines) // len(self.pdf_document)) if len(self.pdf_document) > 0 else len(lines)
                    start_line = page_num * lines_per_page
                    end_line = min(start_line + lines_per_page, len(lines))
                    
                    for i, line in enumerate(lines[start_line:end_line]):
                        if line:
                            # Create realistic bounding box based on text length
                            line_height = max(15, min(25, page_height // 40))  # Adaptive line height
                            y_pos = (i * line_height * 1.2) + 20  # Some spacing between lines
                            
                            # Estimate width based on character count (rough approximation)
                            char_width = max(6, min(12, page_width // 100))
                            estimated_width = min(len(line) * char_width, page_width - 40)
                            
                            x1 = 20
                            y1 = y_pos
                            x2 = x1 + estimated_width
                            y2 = y1 + line_height
                            
                            # Ensure coordinates are valid
                            if y2 > page_height - 20:
                                continue  # Skip if would go off page
                            
                            bbox = (x1, y1, x2, y2)
                            
                            text_block = TextBlock(
                                text=line,
                                confidence=1.0,
                                bbox=bbox,
                                page_num=page_num
                            )
                            self.text_blocks.append(text_block)
                            
        except Exception as e:
            print(f"Error en l'extracció bàsica de text: {e}")
            # Create at least one text block with the full text
            if hasattr(document, 'text') and document.text:
                # Safe default bounding box
                page_width = self.pdf_document[0].rect.width if self.pdf_document else 500
                page_height = self.pdf_document[0].rect.height if self.pdf_document else 700
                
                x1, y1 = 20, 20
                x2, y2 = min(400, page_width - 20), min(100, page_height - 20)
                
                text_preview = document.text[:200] + "..." if len(document.text) > 200 else document.text
                text_block = TextBlock(
                    text=text_preview,
                    confidence=1.0,
                    bbox=(x1, y1, x2, y2),
                    page_num=0
                )
                self.text_blocks.append(text_block)
            
    def _extract_text_blocks(self, document):
        """Extract text blocks from Document AI response"""
        self.text_blocks = []
        
        for page_num, page in enumerate(document.pages):
            # Extract text from paragraphs directly
            if hasattr(page, 'paragraphs'):
                for paragraph in page.paragraphs:
                    # Get text content
                    text_content = self._get_text_from_layout(document.text, paragraph.layout)
                    
                    # Get bounding box
                    bbox = self._get_bounding_box(paragraph.layout, page_num)
                    
                    # Get confidence
                    confidence = getattr(paragraph.layout, 'confidence', 1.0)
                    
                    if text_content and text_content.strip():
                        text_block = TextBlock(
                            text=text_content.strip(),
                            confidence=confidence,
                            bbox=bbox,
                            page_num=page_num
                        )
                        self.text_blocks.append(text_block)
            
            # Also extract from blocks if available
            elif hasattr(page, 'blocks'):
                for block in page.blocks:
                    # Get text content from block
                    text_content = self._get_text_from_layout(document.text, block.layout)
                    
                    # Get bounding box
                    bbox = self._get_bounding_box(block.layout, page_num)
                    
                    # Get confidence
                    confidence = getattr(block.layout, 'confidence', 1.0)
                    
                    if text_content and text_content.strip():
                        text_block = TextBlock(
                            text=text_content.strip(),
                            confidence=confidence,
                            bbox=bbox,
                            page_num=page_num
                        )
                        self.text_blocks.append(text_block)
            
            # Fallback: extract from lines
            else:
                if hasattr(page, 'lines'):
                    for line in page.lines:
                        # Get text content
                        text_content = self._get_text_from_layout(document.text, line.layout)
                        
                        # Get bounding box
                        bbox = self._get_bounding_box(line.layout, page_num)
                        
                        # Get confidence
                        confidence = getattr(line.layout, 'confidence', 1.0)
                        
                        if text_content and text_content.strip():
                            text_block = TextBlock(
                                text=text_content.strip(),
                                confidence=confidence,
                                bbox=bbox,
                                page_num=page_num
                            )
                            self.text_blocks.append(text_block)
    
    def _get_text_from_layout(self, document_text, layout):
        """Extract text from layout using text segments"""
        if hasattr(layout, 'text_anchor') and layout.text_anchor:
            text_content = ""
            for segment in layout.text_anchor.text_segments:
                start_index = int(segment.start_index) if hasattr(segment, 'start_index') else 0
                end_index = int(segment.end_index) if hasattr(segment, 'end_index') else len(document_text)
                text_content += document_text[start_index:end_index]
            return text_content
        return ""
    
    def _get_bounding_box(self, layout, page_num):
        """Get bounding box coordinates from layout"""
        try:
            if hasattr(layout, 'bounding_poly') and layout.bounding_poly:
                if hasattr(layout.bounding_poly, 'normalized_vertices') and layout.bounding_poly.normalized_vertices:
                    vertices = layout.bounding_poly.normalized_vertices
                    if len(vertices) >= 4:
                        page_width = self.pdf_document[page_num].rect.width
                        page_height = self.pdf_document[page_num].rect.height
                        
                        # Get all x and y coordinates
                        x_coords = [v.x * page_width for v in vertices if hasattr(v, 'x')]
                        y_coords = [v.y * page_height for v in vertices if hasattr(v, 'y')]
                        
                        if len(x_coords) >= 2 and len(y_coords) >= 2:
                            # Use min/max to ensure proper coordinate order
                            x1 = min(x_coords)
                            x2 = max(x_coords)
                            y1 = min(y_coords)
                            y2 = max(y_coords)
                            
                            # Ensure valid dimensions
                            if x2 <= x1:
                                x2 = x1 + 10
                            if y2 <= y1:
                                y2 = y1 + 10
                                
                            return (x1, y1, x2, y2)
                        
                elif hasattr(layout.bounding_poly, 'vertices') and layout.bounding_poly.vertices:
                    vertices = layout.bounding_poly.vertices
                    if len(vertices) >= 4:
                        # Get all x and y coordinates
                        x_coords = [float(v.x) for v in vertices if hasattr(v, 'x')]
                        y_coords = [float(v.y) for v in vertices if hasattr(v, 'y')]
                        
                        if len(x_coords) >= 2 and len(y_coords) >= 2:
                            # Use min/max to ensure proper coordinate order
                            x1 = min(x_coords)
                            x2 = max(x_coords)
                            y1 = min(y_coords)
                            y2 = max(y_coords)
                            
                            # Ensure valid dimensions
                            if x2 <= x1:
                                x2 = x1 + 10
                            if y2 <= y1:
                                y2 = y1 + 10
                                
                            return (x1, y1, x2, y2)
                            
        except Exception as e:
            print(f"Avís: No s'ha pogut extreure la caixa delimitadora: {e}")
            
        # Return a default valid rectangle
        return (10, 10, 100, 30)
                        
    def _update_ui_after_processing(self):
        """Update UI after document processing is complete"""
        # Update text widget
        full_text = "\n".join([block.text for block in self.text_blocks])
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(1.0, full_text)
        self.text_widget.config(state=tk.DISABLED)
        
        # Enable export and validation buttons
        if hasattr(self, 'export_button'):
            self.export_button.config(state='normal')
        if hasattr(self, 'validate_button'):
            self.validate_button.config(state='normal')
        
        # Process structured data automatically for technical drawings
        self.process_structured_data()
        
        # Update status
        self.update_status(f"Processament complet. S'han trobat {len(self.text_blocks)} blocs de text.")
        
    def process_structured_data(self):
        """Process text blocks into structured technical drawing data"""
        if not self.text_blocks:
            self.update_status("No hi ha blocs de text per processar")
            return
        
        try:
            self.update_status("Processant dades estructurades...")
            
            # Process with post-processor
            self.structured_data = self.post_processor.process_drawing(self.text_blocks)
            
            # Update structured data views
            self._update_structured_data_views()
            
            # Show statistics
            stats = self.structured_data.get('statistics', {})
            total_elements = stats.get('total_elements', 0)
            total_blocks = stats.get('total_blocks', 0)
            
            self.update_status(f"Dades estructurades processades: {total_elements} elements en {total_blocks} blocs lògics")
            
            # Ask user if they want to validate the data
            if total_elements > 0:
                response = messagebox.askyesnocancel(
                    "Validació de Dades",
                    f"S'han detectat {total_elements} elements estructurats.\n\n"
                    "Vols obrir l'editor de validació per revisar i ajustar les dades?\n\n"
                    "• Sí: Obrir editor de validació\n"
                    "• No: Continuar sense validar\n"
                    "• Cancel·lar: No fer res"
                )
                
                if response is True:  # Yes - open validation editor
                    self.root.after(1000, self.validate_structured_data)  # Delay to let UI update
                elif response is False:  # No - continue without validation
                    self.update_status("Processament complet - Dades disponibles per exportar")
                # None (Cancel) - do nothing
            
        except Exception as e:
            error_msg = f"Error processant dades estructurades: {str(e)}"
            print(error_msg)
            messagebox.showerror("Error", error_msg)
            self.update_status("Error en el processament de dades estructurades")
    
    def _update_structured_data_views(self):
        """Update structured data view"""
        if not self.structured_data:
            return
        
        structured = self.structured_data.get('structured_data', {})
        
        # Update main treeview with all data
        self._populate_main_treeview(structured)
    
    def _populate_main_treeview(self, structured_data):
        """Populate the main treeview with structured data"""
        # Clear existing data
        self.tree.delete(*self.tree.get_children())
        
        # Add parts list data
        parts_list = structured_data.get('parts_list', [])
        for i, part in enumerate(parts_list):
            self.tree.insert('', tk.END, iid=f'part_{i}', values=(
                part.get('element_number', ''),
                part.get('description', ''),
                part.get('value', ''),
                part.get('tolerance', '')
            ))
        
        # Add dimensions data
        dimensions = structured_data.get('dimensions', [])
        for i, dimension in enumerate(dimensions):
            self.tree.insert('', tk.END, iid=f'dim_{i}', values=(
                dimension.get('element_number', ''),
                dimension.get('description', ''),
                dimension.get('value', ''),
                dimension.get('tolerance', '')
            ))
        
        # Add annotations data
        annotations = structured_data.get('annotations', [])
        for i, annotation in enumerate(annotations):
            self.tree.insert('', tk.END, iid=f'ann_{i}', values=(
                annotation.get('element_number', ''),
                annotation.get('description', ''),
                annotation.get('value', ''),
                annotation.get('tolerance', '')
            ))
    
    def _update_parts_list_view(self, parts_data):
        """Update parts list treeview"""
        # Clear existing data
        self.parts_tree.delete(*self.parts_tree.get_children())
        
        # Add new data
        for i, part in enumerate(parts_data):
            self.parts_tree.insert('', tk.END, iid=i, values=(
                part.get('element_number', ''),
                part.get('description', ''),
                part.get('value', ''),
                part.get('tolerance', ''),
                f"{part.get('confidence', 0.0):.2f}"
            ))
    
    def _update_dimensions_view(self, dimensions_data):
        """Update dimensions treeview"""
        # Clear existing data
        self.dimensions_tree.delete(*self.dimensions_tree.get_children())
        
        # Add new data
        for i, dimension in enumerate(dimensions_data):
            self.dimensions_tree.insert('', tk.END, iid=i, values=(
                dimension.get('element_number', ''),
                dimension.get('description', ''),
                dimension.get('value', ''),
                dimension.get('tolerance', ''),
                f"{dimension.get('confidence', 0.0):.2f}"
            ))
    
    def _update_annotations_view(self, annotations_data):
        """Update annotations treeview"""
        # Clear existing data
        self.annotations_tree.delete(*self.annotations_tree.get_children())
        
        # Add new data
        for i, annotation in enumerate(annotations_data):
            self.annotations_tree.insert('', tk.END, iid=i, values=(
                annotation.get('element_number', ''),
                annotation.get('description', ''),
                annotation.get('value', ''),
                annotation.get('tolerance', ''),
                f"{annotation.get('confidence', 0.0):.2f}"
            ))
    
    def _update_block_overview(self):
        """Update block overview text"""
        if not self.structured_data:
            return
        
        logical_blocks = self.structured_data.get('logical_blocks', [])
        statistics = self.structured_data.get('statistics', {})
        
        overview_text = "RESUM DE BLOCS LÒGICS\n"
        overview_text += "=" * 50 + "\n\n"
        
        # Statistics
        overview_text += f"Total d'elements detectats: {statistics.get('total_elements', 0)}\n"
        overview_text += f"Total de blocs lògics: {statistics.get('total_blocks', 0)}\n"
        overview_text += f"Elements amb números: {statistics.get('elements_with_numbers', 0)}\n"
        overview_text += f"Elements amb valors: {statistics.get('elements_with_values', 0)}\n"
        overview_text += f"Elements amb toleràncies: {statistics.get('elements_with_tolerances', 0)}\n"
        overview_text += f"Confiança mitjana: {statistics.get('average_confidence', 0.0):.2f}\n\n"
        
        # Block types
        block_types = statistics.get('block_types', {})
        if block_types:
            overview_text += "TIPUS DE BLOCS:\n"
            overview_text += "-" * 20 + "\n"
            for block_type, count in block_types.items():
                overview_text += f"{block_type.replace('_', ' ').title()}: {count}\n"
            overview_text += "\n"
        
        # Individual blocks
        overview_text += "DETALLS DELS BLOCS:\n"
        overview_text += "-" * 20 + "\n\n"
        
        for block in logical_blocks:
            overview_text += f"Bloc ID: {block.block_id}\n"
            overview_text += f"Tipus: {block.block_type}\n"
            overview_text += f"Elements: {len(block.elements)}\n"
            overview_text += f"Confiança: {block.confidence:.2f}\n"
            overview_text += f"Centroide: ({block.centroid[0]:.1f}, {block.centroid[1]:.1f})\n"
            
            # Show element details
            for j, element in enumerate(block.elements):
                overview_text += f"  {j+1}. "
                if element.element_number:
                    overview_text += f"[{element.element_number}] "
                if element.description:
                    overview_text += f"{element.description} "
                if element.value:
                    overview_text += f"= {element.value} "
                if element.tolerance:
                    overview_text += f"± {element.tolerance}"
                overview_text += f" (conf: {element.confidence:.2f})\n"
            
            overview_text += "\n"
        
        # Update text widget
        self.block_overview_text.config(state=tk.NORMAL)
        self.block_overview_text.delete(1.0, tk.END)
        self.block_overview_text.insert(1.0, overview_text)
        self.block_overview_text.config(state=tk.DISABLED)
    
    def export_structured_data(self):
        """Export structured data to various formats"""
        if not self.structured_data:
            messagebox.showwarning("Avís", "No hi ha dades estructurades per exportar. Si us plau, processa primer el document.")
            return
        
        # Ask user for format
        export_window = tk.Toplevel(self.root)
        export_window.title("📤 Exportar Dades")
        export_window.geometry("500x400")
        export_window.configure(bg=self.theme.colors['bg_primary'])
        export_window.transient(self.root)
        export_window.grab_set()
        
        # Title
        title_frame = self.theme.create_card_frame(export_window)
        title_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        title_label = tk.Label(
            title_frame,
            text="📤 Selecciona el Format d'Exportació",
            font=self.theme.fonts['heading_medium'],
            fg=self.theme.colors['text_primary'],
            bg=self.theme.colors['bg_secondary']
        )
        title_label.pack(pady=15)
        
        # Format selection frame
        format_frame = self.theme.create_card_frame(export_window)
        format_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Export options
        export_var = tk.StringVar(value="csv")
        
        formats = [
            ("csv", "📊 CSV (Comma Separated Values)", "Ideal per a Excel i altres aplicacions de full de càlcul"),
            ("txt", "📝 TXT (Text Pla)", "Text simple amb totes les dades extretes"),
            ("pdf", "📄 PDF (Informe)", "Informe professional amb format i estructura"),
            ("json", "⚙️ JSON (Dades Estructurades)", "Format tècnic per a desenvolupadors")
        ]
        
        for value, title, description in formats:
            frame = tk.Frame(format_frame, bg=self.theme.colors['bg_secondary'])
            frame.pack(fill='x', pady=5, padx=10)
            
            rb = tk.Radiobutton(
                frame,
                text=title,
                variable=export_var,
                value=value,
                font=self.theme.fonts['body_medium'],
                bg=self.theme.colors['bg_secondary'],
                fg=self.theme.colors['text_primary'],
                selectcolor=self.theme.colors['primary_blue']
            )
            rb.pack(anchor='w')
            
            desc_label = tk.Label(
                frame,
                text=description,
                font=self.theme.fonts['body_small'],
                fg=self.theme.colors['text_secondary'],
                bg=self.theme.colors['bg_secondary']
            )
            desc_label.pack(anchor='w', padx=20)
        
        # Buttons
        button_frame = tk.Frame(export_window, bg=self.theme.colors['bg_primary'])
        button_frame.pack(fill='x', padx=20, pady=20)
        
        def do_export():
            format_type = export_var.get()
            export_window.destroy()
            self._export_data(format_type)
        
        export_btn = self.theme.create_modern_button(
            button_frame,
            text="📤 Exportar",
            command=do_export,
            style='primary'
        )
        export_btn.pack(side='right', padx=(10, 0))
        
        cancel_btn = self.theme.create_modern_button(
            button_frame,
            text="❌ Cancel·lar",
            command=export_window.destroy,
            style='secondary'
        )
        cancel_btn.pack(side='right')
    
    def _export_data(self, format_type):
        """Export data in the specified format"""
        try:
            if format_type == "csv":
                self._export_to_csv()
            elif format_type == "txt":
                self._export_to_txt()
            elif format_type == "pdf":
                self._export_to_pdf()
            elif format_type == "json":
                self._export_to_json()
            
        except Exception as e:
            messagebox.showerror("Error d'Exportació", f"Error exportant dades: {str(e)}")
    
    def _export_to_csv(self):
        """Export to CSV format"""
        file_path = filedialog.asksaveasfilename(
            title="Guardar com CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            import csv
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(['Tipus', 'Núm Element', 'Descripció', 'Valor', 'Tolerància', 'Confiança'])
                
                if self.structured_data:
                    structured = self.structured_data.get('structured_data', {})
                    
                    # Write parts list
                    for part in structured.get('parts_list', []):
                        writer.writerow([
                            'Peça',
                            part.get('element_number', ''),
                            part.get('description', ''),
                            part.get('value', ''),
                            part.get('tolerance', ''),
                            f"{part.get('confidence', 0.0):.2f}"
                        ])
                    
                    # Write dimensions
                    for dim in structured.get('dimensions', []):
                        writer.writerow([
                            'Dimensió',
                            dim.get('element_number', ''),
                            dim.get('description', ''),
                            dim.get('value', ''),
                            dim.get('tolerance', ''),
                            f"{dim.get('confidence', 0.0):.2f}"
                        ])
                    
                    # Write annotations
                    for ann in structured.get('annotations', []):
                        writer.writerow([
                            'Anotació',
                            ann.get('element_number', ''),
                            ann.get('description', ''),
                            ann.get('value', ''),
                            ann.get('tolerance', ''),
                            f"{ann.get('confidence', 0.0):.2f}"
                        ])
            
            messagebox.showinfo("Exportació Completada", f"Dades exportades correctament a:\n{file_path}")
            self.update_status("Dades exportades a CSV correctament")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error exportant a CSV: {str(e)}")
    
    def _export_to_txt(self):
        """Export to plain text format"""
        file_path = filedialog.asksaveasfilename(
            title="Guardar com TXT",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as txtfile:
                txtfile.write("=== DADES EXTRETES DEL DOCUMENT OCR ===\n\n")
                
                # Write extracted text
                if self.text_blocks:
                    txtfile.write("TEXT EXTRET:\n")
                    txtfile.write("-" * 50 + "\n")
                    full_text = "\n".join([block.text for block in self.text_blocks])
                    txtfile.write(full_text + "\n\n")
                
                # Write structured data
                if self.structured_data:
                    structured = self.structured_data.get('structured_data', {})
                    
                    if structured.get('parts_list'):
                        txtfile.write("LLISTA DE PECES DETECTADES:\n")
                        txtfile.write("-" * 50 + "\n")
                        for part in structured['parts_list']:
                            txtfile.write(f"Element: {part.get('element_number', 'N/A')}\n")
                            txtfile.write(f"Descripció: {part.get('description', 'N/A')}\n")
                            txtfile.write(f"Valor: {part.get('value', 'N/A')}\n")
                            txtfile.write(f"Tolerància: {part.get('tolerance', 'N/A')}\n")
                            txtfile.write(f"Confiança: {part.get('confidence', 0.0):.2f}\n\n")
            
            messagebox.showinfo("Exportació Completada", f"Dades exportades correctament a:\n{file_path}")
            self.update_status("Dades exportades a TXT correctament")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error exportant a TXT: {str(e)}")
    
    def _export_to_pdf(self):
        """Export to PDF report format"""
        file_path = filedialog.asksaveasfilename(
            title="Guardar com PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.lib.units import inch
            
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1  # Center
            )
            story.append(Paragraph("Informe OCR - Plànol Tècnic", title_style))
            story.append(Spacer(1, 20))
            
            # Summary
            if self.structured_data:
                structured = self.structured_data.get('structured_data', {})
                parts_count = len(structured.get('parts_list', []))
                dims_count = len(structured.get('dimensions', []))
                anns_count = len(structured.get('annotations', []))
                
                summary_text = f"""
                <b>Resum de l'Anàlisi:</b><br/>
                • Elements de llista de peces: {parts_count}<br/>
                • Dimensions detectades: {dims_count}<br/>
                • Anotacions trobades: {anns_count}<br/>
                """
                story.append(Paragraph(summary_text, styles['Normal']))
                story.append(Spacer(1, 20))
                
                # Data table
                if parts_count > 0:
                    story.append(Paragraph("Llista de Peces Detectades", styles['Heading2']))
                    
                    table_data = [['Núm Element', 'Descripció', 'Valor', 'Tolerància', 'Confiança']]
                    for part in structured.get('parts_list', []):
                        table_data.append([
                            part.get('element_number', ''),
                            part.get('description', ''),
                            part.get('value', ''),
                            part.get('tolerance', ''),
                            f"{part.get('confidence', 0.0):.2f}"
                        ])
                    
                    table = Table(table_data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 14),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    story.append(table)
            
            doc.build(story)
            
            messagebox.showinfo("Exportació Completada", f"Informe PDF creat correctament a:\n{file_path}")
            self.update_status("Informe PDF generat correctament")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generant PDF: {str(e)}")
    
    def _export_to_json(self):
        """Export to JSON format"""
        file_path = filedialog.asksaveasfilename(
            title="Guardar com JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            export_data = {
                "document_info": {
                    "file_path": self.current_pdf_path,
                    "processed_at": str(tk.datetime.datetime.now()),
                    "total_text_blocks": len(self.text_blocks) if self.text_blocks else 0
                },
                "extracted_text": [block.text for block in self.text_blocks] if self.text_blocks else [],
                "structured_data": self.structured_data if self.structured_data else {}
            }
            
            with open(file_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Exportació Completada", f"Dades JSON exportades correctament a:\n{file_path}")
            self.update_status("Dades exportades a JSON correctament")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error exportant a JSON: {str(e)}")
    
    def load_recent_files(self):
        """Load recent files from settings"""
        try:
            # You could implement persistent storage here (e.g., JSON file)
            return []
        except:
            return []
    
    def save_recent_files(self):
        """Save recent files to settings"""
        try:
            # You could implement persistent storage here (e.g., JSON file)
            pass
        except:
            pass
    
    def add_recent_file(self, file_path):
        """Add file to recent files list"""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:10]  # Keep only 10 recent files
        self.save_recent_files()
        self.update_recent_files_menu()
    
    def update_recent_files_menu(self):
        """Update recent files menu - modern UI doesn't use menu"""
        # In modern UI, we don't have a menu bar, so this is a no-op
        # Recent files functionality could be implemented differently if needed
        pass
    
    def batch_process(self):
        """Process multiple PDF files in batch"""
        file_paths = filedialog.askopenfilenames(
            title="Selecciona fitxers PDF per al processament en lot",
            filetypes=[("Fitxers PDF", "*.pdf")]
        )
        
        if not file_paths:
            return
            
        # Create progress window
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Processament en lot")
        progress_window.geometry("400x150")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        # Progress bar
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_window, variable=progress_var, maximum=len(file_paths))
        progress_bar.pack(pady=20, padx=20, fill=tk.X)

        status_label = ttk.Label(progress_window, text="Iniciant el processament en lot...")
        status_label.pack(pady=10)
        
        def process_batch():
            results = []
            for i, file_path in enumerate(file_paths):
                try:
                    status_label.config(text=f"Processant: {os.path.basename(file_path)}")
                    progress_window.update()
                    
                    # Load and process file
                    self.load_pdf(file_path)
                    self._process_document_thread()
                    
                    # Collect results
                    results.append({
                        'file': file_path,
                        'blocks': len(self.text_blocks),
                        'success': True
                    })
                    
                except Exception as e:
                    results.append({
                        'file': file_path,
                        'error': str(e),
                        'success': False
                    })
                
                progress_var.set(i + 1)
                progress_window.update()
            
            # Show results
            self.show_batch_results(results)
            progress_window.destroy()
        
        # Start processing in thread
        threading.Thread(target=process_batch, daemon=True).start()
    
    def show_batch_results(self, results):
        """Show batch processing results"""
        result_window = tk.Toplevel(self.root)
        result_window.title("Resultats del Processament en Lot")
        result_window.geometry("600x400")
        
        # Results tree
        columns = ('Fitxer', 'Estat', 'Blocs de Text')
        results_tree = ttk.Treeview(result_window, columns=columns, show='headings')
        
        for col in columns:
            results_tree.heading(col, text=col)
            
        results_tree.column('Fitxer', width=300)
        results_tree.column('Estat', width=100)
        results_tree.column('Blocs de Text', width=100)
        
        for result in results:
            filename = os.path.basename(result['file'])
            if result['success']:
                results_tree.insert('', tk.END, values=(filename, 'Èxit', result['blocks']))
            else:
                results_tree.insert('', tk.END, values=(filename, 'Error', 'N/A'))

        results_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Close button
        ttk.Button(result_window, text="Tancar", command=result_window.destroy).pack(pady=10)

    def toggle_heatmap(self):
        """Toggle confidence heatmap view"""
        self.heatmap_mode = not self.heatmap_mode
        self.display_current_page()
        
        mode_text = "enabled" if self.heatmap_mode else "disabled"
        self.update_status(f"Mapa de calor de confiança {mode_text}")
    
    def show_reading_order(self):
        """Show reading order of text blocks"""
        self.show_reading_order_mode = not self.show_reading_order_mode
        self.display_current_page()
        
        mode_text = "enabled" if self.show_reading_order_mode else "disabled"
        self.update_status(f"Reading order display {mode_text}")
    
    def detect_language(self):
        """Detect language of extracted text"""
        if not self.text_blocks:
            messagebox.showwarning("Avís", "No hi ha dades de text disponibles")
            return
        
        # Simple language detection based on character patterns
        full_text = " ".join([block.text for block in self.text_blocks])
        
        # Basic language detection logic (you could integrate a proper library)
        languages = {
            'English': len([c for c in full_text if c.isascii()]) / len(full_text) if full_text else 0,
            'Spanish': full_text.count('ñ') + full_text.count('á') + full_text.count('é'),
            'French': full_text.count('ç') + full_text.count('à') + full_text.count('é'),
        }
        
        detected = max(languages, key=languages.get)
        confidence = languages[detected]
        
        messagebox.showinfo("Language Detection", 
                          f"Detected Language: {detected}\n"
                          f"Confidence: {confidence:.2%}\n\n"
                          f"Total characters analyzed: {len(full_text):,}")
    
    def extract_tables(self):
        """Extracció d'estructures de taula dels blocs de text"""
        if not self.text_blocks:
            messagebox.showwarning("Avís", "No hi ha dades de text disponibles")
            return
        
        # Detecció simple de taules basada en alineació i espaiat
        table_candidates = []
        
        for page_num in range(len(self.pdf_document)):
            page_blocks = [b for b in self.text_blocks if b.page_num == page_num]
            
            # Agrupa blocs per coordenada Y similar (possibles files de taula)
            rows = {}
            for block in page_blocks:
                y_pos = int(block.bbox[1] / 10) * 10  # Arrodonir a la desena més propera
                if y_pos not in rows:
                    rows[y_pos] = []
                rows[y_pos].append(block)
            
            # Troba files amb múltiples blocs alineats (possibles taules)
            for y_pos, row_blocks in rows.items():
                if len(row_blocks) >= 3:  # Almenys 3 columnes
                    # Ordena per posició X
                    row_blocks.sort(key=lambda b: b.bbox[0])
                    table_candidates.append({
                        'page': page_num + 1,
                        'row_y': y_pos,
                        'columns': len(row_blocks),
                        'content': [b.text for b in row_blocks]
                    })
        
        if table_candidates:
            # Mostra els resultats de l'extracció de taules
            result_window = tk.Toplevel(self.root)
            result_window.title("Taules extretes")
            result_window.geometry("800x500")
            
            text_widget = scrolledtext.ScrolledText(result_window, wrap=tk.WORD)
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            text_widget.insert(tk.END, f"S'han trobat {len(table_candidates)} files potencials de taula:\n\n")
            
            for i, table in enumerate(table_candidates):
                text_widget.insert(tk.END, f"Fila de taula {i+1} (Pàgina {table['page']}):\n")
                text_widget.insert(tk.END, " | ".join(table['content']) + "\n\n")
        else:
            messagebox.showinfo("Extracció de taules", "No s'han detectat estructures de taula al document.")
    
    def show_detailed_stats(self):
        """Mostra estadístiques detallades del text"""
        if not self.text_blocks:
            messagebox.showwarning("Avís", "No hi ha dades de text disponibles")
            return
        
        # Calcula estadístiques detallades
        full_text = " ".join([block.text for block in self.text_blocks])
        
        stats = {
            'Total de caràcters': len(full_text),
            'Total de paraules': len(full_text.split()),
            'Total de frases': full_text.count('.') + full_text.count('!') + full_text.count('?'),
            'Total de paràgrafs': len(self.text_blocks),
            'Mitjana de paraules per bloc': len(full_text.split()) / len(self.text_blocks) if self.text_blocks else 0,
            'Paraules més comunes': self.get_word_frequency(full_text),
        }
        
        # Mostra en una nova finestra
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Estadístiques detallades del text")
        stats_window.geometry("500x400")
        
        text_widget = scrolledtext.ScrolledText(stats_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget.insert(tk.END, "ESTADÍSTIQUES DETALLADES DEL TEXT\n")
        text_widget.insert(tk.END, "=" * 30 + "\n\n")
        
        for key, value in stats.items():
            if key == 'Paraules més comunes':
                text_widget.insert(tk.END, f"{key}:\n")
                for word, count in value:
                    text_widget.insert(tk.END, f"  {word}: {count}\n")
                text_widget.insert(tk.END, "\n")
            else:
                text_widget.insert(tk.END, f"{key}: {value:,.2f}\n" if isinstance(value, float) else f"{key}: {value:,}\n")
    
    def get_word_frequency(self, text):
        """Obté les 10 paraules més freqüents"""
        import re
        from collections import Counter
        
        # Neteja i separa el text
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # Filtra paraules comunes
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        return Counter(filtered_words).most_common(10)
    
    def show_shortcuts(self):
        """Show keyboard shortcuts help"""
        shortcuts_window = tk.Toplevel(self.root)
        shortcuts_window.title("Dreceres de teclat")
        shortcuts_window.geometry("400x500")
        shortcuts_window.transient(self.root)
        
        shortcuts_text = """
    DRECERES DE TECLAT

    Operacions de fitxer:
      Ctrl + O        Obre fitxer PDF
      Ctrl + P        Processa document
      Ctrl + B        Processament per lot

    Controls de visualització:
      Ctrl + +        Apropa (zoom in)
      Ctrl + -        Allunya (zoom out)
      Ctrl + 0        Ajusta a la finestra
      Ctrl + H        Activa/desactiva mapa de calor de confiança
      Ctrl + R        Activa/desactiva ordre de lectura

    Navegació:
      Re Pàgina/Av Pàgina    Navega entre pàgines
      Inici/Fi               Primera/Última pàgina
      Fletxes                Desplaça la vista

    Altres:
      F1             Mostra aquesta ajuda
      Ctrl + Q        Surt de l'aplicació
      Escape         Neteja la selecció

    Accions amb el ratolí:
      Clic           Selecciona bloc de text
      Arrossega      Desplaça la vista PDF
      Roda           Apropa/allunya
      Doble clic     Ajusta el bloc a la vista
        """
        
        text_widget = scrolledtext.ScrolledText(shortcuts_window, wrap=tk.WORD, font=('Consolas', 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_widget.insert(tk.END, shortcuts_text)
        text_widget.config(state=tk.DISABLED)
        
        ttk.Button(shortcuts_window, text="Close", command=shortcuts_window.destroy).pack(pady=10)
    
    def show_about(self):
        """Mostra el diàleg Quant a"""
        about_text = """Visor OCR Professional v2.0

    Una aplicació d'escriptori per a Windows per visualitzar 
    els resultats de Google Cloud Document AI amb renderització 
    de PDF i anàlisi interactiva de text.

    Característiques:
    • Visualització de PDF amb zoom i navegació
    • Integració amb Google Cloud Document AI
    • Visualització interactiva de blocs de text
    • Capacitats avançades d'exportació
    • Suport per a processament per lots
    • Anàlisi de confiança i estadístiques

    Desenvolupat amb Python, tkinter i Google Cloud AI

    © 2025 - Projecte de codi obert"""
        
        messagebox.showinfo("About", about_text)
    
    def show_progress(self, text="Processing..."):
        """Show progress in modern UI status bar"""
        if hasattr(self, 'progress_var'):
            self.progress_var.set(f"⏳ {text}")
        self.update_status(text)
        self.root.update_idletasks()
    
    def update_progress(self, value, text=None):
        """Update progress in modern UI"""
        if text and hasattr(self, 'progress_var'):
            self.progress_var.set(f"⏳ {text}")
        if text:
            self.update_status(text)
        self.root.update_idletasks()
    
    def hide_progress(self):
        """Hide progress in modern UI"""
        if hasattr(self, 'progress_var'):
            self.progress_var.set("")
        self.update_status("✅ Llest per processar documents")

    def export_text(self):
        """Export text using structured export system"""
        if not self.text_blocks:
            messagebox.showwarning("Avís", "No hi ha text per exportar. Si us plau, processa primer el document.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Guardar com a text"
        )
        
        if file_path:
            try:
                full_text = "\n".join([block.text for block in self.text_blocks])
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(full_text)
                messagebox.showinfo("Èxit", f"Text exportat correctament a:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error en exportar el text:\n{str(e)}")

    def export_json(self):
        """Export JSON using structured export system"""
        if not self.text_blocks:
            messagebox.showwarning("Avís", "No hi ha dades per exportar. Si us plau, processa primer el document.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Guardar com a JSON"
        )
        
        if file_path:
            try:
                data = {
                    "document_info": {
                        "source_file": self.current_pdf_path,
                        "total_pages": len(set(block.page_num for block in self.text_blocks)) if self.text_blocks else 0,
                        "total_blocks": len(self.text_blocks),
                        "extraction_date": str(datetime.now())
                    },
                    "text_blocks": [
                        {
                            "text": block.text,
                            "confidence": block.confidence,
                            "bbox": block.bbox,
                            "page_num": block.page_num
                        }
                        for block in self.text_blocks
                    ]
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Èxit", f"Dades JSON exportades correctament a:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error en exportar JSON:\n{str(e)}")

    def export_csv(self):
        """Export CSV using structured export system"""
        if not self.text_blocks:
            messagebox.showwarning("Avís", "No hi ha dades per exportar. Si us plau, processa primer el document.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Guardar com a CSV"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Pàgina', 'Text', 'Confiança', 'X1', 'Y1', 'X2', 'Y2'])
                    
                    for block in self.text_blocks:
                        writer.writerow([
                            block.page_num,
                            block.text.replace('\n', ' '),
                            f"{block.confidence:.3f}",
                            block.bbox[0],
                            block.bbox[1],
                            block.bbox[2],
                            block.bbox[3]
                        ])
                
                messagebox.showinfo("Èxit", f"Dades CSV exportades correctament a:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error en exportar CSV:\n{str(e)}")

    def export_pdf_report(self):
        """Export PDF report using structured export system"""
        if not self.text_blocks:
            messagebox.showwarning("Avís", "No hi ha dades per exportar. Si us plau, processa primer el document.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            title="Guardar informe PDF"
        )
        
        if file_path:
            try:
                # Use the existing PDF export functionality
                self._export_to_pdf_file(file_path)
                messagebox.showinfo("Èxit", f"Informe PDF exportat correctament a:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error en exportar informe PDF:\n{str(e)}")

    def _export_to_pdf_file(self, file_path):
        """Helper method to export PDF report"""
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
        )
        story.append(Paragraph("📄 Informe d'Anàlisi OCR", title_style))
        story.append(Spacer(1, 12))
        
        # Document info
        if self.current_pdf_path:
            story.append(Paragraph(f"<b>Document:</b> {os.path.basename(self.current_pdf_path)}", styles['Normal']))
            story.append(Spacer(1, 6))
        
        # Statistics
        total_words = sum(len(block.text.split()) for block in self.text_blocks)
        avg_confidence = sum(block.confidence for block in self.text_blocks) / len(self.text_blocks) if self.text_blocks else 0
        
        story.append(Paragraph(f"<b>Total de blocs:</b> {len(self.text_blocks)}", styles['Normal']))
        story.append(Paragraph(f"<b>Total de paraules:</b> {total_words}", styles['Normal']))
        story.append(Paragraph(f"<b>Confiança mitjana:</b> {avg_confidence:.1%}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Text content
        story.append(Paragraph("Contingut Extret", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        for i, block in enumerate(self.text_blocks[:20]):  # Limit to first 20 blocks
            story.append(Paragraph(f"<b>Bloc {i+1}:</b> {block.text[:200]}{'...' if len(block.text) > 200 else ''}", styles['Normal']))
            story.append(Spacer(1, 6))
        
        doc.build(story)

    def validate_structured_data(self):
        """Open data validation editor"""
        if not self.structured_data:
            messagebox.showwarning("Avís", "No hi ha dades estructurades per validar. Si us plau, processa primer el document.")
            return
        
        try:
            from data_validation_editor import DataValidationEditor
            editor = DataValidationEditor(self.root, self.structured_data)
            # Wait for the editor to complete
            self.root.wait_window(editor.window)
            # Update our data with the validated results
            if editor.validated_data:
                self.structured_data = editor.validated_data
                self.update_treeview()
                messagebox.showinfo("Èxit", "Dades validades i actualitzades correctament!")
        except ImportError:
            messagebox.showerror("Error", "El mòdul de validació de dades no està disponible.")
        except Exception as e:
            messagebox.showerror("Error", f"Error en obrir l'editor de validació:\n{str(e)}")

    def check_google_auth(self):
        """Check Google Cloud authentication status"""
        try:
            # Try to initialize the client
            client_options = ClientOptions(api_endpoint=f"eu-documentai.googleapis.com")
            client = documentai.DocumentProcessorServiceClient(client_options=client_options)
            
            # Try to list processors to verify auth
            parent = f"projects/{self.project_id}/locations/{self.location}"
            request = documentai.ListProcessorsRequest(parent=parent)
            response = client.list_processors(request=request)
            
            processor_count = len(list(response))
            
            auth_info = f"""✅ Autenticació Google Cloud verificada correctament!

📊 Informació del projecte:
• Project ID: {self.project_id}
• Ubicació: {self.location}
• Processadors disponibles: {processor_count}

🔑 Credencials:
• Fitxer: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'No definit')}

🌐 Endpoint API: eu-documentai.googleapis.com"""
            
            messagebox.showinfo("Estat d'Autenticació", auth_info)
            
        except Exception as e:
            error_info = f"""❌ Error d'autenticació Google Cloud:

{str(e)}

💡 Possibles solucions:
1. Executar setup_google_auth.py
2. Verificar el fitxer de credencials
3. Comprovar els permisos del projecte
4. Verificar la connexió a Internet"""
            
            messagebox.showerror("Error d'Autenticació", error_info)

def main():
    """Main application entry point"""
    try:
        root = tk.Tk()
        
        # Set window icon and properties
        try:
            root.iconbitmap(default='')  # Use default icon
        except:
            pass  # Ignore if no icon available
            
        # Center window on screen
        root.update_idletasks()
        width = 1400
        height = 900
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Create application
        app = OCRViewerApp(root)
        
        # Handle window close event
        def on_closing():
            try:
                if app.pdf_document:
                    app.pdf_document.close()
            except:
                pass
            root.destroy()
            
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Inicia l'aplicació
        print("✅ Finestra de l'aplicació creada correctament!")
        print("📖 Ara pots obrir fitxers PDF i processar-los amb Document AI")
        
      

        root.mainloop()
    except KeyboardInterrupt:
        print("\n🛑 Aplicació interrompuda per l'usuari")
    except Exception as e:
        print(f"❌ Error en iniciar l'aplicació: {e}")
        messagebox.showerror("Error d'inici", f"No s'ha pogut iniciar l'aplicació:\n{str(e)}")
    finally:
        print("👋 Aplicació tancada")

if __name__ == "__main__":
    main()
