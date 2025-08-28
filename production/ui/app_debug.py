#!/usr/bin/env python3
"""
Simple Flask OCR Web Application - Debug Version
"""

import os
import json
import time
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import logging

app = Flask(__name__)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'uploads'))
app.config['OUTPUT_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'output'))
app.config['SECRET_KEY'] = 'debug-key'

# Ensure upload and output directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
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

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads - Debug version"""
    try:
        logger.info("=== UPLOAD REQUEST START ===")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request files keys: {list(request.files.keys())}")
        logger.info(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
        logger.info(f"Upload folder exists: {os.path.exists(app.config['UPLOAD_FOLDER'])}")
        
        if 'files' not in request.files:
            logger.warning("No 'files' key in request.files")
            return jsonify({'success': False, 'error': 'No s\'han proporcionat fitxers'}), 400
        
        files = request.files.getlist('files')
        logger.info(f"Received {len(files)} files")
        
        for i, file in enumerate(files):
            logger.info(f"File {i}: filename='{file.filename}', content_type='{file.content_type}'")
        
        if not files or all(file.filename == '' for file in files):
            logger.warning("No files selected or all filenames empty")
            return jsonify({'success': False, 'error': 'No s\'han seleccionat fitxers'}), 400
        
        uploaded_files = []
        for i, file in enumerate(files):
            logger.info(f"Processing file {i}: {file.filename}")
            
            if not file.filename:
                logger.warning(f"File {i} has empty filename")
                continue
                
            if not allowed_file(file.filename):
                logger.warning(f"File {i} type not allowed: {file.filename}")
                return jsonify({'success': False, 'error': f'Tipus de fitxer no permès: {file.filename}'}), 400
            
            try:
                filename = secure_filename(file.filename)
                if not filename:
                    logger.warning(f"Filename became empty after securing: {file.filename}")
                    return jsonify({'success': False, 'error': f'Nom de fitxer no vàlid: {file.filename}'}), 400
                
                # Add timestamp to avoid conflicts
                timestamp = str(int(time.time()))
                filename = f"{timestamp}_{filename}"
                
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                logger.info(f"Saving file to: {filepath}")
                
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
                logger.error(f"Error saving file {file.filename}: {str(save_error)}")
                return jsonify({'success': False, 'error': f'Error guardant el fitxer: {str(save_error)}'}), 500
        
        logger.info(f"Successfully uploaded {len(uploaded_files)} files")
        logger.info("=== UPLOAD REQUEST END ===")
        
        return jsonify({
            'success': True,
            'files': uploaded_files,
            'message': f'S\'han pujat correctament {len(uploaded_files)} fitxers'
        })
        
    except RequestEntityTooLarge:
        logger.error("File too large")
        return jsonify({'success': False, 'error': 'Fitxer massa gran. Mida màxima: 16MB.'}), 413
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({'success': False, 'error': f'Error en la pujada: {str(e)}'}), 500

@app.route('/process', methods=['POST'])
def process_files():
    """Process uploaded files - Simulation"""
    try:
        data = request.get_json()
        logger.info(f"Process request: {data}")
        
        if not data or 'files' not in data:
            return jsonify({'success': False, 'error': 'No files to process'}), 400
        
        files = data['files']
        
        # Simulate processing
        import random
        results = []
        
        for file_info in files:
            sample_text = f"""
Text extret del fitxer: {file_info['original_name']}

Aquest és un exemple de text OCR simulat.
Paràgrafs detectats: 2
Paraules: {random.randint(50, 200)}
            """
            
            results.append({
                'filename': file_info['original_name'],
                'result': {
                    'text': sample_text.strip(),
                    'confidence': random.uniform(85, 98),
                    'processing_time': random.uniform(1, 3),
                    'word_count': random.randint(50, 200),
                    'tables_found': random.randint(0, 2)
                }
            })
        
        return jsonify({
            'success': True,
            'results': results,
            'simulation': True
        })
        
    except Exception as e:
        logger.error(f"Process error: {str(e)}")
        return jsonify({'success': False, 'error': f'Error de processament: {str(e)}'}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'success': False, 'error': 'Fitxer massa gran. Mida màxima: 16MB.'}), 413

if __name__ == '__main__':
    print("=== OCR DEBUG APPLICATION ===")
    print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"Upload folder exists: {os.path.exists(app.config['UPLOAD_FOLDER'])}")
    print(f"Output folder: {app.config['OUTPUT_FOLDER']}")
    print("Starting debug server on http://localhost:5001")
    print("Test debug info at: http://localhost:5001/debug")
    
    app.run(debug=True, host='127.0.0.1', port=5001)
