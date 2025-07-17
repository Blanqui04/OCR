"""
Professional OCR Viewer Application
A Windows desktop app for visualizing Google Cloud Document AI results
with PDF rendering and text bounding boxes overlay.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import tkinter.font as tkFont
from PIL import Image, ImageTk, ImageDraw
import fitz  # PyMuPDF for PDF rendering
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

# Suppress Google Cloud authentication warnings
warnings.filterwarnings("ignore", message="Your application has authenticated using end user credentials")

@dataclass
class TextBlock:
    """Represents a text block with its content and bounding box"""
    text: str
    confidence: float
    bbox: tuple  # (x1, y1, x2, y2)
    page_num: int

class OCRViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Professional OCR Viewer - Google Cloud Document AI")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # Application state
        self.current_pdf_path = None
        self.pdf_document = None
        self.text_blocks = []
        self.current_page = 0
        self.zoom_factor = 1.0
        self.selected_block = None
        
        # Google Cloud settings
        self.project_id = "natural-bison-465607-b6"
        self.location = "eu"
        self.processor_id = "4369d16f70cb0a26"
        
        self.setup_ui()
        self.setup_styles()
        
    def setup_styles(self):
        """Configure modern UI styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure button styles
        style.configure('Modern.TButton', 
                       padding=10, 
                       font=('Segoe UI', 9))
        
        style.configure('Header.TLabel', 
                       font=('Segoe UI', 12, 'bold'),
                       background='#f0f0f0')
        
    def setup_ui(self):
        """Create the main user interface"""
        # Create main menu
        self.create_menu()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create main content area with paned window
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel - PDF viewer
        self.create_pdf_viewer(main_paned)
        
        # Right panel - Text analysis
        self.create_text_panel(main_paned)
        
        # Status bar
        self.create_status_bar()
        
    def create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open PDF...", command=self.open_pdf, accelerator="Ctrl+O")
        file_menu.add_command(label="Process Document", command=self.process_document, accelerator="Ctrl+P")
        file_menu.add_separator()
        file_menu.add_command(label="Export Text...", command=self.export_text)
        file_menu.add_command(label="Export JSON...", command=self.export_json)
        file_menu.add_command(label="Export CSV...", command=self.export_csv)
        file_menu.add_command(label="Export PDF Report...", command=self.export_pdf_report)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Zoom In", command=self.zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="Zoom Out", command=self.zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="Fit to Window", command=self.fit_to_window, accelerator="Ctrl+0")
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.open_pdf())
        self.root.bind('<Control-p>', lambda e: self.process_document())
        self.root.bind('<Control-plus>', lambda e: self.zoom_in())
        self.root.bind('<Control-minus>', lambda e: self.zoom_out())
        self.root.bind('<Control-0>', lambda e: self.fit_to_window())
        
    def create_toolbar(self):
        """Create application toolbar"""
        toolbar_frame = ttk.Frame(self.root)
        toolbar_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(toolbar_frame, text="Open PDF", command=self.open_pdf, 
                  style='Modern.TButton').pack(side=tk.LEFT, padx=2)
        
        ttk.Button(toolbar_frame, text="Process Document", command=self.process_document,
                  style='Modern.TButton').pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        ttk.Button(toolbar_frame, text="Zoom In", command=self.zoom_in,
                  style='Modern.TButton').pack(side=tk.LEFT, padx=2)
        
        ttk.Button(toolbar_frame, text="Zoom Out", command=self.zoom_out,
                  style='Modern.TButton').pack(side=tk.LEFT, padx=2)
        
        ttk.Button(toolbar_frame, text="Fit Window", command=self.fit_to_window,
                  style='Modern.TButton').pack(side=tk.LEFT, padx=2)
        
        # Export buttons
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        ttk.Button(toolbar_frame, text="Export CSV", command=self.export_csv,
                  style='Modern.TButton').pack(side=tk.LEFT, padx=2)
        
        ttk.Button(toolbar_frame, text="Export PDF", command=self.export_pdf_report,
                  style='Modern.TButton').pack(side=tk.LEFT, padx=2)
        
        # Page navigation
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        ttk.Label(toolbar_frame, text="Page:").pack(side=tk.LEFT, padx=2)
        self.page_var = tk.StringVar(value="0")
        page_spinbox = ttk.Spinbox(toolbar_frame, from_=0, to=0, width=5, 
                                  textvariable=self.page_var, command=self.change_page)
        page_spinbox.pack(side=tk.LEFT, padx=2)
        
        self.page_label = ttk.Label(toolbar_frame, text="of 0")
        self.page_label.pack(side=tk.LEFT, padx=2)
        
    def create_pdf_viewer(self, parent):
        """Create PDF viewer panel"""
        pdf_frame = ttk.LabelFrame(parent, text="PDF Viewer", padding=10)
        parent.add(pdf_frame, weight=2)
        
        # Create canvas with scrollbars
        canvas_frame = ttk.Frame(pdf_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.pdf_canvas = tk.Canvas(canvas_frame, bg='white', cursor='hand2')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.pdf_canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.pdf_canvas.xview)
        
        self.pdf_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars and canvas
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.pdf_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind mouse events for text block selection
        self.pdf_canvas.bind("<Button-1>", self.on_canvas_click)
        self.pdf_canvas.bind("<Motion>", self.on_canvas_motion)
        
    def create_text_panel(self, parent):
        """Create text analysis panel"""
        text_frame = ttk.LabelFrame(parent, text="Text Analysis", padding=10)
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
        """Create full text view tab"""
        text_tab = ttk.Frame(notebook)
        notebook.add(text_tab, text="Full Text")
        
        # Search frame
        search_frame = ttk.Frame(text_tab)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        search_entry.bind('<KeyRelease>', self.search_text)
        
        # Text widget
        self.full_text_widget = scrolledtext.ScrolledText(text_tab, 
                                                         wrap=tk.WORD, 
                                                         font=('Consolas', 10),
                                                         state=tk.DISABLED)
        self.full_text_widget.pack(fill=tk.BOTH, expand=True)
        
    def create_text_blocks_tab(self, notebook):
        """Create text blocks view tab"""
        blocks_tab = ttk.Frame(notebook)
        notebook.add(blocks_tab, text="Text Blocks")
        
        # Treeview for text blocks
        columns = ('Page', 'Text', 'Confidence')
        self.blocks_tree = ttk.Treeview(blocks_tab, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.blocks_tree.heading('Page', text='Page')
        self.blocks_tree.heading('Text', text='Text Content')
        self.blocks_tree.heading('Confidence', text='Confidence')
        
        self.blocks_tree.column('Page', width=60)
        self.blocks_tree.column('Text', width=300)
        self.blocks_tree.column('Confidence', width=80)
        
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
        notebook.add(stats_tab, text="Statistics")
        
        self.stats_text = scrolledtext.ScrolledText(stats_tab, 
                                                   wrap=tk.WORD, 
                                                   font=('Segoe UI', 10),
                                                   state=tk.DISABLED)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def update_status(self, message):
        """Update status bar message"""
        self.status_bar.config(text=message)
        self.root.update_idletasks()
        
    def open_pdf(self):
        """Open PDF file dialog"""
        file_path = filedialog.askopenfilename(
            title="Select PDF file",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if file_path:
            self.load_pdf(file_path)
            
    def load_pdf(self, file_path):
        """Load PDF file"""
        try:
            self.update_status("Loading PDF...")
            
            if self.pdf_document:
                self.pdf_document.close()
                
            self.pdf_document = fitz.open(file_path)
            self.current_pdf_path = file_path
            self.current_page = 0
            self.text_blocks = []
            
            # Update page navigation
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
            self.update_status(f"Loaded: {os.path.basename(file_path)} ({page_count} pages)")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load PDF: {str(e)}")
            self.update_status("Error loading PDF")
            
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
            messagebox.showerror("Error", f"Failed to display page: {str(e)}")
            
    def draw_text_overlays(self, image):
        """Draw text block bounding boxes on image"""
        draw = ImageDraw.Draw(image)
        
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
            
            # Choose color based on confidence
            if block.confidence > 0.9:
                color = "green"
            elif block.confidence > 0.7:
                color = "orange"
            else:
                color = "red"
                
            try:
                # Draw rectangle
                if block == self.selected_block:
                    draw.rectangle([x1, y1, x2, y2], outline="blue", width=3)
                else:
                    draw.rectangle([x1, y1, x2, y2], outline=color, width=2)
            except Exception as e:
                print(f"Warning: Could not draw bounding box for block {i}: {e}")
                # Skip this block if drawing fails
                continue
                
    def process_document(self):
        """Process document with Google Cloud Document AI"""
        if not self.current_pdf_path:
            messagebox.showwarning("Warning", "Please open a PDF file first")
            return
            
        # Run processing in separate thread to avoid UI freeze
        threading.Thread(target=self._process_document_thread, daemon=True).start()
        
    def _process_document_thread(self):
        """Process document in background thread"""
        try:
            self.root.after(0, lambda: self.update_status("Processing document with Google Cloud Document AI..."))
            
            # Set up Document AI client
            opts = ClientOptions(api_endpoint=f"{self.location}-documentai.googleapis.com")
            client = documentai.DocumentProcessorServiceClient(client_options=opts)
            
            # Read file
            with open(self.current_pdf_path, "rb") as pdf_file:
                content = pdf_file.read()
                
            # Create request
            raw_document = documentai.RawDocument(content=content, mime_type="application/pdf")
            name = f"projects/{self.project_id}/locations/{self.location}/processors/{self.processor_id}"
            request = documentai.ProcessRequest(name=name, raw_document=raw_document)
            
            # Process document
            self.root.after(0, lambda: self.update_status("Sending document to Google Cloud for processing..."))
            result = client.process_document(request=request)
            document = result.document
            
            self.root.after(0, lambda: self.update_status("Extracting text blocks from response..."))
            
            # Extract text blocks with error handling
            try:
                self._extract_text_blocks(document)
                self.root.after(0, lambda: self.update_status("Text extraction completed successfully"))
            except Exception as extract_error:
                print(f"Error extracting text blocks: {extract_error}")
                # Fallback: extract basic text
                self._extract_basic_text(document)
                self.root.after(0, lambda: self.update_status("Basic text extraction completed (with limitations)"))
            
            # Update UI on main thread
            self.root.after(0, self._update_ui_after_processing)
            
        except Exception as e:
            error_msg = f"Processing failed: {str(e)}"
            print(f"Full error: {e}")
            self.root.after(0, lambda: messagebox.showerror("Processing Error", error_msg))
            self.root.after(0, lambda: self.update_status("Processing failed"))
    
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
            print(f"Error in basic text extraction: {e}")
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
            print(f"Warning: Could not extract bounding box: {e}")
            
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
        
        self.update_status(f"Processing complete. Found {len(self.text_blocks)} text blocks.")
        
    def _update_statistics(self):
        """Update statistics tab"""
        if not self.text_blocks:
            return
            
        total_blocks = len(self.text_blocks)
        total_chars = sum(len(block.text) for block in self.text_blocks)
        total_words = sum(len(block.text.split()) for block in self.text_blocks)
        
        avg_confidence = sum(block.confidence for block in self.text_blocks) / total_blocks
        
        pages_with_text = len(set(block.page_num for block in self.text_blocks))
        
        stats_text = f"""Document Statistics:
        
Total Pages: {len(self.pdf_document)}
Pages with Text: {pages_with_text}
Total Text Blocks: {total_blocks}
Total Characters: {total_chars:,}
Total Words: {total_words:,}
Average Confidence: {avg_confidence:.2%}

Confidence Distribution:
High (>90%): {sum(1 for b in self.text_blocks if b.confidence > 0.9)}
Medium (70-90%): {sum(1 for b in self.text_blocks if 0.7 <= b.confidence <= 0.9)}
Low (<70%): {sum(1 for b in self.text_blocks if b.confidence < 0.7)}

File: {os.path.basename(self.current_pdf_path) if self.current_pdf_path else 'N/A'}
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
                    print(f"Warning: Could not update tree selection: {e}")
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
            messagebox.showwarning("Warning", "No text data to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save text as...",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    for block in self.text_blocks:
                        f.write(f"Page {block.page_num + 1}: {block.text}\n\n")
                        
                messagebox.showinfo("Success", f"Text exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export text: {str(e)}")
                
    def export_json(self):
        """Export text blocks data as JSON"""
        if not self.text_blocks:
            messagebox.showwarning("Warning", "No text data to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save JSON as...",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
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
                    
                messagebox.showinfo("Success", f"JSON data exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export JSON: {str(e)}")
    
    def export_csv(self):
        """Export text blocks data as CSV"""
        if not self.text_blocks:
            messagebox.showwarning("Warning", "No text data to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save CSV as...",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
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
                        
                messagebox.showinfo("Success", f"CSV data exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export CSV: {str(e)}")
    
    def export_pdf_report(self):
        """Export comprehensive PDF report with tables and statistics"""
        if not self.text_blocks:
            messagebox.showwarning("Warning", "No text data to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save PDF Report as...",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
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
                story.append(Paragraph("Confidence Statistics", heading_style))
                
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
                story.append(Paragraph("Detailed Text Blocks", heading_style))
                
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
                        f"<i>Note: Showing first 50 of {len(self.text_blocks)} total text blocks. "
                        f"Export CSV for complete data.</i>", 
                        styles['Normal']
                    ))
                
                # Summary statistics by page
                if self.pdf_document and len(self.pdf_document) > 1:
                    story.append(Spacer(1, 20))
                    story.append(Paragraph("Statistics by Page", heading_style))
                    
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
                messagebox.showinfo("Success", f"PDF report exported to {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export PDF report: {str(e)}")
                print(f"PDF export error details: {e}")  # For debugging

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
        
        # Start the application
        print("✅ Application window created successfully!")
        print("📖 You can now open PDF files and process them with Document AI")
        root.mainloop()
        
    except KeyboardInterrupt:
        print("\n🛑 Application interrupted by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        messagebox.showerror("Startup Error", f"Failed to start application:\n{str(e)}")
    finally:
        print("👋 Application closed")

if __name__ == "__main__":
    main()
