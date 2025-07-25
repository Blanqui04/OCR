#!/usr/bin/env python3
"""
OCR Viewer Application
Professional OCR visualization tool with Google Cloud Document AI integration
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import json
import logging
from datetime import datetime
from pathlib import Path
import threading
from typing import Dict, List, Optional, Tuple

# Import for PDF handling
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

# Import for image handling
try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

# Import for Google Cloud Document AI
try:
    from google.cloud import documentai
except ImportError:
    documentai = None

# Import for modern UI theme
try:
    from ui_theme import ModernTheme
except ImportError:
    ModernTheme = None

# Import data labeling editor
try:
    from data_labeling_editor import DataLabelingEditor
except ImportError:
    DataLabelingEditor = None

# Import custom modules
try:
    from pdf_handler import PDFHandler
except ImportError:
    PDFHandler = None

try:
    from google_ocr import GoogleCloudOCR
except ImportError:
    GoogleCloudOCR = None

try:
    from data_exporter import DataExporter
except ImportError:
    DataExporter = None

logger = logging.getLogger(__name__)

class OCRViewerApp:
    """Main OCR Viewer Application"""
    
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.setup_variables()
        self.create_ui()
        self.apply_theme()
        
    def setup_window(self):
        """Configure the main window"""
        self.root.title("OCR Viewer - Professional Document Analysis")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (900 // 2)
        self.root.geometry(f"1400x900+{x}+{y}")
        
    def setup_variables(self):
        """Initialize application variables"""
        self.current_pdf_path = None
        self.current_page = 0
        self.total_pages = 0
        self.zoom_level = 1.0
        self.pdf_document = None
        self.ocr_results = None
        self.text_blocks = []
        self.selected_block = None
        
        # Structured data storage for element-value relations
        self.structured_data = {
            'relations': [],  # List of {element: str, value: str, confidence: float}
            'metadata': {
                'created': None,
                'last_modified': None,
                'pdf_file': None,
                'total_relations': 0
            }
        }
        
        # Initialize handlers
        self.pdf_handler = PDFHandler() if PDFHandler else None
        self.google_ocr = GoogleCloudOCR() if GoogleCloudOCR else None
        self.data_exporter = DataExporter() if DataExporter else None
        
        # Google Cloud Document AI client
        self.document_ai_client = None
        self.processor_path = None
        
        # UI state
        self.show_confidence_overlay = tk.BooleanVar(value=True)
        self.show_text_blocks = tk.BooleanVar(value=True)
        self.confidence_threshold = tk.DoubleVar(value=0.7)
        
    def create_ui(self):
        """Create the user interface"""
        self.create_menu()
        self.create_toolbar()
        self.create_main_layout()
        self.create_status_bar()
        
    def create_menu(self):
        """Create the application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open PDF...", command=self.open_pdf, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Export Text...", command=self.export_text)
        file_menu.add_command(label="Export JSON...", command=self.export_json)
        file_menu.add_command(label="Export CSV...", command=self.export_csv)
        file_menu.add_separator()
        
        # Structured Data submenu
        structured_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Structured Data", menu=structured_menu)
        structured_menu.add_command(label="Export JSON...", command=self.export_structured_json)
        structured_menu.add_command(label="Export CSV...", command=self.export_structured_csv)
        structured_menu.add_command(label="Export Excel...", command=self.export_structured_excel)
        
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # OCR menu
        ocr_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="OCR", menu=ocr_menu)
        ocr_menu.add_command(label="Process Current Page", command=self.process_current_page)
        ocr_menu.add_command(label="Process All Pages", command=self.process_all_pages)
        ocr_menu.add_separator()
        ocr_menu.add_command(label="Data Labeling Editor", command=self.open_data_labeling_editor)
        ocr_menu.add_separator()
        ocr_menu.add_command(label="Setup Google Cloud", command=self.setup_google_cloud)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_checkbutton(label="Show Confidence Overlay", variable=self.show_confidence_overlay)
        view_menu.add_checkbutton(label="Show Text Blocks", variable=self.show_text_blocks)
        view_menu.add_separator()
        view_menu.add_command(label="Zoom In", command=self.zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="Zoom Out", command=self.zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="Fit to Window", command=self.fit_to_window, accelerator="Ctrl+0")
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
    def create_toolbar(self):
        """Create the application toolbar"""
        self.toolbar = ttk.Frame(self.root)
        self.toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        
        # File operations
        ttk.Button(self.toolbar, text="Open PDF", command=self.open_pdf).pack(side=tk.LEFT, padx=2)
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        # OCR operations
        ttk.Button(self.toolbar, text="Process Page", command=self.process_current_page).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="Process All", command=self.process_all_pages).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="Edit Data", command=self.open_data_labeling_editor).pack(side=tk.LEFT, padx=2)
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        # Navigation
        ttk.Button(self.toolbar, text="◀", command=self.prev_page).pack(side=tk.LEFT, padx=2)
        self.page_label = ttk.Label(self.toolbar, text="Page 0 of 0")
        self.page_label.pack(side=tk.LEFT, padx=5)
        ttk.Button(self.toolbar, text="▶", command=self.next_page).pack(side=tk.LEFT, padx=2)
        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        # Zoom controls
        ttk.Button(self.toolbar, text="Zoom In", command=self.zoom_in).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="Zoom Out", command=self.zoom_out).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="Fit", command=self.fit_to_window).pack(side=tk.LEFT, padx=2)
        
        # Confidence threshold
        ttk.Label(self.toolbar, text="Confidence:").pack(side=tk.RIGHT, padx=5)
        confidence_scale = ttk.Scale(
            self.toolbar, 
            from_=0.0, 
            to=1.0, 
            variable=self.confidence_threshold,
            orient=tk.HORIZONTAL,
            length=100
        )
        confidence_scale.pack(side=tk.RIGHT, padx=2)
        
    def create_main_layout(self):
        """Create the main application layout"""
        # Create main paned window
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - PDF viewer
        self.create_pdf_viewer()
        
        # Right panel - Analysis tabs
        self.create_analysis_panel()
        
    def create_pdf_viewer(self):
        """Create the PDF viewer panel"""
        # PDF viewer frame
        self.pdf_frame = ttk.LabelFrame(self.main_paned, text="PDF Viewer", padding=5)
        self.main_paned.add(self.pdf_frame, weight=3)
        
        # Canvas for PDF display
        self.canvas_frame = ttk.Frame(self.pdf_frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.pdf_canvas = tk.Canvas(
            self.canvas_frame,
            bg='white',
            scrollregion=(0, 0, 0, 0)
        )
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.pdf_canvas.yview)
        h_scrollbar = ttk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.pdf_canvas.xview)
        
        self.pdf_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars and canvas
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.pdf_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind mouse events
        self.pdf_canvas.bind("<Button-1>", self.on_canvas_click)
        self.pdf_canvas.bind("<Motion>", self.on_canvas_motion)
        self.pdf_canvas.bind("<MouseWheel>", self.on_canvas_scroll)
        
    def create_analysis_panel(self):
        """Create the analysis panel with tabs"""
        # Analysis panel frame
        self.analysis_frame = ttk.LabelFrame(self.main_paned, text="Analysis", padding=5)
        self.main_paned.add(self.analysis_frame, weight=2)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.analysis_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Text tab
        self.create_text_tab()
        
        # Blocks tab
        self.create_blocks_tab()
        
        # Structured Data tab
        self.create_structured_data_tab()
        
        # Statistics tab
        self.create_statistics_tab()
        
        # Settings tab
        self.create_settings_tab()
        
    def create_text_tab(self):
        """Create the extracted text tab"""
        text_frame = ttk.Frame(self.notebook)
        self.notebook.add(text_frame, text="Extracted Text")
        
        # Search frame
        search_frame = ttk.Frame(text_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(search_frame, text="Find", command=self.search_text).pack(side=tk.LEFT)
        
        # Text display
        self.text_display = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            height=20,
            font=("Consolas", 10)
        )
        self.text_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def create_blocks_tab(self):
        """Create the text blocks tab"""
        blocks_frame = ttk.Frame(self.notebook)
        self.notebook.add(blocks_frame, text="Text Blocks")
        
        # Blocks treeview
        columns = ('Block', 'Text', 'Confidence', 'X', 'Y', 'Width', 'Height')
        self.blocks_tree = ttk.Treeview(blocks_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        for col in columns:
            self.blocks_tree.heading(col, text=col)
            if col == 'Text':
                self.blocks_tree.column(col, width=200)
            else:
                self.blocks_tree.column(col, width=80)
        
        # Scrollbar for treeview
        blocks_scrollbar = ttk.Scrollbar(blocks_frame, orient=tk.VERTICAL, command=self.blocks_tree.yview)
        self.blocks_tree.configure(yscrollcommand=blocks_scrollbar.set)
        
        # Pack treeview and scrollbar
        self.blocks_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        blocks_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.blocks_tree.bind('<<TreeviewSelect>>', self.on_block_select)
        
    def create_structured_data_tab(self):
        """Create the structured data tab for element-value relations"""
        structured_frame = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.notebook.add(structured_frame, text="Structured Data")
        
        # Top controls frame
        controls_frame = ttk.Frame(structured_frame, style='Modern.TFrame')
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Load relations from data labeling editor
        ttk.Button(
            controls_frame, 
            text="Refresh Relations", 
            command=self.load_relations_from_editor,
            style='Secondary.TButton'
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(controls_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        # Export buttons
        ttk.Button(
            controls_frame, 
            text="Export JSON", 
            command=self.export_structured_json,
            style='Secondary.TButton'
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            controls_frame, 
            text="Export CSV", 
            command=self.export_structured_csv,
            style='Secondary.TButton'
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            controls_frame, 
            text="Export Excel", 
            command=self.export_structured_excel,
            style='Secondary.TButton'
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(controls_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        # Clear button
        ttk.Button(
            controls_frame, 
            text="Clear All", 
            command=self.clear_structured_data,
            style='Secondary.TButton'
        ).pack(side=tk.LEFT, padx=2)
        
        # Relations count label and auto-sync info
        info_frame = ttk.Frame(controls_frame, style='Modern.TFrame')
        info_frame.pack(side=tk.RIGHT, padx=10)
        
        self.relations_count_label = ttk.Label(
            info_frame, 
            text="Relations: 0",
            style='Info.TLabel'
        )
        self.relations_count_label.pack(side=tk.TOP)
        
        auto_sync_label = ttk.Label(
            info_frame,
            text="⚡ Auto-synced with Data Editor",
            style='Modern.TLabel',
            font=('Segoe UI', 8, 'italic')
        )
        auto_sync_label.pack(side=tk.TOP)
        
        # Relations treeview
        tree_frame = ttk.Frame(structured_frame, style='Modern.TFrame')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create treeview for structured data
        columns = ('Element', 'Value', 'Confidence', 'Source')
        self.structured_tree = ttk.Treeview(
            tree_frame, 
            columns=columns, 
            show='headings',
            style='Modern.Treeview'
        )
        
        # Configure columns
        self.structured_tree.heading('Element', text='Element')
        self.structured_tree.heading('Value', text='Value')
        self.structured_tree.heading('Confidence', text='Confidence')
        self.structured_tree.heading('Source', text='Source')
        
        # Set column widths
        self.structured_tree.column('Element', width=150, minwidth=100)
        self.structured_tree.column('Value', width=200, minwidth=150)
        self.structured_tree.column('Confidence', width=100, minwidth=80)
        self.structured_tree.column('Source', width=120, minwidth=100)
        
        # Scrollbars for structured data treeview
        structured_v_scrollbar = ttk.Scrollbar(
            tree_frame, 
            orient=tk.VERTICAL, 
            command=self.structured_tree.yview
        )
        structured_h_scrollbar = ttk.Scrollbar(
            tree_frame, 
            orient=tk.HORIZONTAL, 
            command=self.structured_tree.xview
        )
        
        self.structured_tree.configure(
            yscrollcommand=structured_v_scrollbar.set,
            xscrollcommand=structured_h_scrollbar.set
        )
        
        # Pack treeview and scrollbars
        self.structured_tree.grid(row=0, column=0, sticky='nsew')
        structured_v_scrollbar.grid(row=0, column=1, sticky='ns')
        structured_h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.structured_tree.bind('<Double-1>', self.on_structured_data_double_click)
        self.structured_tree.bind('<Delete>', self.delete_selected_relation)

    def create_statistics_tab(self):
        """Create the statistics tab"""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="Statistics")
        
        self.stats_display = scrolledtext.ScrolledText(
            stats_frame,
            wrap=tk.WORD,
            height=20,
            font=("Consolas", 10)
        )
        self.stats_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def create_settings_tab(self):
        """Create the settings tab"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Settings")
        
        # Google Cloud settings
        cloud_frame = ttk.LabelFrame(settings_frame, text="Google Cloud Document AI", padding=10)
        cloud_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(cloud_frame, text="Project ID:").grid(row=0, column=0, sticky='w', pady=2)
        self.project_id_var = tk.StringVar()
        ttk.Entry(cloud_frame, textvariable=self.project_id_var, width=40).grid(row=0, column=1, pady=2, padx=5)
        
        ttk.Label(cloud_frame, text="Location:").grid(row=1, column=0, sticky='w', pady=2)
        self.location_var = tk.StringVar(value="eu")
        ttk.Entry(cloud_frame, textvariable=self.location_var, width=40).grid(row=1, column=1, pady=2, padx=5)
        
        ttk.Label(cloud_frame, text="Processor ID:").grid(row=2, column=0, sticky='w', pady=2)
        self.processor_id_var = tk.StringVar()
        ttk.Entry(cloud_frame, textvariable=self.processor_id_var, width=40).grid(row=2, column=1, pady=2, padx=5)
        
        ttk.Button(cloud_frame, text="Test Connection", command=self.test_google_cloud).grid(row=3, column=1, pady=10, sticky='e')
        
        # Display settings
        display_frame = ttk.LabelFrame(settings_frame, text="Display Settings", padding=10)
        display_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Checkbutton(display_frame, text="Show confidence overlay", variable=self.show_confidence_overlay).pack(anchor='w', pady=2)
        ttk.Checkbutton(display_frame, text="Show text blocks", variable=self.show_text_blocks).pack(anchor='w', pady=2)
        
    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(self.status_bar, text="Ready")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.status_bar,
            variable=self.progress_var,
            length=200
        )
        self.progress_bar.pack(side=tk.RIGHT, padx=5, pady=2)
        
    def apply_theme(self):
        """Apply the modern theme to the application"""
        try:
            if ModernTheme:
                theme = ModernTheme()
                theme.apply_theme(self.root)
            else:
                logger.warning("ModernTheme not available")
        except Exception as e:
            logger.warning(f"Could not apply modern theme: {str(e)}")
    
    # PDF Operations
    def open_pdf(self):
        """Open a PDF file"""
        try:
            file_path = filedialog.askopenfilename(
                title="Open PDF File",
                filetypes=[
                    ("PDF files", "*.pdf"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path and self.pdf_handler:
                self.set_status("Opening PDF...")
                
                if self.pdf_handler.open_pdf(file_path):
                    self.current_pdf_path = file_path
                    self.total_pages = self.pdf_handler.get_page_count()
                    self.current_page = 0
                    
                    self.update_page_display()
                    self.render_current_page()
                    self.set_status(f"PDF opened: {Path(file_path).name}")
                    
                    # Clear previous OCR results
                    self.ocr_results = None
                    self.clear_analysis_tabs()
                    
                else:
                    messagebox.showerror("Error", "Failed to open PDF file")
                    self.set_status("Ready")
            elif not self.pdf_handler:
                messagebox.showerror("Error", "PDF handler not available. Please install PyMuPDF.")
                
        except Exception as e:
            logger.error(f"Error opening PDF: {str(e)}")
            messagebox.showerror("Error", f"Failed to open PDF: {str(e)}")
            self.set_status("Ready")
    
    def render_current_page(self):
        """Render the current PDF page"""
        try:
            if not self.pdf_handler or not self.current_pdf_path:
                return
                
            # Render page
            img = self.pdf_handler.render_page(self.current_page, self.zoom_level)
            if img and ImageTk:
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(img)
                
                # Clear canvas
                self.pdf_canvas.delete("all")
                
                # Display image
                self.pdf_canvas.create_image(0, 0, anchor=tk.NW, image=photo)
                self.pdf_canvas.image = photo  # Keep a reference
                
                # Update scroll region
                self.pdf_canvas.configure(scrollregion=self.pdf_canvas.bbox("all"))
                
                # Draw OCR overlays if available
                self.draw_ocr_overlays()
                
        except Exception as e:
            logger.error(f"Error rendering page: {str(e)}")
    
    def draw_ocr_overlays(self):
        """Draw OCR result overlays on the PDF"""
        try:
            if not self.ocr_results or not self.show_text_blocks.get():
                return
                
            blocks = self.ocr_results.get('blocks', [])
            current_page_blocks = [b for b in blocks if b.get('page', 1) == self.current_page + 1]
            
            # Get page size for coordinate conversion
            page_width, page_height = self.pdf_handler.get_page_size(self.current_page)
            if not page_width or not page_height:
                return
                
            # Scale coordinates for current zoom
            scale_factor = self.zoom_level * 72  # 72 DPI base
            
            for block in current_page_blocks:
                confidence = block.get('confidence', 0)
                
                # Skip blocks below confidence threshold
                if confidence < self.confidence_threshold.get():
                    continue
                    
                # Get block coordinates (normalized 0-1)
                x = block.get('x', 0) * page_width * self.zoom_level
                y = block.get('y', 0) * page_height * self.zoom_level
                width = block.get('width', 0) * page_width * self.zoom_level
                height = block.get('height', 0) * page_height * self.zoom_level
                
                # Determine color based on confidence
                if ModernTheme:
                    theme = ModernTheme()
                    color = theme.get_confidence_color(confidence)
                else:
                    if confidence >= 0.9:
                        color = "#10b981"  # Green
                    elif confidence >= 0.7:
                        color = "#f59e0b"  # Orange
                    else:
                        color = "#ef4444"  # Red
                
                # Draw rectangle
                self.pdf_canvas.create_rectangle(
                    x, y, x + width, y + height,
                    outline=color,
                    width=2,
                    fill="",
                    tags="ocr_overlay"
                )
                
        except Exception as e:
            logger.error(f"Error drawing OCR overlays: {str(e)}")
    
    # OCR Operations
    def process_current_page(self):
        """Process the current page with OCR"""
        try:
            if not self.current_pdf_path:
                messagebox.showwarning("Warning", "Please open a PDF file first")
                return
                
            if not self.google_ocr:
                messagebox.showerror("Error", "Google Cloud OCR not available")
                return
                
            self.set_status("Processing page with OCR...")
            self.progress_var.set(0)
            
            # Process in a separate thread to avoid blocking UI
            def process_thread():
                try:
                    result = self.google_ocr.process_document(self.current_pdf_path)
                    
                    # Update UI in main thread
                    self.root.after(0, lambda: self.on_ocr_complete(result))
                    
                except Exception as e:
                    self.root.after(0, lambda: self.on_ocr_error(str(e)))
                    
            thread = threading.Thread(target=process_thread, daemon=True)
            thread.start()
            
        except Exception as e:
            logger.error(f"Error starting OCR processing: {str(e)}")
            self.set_status("Ready")
    
    def process_all_pages(self):
        """Process all pages with OCR"""
        self.process_current_page()  # For now, just process current page
    
    def on_ocr_complete(self, result):
        """Handle OCR completion"""
        try:
            if result:
                self.ocr_results = result
                self.update_analysis_tabs()
                self.render_current_page()  # Redraw with overlays
                self.set_status("OCR processing completed")
            else:
                self.set_status("OCR processing failed")
                messagebox.showerror("Error", "OCR processing failed")
                
            self.progress_var.set(0)
            
        except Exception as e:
            logger.error(f"Error handling OCR completion: {str(e)}")
            
    def on_ocr_error(self, error_msg):
        """Handle OCR error"""
        self.set_status("OCR processing failed")
        messagebox.showerror("OCR Error", f"OCR processing failed:\n{error_msg}")
        self.progress_var.set(0)
    
    # Navigation
    def prev_page(self):
        """Go to previous page"""
        if self.pdf_handler and self.pdf_handler.prev_page():
            self.current_page = self.pdf_handler.get_current_page()
            self.update_page_display()
            self.render_current_page()
    
    def next_page(self):
        """Go to next page"""
        if self.pdf_handler and self.pdf_handler.next_page():
            self.current_page = self.pdf_handler.get_current_page()
            self.update_page_display()
            self.render_current_page()
    
    def update_page_display(self):
        """Update page number display"""
        self.page_label.config(text=f"Page {self.current_page + 1} of {self.total_pages}")
    
    # Zoom Operations
    def zoom_in(self):
        """Zoom in"""
        self.zoom_level = min(self.zoom_level * 1.2, 5.0)
        if self.pdf_handler:
            self.pdf_handler.set_zoom_level(self.zoom_level)
        self.render_current_page()
    
    def zoom_out(self):
        """Zoom out"""
        self.zoom_level = max(self.zoom_level / 1.2, 0.2)
        if self.pdf_handler:
            self.pdf_handler.set_zoom_level(self.zoom_level)
        self.render_current_page()
    
    def fit_to_window(self):
        """Fit page to window"""
        # This would require calculating the optimal zoom level
        self.zoom_level = 1.0
        if self.pdf_handler:
            self.pdf_handler.set_zoom_level(self.zoom_level)
        self.render_current_page()
    
    # Export Operations
    def export_text(self):
        """Export extracted text"""
        if not self.ocr_results:
            messagebox.showwarning("Warning", "No OCR results to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Export Text",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path and self.data_exporter:
            if self.data_exporter.export_text(self.ocr_results, file_path):
                messagebox.showinfo("Success", f"Text exported to:\n{file_path}")
            else:
                messagebox.showerror("Error", "Failed to export text")
    
    def export_json(self):
        """Export OCR results as JSON"""
        if not self.ocr_results:
            messagebox.showwarning("Warning", "No OCR results to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Export JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path and self.data_exporter:
            if self.data_exporter.export_json(self.ocr_results, file_path):
                messagebox.showinfo("Success", f"JSON exported to:\n{file_path}")
            else:
                messagebox.showerror("Error", "Failed to export JSON")
    
    def export_csv(self):
        """Export text blocks as CSV"""
        if not self.ocr_results:
            messagebox.showwarning("Warning", "No OCR results to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Export CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path and self.data_exporter:
            if self.data_exporter.export_csv(self.ocr_results, file_path):
                messagebox.showinfo("Success", f"CSV exported to:\n{file_path}")
            else:
                messagebox.showerror("Error", "Failed to export CSV")
    
    # Analysis Tab Updates
    def update_analysis_tabs(self):
        """Update all analysis tabs with OCR results"""
        try:
            if not self.ocr_results:
                return
                
            self.update_text_tab()
            self.update_blocks_tab()
            self.update_statistics_tab()
            
        except Exception as e:
            logger.error(f"Error updating analysis tabs: {str(e)}")
    
    def update_text_tab(self):
        """Update the text tab with extracted text"""
        try:
            text = self.ocr_results.get('text', '')
            self.text_display.delete(1.0, tk.END)
            self.text_display.insert(1.0, text)
            
        except Exception as e:
            logger.error(f"Error updating text tab: {str(e)}")
    
    def update_blocks_tab(self):
        """Update the blocks tab with text block information"""
        try:
            # Clear existing items
            for item in self.blocks_tree.get_children():
                self.blocks_tree.delete(item)
                
            blocks = self.ocr_results.get('blocks', [])
            for i, block in enumerate(blocks, 1):
                text = block.get('text', '').strip()[:50] + "..." if len(block.get('text', '')) > 50 else block.get('text', '').strip()
                
                self.blocks_tree.insert('', 'end', values=(
                    i,
                    text,
                    f"{block.get('confidence', 0):.3f}",
                    f"{block.get('x', 0):.3f}",
                    f"{block.get('y', 0):.3f}",
                    f"{block.get('width', 0):.3f}",
                    f"{block.get('height', 0):.3f}"
                ))
                
        except Exception as e:
            logger.error(f"Error updating blocks tab: {str(e)}")
    
    def update_statistics_tab(self):
        """Update the statistics tab"""
        try:
            stats_text = self.generate_statistics_text()
            self.stats_display.delete(1.0, tk.END)
            self.stats_display.insert(1.0, stats_text)
            
        except Exception as e:
            logger.error(f"Error updating statistics tab: {str(e)}")
    
    def generate_statistics_text(self) -> str:
        """Generate statistics text"""
        try:
            if not self.ocr_results:
                return "No OCR results available"
                
            stats = self.ocr_results.get('statistics', {})
            blocks = self.ocr_results.get('blocks', [])
            
            text = "OCR ANALYSIS STATISTICS\n"
            text += "=" * 50 + "\n\n"
            
            text += f"Document Information:\n"
            text += f"  Total Pages: {stats.get('page_count', 0)}\n"
            text += f"  Total Text Blocks: {stats.get('total_blocks', 0)}\n"
            text += f"  Average Confidence: {stats.get('avg_confidence', 0):.2%}\n\n"
            
            if blocks:
                confidences = [b.get('confidence', 0) for b in blocks]
                high_conf = sum(1 for c in confidences if c >= 0.9)
                med_conf = sum(1 for c in confidences if 0.7 <= c < 0.9)
                low_conf = sum(1 for c in confidences if c < 0.7)
                
                text += f"Confidence Distribution:\n"
                text += f"  High Confidence (≥90%): {high_conf} blocks ({high_conf/len(blocks)*100:.1f}%)\n"
                text += f"  Medium Confidence (70-90%): {med_conf} blocks ({med_conf/len(blocks)*100:.1f}%)\n"
                text += f"  Low Confidence (<70%): {low_conf} blocks ({low_conf/len(blocks)*100:.1f}%)\n\n"
                
                total_chars = sum(len(b.get('text', '')) for b in blocks)
                total_words = sum(len(b.get('text', '').split()) for b in blocks)
                
                text += f"Text Statistics:\n"
                text += f"  Total Characters: {total_chars:,}\n"
                text += f"  Total Words: {total_words:,}\n"
                text += f"  Average Characters per Block: {total_chars/len(blocks):.1f}\n"
                text += f"  Average Words per Block: {total_words/len(blocks):.1f}\n\n"
            
            languages = stats.get('languages', [])
            if languages:
                text += f"Detected Languages: {', '.join(languages)}\n\n"
                
            return text
            
        except Exception as e:
            logger.error(f"Error generating statistics: {str(e)}")
            return "Error generating statistics"
    
    def clear_analysis_tabs(self):
        """Clear all analysis tabs"""
        try:
            self.text_display.delete(1.0, tk.END)
            
            for item in self.blocks_tree.get_children():
                self.blocks_tree.delete(item)
                
            self.stats_display.delete(1.0, tk.END)
            
        except Exception as e:
            logger.error(f"Error clearing analysis tabs: {str(e)}")
    
    # Settings and Configuration
    def setup_google_cloud(self):
        """Setup Google Cloud configuration"""
        # This would open a configuration dialog
        messagebox.showinfo("Setup", "Please configure Google Cloud settings in the Settings tab")
    
    def test_google_cloud(self):
        """Test Google Cloud connection"""
        try:
            if not self.google_ocr:
                messagebox.showerror("Error", "Google Cloud OCR not available")
                return
                
            # Get values from UI
            project_id = self.project_id_var.get().strip()
            location = self.location_var.get().strip()
            processor_id = self.processor_id_var.get().strip()
            
            if not all([project_id, location, processor_id]):
                messagebox.showwarning("Warning", "Please fill in all Google Cloud settings")
                return
                
            # Update OCR client settings
            self.google_ocr.project_id = project_id
            self.google_ocr.location = location
            self.google_ocr.processor_id = processor_id
            
            # Test connection
            success, message = self.google_ocr.test_connection()
            
            if success:
                messagebox.showinfo("Success", f"Connection successful!\n{message}")
                # Save configuration
                self.google_ocr.save_config()
            else:
                messagebox.showerror("Error", f"Connection failed:\n{message}")
                
        except Exception as e:
            logger.error(f"Error testing Google Cloud connection: {str(e)}")
            messagebox.showerror("Error", f"Connection test failed:\n{str(e)}")
    
    def search_text(self):
        """Search for text in the extracted content"""
        try:
            search_term = self.search_var.get().strip()
            if not search_term:
                return
                
            # Simple text search
            text_widget = self.text_display
            text_widget.tag_remove("search", "1.0", tk.END)
            
            if search_term:
                start = "1.0"
                while True:
                    pos = text_widget.search(search_term, start, tk.END)
                    if not pos:
                        break
                    end = f"{pos}+{len(search_term)}c"
                    text_widget.tag_add("search", pos, end)
                    start = end
                
                # Configure search highlight
                text_widget.tag_config("search", background="yellow")
                
        except Exception as e:
            logger.error(f"Error searching text: {str(e)}")
    
    # Event Handlers
    def on_canvas_click(self, event):
        """Handle canvas click events"""
        # This would handle clicking on text blocks
        pass
    
    def on_canvas_motion(self, event):
        """Handle canvas mouse motion"""
        # This would handle hover effects
        pass
    
    def on_canvas_scroll(self, event):
        """Handle canvas scroll events"""
        # This would handle mouse wheel scrolling
        pass
    
    def on_block_select(self, event):
        """Handle text block selection in the tree"""
        try:
            selection = self.blocks_tree.selection()
            if selection:
                item = self.blocks_tree.item(selection[0])
                # Could highlight the selected block on the PDF
                pass
                
        except Exception as e:
            logger.error(f"Error handling block selection: {str(e)}")
    
    def set_status(self, message: str):
        """Set the status bar message"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
        
    def show_about(self):
        """Show about dialog"""
        about_text = """OCR Viewer - Professional Document Analysis

Version: 2.0
Built with Python and Google Cloud Document AI

Features:
• PDF visualization with high-quality rendering
• Google Cloud Document AI integration
• Interactive text block overlay
• Confidence level visualization
• Export to multiple formats
• Modern, professional interface

© 2025 - Professional OCR Solutions"""
        
        messagebox.showinfo("About OCR Viewer", about_text)
    
    def open_data_labeling_editor(self):
        """Open the data labeling editor with automatic data transfer"""
        try:
            if not self.ocr_results:
                messagebox.showwarning(
                    "No OCR Results", 
                    "Please process a PDF with OCR first before opening the data labeling editor."
                )
                return
                
            if not DataLabelingEditor:
                messagebox.showerror(
                    "Feature Not Available", 
                    "Data labeling editor is not available. Please check the installation."
                )
                return
                
            # Create callback function to automatically update structured data
            def on_data_changed(relations):
                """Callback function to update structured data automatically"""
                try:
                    # Update structured data
                    self.structured_data['relations'] = relations
                    self.structured_data['metadata']['last_modified'] = datetime.now().isoformat()
                    self.structured_data['metadata']['pdf_file'] = self.current_pdf_path
                    self.structured_data['metadata']['total_relations'] = len(relations)
                    
                    if not self.structured_data['metadata']['created']:
                        self.structured_data['metadata']['created'] = datetime.now().isoformat()
                    
                    # Update display immediately
                    self.update_structured_data_display()
                    
                    logger.info(f"Automatically updated structured data with {len(relations)} relations")
                    
                except Exception as e:
                    logger.error(f"Error in data change callback: {str(e)}")
                
            # Open the data labeling editor with callback
            editor = DataLabelingEditor(self.root, self.ocr_results, callback=on_data_changed)
            editor.open_editor()
            
        except Exception as e:
            logger.error(f"Error opening data labeling editor: {str(e)}")
            messagebox.showerror("Error", f"Failed to open data labeling editor:\n{str(e)}")

    # Structured Data Methods
    def load_relations_from_editor(self):
        """Load relations from the data labeling editor (now mostly automatic)"""
        try:
            if not self.structured_data['relations']:
                messagebox.showinfo(
                    "No Relations", 
                    "No relations found. Use the Data Labeling Editor to create element-value connections.\n\nRelations are automatically transferred when you create connections in the editor."
                )
                return
                
            # Refresh the display in case of any sync issues
            self.update_structured_data_display()
            
            messagebox.showinfo(
                "Current Relations", 
                f"Currently showing {len(self.structured_data['relations'])} relations.\n\nNote: Relations are automatically updated when you use the Data Labeling Editor."
            )
                
        except Exception as e:
            logger.error(f"Error refreshing relations: {str(e)}")
            messagebox.showerror("Error", f"Failed to refresh relations:\n{str(e)}")
    
    def update_structured_data_display(self):
        """Update the structured data treeview display"""
        try:
            # Clear existing items
            for item in self.structured_tree.get_children():
                self.structured_tree.delete(item)
            
            # Add relations to treeview
            for i, relation in enumerate(self.structured_data['relations']):
                confidence = relation.get('confidence', 0.0)
                confidence_str = f"{confidence:.2%}" if confidence > 0 else "N/A"
                
                # Determine source
                source = relation.get('source', 'Manual')
                
                self.structured_tree.insert(
                    '',
                    'end',
                    values=(
                        relation.get('element', ''),
                        relation.get('value', ''),
                        confidence_str,
                        source
                    )
                )
            
            # Update count label
            count = len(self.structured_data['relations'])
            self.relations_count_label.config(text=f"Relations: {count}")
            
        except Exception as e:
            logger.error(f"Error updating structured data display: {str(e)}")
    
    def export_structured_json(self):
        """Export structured data to JSON"""
        try:
            if not self.structured_data['relations']:
                messagebox.showwarning("No Data", "No structured data to export.")
                return
                
            file_path = filedialog.asksaveasfilename(
                title="Export Structured Data as JSON",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if file_path:
                export_data = {
                    'metadata': self.structured_data['metadata'],
                    'relations': self.structured_data['relations'],
                    'export_timestamp': datetime.now().isoformat()
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Success", f"Structured data exported to:\n{file_path}")
                
        except Exception as e:
            logger.error(f"Error exporting structured JSON: {str(e)}")
            messagebox.showerror("Error", f"Failed to export JSON:\n{str(e)}")
    
    def export_structured_csv(self):
        """Export structured data to CSV"""
        try:
            if not self.structured_data['relations']:
                messagebox.showwarning("No Data", "No structured data to export.")
                return
                
            file_path = filedialog.asksaveasfilename(
                title="Export Structured Data as CSV",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if file_path and self.data_exporter:
                success = self.data_exporter.export_structured_csv(
                    self.structured_data['relations'], 
                    file_path
                )
                
                if success:
                    messagebox.showinfo("Success", f"Structured data exported to:\n{file_path}")
                else:
                    messagebox.showerror("Error", "Failed to export CSV file.")
                    
        except Exception as e:
            logger.error(f"Error exporting structured CSV: {str(e)}")
            messagebox.showerror("Error", f"Failed to export CSV:\n{str(e)}")
    
    def export_structured_excel(self):
        """Export structured data to Excel"""
        try:
            if not self.structured_data['relations']:
                messagebox.showwarning("No Data", "No structured data to export.")
                return
                
            file_path = filedialog.asksaveasfilename(
                title="Export Structured Data as Excel",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if file_path and self.data_exporter:
                success = self.data_exporter.export_structured_excel(
                    self.structured_data['relations'], 
                    file_path,
                    self.structured_data['metadata']
                )
                
                if success:
                    messagebox.showinfo("Success", f"Structured data exported to:\n{file_path}")
                else:
                    messagebox.showerror("Error", "Failed to export Excel file.")
                    
        except Exception as e:
            logger.error(f"Error exporting structured Excel: {str(e)}")
            messagebox.showerror("Error", f"Failed to export Excel:\n{str(e)}")
    
    def clear_structured_data(self):
        """Clear all structured data"""
        try:
            if not self.structured_data['relations']:
                messagebox.showinfo("No Data", "No structured data to clear.")
                return
                
            result = messagebox.askyesno(
                "Confirm Clear", 
                f"Are you sure you want to clear all {len(self.structured_data['relations'])} relations?\n\nThis action cannot be undone."
            )
            
            if result:
                self.structured_data['relations'] = []
                self.structured_data['metadata']['total_relations'] = 0
                self.structured_data['metadata']['last_modified'] = datetime.now().isoformat()
                self.update_structured_data_display()
                messagebox.showinfo("Success", "All structured data cleared.")
                
        except Exception as e:
            logger.error(f"Error clearing structured data: {str(e)}")
            messagebox.showerror("Error", f"Failed to clear data:\n{str(e)}")
    
    def on_structured_data_double_click(self, event):
        """Handle double-click on structured data item"""
        try:
            selection = self.structured_tree.selection()
            if selection:
                item = self.structured_tree.item(selection[0])
                values = item['values']
                
                # Show detailed information about the relation
                info_text = f"""Element: {values[0]}
Value: {values[1]}
Confidence: {values[2]}
Source: {values[3]}"""
                
                messagebox.showinfo("Relation Details", info_text)
                
        except Exception as e:
            logger.error(f"Error handling structured data double-click: {str(e)}")
    
    def delete_selected_relation(self, event):
        """Delete selected relation from structured data"""
        try:
            selection = self.structured_tree.selection()
            if not selection:
                return
                
            result = messagebox.askyesno(
                "Confirm Delete", 
                "Are you sure you want to delete the selected relation?"
            )
            
            if result:
                # Get the index of the selected item
                item_index = self.structured_tree.index(selection[0])
                
                # Remove from data
                if 0 <= item_index < len(self.structured_data['relations']):
                    del self.structured_data['relations'][item_index]
                    self.structured_data['metadata']['total_relations'] = len(self.structured_data['relations'])
                    self.structured_data['metadata']['last_modified'] = datetime.now().isoformat()
                    
                    # Update display
                    self.update_structured_data_display()
                    
        except Exception as e:
            logger.error(f"Error deleting relation: {str(e)}")
            messagebox.showerror("Error", f"Failed to delete relation:\n{str(e)}")
