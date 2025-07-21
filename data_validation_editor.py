"""
Data Validation Editor for OCR Viewer
Provides a user interface for validating and editing extracted OCR data
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
from dataclasses import asdict, is_dataclass

class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle dataclass objects"""
    def default(self, obj):
        if is_dataclass(obj):
            return asdict(obj)
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        elif isinstance(obj, (list, tuple)):
            return [self.default(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: self.default(value) for key, value in obj.items()}
        return super().default(obj)

class DataValidationEditor:
    """
    A simple data validation editor for OCR results
    """
    
    def __init__(self, parent, structured_data):
        self.parent = parent
        self.original_data = structured_data
        self.validated_data = None
        
        # Create the window
        self.window = tk.Toplevel(parent)
        self.window.title("📝 Editor de Validació de Dades")
        self.window.geometry("800x600")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """Set up the user interface"""
        # Title
        title_frame = tk.Frame(self.window, bg='white', pady=10)
        title_frame.pack(fill='x')
        
        title_label = tk.Label(
            title_frame,
            text="📝 Editor de Validació de Dades Estructurades",
            font=('Segoe UI', 14, 'bold'),
            bg='white',
            fg='#2563eb'
        )
        title_label.pack()
        
        # Main content area
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Instructions
        instructions = tk.Label(
            main_frame,
            text="Revisa i edita les dades extretes. Els canvis es guardaran quan facis clic a 'Acceptar'.",
            font=('Segoe UI', 10),
            wraplength=700,
            justify='left'
        )
        instructions.pack(anchor='w', pady=(0, 10))
        
        # Data display area
        data_frame = tk.LabelFrame(main_frame, text="Dades Extretes", font=('Segoe UI', 10, 'bold'))
        data_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Text widget with scrollbar
        text_frame = tk.Frame(data_frame)
        text_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.text_widget = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg='#f8f9fa',
            relief='solid',
            borderwidth=1
        )
        
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        
        self.text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Status label
        self.status_label = tk.Label(
            main_frame,
            text="ℹ️ Edita les dades segons sigui necessari",
            font=('Segoe UI', 9),
            fg='#666666'
        )
        self.status_label.pack(anchor='w', pady=(5, 10))
        
        # Button frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        # Buttons
        self.accept_btn = tk.Button(
            button_frame,
            text="✅ Acceptar Canvis",
            command=self.accept_changes,
            bg='#2563eb',
            fg='white',
            font=('Segoe UI', 10),
            padx=20,
            pady=8,
            relief='flat'
        )
        self.accept_btn.pack(side='right', padx=(10, 0))
        
        self.cancel_btn = tk.Button(
            button_frame,
            text="❌ Cancel·lar",
            command=self.cancel_changes,
            bg='#6b7280',
            fg='white',
            font=('Segoe UI', 10),
            padx=20,
            pady=8,
            relief='flat'
        )
        self.cancel_btn.pack(side='right')
        
        self.reset_btn = tk.Button(
            button_frame,
            text="🔄 Reiniciar",
            command=self.reset_data,
            bg='#f59e0b',
            fg='white',
            font=('Segoe UI', 10),
            padx=20,
            pady=8,
            relief='flat'
        )
        self.reset_btn.pack(side='left')
        
    def load_data(self):
        """Load the structured data into the editor"""
        try:
            if self.original_data:
                # Convert data to JSON format for editing using custom encoder
                json_data = json.dumps(
                    self.original_data, 
                    indent=2, 
                    ensure_ascii=False,
                    cls=CustomJSONEncoder
                )
                self.text_widget.delete(1.0, tk.END)
                self.text_widget.insert(1.0, json_data)
                
                # Count data entries
                data_count = 0
                if isinstance(self.original_data, dict):
                    data_count = sum(len(v) if isinstance(v, list) else 1 for v in self.original_data.values())
                elif isinstance(self.original_data, list):
                    data_count = len(self.original_data)
                else:
                    data_count = 1
                    
                self.status_label.config(text=f"✅ Carregades {data_count} entrades de dades")
            else:
                self.text_widget.insert(1.0, "# No hi ha dades estructurades per editar\n")
                self.status_label.config(text="⚠️ No hi ha dades per validar")
        except Exception as e:
            error_msg = str(e)
            self.status_label.config(text=f"❌ Error en carregar les dades: {error_msg}")
            
            # Try to show a more user-friendly representation
            try:
                if self.original_data:
                    # If JSON fails, create a readable text representation
                    readable_data = self._create_readable_representation(self.original_data)
                    self.text_widget.delete(1.0, tk.END)
                    self.text_widget.insert(1.0, readable_data)
                    self.status_label.config(text="⚠️ Dades carregades en format text (no JSON)")
                else:
                    messagebox.showerror("Error", f"No s'han pogut carregar les dades:\n{error_msg}")
            except Exception as e2:
                messagebox.showerror("Error", f"No s'han pogut carregar les dades:\n{error_msg}\n\nError secundari: {str(e2)}")
    
    def _create_readable_representation(self, data):
        """Create a human-readable representation of the data"""
        try:
            result = "# DADES ESTRUCTURADES EXTRETES\n"
            result += "# Format: Text llegible (editar amb cura)\n\n"
            
            if isinstance(data, dict):
                for key, value in data.items():
                    result += f"=== {key.upper()} ===\n"
                    if isinstance(value, list):
                        for i, item in enumerate(value, 1):
                            result += f"\n{i}. {self._item_to_string(item)}\n"
                    else:
                        result += f"{self._item_to_string(value)}\n"
                    result += "\n"
            elif isinstance(data, list):
                result += "=== ELEMENTS ===\n"
                for i, item in enumerate(data, 1):
                    result += f"\n{i}. {self._item_to_string(item)}\n"
            else:
                result += f"Dada: {self._item_to_string(data)}\n"
                
            return result
        except Exception as e:
            return f"# Error en crear representació llegible: {str(e)}\n# Dades originals: {str(data)[:500]}..."
    
    def _item_to_string(self, item):
        """Convert an item to a readable string"""
        try:
            if hasattr(item, '__dict__'):
                # For custom objects with attributes
                attrs = []
                for key, value in item.__dict__.items():
                    attrs.append(f"{key}: {value}")
                return f"({', '.join(attrs)})"
            elif is_dataclass(item):
                # For dataclass objects
                attrs = []
                for key, value in asdict(item).items():
                    attrs.append(f"{key}: {value}")
                return f"({', '.join(attrs)})"
            else:
                return str(item)
        except Exception:
            return str(item)
    
    def reset_data(self):
        """Reset data to original values"""
        self.load_data()
        self.status_label.config(text="🔄 Dades reiniciades als valors originals")
    
    def accept_changes(self):
        """Accept and validate the changes"""
        try:
            # Get the edited data
            edited_text = self.text_widget.get(1.0, tk.END).strip()
            
            if not edited_text or edited_text.startswith("# No hi ha dades"):
                self.validated_data = self.original_data
                self.status_label.config(text="✅ No hi ha canvis per aplicar")
            else:
                # Try to parse as JSON
                try:
                    self.validated_data = json.loads(edited_text)
                    self.status_label.config(text="✅ Dades validades correctament")
                except json.JSONDecodeError as e:
                    # If JSON parsing fails, treat as simple text data
                    self.validated_data = {"validated_text": edited_text}
                    self.status_label.config(text="✅ Dades validades com a text")
            
            # Close the window
            self.window.after(500, self.window.destroy)
            
        except Exception as e:
            self.status_label.config(text=f"❌ Error en validar: {str(e)}")
            messagebox.showerror("Error de Validació", f"No s'han pogut validar les dades:\n{str(e)}")
    
    def cancel_changes(self):
        """Cancel without saving changes"""
        self.validated_data = None
        self.window.destroy()

if __name__ == "__main__":
    # Test the editor
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    
    test_data = [
        {"element": "test1", "value": "123", "confidence": 0.95},
        {"element": "test2", "value": "456", "confidence": 0.87}
    ]
    
    editor = DataValidationEditor(root, test_data)
    root.wait_window(editor.window)
    
    if editor.validated_data:
        print("Validated data:", editor.validated_data)
    else:
        print("No changes made")
    
    root.destroy()
