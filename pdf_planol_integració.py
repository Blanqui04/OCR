from_sql.py

def get_planol_pdf(ref_client):
    """Retrieve PDF data from database for a specific referencia_client."""
    query = """
    SELECT num_planol, imatge 
    FROM planol 
    WHERE id_referencia_client = %s
    ORDER BY num_planol DESC
    LIMIT 1
    """
    params = (ref_client,)
    
    db = PostgresConn(**db_params)
    try:
        conn = db.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        
        if result:
            num_planol, imatge_json = result
            
            # Parse the JSON data
            if isinstance(imatge_json, str):
                imatge_data = json.loads(imatge_json)
            else:
                imatge_data = imatge_json
            
            # Extract PDF data
            pdf_base64 = imatge_data.get('data', '')
            filename = imatge_data.get('nom', f'planol_{num_planol}.pdf')
            
            # Decode base64 to binary
            pdf_binary = base64.b64decode(pdf_base64)
            
            # Log successful retrieval
            db_logger.log_select(query, params, 1)
            
            return {
                'num_planol': num_planol,
                'filename': filename,
                'pdf_data': pdf_binary,
                'success': True
            }
        else:
            # Log no results found
            db_logger.log_select(query, params, 0)
            return {
                'success': False,
                'error': f'No planol found for referencia_client: {ref_client}'
            }
            
    except Exception as e:
        db_logger.log_error("Error retrieving planol PDF", str(e))
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    finally:
        db.close()
		
		

def save_temp_pdf(pdf_data, filename):
    """Save PDF data to a temporary file and return the path."""
    try:
        # Create a temporary file
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, filename)
        
        # Write PDF data to temporary file
        with open(temp_path, 'wb') as f:
            f.write(pdf_data)
        
        return temp_path
    except Exception as e:
        db_logger.log_error("Error saving temporary PDF", str(e))
        return None
		
		

proves_imatges.py

import psycopg2
import base64
import json
import os
from db_logger import db_logger

# Fitxer que vols carregar
nom_fitxer = "6555945_003.pdf"
path_fitxer = os.path.join(os.getcwd(), nom_fitxer)

# Obtenir camps des del nom
id_referencia_client = nom_fitxer.split("_")[0]
num_planol = nom_fitxer.split("_")[1].split(".")[0]

# Connexió a la base de dades
try:
    conn = psycopg2.connect(
        dbname="documentacio_tecnica",
        user="administrador",
        password="Some2025.!$%",
        host="172.26.5.159",
        port=5433
    )
    cursor = conn.cursor()
    
    # Log successful connection
    db_logger.log_connection("CONNECT", "Connected to documentacio_tecnica database")

    # Llegir i codificar
    with open(path_fitxer, "rb") as f:
        imatge_base64 = base64.b64encode(f.read()).decode("utf-8")

    imatge_json = {
        "nom": nom_fitxer,
        "mime": "application/pdf",  # correcte per PDFs
        "data": imatge_base64
    }

    # Inserir
    sql = """
    INSERT INTO planol (num_planol, id_referencia_client, imatge)
    VALUES (%s, %s, %s::jsonb)
    ON CONFLICT (num_planol) DO UPDATE SET imatge = EXCLUDED.imatge
    """

    cursor.execute(sql, (num_planol, id_referencia_client, json.dumps(imatge_json)))
    conn.commit()

    # Log the INSERT operation
    db_logger.log_insert(
        sql, 
        (num_planol, id_referencia_client, "JSON_DATA"), 
        1
    )

    # Comprovació immediata
    select_query = "SELECT num_planol, jsonb_pretty(imatge) FROM planol WHERE num_planol = %s"
    cursor.execute(select_query, (num_planol,))
    row = cursor.fetchone()
    if row:
        db_logger.log_select(
            select_query,
            (num_planol,),
            1
        )

except Exception as e:
    db_logger.log_error("Database operation failed", str(e))

finally:
    cursor.close()
    conn.close()
    db_logger.log_connection("DISCONNECT", "Connection terminated successfully")
	
	

dbb_ui.py

class PDFViewer(QLabel):
    """Custom PDF viewer widget"""
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 2px dashed #ccc;
                border-radius: 8px;
                color: #666;
                font-size: 14px;
            }
        """)
        self.setText("PDF Preview\n\nClick 'Veure Plànol' to load and preview a PDF")
        self.setMinimumSize(400, 500)
        self.current_pdf_doc = None
        self.current_page = 0
        self.zoom_factor = 1.0
        
    def load_pdf_from_data(self, pdf_data, filename):
        """Load PDF from binary data"""
        try:
            # Create a PDF document from binary data
            self.current_pdf_doc = fitz.open(stream=pdf_data, filetype="pdf")
            self.current_page = 0
            self.zoom_factor = 1.0
            self.display_current_page()
            return True
        except Exception as e:
            self.setText(f"Error loading PDF:\n{str(e)}")
            return False
            
    def display_current_page(self):
        """Display the current page of the PDF"""
        if not self.current_pdf_doc:
            return
            
        try:
            # Get the page
            page = self.current_pdf_doc[self.current_page]
            
            # Create a matrix for zoom
            mat = fitz.Matrix(self.zoom_factor, self.zoom_factor)
            
            # Render page to image
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to QPixmap
            img_data = pix.tobytes("ppm")
            qimg = QPixmap()
            qimg.loadFromData(img_data)
            
            # Scale to fit the widget while maintaining aspect ratio
            scaled_pixmap = qimg.scaled(
                self.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            
            self.setPixmap(scaled_pixmap)
            
            # Update text info with zoom level
            zoom_info = f"Zoom: {int(self.zoom_factor * 100)}%"
            if hasattr(self, 'parent_widget'):
                self.parent_widget.update_pdf_info(zoom_info)
                
        except Exception as e:
            self.setText(f"Error displaying PDF page:\n{str(e)}")
            
            
    def zoom_in(self):
        """Zoom in"""
        self.zoom_factor = min(self.zoom_factor * 1.2, 3.0)
        self.display_current_page()
        
    def zoom_out(self):
        """Zoom out"""
        self.zoom_factor = max(self.zoom_factor / 1.2, 0.3)
        self.display_current_page()
        
    def reset_zoom(self):
        """Reset zoom to fit"""
        self.zoom_factor = 1.0
        self.display_current_page()
        
    def clear_pdf(self):
        """Clear the current PDF"""
        if self.current_pdf_doc:
            self.current_pdf_doc.close()
            self.current_pdf_doc = None
        self.clear()
        self.setText("PDF Preview\n\nClick 'Veure Plànol' to load and preview a PDF")
    
    def resizeEvent(self, event):
        """Handle resize events to update PDF display"""
        super().resizeEvent(event)
        if self.current_pdf_doc:
            # Redisplay current page with new size
            self.display_current_page()
        
class PDFLoadThread(QThread):
    """Thread for loading PDF data"""
    pdf_loaded = Signal(dict)
    error_occurred = Signal(str)
    
    def __init__(self, client_ref):
        super().__init__()
        self.client_ref = client_ref
        
    def run(self):
        try:
            from from_sql import get_planol_pdf
            result = get_planol_pdf(self.client_ref)
            self.pdf_loaded.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))

def accio_planol(self):
        """View plan - Visualize PDF from database with preview"""
        if not self.client:
            self.show_warning("Please fill in 'Ref. Client' field to view the plan.")
            return
        
        self.update_status("Loading plan from database...")
        self.update_visualizer(f"Plan Viewer\n\nLoading plan for client: {self.client}\n\nSearching database...")
        
        try:
            # Clear previous PDF
            self.pdf_viewer.clear_pdf()
            self.update_pdf_info("Loading...")
            
            # Import the function to get PDF from database
            self.update_visualizer(f"Plan Viewer\n\nStep 1: Importing functions...\nClient: {self.client}")
            from from_sql import get_planol_pdf, save_temp_pdf
            
            # Get PDF data from database
            self.update_visualizer(f"Plan Viewer\n\nStep 2: Querying database...\nClient: {self.client}")
            pdf_result = get_planol_pdf(self.client)
            
            if pdf_result['success']:
                # Save PDF to temporary file
                self.update_visualizer(f"Plan Viewer\n\nStep 3: Saving PDF to temporary file...\nClient: {self.client}\nPlan: {pdf_result['num_planol']}")
                temp_path = save_temp_pdf(pdf_result['pdf_data'], pdf_result['filename'])
                
                if temp_path:
                    # Load PDF preview
                    self.update_visualizer(f"Plan Viewer\n\nStep 4: Loading PDF preview...\nFile: {pdf_result['filename']}")
                    
                    preview_success = self.load_pdf_preview(
                        pdf_result['pdf_data'], 
                        pdf_result['filename'], 
                        temp_path
                    )
                    
                    if preview_success:
                        success_msg = f"Plan Viewer\n\nPDF successfully loaded and previewed!\n\nClient: {self.client}\nPlan Number: {pdf_result['num_planol']}\nFile: {pdf_result['filename']}\nPages: {len(self.pdf_viewer.current_pdf_doc) if self.pdf_viewer.current_pdf_doc else 'Unknown'}\n\nUse the zoom controls above to adjust the view.\nClick 'Open External' to open in your default PDF viewer.\n\nTemporary file location: {temp_path}"
                        
                        self.update_visualizer(success_msg)
                        self.update_status("Plan loaded successfully")
                        
                    else:
                        # Fallback to external opening if preview fails
                        try:
                            if platform.system() == 'Windows':
                                os.startfile(temp_path)
                            elif platform.system() == 'Darwin':  # macOS
                                subprocess.run(['open', temp_path])
                            else:  # Linux
                                subprocess.run(['xdg-open', temp_path])
                            
                            fallback_msg = f"Plan Viewer\n\nPDF preview failed but file opened externally.\n\nClient: {self.client}\nPlan Number: {pdf_result['num_planol']}\nFile: {pdf_result['filename']}\n\nThe PDF has been opened in your default PDF viewer.\nTemporary file location: {temp_path}"
                            
                            self.update_visualizer(fallback_msg)
                            self.update_status("Plan opened externally")
                            
                        except Exception as e:
                            error_msg = f"Plan Viewer\n\nPDF retrieved but both preview and external opening failed:\n\nError: {str(e)}\n\nThe PDF file has been saved to: {temp_path}\nYou can manually open it with any PDF viewer."
                            self.update_visualizer(error_msg)
                            self.update_status("Plan retrieved but failed to display")
                        
                else:
                    self.show_error("Failed to save PDF to temporary file")
                    self.update_status("Failed to save PDF")
                    self.update_visualizer(f"Plan Viewer Error\n\nFailed to save PDF to temporary file.\nClient: {self.client}")
            else:
                error_msg = f"Plan Viewer\n\nNo plan found for client: {self.client}\n\nError: {pdf_result['error']}\n\nPlease verify:\n1. The client reference is correct\n2. A plan has been uploaded for this client\n3. Database connection is working"
                self.update_visualizer(error_msg)
                self.update_status("No plan found")
                self.update_pdf_info("No PDF found")
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            error_msg = f"Plan Viewer Error\n\nFailed to load plan from database:\n\nError: {str(e)}\n\nDetailed error:\n{error_details}\n\nPlease check:\n1. Database connection\n2. Client reference format\n3. Database table structure"
            self.show_error(f"Error: {str(e)}")
            self.update_visualizer(error_msg)
            self.update_status("Plan loading failed")
            self.update_pdf_info("Error loading PDF")
			

def obrir_planol(self):
        """Open plan file from database"""
        if not self.client:
            self.show_warning("Please fill in 'Ref. Client' field to open plan files.")
            return
            
        self.update_status("Opening plan file from database...")
        self.update_visualizer(f"Plan File Opener\n\nOpening plan file for client: {self.client}\n\nSearching database...")
        
        try:
            # Import the function to get PDF from database
            from from_sql import get_planol_pdf, save_temp_pdf
            
            # Get PDF data from database
            pdf_result = get_planol_pdf(self.client)
            
            if pdf_result['success']:
                # Save PDF to temporary file
                temp_path = save_temp_pdf(pdf_result['pdf_data'], pdf_result['filename'])
                
                if temp_path:
                    # Open PDF with default system viewer
                    import subprocess
                    import platform
                    
                    try:
                        if platform.system() == 'Windows':
                            os.startfile(temp_path)
                        elif platform.system() == 'Darwin':  # macOS
                            subprocess.run(['open', temp_path])
                        else:  # Linux
                            subprocess.run(['xdg-open', temp_path])
                        
                        success_msg = f"Plan File Opened\n\nPlan file successfully opened!\n\nClient: {self.client}\nPlan Number: {pdf_result['num_planol']}\nFile: {pdf_result['filename']}\n\nThe PDF has been opened in your default PDF viewer.\nTemporary file location: {temp_path}"
                        
                        self.update_visualizer(success_msg)
                        self.update_status("Plan file opened successfully")
                        
                    except Exception as e:
                        error_msg = f"Plan File Error\n\nPDF retrieved from database but failed to open:\n\nError: {str(e)}\n\nThe PDF file has been saved to: {temp_path}\nYou can manually open it with any PDF viewer."
                        self.update_visualizer(error_msg)
                        self.update_status("Plan retrieved but failed to open")
                        
                else:
                    self.show_error("Failed to save PDF to temporary file")
                    self.update_status("Failed to save PDF")
            else:
                error_msg = f"Plan File Error\n\nNo plan found for client: {self.client}\n\nError: {pdf_result['error']}\n\nPlease verify:\n1. The client reference is correct\n2. A plan has been uploaded for this client\n3. Database connection is working"
                self.update_visualizer(error_msg)
                self.update_status("No plan found")
                
        except Exception as e:
            error_msg = f"Plan File Error\n\nFailed to open plan file from database:\n\nError: {str(e)}\n\nPlease check:\n1. Database connection\n2. Client reference format\n3. Database table structure"
            self.show_error(error_msg)
            self.update_visualizer(error_msg)
            self.update_status("Plan file opening failed")
			
			
def load_pdf_preview(self, pdf_data, filename, temp_path):
        """Load PDF preview in the viewer"""
        try:
            # Load PDF in viewer
            success = self.pdf_viewer.load_pdf_from_data(pdf_data, filename)
            
            if success:
                self.current_pdf_path = temp_path
                self.current_pdf_data = pdf_data
                self.update_pdf_info(f"Loaded: {filename}")
                return True
            else:
                self.update_pdf_info("Failed to load PDF")
                return False
        except Exception as e:
            self.show_error(f"Error loading PDF preview: {str(e)}")
            self.update_pdf_info(f"Error: {str(e)}")
            return False
			

class PostgresConn:
    def __init__(self, host, database, user, password, port=5432):
        self.conn_params = {
            'host': host,
            'database': database,
            'user': user,
            'password': password,
            'port': port
        }
        self.connection = None


    def connect(self):
        if self.connection is None or self.connection.closed:
            self.connection = psycopg2.connect(**self.conn_params)
            db_logger.log_connection("CONNECT", f"Connected to {self.conn_params['database']} at {self.conn_params['host']}")
        return self.connection


    def close(self):
        if self.connection and not self.connection.closed:
            self.connection.close()
            self.connection = None
            db_logger.log_connection("DISCONNECT", "Connection closed")


    def execute(self, query, params=None, commit=False):
        conn = self.connect()
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            if commit:
                conn.commit()
                db_logger.log_operation("EXECUTE", query, params, "Query executed and committed")
            else:
                db_logger.log_operation("EXECUTE", query, params, "Query executed")


    def fetchall(self, query, params=None):
        conn = self.connect()
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()
            db_logger.log_select(query, params, len(results))
            return results


    def fetchone(self, query, params=None):
        conn = self.connect()
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchone()
            db_logger.log_select(query, params, 1 if result else 0)
            return result
        