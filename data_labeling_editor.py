#!/usr/bin/env python3
"""
Data Labeling Editor for OCR Viewer Application
Interactive interface for connecting element numbers to values
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import re
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DataLabelingEditor:
    """Interactive data labeling editor for OCR results"""
    
    def __init__(self, parent_window, ocr_results: Dict, callback=None):
        """
        Initialize the data labeling editor
        
        Args:
            parent_window: Parent tkinter window
            ocr_results: OCR results dictionary
            callback: Optional callback function to call when data changes
        """
        self.parent = parent_window
        self.ocr_results = ocr_results
        self.window = None
        self.callback = callback  # Callback function for data changes
        
        # Data structures
        self.element_numbers = []  # List of detected element numbers
        self.values = []          # List of detected values/decimals
        self.connections = {}     # Dict mapping element numbers to values
        self.canvas_items = {}    # Canvas items for visual connections
        
        # UI components
        self.elements_tree = None
        self.values_tree = None
        self.connection_canvas = None
        self.connection_listbox = None
        
        # Selection state
        self.selected_element = None
        self.selected_value = None
        
        # Parse OCR results
        self.parse_ocr_results()
        
    def parse_ocr_results(self):
        """Parse OCR results to extract element numbers and values"""
        try:
            blocks = self.ocr_results.get('blocks', [])
            
            # Patterns for detection
            element_pattern = r'(?i)(?:element|elem|no\.?|num\.?|#)\s*([A-Z]?\d+[A-Z]?)'
            number_pattern = r'^\d+[A-Z]?$'  # Pure numbers or numbers with letter suffix
            value_pattern = r'\d+[.,]\d+'    # Decimal numbers
            
            for block in blocks:
                text = block.get('text', '').strip()
                confidence = block.get('confidence', 0)
                
                # Skip low confidence blocks
                if confidence < 0.6:
                    continue
                
                # Check for element numbers
                element_match = re.search(element_pattern, text)
                if element_match:
                    element_num = element_match.group(1)
                    self.element_numbers.append({
                        'text': element_num,
                        'original_text': text,
                        'confidence': confidence,
                        'block_id': block.get('block_id', ''),
                        'bbox': block.get('bbox', {}),
                        'page': block.get('page', 1)
                    })
                elif re.match(number_pattern, text):
                    # Pure number - could be element number
                    self.element_numbers.append({
                        'text': text,
                        'original_text': text,
                        'confidence': confidence,
                        'block_id': block.get('block_id', ''),
                        'bbox': block.get('bbox', {}),
                        'page': block.get('page', 1)
                    })
                
                # Check for decimal values
                if re.search(value_pattern, text):
                    # Clean the value (replace comma with dot)
                    clean_value = text.replace(',', '.')
                    try:
                        float_value = float(clean_value)
                        self.values.append({
                            'text': clean_value,
                            'original_text': text,
                            'value': float_value,
                            'confidence': confidence,
                            'block_id': block.get('block_id', ''),
                            'bbox': block.get('bbox', {}),
                            'page': block.get('page', 1)
                        })
                    except ValueError:
                        continue
            
            logger.info(f"Parsed {len(self.element_numbers)} element numbers and {len(self.values)} values")
            
        except Exception as e:
            logger.error(f"Error parsing OCR results: {str(e)}")
            
    def open_editor(self):
        """Open the data labeling editor window"""
        try:
            self.window = tk.Toplevel(self.parent)
            self.window.title("Data Labeling Editor - Connect Elements to Values")
            self.window.geometry("1200x800")
            self.window.transient(self.parent)
            self.window.grab_set()
            
            self.create_editor_ui()
            self.populate_data()
            
        except Exception as e:
            logger.error(f"Error opening editor: {str(e)}")
            messagebox.showerror("Error", f"Failed to open editor: {str(e)}")
            
    def create_editor_ui(self):
        """Create the editor user interface"""
        try:
            # Main frame
            main_frame = ttk.Frame(self.window)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Title
            title_label = ttk.Label(
                main_frame, 
                text="Data Labeling Editor - Connect Element Numbers to Values",
                font=("Arial", 14, "bold")
            )
            title_label.pack(pady=(0, 10))
            
            # Instructions
            instructions = ttk.Label(
                main_frame,
                text="Select an element number from the left, then a value from the right, and click 'Connect' to create a relationship.",
                font=("Arial", 10)
            )
            instructions.pack(pady=(0, 10))
            
            # Main content frame
            content_frame = ttk.Frame(main_frame)
            content_frame.pack(fill=tk.BOTH, expand=True)
            
            # Left panel - Element Numbers
            self.create_elements_panel(content_frame)
            
            # Middle panel - Connection Canvas
            self.create_connection_panel(content_frame)
            
            # Right panel - Values
            self.create_values_panel(content_frame)
            
            # Bottom panel - Controls and Connections List
            self.create_controls_panel(main_frame)
            
        except Exception as e:
            logger.error(f"Error creating editor UI: {str(e)}")
            
    def create_elements_panel(self, parent):
        """Create the element numbers panel"""
        elements_frame = ttk.LabelFrame(parent, text="Element Numbers", padding=5)
        elements_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Search frame
        search_frame = ttk.Frame(elements_frame)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(search_frame, text="Filter:").pack(side=tk.LEFT)
        self.elements_filter = tk.StringVar()
        self.elements_filter.trace('w', self.filter_elements)
        ttk.Entry(search_frame, textvariable=self.elements_filter).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Manual add frame
        add_frame = ttk.Frame(elements_frame)
        add_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(add_frame, text="Add:").pack(side=tk.LEFT)
        self.new_element_var = tk.StringVar()
        element_entry = ttk.Entry(add_frame, textvariable=self.new_element_var, width=15)
        element_entry.pack(side=tk.LEFT, padx=(5, 2))
        element_entry.bind('<Return>', self.add_manual_element)
        
        ttk.Button(add_frame, text="Add Element", command=self.add_manual_element).pack(side=tk.LEFT, padx=2)
        
        # Treeview
        columns = ('Element', 'Original', 'Confidence', 'Page')
        self.elements_tree = ttk.Treeview(elements_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.elements_tree.heading('Element', text='Element #')
        self.elements_tree.heading('Original', text='Original Text')
        self.elements_tree.heading('Confidence', text='Confidence')
        self.elements_tree.heading('Page', text='Page')
        
        self.elements_tree.column('Element', width=100)
        self.elements_tree.column('Original', width=150)
        self.elements_tree.column('Confidence', width=80)
        self.elements_tree.column('Page', width=50)
        
        # Scrollbar
        elements_scroll = ttk.Scrollbar(elements_frame, orient=tk.VERTICAL, command=self.elements_tree.yview)
        self.elements_tree.configure(yscrollcommand=elements_scroll.set)
        
        # Pack
        self.elements_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        elements_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection and context menu
        self.elements_tree.bind('<<TreeviewSelect>>', self.on_element_select)
        self.elements_tree.bind('<Button-3>', self.show_element_context_menu)  # Right-click
        
        # Create context menu for elements
        self.element_context_menu = tk.Menu(self.elements_tree, tearoff=0)
        self.element_context_menu.add_command(label="Delete Manual Entry", command=self.delete_selected_element)
        
    def create_values_panel(self, parent):
        """Create the values panel"""
        values_frame = ttk.LabelFrame(parent, text="Values/Decimals", padding=5)
        values_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Search frame
        search_frame = ttk.Frame(values_frame)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(search_frame, text="Filter:").pack(side=tk.LEFT)
        self.values_filter = tk.StringVar()
        self.values_filter.trace('w', self.filter_values)
        ttk.Entry(search_frame, textvariable=self.values_filter).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Manual add frame
        add_frame = ttk.Frame(values_frame)
        add_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(add_frame, text="Add:").pack(side=tk.LEFT)
        self.new_value_var = tk.StringVar()
        value_entry = ttk.Entry(add_frame, textvariable=self.new_value_var, width=15)
        value_entry.pack(side=tk.LEFT, padx=(5, 2))
        value_entry.bind('<Return>', self.add_manual_value)
        
        ttk.Button(add_frame, text="Add Value", command=self.add_manual_value).pack(side=tk.LEFT, padx=2)
        
        # Treeview
        columns = ('Value', 'Original', 'Confidence', 'Page')
        self.values_tree = ttk.Treeview(values_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.values_tree.heading('Value', text='Value')
        self.values_tree.heading('Original', text='Original Text')
        self.values_tree.heading('Confidence', text='Confidence')
        self.values_tree.heading('Page', text='Page')
        
        self.values_tree.column('Value', width=100)
        self.values_tree.column('Original', width=150)
        self.values_tree.column('Confidence', width=80)
        self.values_tree.column('Page', width=50)
        
        # Scrollbar
        values_scroll = ttk.Scrollbar(values_frame, orient=tk.VERTICAL, command=self.values_tree.yview)
        self.values_tree.configure(yscrollcommand=values_scroll.set)
        
        # Pack
        self.values_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        values_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection and context menu
        self.values_tree.bind('<<TreeviewSelect>>', self.on_value_select)
        self.values_tree.bind('<Button-3>', self.show_value_context_menu)  # Right-click
        
        # Create context menu for values
        self.value_context_menu = tk.Menu(self.values_tree, tearoff=0)
        self.value_context_menu.add_command(label="Delete Manual Entry", command=self.delete_selected_value)
        
    def create_connection_panel(self, parent):
        """Create the connection visualization panel"""
        connection_frame = ttk.LabelFrame(parent, text="Connections", padding=5)
        connection_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=5)
        
        # Canvas for drawing connections
        self.connection_canvas = tk.Canvas(
            connection_frame,
            width=200,
            height=400,
            bg='white',
            relief=tk.SUNKEN,
            borderwidth=1
        )
        self.connection_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Add instructions
        self.connection_canvas.create_text(
            100, 50,
            text="Visual connections\nwill appear here\nwhen you link\nelements to values",
            fill="gray",
            font=("Arial", 10),
            justify=tk.CENTER
        )
        
    def create_controls_panel(self, parent):
        """Create the controls and connections list panel"""
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Control buttons
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Connect button
        self.connect_btn = ttk.Button(
            buttons_frame,
            text="Connect Selected",
            command=self.connect_selected,
            style="Accent.TButton"
        )
        self.connect_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.connect_btn.config(state=tk.DISABLED)
        
        # Disconnect button
        ttk.Button(
            buttons_frame,
            text="Disconnect Selected",
            command=self.disconnect_selected
        ).pack(side=tk.LEFT, padx=5)
        
        # Clear all button
        ttk.Button(
            buttons_frame,
            text="Clear All",
            command=self.clear_all_connections
        ).pack(side=tk.LEFT, padx=5)
        
        # Export buttons
        ttk.Separator(buttons_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=10, fill=tk.Y)
        
        ttk.Button(
            buttons_frame,
            text="Export Dataset",
            command=self.export_dataset
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            buttons_frame,
            text="Load Dataset",
            command=self.load_dataset
        ).pack(side=tk.LEFT, padx=5)
        
        # Close button
        ttk.Button(
            buttons_frame,
            text="Close",
            command=self.close_editor
        ).pack(side=tk.RIGHT)
        
        # Connections list
        connections_frame = ttk.LabelFrame(controls_frame, text="Current Connections", padding=5)
        connections_frame.pack(fill=tk.BOTH, expand=True)
        
        # Listbox for connections
        self.connection_listbox = tk.Listbox(connections_frame, height=6)
        connections_scroll = ttk.Scrollbar(connections_frame, orient=tk.VERTICAL, command=self.connection_listbox.yview)
        self.connection_listbox.configure(yscrollcommand=connections_scroll.set)
        
        self.connection_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        connections_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection
        self.connection_listbox.bind('<<ListboxSelect>>', self.on_connection_select)
        
    def populate_data(self):
        """Populate the treeviews with data"""
        try:
            # Use the refresh methods to populate data
            self.refresh_elements_tree()
            self.refresh_values_tree()
                
            # Update status
            self.update_status()
            
        except Exception as e:
            logger.error(f"Error populating data: {str(e)}")
            
    def filter_elements(self, *args):
        """Filter elements based on search term"""
        try:
            self.refresh_elements_tree()
        except Exception as e:
            logger.error(f"Error filtering elements: {str(e)}")
            
    def filter_values(self, *args):
        """Filter values based on search term"""
        try:
            self.refresh_values_tree()
        except Exception as e:
            logger.error(f"Error filtering values: {str(e)}")
    
    def add_manual_element(self, event=None):
        """Add a manual element number"""
        try:
            element_text = self.new_element_var.get().strip()
            if not element_text:
                messagebox.showwarning("Warning", "Please enter an element number")
                return
            
            # Check if element already exists
            for existing in self.element_numbers:
                if existing['text'] == element_text:
                    messagebox.showwarning("Warning", f"Element '{element_text}' already exists")
                    return
            
            # Create new manual element
            new_element = {
                'text': element_text,
                'original_text': f"Manual: {element_text}",
                'confidence': 1.0,  # Manual entries have 100% confidence
                'block_id': f"manual_element_{len(self.element_numbers)}",
                'bbox': {'x': 0, 'y': 0, 'width': 0, 'height': 0},
                'page': 1,
                'manual': True
            }
            
            # Add to list
            self.element_numbers.append(new_element)
            
            # Update treeview
            self.refresh_elements_tree()
            
            # Clear entry
            self.new_element_var.set("")
            
            logger.info(f"Added manual element: {element_text}")
            messagebox.showinfo("Success", f"Added element '{element_text}' successfully")
            
        except Exception as e:
            logger.error(f"Error adding manual element: {str(e)}")
            messagebox.showerror("Error", f"Failed to add element: {str(e)}")
    
    def add_manual_value(self, event=None):
        """Add a manual value"""
        try:
            value_text = self.new_value_var.get().strip()
            if not value_text:
                messagebox.showwarning("Warning", "Please enter a value")
                return
            
            # Check if value already exists
            for existing in self.values:
                if existing['text'] == value_text:
                    messagebox.showwarning("Warning", f"Value '{value_text}' already exists")
                    return
            
            # Try to parse as float for validation
            try:
                float_value = float(value_text.replace(',', '.'))
            except ValueError:
                result = messagebox.askyesno(
                    "Invalid Number",
                    f"'{value_text}' is not a valid number. Add anyway?"
                )
                if not result:
                    return
                float_value = 0.0
            
            # Create new manual value
            new_value = {
                'text': value_text,
                'original_text': f"Manual: {value_text}",
                'value': float_value,
                'confidence': 1.0,  # Manual entries have 100% confidence
                'block_id': f"manual_value_{len(self.values)}",
                'bbox': {'x': 0, 'y': 0, 'width': 0, 'height': 0},
                'page': 1,
                'manual': True
            }
            
            # Add to list
            self.values.append(new_value)
            
            # Update treeview
            self.refresh_values_tree()
            
            # Clear entry
            self.new_value_var.set("")
            
            logger.info(f"Added manual value: {value_text}")
            messagebox.showinfo("Success", f"Added value '{value_text}' successfully")
            
        except Exception as e:
            logger.error(f"Error adding manual value: {str(e)}")
            messagebox.showerror("Error", f"Failed to add value: {str(e)}")
    
    def refresh_elements_tree(self):
        """Refresh the elements treeview"""
        try:
            # Clear current items
            for item in self.elements_tree.get_children():
                self.elements_tree.delete(item)
            
            # Apply current filter
            search_term = self.elements_filter.get().lower()
            
            # Add filtered items
            for i, element in enumerate(self.element_numbers):
                if (not search_term or 
                    search_term in element['text'].lower() or 
                    search_term in element['original_text'].lower()):
                    
                    # Mark manual entries with special formatting
                    display_text = element['text']
                    if element.get('manual', False):
                        display_text = f"🔧 {display_text}"
                    
                    self.elements_tree.insert('', 'end', iid=i, values=(
                        display_text,
                        element['original_text'][:20] + "..." if len(element['original_text']) > 20 else element['original_text'],
                        f"{element['confidence']:.3f}",
                        element['page']
                    ))
                    
        except Exception as e:
            logger.error(f"Error refreshing elements tree: {str(e)}")
    
    def refresh_values_tree(self):
        """Refresh the values treeview"""
        try:
            # Clear current items
            for item in self.values_tree.get_children():
                self.values_tree.delete(item)
            
            # Apply current filter
            search_term = self.values_filter.get().lower()
            
            # Add filtered items
            for i, value in enumerate(self.values):
                if (not search_term or 
                    search_term in value['text'].lower() or 
                    search_term in value['original_text'].lower()):
                    
                    # Mark manual entries with special formatting
                    display_text = value['text']
                    if value.get('manual', False):
                        display_text = f"🔧 {display_text}"
                    
                    self.values_tree.insert('', 'end', iid=i, values=(
                        display_text,
                        value['original_text'][:20] + "..." if len(value['original_text']) > 20 else value['original_text'],
                        f"{value['confidence']:.3f}",
                        value['page']
                    ))
                    
        except Exception as e:
            logger.error(f"Error refreshing values tree: {str(e)}")
            
    def on_element_select(self, event):
        """Handle element selection"""
        try:
            selection = self.elements_tree.selection()
            if selection:
                self.selected_element = int(selection[0])
                self.update_connect_button()
                
        except Exception as e:
            logger.error(f"Error handling element selection: {str(e)}")
            
    def on_value_select(self, event):
        """Handle value selection"""
        try:
            selection = self.values_tree.selection()
            if selection:
                self.selected_value = int(selection[0])
                self.update_connect_button()
                
        except Exception as e:
            logger.error(f"Error handling value selection: {str(e)}")
            
    def update_connect_button(self):
        """Update the connect button state"""
        if self.selected_element is not None and self.selected_value is not None:
            self.connect_btn.config(state=tk.NORMAL)
        else:
            self.connect_btn.config(state=tk.DISABLED)
            
    def connect_selected(self):
        """Connect the selected element to the selected value"""
        try:
            if self.selected_element is None or self.selected_value is None:
                return
                
            element = self.element_numbers[self.selected_element]
            value = self.values[self.selected_value]
            
            # Check if element is already connected
            if element['text'] in self.connections:
                result = messagebox.askyesno(
                    "Element Already Connected",
                    f"Element '{element['text']}' is already connected to '{self.connections[element['text']]['value']['text']}'. Replace?"
                )
                if not result:
                    return
            
            # Create connection
            self.connections[element['text']] = {
                'element': element,
                'value': value,
                'timestamp': datetime.now().isoformat()
            }
            
            # Update UI
            self.update_connections_list()
            self.update_status()
            
            # Notify parent about data change
            self.notify_data_changed()
            
            # Clear selections
            self.elements_tree.selection_remove(self.elements_tree.selection())
            self.values_tree.selection_remove(self.values_tree.selection())
            self.selected_element = None
            self.selected_value = None
            self.update_connect_button()
            
            logger.info(f"Connected element '{element['text']}' to value '{value['text']}'")
            
        except Exception as e:
            logger.error(f"Error connecting elements: {str(e)}")
            messagebox.showerror("Error", f"Failed to connect elements: {str(e)}")
            
    def disconnect_selected(self):
        """Disconnect the selected connection"""
        try:
            selection = self.connection_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a connection to disconnect")
                return
                
            connection_text = self.connection_listbox.get(selection[0])
            element_text = connection_text.split(" → ")[0]
            
            if element_text in self.connections:
                del self.connections[element_text]
                self.update_connections_list()
                self.update_status()
                
                # Notify parent about data change
                self.notify_data_changed()
                
                logger.info(f"Disconnected element '{element_text}'")
            
        except Exception as e:
            logger.error(f"Error disconnecting: {str(e)}")
            
    def clear_all_connections(self):
        """Clear all connections"""
        try:
            if self.connections:
                result = messagebox.askyesno(
                    "Clear All Connections",
                    f"Are you sure you want to clear all {len(self.connections)} connections?"
                )
                if result:
                    self.connections.clear()
                    self.update_connections_list()
                    self.update_status()
                    
                    # Notify parent about data change
                    self.notify_data_changed()
                    
                    logger.info("Cleared all connections")
            
        except Exception as e:
            logger.error(f"Error clearing connections: {str(e)}")
            
    def update_connections_list(self):
        """Update the connections listbox"""
        try:
            self.connection_listbox.delete(0, tk.END)
            
            for element_text, connection in self.connections.items():
                connection_text = f"{element_text} → {connection['value']['text']}"
                self.connection_listbox.insert(tk.END, connection_text)
                
        except Exception as e:
            logger.error(f"Error updating connections list: {str(e)}")
            
    def update_status(self):
        """Update the status display"""
        try:
            self.window.title(
                f"Data Labeling Editor - {len(self.element_numbers)} Elements, "
                f"{len(self.values)} Values, {len(self.connections)} Connections"
            )
            
        except Exception as e:
            logger.error(f"Error updating status: {str(e)}")
            
    def on_connection_select(self, event):
        """Handle connection selection"""
        # Could highlight the selected connection visually
        pass
        
    def export_dataset(self):
        """Export the dataset with connections"""
        try:
            if not self.connections:
                messagebox.showwarning("Warning", "No connections to export")
                return
                
            file_path = filedialog.asksaveasfilename(
                title="Export Dataset",
                defaultextension=".json",
                filetypes=[
                    ("JSON files", "*.json"),
                    ("CSV files", "*.csv"),
                    ("All files", "*.*")
                ]
            )
            
            if not file_path:
                return
                
            # Prepare export data
            export_data = {
                'metadata': {
                    'export_time': datetime.now().isoformat(),
                    'total_connections': len(self.connections),
                    'total_elements': len(self.element_numbers),
                    'total_values': len(self.values)
                },
                'connections': [],
                'unconnected_elements': [],
                'unconnected_values': []
            }
            
            # Add connections
            for element_text, connection in self.connections.items():
                export_data['connections'].append({
                    'element_number': element_text,
                    'element_original_text': connection['element']['original_text'],
                    'element_confidence': connection['element']['confidence'],
                    'element_page': connection['element']['page'],
                    'element_bbox': connection['element']['bbox'],
                    'value': connection['value']['text'],
                    'value_original_text': connection['value']['original_text'],
                    'value_confidence': connection['value']['confidence'],
                    'value_page': connection['value']['page'],
                    'value_bbox': connection['value']['bbox'],
                    'connection_timestamp': connection['timestamp']
                })
            
            # Add unconnected elements
            connected_elements = set(self.connections.keys())
            for element in self.element_numbers:
                if element['text'] not in connected_elements:
                    export_data['unconnected_elements'].append({
                        'element_number': element['text'],
                        'original_text': element['original_text'],
                        'confidence': element['confidence'],
                        'page': element['page'],
                        'bbox': element['bbox']
                    })
            
            # Add unconnected values
            connected_values = {conn['value']['text'] for conn in self.connections.values()}
            for value in self.values:
                if value['text'] not in connected_values:
                    export_data['unconnected_values'].append({
                        'value': value['text'],
                        'original_text': value['original_text'],
                        'confidence': value['confidence'],
                        'page': value['page'],
                        'bbox': value['bbox']
                    })
            
            # Export based on file extension
            if file_path.endswith('.csv'):
                self.export_csv(export_data, file_path)
            else:
                self.export_json(export_data, file_path)
            
            messagebox.showinfo("Success", f"Dataset exported to:\n{file_path}")
            logger.info(f"Dataset exported to {file_path}")
            
        except Exception as e:
            logger.error(f"Error exporting dataset: {str(e)}")
            messagebox.showerror("Error", f"Failed to export dataset: {str(e)}")
            
    def export_json(self, data: Dict, file_path: str):
        """Export data as JSON"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
    def export_csv(self, data: Dict, file_path: str):
        """Export data as CSV"""
        import csv
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'Element_Number',
                'Element_Original_Text',
                'Element_Confidence',
                'Element_Page',
                'Value',
                'Value_Original_Text',
                'Value_Confidence',
                'Value_Page',
                'Connection_Timestamp'
            ])
            
            # Write connections
            for connection in data['connections']:
                writer.writerow([
                    connection['element_number'],
                    connection['element_original_text'],
                    connection['element_confidence'],
                    connection['element_page'],
                    connection['value'],
                    connection['value_original_text'],
                    connection['value_confidence'],
                    connection['value_page'],
                    connection['connection_timestamp']
                ])
                
    def load_dataset(self):
        """Load a previously saved dataset"""
        try:
            file_path = filedialog.askopenfilename(
                title="Load Dataset",
                filetypes=[
                    ("JSON files", "*.json"),
                    ("All files", "*.*")
                ]
            )
            
            if not file_path:
                return
                
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Clear existing connections
            self.connections.clear()
            
            # Load connections
            connections_data = data.get('connections', [])
            for conn in connections_data:
                element_text = conn['element_number']
                
                # Find matching element and value
                element = None
                value = None
                
                for elem in self.element_numbers:
                    if elem['text'] == element_text:
                        element = elem
                        break
                
                for val in self.values:
                    if val['text'] == conn['value']:
                        value = val
                        break
                
                if element and value:
                    self.connections[element_text] = {
                        'element': element,
                        'value': value,
                        'timestamp': conn.get('connection_timestamp', datetime.now().isoformat())
                    }
            
            # Update UI
            self.update_connections_list()
            self.update_status()
            
            # Notify parent about data change
            self.notify_data_changed()
            
            messagebox.showinfo("Success", f"Loaded {len(self.connections)} connections from dataset")
            logger.info(f"Dataset loaded from {file_path}")
            
        except Exception as e:
            logger.error(f"Error loading dataset: {str(e)}")
            messagebox.showerror("Error", f"Failed to load dataset: {str(e)}")
            
    def close_editor(self):
        """Close the editor window"""
        try:
            if self.connections:
                result = messagebox.askyesnocancel(
                    "Save Changes",
                    f"You have {len(self.connections)} connections. Do you want to export them before closing?"
                )
                if result is True:  # Yes - export
                    self.export_dataset()
                elif result is None:  # Cancel
                    return
                # No - continue closing
            
            self.window.destroy()
            
        except Exception as e:
            logger.error(f"Error closing editor: {str(e)}")
            self.window.destroy()
    
    def show_element_context_menu(self, event):
        """Show context menu for elements"""
        try:
            # Select the item under cursor
            item = self.elements_tree.identify_row(event.y)
            if item:
                self.elements_tree.selection_set(item)
                
                # Check if it's a manual entry
                element_index = int(item)
                if element_index < len(self.element_numbers):
                    element = self.element_numbers[element_index]
                    if element.get('manual', False):
                        self.element_context_menu.post(event.x_root, event.y_root)
                        
        except Exception as e:
            logger.error(f"Error showing element context menu: {str(e)}")
    
    def show_value_context_menu(self, event):
        """Show context menu for values"""
        try:
            # Select the item under cursor
            item = self.values_tree.identify_row(event.y)
            if item:
                self.values_tree.selection_set(item)
                
                # Check if it's a manual entry
                value_index = int(item)
                if value_index < len(self.values):
                    value = self.values[value_index]
                    if value.get('manual', False):
                        self.value_context_menu.post(event.x_root, event.y_root)
                        
        except Exception as e:
            logger.error(f"Error showing value context menu: {str(e)}")
    
    def delete_selected_element(self):
        """Delete the selected manual element"""
        try:
            selection = self.elements_tree.selection()
            if not selection:
                return
                
            element_index = int(selection[0])
            if element_index >= len(self.element_numbers):
                return
                
            element = self.element_numbers[element_index]
            
            # Only allow deletion of manual entries
            if not element.get('manual', False):
                messagebox.showwarning("Warning", "Only manual entries can be deleted")
                return
                
            # Confirm deletion
            result = messagebox.askyesno(
                "Delete Element",
                f"Are you sure you want to delete element '{element['text']}'?"
            )
            
            if result:
                # Remove from connections if connected
                if element['text'] in self.connections:
                    del self.connections[element['text']]
                    self.update_connections_list()
                
                # Remove from list
                self.element_numbers.pop(element_index)
                
                # Refresh display
                self.refresh_elements_tree()
                self.update_status()
                
                logger.info(f"Deleted manual element: {element['text']}")
                
        except Exception as e:
            logger.error(f"Error deleting element: {str(e)}")
            messagebox.showerror("Error", f"Failed to delete element: {str(e)}")
    
    def delete_selected_value(self):
        """Delete the selected manual value"""
        try:
            selection = self.values_tree.selection()
            if not selection:
                return
                
            value_index = int(selection[0])
            if value_index >= len(self.values):
                return
                
            value = self.values[value_index]
            
            # Only allow deletion of manual entries
            if not value.get('manual', False):
                messagebox.showwarning("Warning", "Only manual entries can be deleted")
                return
                
            # Confirm deletion
            result = messagebox.askyesno(
                "Delete Value",
                f"Are you sure you want to delete value '{value['text']}'?"
            )
            
            if result:
                # Remove from connections if connected
                connections_to_remove = []
                for element_text, connection in self.connections.items():
                    if connection['value']['text'] == value['text']:
                        connections_to_remove.append(element_text)
                
                for element_text in connections_to_remove:
                    del self.connections[element_text]
                
                if connections_to_remove:
                    self.update_connections_list()
                
                # Remove from list
                self.values.pop(value_index)
                
                # Refresh display
                self.refresh_values_tree()
                self.update_status()
                
                logger.info(f"Deleted manual value: {value['text']}")
                
        except Exception as e:
            logger.error(f"Error deleting value: {str(e)}")
            messagebox.showerror("Error", f"Failed to delete value: {str(e)}")
    
    def get_relations(self) -> List[Dict]:
        """
        Get all element-value relations in structured format
        
        Returns:
            List of relation dictionaries with element, value, confidence, and source
        """
        relations = []
        
        try:
            for element_text, connection in self.connections.items():
                element = connection['element']
                value = connection['value']
                
                # Calculate confidence based on OCR confidence
                element_confidence = element.get('confidence', 0.0)
                value_confidence = value.get('confidence', 0.0)
                
                # Use average confidence, or 0.5 for manual entries
                if element_confidence > 0 and value_confidence > 0:
                    avg_confidence = (element_confidence + value_confidence) / 2
                elif element_confidence > 0:
                    avg_confidence = element_confidence
                elif value_confidence > 0:
                    avg_confidence = value_confidence
                else:
                    avg_confidence = 0.5  # Default for manual entries
                
                # Determine source
                source = "OCR"
                if element.get('manual', False) or value.get('manual', False):
                    source = "Manual"
                elif element.get('manual', False) and value.get('manual', False):
                    source = "Manual"
                
                relation = {
                    'element': element['text'],
                    'value': value['text'],
                    'confidence': avg_confidence,
                    'source': source,
                    'created': datetime.now().isoformat(),
                    'element_bbox': element.get('bbox', []),
                    'value_bbox': value.get('bbox', [])
                }
                
                relations.append(relation)
                
            logger.info(f"Retrieved {len(relations)} relations from data labeling editor")
            return relations
            
        except Exception as e:
            logger.error(f"Error getting relations: {str(e)}")
            return []
    
    def notify_data_changed(self):
        """Notify the parent application that data has changed"""
        try:
            if self.callback:
                relations = self.get_relations()
                self.callback(relations)
        except Exception as e:
            logger.error(f"Error in data change callback: {str(e)}")
