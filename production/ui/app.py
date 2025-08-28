#!/usr/bin/env python3
"""
Flask OCR Web Application
Aplicació web per al reconeixement òptic de caràcters
"""

import os
import json
import time
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import sys
import logging

# Add the parent directory to the path to import our OCR modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our OCR processing modules
try:
    from pipeline import OCRPipeline
    from ai_enhanced_pipeline import EnhancedOCRPipeline
    from integrator import DataIntegrator
except ImportError as e:
    print(f"Warning: Could not import OCR modules: {e}")
    print("Some functionality may be limited.")

app = Flask(__name__)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'uploads')
app.config['OUTPUT_FOLDER'] = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'output')
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this in production

# Ensure upload and output directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'tiff', 'bmp', 'gif'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Serve the main interface"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads"""
    try:
        logger.info("Upload request received")
        
        if 'files' not in request.files:
            logger.warning("No files provided in request")
            return jsonify({'error': 'No s\'han proporcionat fitxers'}), 400
        
        files = request.files.getlist('files')
        logger.info(f"Received {len(files)} files")
        
        if not files or all(file.filename == '' for file in files):
            logger.warning("No files selected")
            return jsonify({'error': 'No s\'han seleccionat fitxers'}), 400
        
        uploaded_files = []
        for file in files:
            logger.info(f"Processing file: {file.filename}, size: {file.content_length if hasattr(file, 'content_length') else 'unknown'}")
            
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                if not filename:
                    logger.warning(f"Invalid filename after securing: {file.filename}")
                    return jsonify({'error': f'Nom de fitxer no vàlid: {file.filename}'}), 400
                
                # Add timestamp to avoid conflicts
                timestamp = str(int(time.time()))
                filename = f"{timestamp}_{filename}"
                
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                try:
                    file.save(filepath)
                    file_size = os.path.getsize(filepath)
                    logger.info(f"File saved successfully: {filename}, size: {file_size}")
                    
                    uploaded_files.append({
                        'filename': filename,
                        'original_name': file.filename,
                        'size': file_size,
                        'path': filepath
                    })
                    
                except Exception as save_error:
                    logger.error(f"Error saving file {filename}: {str(save_error)}")
                    return jsonify({'error': f'Error guardant el fitxer {file.filename}: {str(save_error)}'}), 500
                    
            else:
                logger.warning(f"File type not allowed: {file.filename}")
                return jsonify({'error': f'Tipus de fitxer no permès: {file.filename}. Formats suportats: PDF, PNG, JPG, JPEG, TIFF, BMP'}), 400
        
        logger.info(f"Successfully uploaded {len(uploaded_files)} files")
        return jsonify({
            'success': True,
            'files': uploaded_files,
            'message': f'S\'han pujat correctament {len(uploaded_files)} fitxers'
        })
        
    except RequestEntityTooLarge:
        logger.error("File too large")
        return jsonify({'error': 'Fitxer massa gran. Mida màxima: 16MB.'}), 413
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': f'Error en la pujada: {str(e)}'}), 500

@app.route('/process', methods=['POST'])
def process_files():
    """Process uploaded files with OCR"""
    try:
        data = request.get_json()
        if not data or 'files' not in data:
            return jsonify({'error': 'No files to process'}), 400
        
        files = data['files']
        options = data.get('options', {})
        
        # Extract processing options
        language = options.get('language', 'eng')
        ocr_mode = options.get('ocr_mode', 'fast')
        output_format = options.get('output_format', 'json')
        table_detection = options.get('table_detection', True)
        
        logger.info(f"Processing {len(files)} files with options: {options}")
        
        # Initialize OCR pipeline
        try:
            if ocr_mode == 'enhanced':
                pipeline = EnhancedOCRPipeline()
            else:
                pipeline = OCRPipeline()
        except:
            # Fallback to basic processing if modules not available
            return simulate_processing(files, options)
        
        results = []
        for i, file_info in enumerate(files):
            try:
                # Update progress (this would be sent via WebSocket in a real implementation)
                progress = int((i / len(files)) * 100)
                
                filepath = file_info['path']
                if not os.path.exists(filepath):
                    continue
                
                # Process the file
                if ocr_mode == 'enhanced':
                    result = pipeline.process_enhanced(
                        filepath, 
                        language=language,
                        extract_tables=table_detection
                    )
                else:
                    result = pipeline.process_document(
                        filepath,
                        language=language,
                        extract_tables=table_detection
                    )
                
                results.append({
                    'filename': file_info['original_name'],
                    'result': result,
                    'confidence': result.get('confidence', 0.95),
                    'processing_time': result.get('processing_time', 0)
                })
                
            except Exception as e:
                logger.error(f"Error processing {file_info['filename']}: {str(e)}")
                results.append({
                    'filename': file_info['original_name'],
                    'error': str(e)
                })
        
        # Save results
        output_filename = f"ocr_results_{int(time.time())}.{output_format}"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        if output_format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
        elif output_format == 'txt':
            with open(output_path, 'w', encoding='utf-8') as f:
                for result in results:
                    if 'result' in result:
                        f.write(f"=== {result['filename']} ===\n")
                        f.write(result['result'].get('text', '') + '\n\n')
        
        return jsonify({
            'success': True,
            'results': results,
            'output_file': output_filename,
            'download_url': f'/download/{output_filename}'
        })
        
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

def simulate_processing(files, options):
    """Simulate OCR processing when modules are not available"""
    import random
    
    results = []
    for file_info in files:
        # Simulate processing time
        time.sleep(0.1)
        
        sample_text = f"""
Resultats simulats per al fitxer: {file_info['original_name']}

Aquest és un text d'exemple generat per demostrar el funcionament
de la interfície OCR. En una implementació real, aquest text seria
el resultat del reconeixement òptic de caràcters del document processat.

Paràgrafs detectats: 2
Paraules extretes: {random.randint(50, 200)}
Confiança: {random.uniform(85, 98):.1f}%

Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
        """
        
        results.append({
            'filename': file_info['original_name'],
            'result': {
                'text': sample_text.strip(),
                'confidence': random.uniform(85, 98),
                'processing_time': random.uniform(1, 5),
                'word_count': random.randint(50, 200),
                'tables_found': random.randint(0, 3) if options.get('table_detection') else 0
            }
        })
    
    return jsonify({
        'success': True,
        'results': results,
        'simulation': True,
        'message': 'Results generated by simulation (OCR modules not available)'
    })

@app.route('/download/<filename>')
def download_file(filename):
    """Download processed results"""
    try:
        filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.route('/preview/<filename>')
def preview_file(filename):
    """Preview uploaded file (for images)"""
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            return send_file(filepath)
        else:
            return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        logger.error(f"Preview error: {str(e)}")
        return jsonify({'error': f'Preview failed: {str(e)}'}), 500

@app.route('/debug')
def debug_info():
    """Debug information endpoint"""
    try:
        upload_dir_exists = os.path.exists(app.config['UPLOAD_FOLDER'])
        upload_dir_writable = os.access(app.config['UPLOAD_FOLDER'], os.W_OK) if upload_dir_exists else False
        
        return jsonify({
            'upload_folder': app.config['UPLOAD_FOLDER'],
            'upload_folder_exists': upload_dir_exists,
            'upload_folder_writable': upload_dir_writable,
            'output_folder': app.config['OUTPUT_FOLDER'],
            'max_content_length': app.config['MAX_CONTENT_LENGTH'],
            'allowed_extensions': list(ALLOWED_EXTENSIONS),
            'current_time': time.time()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/status')
def get_status():
    """Get application status"""
    try:
        # Check if OCR modules are available
        ocr_available = True
        try:
            from pipeline import OCRPipeline
            from ai_enhanced_pipeline import EnhancedOCRPipeline
        except ImportError:
            ocr_available = False
        
        return jsonify({
            'status': 'online',
            'ocr_modules_available': ocr_available,
            'upload_folder': app.config['UPLOAD_FOLDER'],
            'max_file_size': app.config['MAX_CONTENT_LENGTH'],
            'allowed_extensions': list(ALLOWED_EXTENSIONS)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/cleanup', methods=['POST'])
def cleanup_files():
    """Clean up old uploaded files"""
    try:
        data = request.get_json()
        files_to_remove = data.get('files', [])
        
        removed_files = []
        for filename in files_to_remove:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                removed_files.append(filename)
                logger.info(f"Removed file: {filename}")
        
        return jsonify({
            'success': True,
            'removed_files': removed_files,
            'message': f'Removed {len(removed_files)} files'
        })
        
    except Exception as e:
        logger.error(f"Cleanup error: {str(e)}")
        return jsonify({'error': f'Cleanup failed: {str(e)}'}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create templates directory and copy HTML file
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    # Copy index.html to templates directory if it doesn't exist there
    html_source = os.path.join(os.path.dirname(__file__), 'index.html')
    html_dest = os.path.join(templates_dir, 'index.html')
    
    if os.path.exists(html_source) and not os.path.exists(html_dest):
        import shutil
        shutil.copy2(html_source, html_dest)
        print(f"Copied index.html to templates directory")
    
    # Create static directory for CSS
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    os.makedirs(static_dir, exist_ok=True)
    
    # Copy style.css to static directory if it doesn't exist there
    css_source = os.path.join(os.path.dirname(__file__), 'style.css')
    css_dest = os.path.join(static_dir, 'style.css')
    
    if os.path.exists(css_source) and not os.path.exists(css_dest):
        import shutil
        shutil.copy2(css_source, css_dest)
        print(f"Copied style.css to static directory")
    
    print("Starting OCR Web Application...")
    print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"Output folder: {app.config['OUTPUT_FOLDER']}")
    print("Open your browser and go to: http://localhost:5000")
    
    # Run the Flask development server
    app.run(debug=True, host='0.0.0.0', port=5000)