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
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

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
        self.root.title("Visor OCR Professional - Google Cloud Document AI")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f8fafc')  # Blau gris molt clar

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
        
        # Google Cloud configuració
        self.project_id = "natural-bison-465607-b6"
        self.location = "eu"
        self.processor_id = "4369d16f70cb0a26"
        
        self.setup_ui()
        self.setup_styles()
        
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
        
    def setup_ui(self):
        """Creació de la interfície d'usuari principal"""
        # Creació del menú principal
        self.create_menu()

        # Creació de la barra d'eines
        self.create_toolbar()

        # Creació de l'àrea de contingut principal amb finestra dividida
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
        
        # Panel esquerre - Visualització de PDF
        self.create_pdf_viewer(main_paned)

        # Panel dret - Anàlisi de text
        self.create_text_panel(main_paned)
        
        # Barra d'estat
        self.create_status_bar()
        
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
            
        self.status_bar.config(text=status_message)
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
            self.page_var.set("1")
            self.page_label.config(text=f"of {page_count}")
            
            # Update spinbox range
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.Spinbox):
                            child.config(from_=1, to=page_count)
            
            self.display_current_page()
            self.update_status(f"Carregat: {os.path.basename(file_path)} ({page_count} pàgines)")
            
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
        # Update full text
        full_text = "\n".join([block.text for block in self.text_blocks])
        self.full_text_widget.config(state=tk.NORMAL)
        self.full_text_widget.delete(1.0, tk.END)
        self.full_text_widget.insert(1.0, full_text)
        self.full_text_widget.config(state=tk.DISABLED)
        
        # Update text blocks tree
        self.blocks_tree.delete(*self.blocks_tree.get_children())
        for i, block in enumerate(self.text_blocks):
            preview = block.text[:50] + "..." if len(block.text) > 50 else block.text
            confidence_str = f"{block.confidence:.2f}" if block.confidence < 1.0 else "N/A"
            self.blocks_tree.insert('', tk.END, iid=i, values=(
                block.page_num + 1,
                preview,
                confidence_str
            ))
        
        # Update statistics
        self._update_statistics()
        
        # Refresh PDF display with overlays
        self.display_current_page()
        
        self.update_status(f"Processament complet. S'han trobat {len(self.text_blocks)} blocs de text.")
        
    def _update_statistics(self):
        """Update statistics tab"""
        if not self.text_blocks:
            return
            
        total_blocks = len(self.text_blocks)
        total_chars = sum(len(block.text) for block in self.text_blocks)
        total_words = sum(len(block.text.split()) for block in self.text_blocks)
        
        avg_confidence = sum(block.confidence for block in self.text_blocks) / total_blocks
        
        pages_with_text = len(set(block.page_num for block in self.text_blocks))
        
        stats_text = f"""Estadístiques del Document OCR:

    Total de pàgines: {len(self.pdf_document)}
    Pàgines amb text: {pages_with_text}
    Total de blocs de text: {total_blocks}
    Total de caràcters: {total_chars:,}
    Total de paraules: {total_words:,}
    Confiança mitjana: {avg_confidence:.2%}

    Distribució de confiança:
    Alta (>90%): {sum(1 for b in self.text_blocks if b.confidence > 0.9)}
    Mitjana (70-90%): {sum(1 for b in self.text_blocks if 0.7 <= b.confidence <= 0.9)}
    Baixa (<70%): {sum(1 for b in self.text_blocks if b.confidence < 0.7)}

    Fitxer: {os.path.basename(self.current_pdf_path) if self.current_pdf_path else 'N/A'}
    """
        
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)
        self.stats_text.config(state=tk.DISABLED)
        
    def on_block_select(self, event):
        """Handle text block selection"""
        selection = self.blocks_tree.selection()
        if selection:
            block_id = int(selection[0])
            self.selected_block = self.text_blocks[block_id]
            
            # Navigate to block's page if different
            if self.selected_block.page_num != self.current_page:
                self.current_page = self.selected_block.page_num
                self.page_var.set(str(self.current_page + 1))
                
            self.display_current_page()
            
    def on_canvas_click(self, event):
        """Handle canvas click for text block selection"""
        # Convert canvas coordinates to image coordinates
        canvas_x = self.pdf_canvas.canvasx(event.x)
        canvas_y = self.pdf_canvas.canvasy(event.y)
        
        # Find clicked text block
        for i, block in enumerate(self.text_blocks):
            if block.page_num != self.current_page:
                continue
                
            x1, y1, x2, y2 = block.bbox
            x1 *= self.zoom_factor
            y1 *= self.zoom_factor
            x2 *= self.zoom_factor
            y2 *= self.zoom_factor
            
            # Ensure proper coordinate order
            x1, x2 = min(x1, x2), max(x1, x2)
            y1, y2 = min(y1, y2), max(y1, y2)
            
            # Check if click is within bounds
            if x1 <= canvas_x <= x2 and y1 <= canvas_y <= y2:
                self.selected_block = block
                self.display_current_page()
                
                # Select in tree view
                try:
                    for item in self.blocks_tree.get_children():
                        if int(item) < len(self.text_blocks) and self.text_blocks[int(item)] == block:
                            self.blocks_tree.selection_set(item)
                            self.blocks_tree.see(item)
                            break
                except Exception as e:
                    print(f"Avís: No s'ha pogut actualitzar la selecció de l'arbre: {e}")
                break
                
    def on_canvas_motion(self, event):
        """Handle canvas mouse motion for cursor changes"""
        canvas_x = self.pdf_canvas.canvasx(event.x)
        canvas_y = self.pdf_canvas.canvasy(event.y)
        
        # Check if mouse is over a text block
        over_block = False
        for block in self.text_blocks:
            if block.page_num != self.current_page:
                continue
                
            x1, y1, x2, y2 = block.bbox
            x1 *= self.zoom_factor
            y1 *= self.zoom_factor
            x2 *= self.zoom_factor
            y2 *= self.zoom_factor
            
            if x1 <= canvas_x <= x2 and y1 <= canvas_y <= y2:
                over_block = True
                break
                
        # Change cursor
        cursor = "hand2" if over_block else "arrow"
        self.pdf_canvas.config(cursor=cursor)
        
    def change_page(self):
        """Handle page change"""
        try:
            new_page = int(self.page_var.get()) - 1
            if 0 <= new_page < len(self.pdf_document):
                self.current_page = new_page
                self.display_current_page()
        except ValueError:
            pass
            
    def zoom_in(self):
        """Zoom in"""
        self.zoom_factor *= 1.2
        self.display_current_page()
        
    def zoom_out(self):
        """Zoom out"""
        self.zoom_factor /= 1.2
        self.display_current_page()
        
    def fit_to_window(self):
        """Fit page to window"""
        if self.pdf_document:
            page = self.pdf_document[self.current_page]
            canvas_width = self.pdf_canvas.winfo_width()
            canvas_height = self.pdf_canvas.winfo_height()
            
            page_width = page.rect.width
            page_height = page.rect.height
            
            scale_x = canvas_width / page_width
            scale_y = canvas_height / page_height
            
            self.zoom_factor = min(scale_x, scale_y) * 0.9  # 90% of fit
            self.display_current_page()
            
    def search_text(self, event=None):
        """Search text in full text widget"""
        search_term = self.search_var.get().lower()
        if not search_term:
            return
            
        # Clear previous highlights
        self.full_text_widget.tag_remove("highlight", "1.0", tk.END)
        
        if search_term:
            # Find all occurrences
            start = "1.0"
            while True:
                pos = self.full_text_widget.search(search_term, start, tk.END, nocase=True)
                if not pos:
                    break
                    
                end = f"{pos}+{len(search_term)}c"
                self.full_text_widget.tag_add("highlight", pos, end)
                start = end
                
            # Configure highlight tag
            self.full_text_widget.tag_config("highlight", background="yellow")
            
    def export_text(self):
        """Export extracted text to file"""
        if not self.text_blocks:
            messagebox.showwarning("Avís", "No hi ha dades de text per exportar")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Gurdar com a...",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    for block in self.text_blocks:
                        f.write(f"Pagina {block.page_num + 1}: {block.text}\n\n")

                messagebox.showinfo("Èxit", f"Text exportat a {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al exportar text: {str(e)}")
                
    def export_json(self):
        """Export text blocks data as JSON"""
        if not self.text_blocks:
            messagebox.showwarning("Avís", "No hi ha dades de text per exportar")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Gurdar com a...",
            defaultextension=".json",
            filetypes=[("arxius JSON", "*.json"), ("Tots els fitxers", "*.*")]
        )
        
        if file_path:
            try:
                data = {
                    "document": os.path.basename(self.current_pdf_path),
                    "total_pages": len(self.pdf_document),
                    "text_blocks": [
                        {
                            "page": block.page_num + 1,
                            "text": block.text,
                            "confidence": block.confidence,
                            "bbox": block.bbox
                        }
                        for block in self.text_blocks
                    ]
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    
                messagebox.showinfo("Èxit", f"Dades JSON exportades a {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"No s'ha pogut exportar el JSON: {str(e)}")
    
    def export_csv(self):
        """Export text blocks data as CSV"""
        if not self.text_blocks:
            messagebox.showwarning("Avís", "No hi ha dades de text per exportar")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Guarda CSV com a...",
            defaultextension=".csv",
            filetypes=[("arxius CSV", "*.csv"), ("Tots els fitxers", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write header
                    writer.writerow([
                        'Page', 'Text Content', 'Confidence', 
                        'X1', 'Y1', 'X2', 'Y2', 
                        'Width', 'Height', 'Character Count', 'Word Count'
                    ])
                    
                    # Write data rows
                    for block in self.text_blocks:
                        x1, y1, x2, y2 = block.bbox
                        width = abs(x2 - x1)
                        height = abs(y2 - y1)
                        char_count = len(block.text)
                        word_count = len(block.text.split())
                        
                        writer.writerow([
                            block.page_num + 1,
                            block.text.replace('\n', ' ').replace('\r', ' '),  # Clean newlines for CSV
                            f"{block.confidence:.3f}",
                            f"{x1:.2f}",
                            f"{y1:.2f}",
                            f"{x2:.2f}",
                            f"{y2:.2f}",
                            f"{width:.2f}",
                            f"{height:.2f}",
                            char_count,
                            word_count
                        ])
                        
                messagebox.showinfo("Èxit", f"Dades CSV exportades a {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"No s'ha pogut exportar el CSV: {str(e)}")
    
    def export_pdf_report(self):
        """Export comprehensive PDF report with tables and statistics"""
        if not self.text_blocks:
            messagebox.showwarning("Avís", "No hi ha dades de text per exportar")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Guarda el informe PDF com a...",
            defaultextension=".pdf",
            filetypes=[("arxius PDF", "*.pdf"), ("Tots els fitxers", "*.*")]
        )
        
        if file_path:
            try:
                # Create PDF document
                doc = SimpleDocTemplate(file_path, pagesize=A4)
                story = []
                styles = getSampleStyleSheet()
                
                # Custom styles
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=24,
                    spaceAfter=30,
                    textColor=colors.darkblue
                )
                
                heading_style = ParagraphStyle(
                    'CustomHeading',
                    parent=styles['Heading2'],
                    fontSize=16,
                    spaceBefore=20,
                    spaceAfter=10,
                    textColor=colors.darkgreen
                )
                
                # Title
                story.append(Paragraph("OCR Analysis Report", title_style))
                story.append(Spacer(1, 12))
                
                # Document information
                doc_info = [
                    ["Document:", os.path.basename(self.current_pdf_path) if self.current_pdf_path else "N/A"],
                    ["Processing Date:", "2025-01-17"],  # You can make this dynamic
                    ["Total Pages:", str(len(self.pdf_document)) if self.pdf_document else "N/A"],
                    ["Total Text Blocks:", str(len(self.text_blocks))],
                    ["Total Characters:", f"{sum(len(block.text) for block in self.text_blocks):,}"],
                    ["Total Words:", f"{sum(len(block.text.split()) for block in self.text_blocks):,}"]
                ]
                
                info_table = Table(doc_info, colWidths=[2*inch, 3*inch])
                info_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                
                story.append(info_table)
                story.append(Spacer(1, 20))
                
                # Statistics by confidence
                story.append(Paragraph("Estadístiques de confiança", heading_style))

                high_conf = sum(1 for b in self.text_blocks if b.confidence > 0.9)
                med_conf = sum(1 for b in self.text_blocks if 0.7 <= b.confidence <= 0.9)
                low_conf = sum(1 for b in self.text_blocks if b.confidence < 0.7)
                avg_conf = sum(b.confidence for b in self.text_blocks) / len(self.text_blocks) if self.text_blocks else 0
                
                conf_data = [
                    ["Confidence Level", "Count", "Percentage"],
                    ["High (>90%)", str(high_conf), f"{(high_conf/len(self.text_blocks)*100):.1f}%"],
                    ["Medium (70-90%)", str(med_conf), f"{(med_conf/len(self.text_blocks)*100):.1f}%"],
                    ["Low (<70%)", str(low_conf), f"{(low_conf/len(self.text_blocks)*100):.1f}%"],
                    ["Average Confidence", f"{avg_conf:.2%}", ""]
                ]
                
                conf_table = Table(conf_data, colWidths=[2*inch, 1*inch, 1*inch])
                conf_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    # Alternate row colors
                    ('BACKGROUND', (0, 1), (-1, 1), colors.lightgreen),
                    ('BACKGROUND', (0, 3), (-1, 3), colors.lightgreen),
                ]))
                
                story.append(conf_table)
                story.append(Spacer(1, 20))
                
                # Detailed text blocks table
                story.append(Paragraph("Blocs de text detallat", heading_style))
                
                # Prepare data for text blocks table
                table_data = [["Page", "Text Preview", "Confidence", "Position (X,Y)", "Size (W×H)"]]
                
                for block in self.text_blocks[:50]:  # Limit to first 50 blocks to avoid huge PDFs
                    x1, y1, x2, y2 = block.bbox
                    width = abs(x2 - x1)
                    height = abs(y2 - y1)
                    
                    # Truncate text for table
                    text_preview = block.text[:40] + "..." if len(block.text) > 40 else block.text
                    text_preview = text_preview.replace('\n', ' ')
                    
                    table_data.append([
                        str(block.page_num + 1),
                        text_preview,
                        f"{block.confidence:.2f}",
                        f"({x1:.0f},{y1:.0f})",
                        f"{width:.0f}×{height:.0f}"
                    ])
                
                # Create table with appropriate column widths
                blocks_table = Table(table_data, colWidths=[0.6*inch, 2.8*inch, 0.8*inch, 1*inch, 0.8*inch])
                blocks_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (2, 0), (2, -1), 'CENTER'),  # Confidence column
                    ('ALIGN', (3, 0), (3, -1), 'CENTER'),  # Position column
                    ('ALIGN', (4, 0), (4, -1), 'CENTER'),  # Size column
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                
                # Add alternating row colors
                for i in range(1, len(table_data)):
                    if i % 2 == 0:
                        blocks_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, i), (-1, i), colors.lightblue)
                        ]))
                
                story.append(blocks_table)
                
                # Add note if there are more blocks
                if len(self.text_blocks) > 50:
                    story.append(Spacer(1, 12))
                    story.append(Paragraph(
                        f"<i>Nota: Mostrant els primers 50 dels {len(self.text_blocks)} blocs de text totals. "
                        f"Exporta CSV per a dades completes.</i>",
                        styles['Normal']
                    ))
                
                # Summary statistics by page
                if self.pdf_document and len(self.pdf_document) > 1:
                    story.append(Spacer(1, 20))
                    story.append(Paragraph("Estadístiques per pàgina", heading_style))

                    page_stats = []
                    page_stats.append(["Page", "Text Blocks", "Characters", "Words", "Avg Confidence"])
                    
                    for page_num in range(len(self.pdf_document)):
                        page_blocks = [b for b in self.text_blocks if b.page_num == page_num]
                        if page_blocks:
                            total_chars = sum(len(b.text) for b in page_blocks)
                            total_words = sum(len(b.text.split()) for b in page_blocks)
                            avg_conf = sum(b.confidence for b in page_blocks) / len(page_blocks)
                            
                            page_stats.append([
                                str(page_num + 1),
                                str(len(page_blocks)),
                                str(total_chars),
                                str(total_words),
                                f"{avg_conf:.2f}"
                            ])
                    
                    page_table = Table(page_stats, colWidths=[1*inch, 1*inch, 1*inch, 1*inch, 1.2*inch])
                    page_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.darkorange),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
                    
                    story.append(page_table)
                
                # Build PDF
                doc.build(story)
                messagebox.showinfo("Èxit", f"Informe PDF exportat a {file_path}")

            except Exception as e:
                messagebox.showerror("Error", f"No s'ha pogut exportar l'informe PDF: {str(e)}")
                print(f"Detalls de l'error d'exportació PDF: {e}")  # Per a depuració
    
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
        """Update recent files menu"""
        self.recent_files_menu.delete(0, tk.END)
        
        if not self.recent_files:
            self.recent_files_menu.add_command(label="(No hi ha fitxers recents)", state=tk.DISABLED)
        else:
            for i, file_path in enumerate(self.recent_files):
                filename = os.path.basename(file_path)
                self.recent_files_menu.add_command(
                    label=f"{i+1}. {filename}",
                    command=lambda fp=file_path: self.load_pdf(fp)
                )
    
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
        """Show progress bar with text"""
        self.progress_bar.pack(side=tk.TOP, pady=(4, 0))
        self.progress_label.config(text=text)
        self.progress_label.pack(side=tk.TOP, pady=(2, 0))
        self.progress_var.set(0)
        self.root.update_idletasks()
    
    def update_progress(self, value, text=None):
        """Update progress bar value and optionally text"""
        self.progress_var.set(value)
        if text:
            self.progress_label.config(text=text)
        self.root.update_idletasks()
    
    def hide_progress(self):
        """Hide progress bar"""
        self.progress_bar.pack_forget()
        self.progress_label.pack_forget()

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
