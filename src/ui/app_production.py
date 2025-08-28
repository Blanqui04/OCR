#!/usr/bin/env python3
"""
Production Flask OCR Web Application
Aplicació web de producció per al reconeixement òptic de caràcters
"""

import os
import json
import time
import sys
import logging
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

app = Flask(__name__)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'uploads'))
app.config['OUTPUT_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'output'))
app.config['SECRET_KEY'] = 'ocr-production-key-2025'

# Ensure upload and output directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ocr_app.log'),
        logging.StreamHandler()
    ]
)
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
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error serving index page: {str(e)}")
        return f"Error loading page: {str(e)}", 500

@app.route('/debug')
def debug():
    """Serve the debug interface with enhanced logging"""
    try:
        logger.info("Serving debug page with enhanced client-side logging")
        return render_template('index_debug.html')
    except Exception as e:
        logger.error(f"Error serving debug page: {str(e)}")
        return f"Error loading debug page: {str(e)}", 500

@app.route('/test')
def test_simple():
    """Serve a simple test page for file upload debugging"""
    try:
        logger.info("Serving simple test page")
        return render_template('test_simple.html')
    except Exception as e:
        logger.error(f"Error serving test page: {str(e)}")
        return f"Error loading test page: {str(e)}", 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'upload_folder_exists': os.path.exists(app.config['UPLOAD_FOLDER']),
        'upload_folder_writable': os.access(app.config['UPLOAD_FOLDER'], os.W_OK) if os.path.exists(app.config['UPLOAD_FOLDER']) else False
    })

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads"""
    try:
        logger.info("=== UPLOAD REQUEST START ===")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Content-Type: {request.content_type}")
        logger.info(f"Content-Length: {request.content_length}")
        
        # Check if files are in the request
        if 'files' not in request.files:
            logger.warning("No 'files' key in request.files")
            return jsonify({
                'success': False, 
                'error': 'No s\'han proporcionat fitxers'
            }), 400
        
        files = request.files.getlist('files')
        logger.info(f"Received {len(files)} files")
        
        # Log details of each file
        for i, file in enumerate(files):
            logger.info(f"File {i}: filename='{file.filename}', content_type='{file.content_type}'")
        
        if not files or all(file.filename == '' for file in files):
            logger.warning("No files selected or all filenames empty")
            return jsonify({
                'success': False, 
                'error': 'No s\'han seleccionat fitxers vàlids'
            }), 400
        
        uploaded_files = []
        
        for i, file in enumerate(files):
            logger.info(f"Processing file {i}: {file.filename}")
            
            if not file.filename:
                logger.warning(f"File {i} has empty filename, skipping")
                continue
                
            if not allowed_file(file.filename):
                logger.warning(f"File {i} type not allowed: {file.filename}")
                return jsonify({
                    'success': False, 
                    'error': f'Tipus de fitxer no permès: {file.filename}. Formats suportats: PDF, PNG, JPG, JPEG, TIFF, BMP'
                }), 400
            
            try:
                # Secure the filename
                filename = secure_filename(file.filename)
                if not filename:
                    logger.warning(f"Filename became empty after securing: {file.filename}")
                    return jsonify({
                        'success': False, 
                        'error': f'Nom de fitxer no vàlid: {file.filename}'
                    }), 400
                
                # Add timestamp to avoid conflicts
                timestamp = str(int(time.time() * 1000))  # Use milliseconds for uniqueness
                name, ext = os.path.splitext(filename)
                filename = f"{timestamp}_{name}{ext}"
                
                # Save the file
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                logger.info(f"Saving file to: {filepath}")
                
                file.save(filepath)
                
                # Verify file was saved
                if not os.path.exists(filepath):
                    raise Exception("File was not saved successfully")
                
                file_size = os.path.getsize(filepath)
                logger.info(f"File saved successfully: {filename}, size: {file_size} bytes")
                
                uploaded_files.append({
                    'filename': filename,
                    'original_name': file.filename,
                    'size': file_size,
                    'path': filepath,
                    'type': file.content_type or 'unknown'
                })
                
            except Exception as save_error:
                logger.error(f"Error saving file {file.filename}: {str(save_error)}")
                return jsonify({
                    'success': False, 
                    'error': f'Error guardant el fitxer {file.filename}: {str(save_error)}'
                }), 500
        
        if not uploaded_files:
            return jsonify({
                'success': False, 
                'error': 'No s\'ha pogut guardar cap fitxer'
            }), 400
        
        logger.info(f"Successfully uploaded {len(uploaded_files)} files")
        logger.info("=== UPLOAD REQUEST END ===")
        
        return jsonify({
            'success': True,
            'files': uploaded_files,
            'message': f'S\'han pujat correctament {len(uploaded_files)} fitxers',
            'total_size': sum(f['size'] for f in uploaded_files)
        })
        
    except RequestEntityTooLarge:
        logger.error("File too large")
        return jsonify({
            'success': False, 
            'error': 'Fitxer massa gran. Mida màxima: 16MB'
        }), 413
    except Exception as e:
        logger.error(f"Unexpected upload error: {str(e)}")
        return jsonify({
            'success': False, 
            'error': f'Error inesperat en la pujada: {str(e)}'
        }), 500

@app.route('/process', methods=['POST'])
def process_files():
    """Process uploaded files with OCR"""
    try:
        data = request.get_json()
        logger.info(f"Process request received: {len(data.get('files', [])) if data else 0} files")
        
        if not data or 'files' not in data:
            return jsonify({
                'success': False, 
                'error': 'No hi ha fitxers per processar'
            }), 400
        
        files = data['files']
        options = data.get('options', {})
        
        # Extract processing options
        language = options.get('language', 'eng')
        ocr_mode = options.get('ocr_mode', 'fast')
        output_format = options.get('output_format', 'json')
        table_detection = options.get('table_detection', True)
        force_simulation = options.get('force_simulation', False)  # Option to force simulation mode
        
        logger.info(f"Processing {len(files)} files with options: {options}")
        
        # Import OCR modules for real processing only if not forced to simulate
        use_real_ocr = False
        pipeline = None
        
        if not force_simulation:
            try:
                # Try to import the web-optimized pipeline
                from web_pipeline import create_web_pipeline
                pipeline = create_web_pipeline()
                
                if pipeline and pipeline.is_available():
                    use_real_ocr = True
                    capabilities = pipeline.get_capabilities()
                    logger.info(f"Web OCR pipeline loaded successfully: {capabilities}")
                else:
                    logger.warning("Web pipeline not available - using simulation")
                    use_real_ocr = False
                    
            except ImportError as e:
                logger.warning(f"Web pipeline not available: {e} - trying production pipeline")
                try:
                    # Fallback to production pipeline
                    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
                    from production.enhanced_pipeline import EnhancedOCRPipeline
                    pipeline = EnhancedOCRPipeline()
                    use_real_ocr = True
                    logger.info("Production enhanced pipeline loaded successfully")
                except ImportError as e2:
                    logger.warning(f"Enhanced pipeline not available: {e2} - using simulation")
                    use_real_ocr = False
            except Exception as e:
                logger.error(f"Error loading OCR modules: {e} - falling back to simulation")
                use_real_ocr = False
        else:
            logger.info("Forced simulation mode - skipping real OCR")
        
        # For production, process with real OCR if available
        results = []
        processing_start = time.time()
        
        for i, file_info in enumerate(files):
            try:
                filepath = file_info['path']
                if not os.path.exists(filepath):
                    logger.warning(f"File not found: {filepath}")
                    continue
                
                file_size_mb = file_info['size'] / (1024 * 1024)
                
                if use_real_ocr and pipeline:
                    # Real OCR processing with web pipeline
                    try:
                        logger.info(f"Starting web pipeline processing for: {file_info['original_name']}")
                        
                        # Process document with web pipeline
                        processing_options = {
                            'language': language,
                            'ocr_mode': ocr_mode,
                            'yolo_confidence': 0.3
                        }
                        
                        result = pipeline.process_document(filepath, processing_options)
                        
                        if result.get('error'):
                            logger.error(f"Pipeline processing error: {result['error']}")
                            use_real_ocr = False
                        else:
                            # Extract results from pipeline
                            processing_time = time.time() - processing_start
                            technical_elements = result.get('technical_elements', [])
                            combined_analysis = result.get('combined_analysis', {})
                            
                            results.append({
                                'filename': file_info['original_name'],
                                'result': {
                                    'text': result.get('ocr_text', ''),
                                    'confidence': result.get('ocr_confidence', 0),
                                    'processing_time': processing_time,
                                    'word_count': len(result.get('ocr_text', '').split()),
                                    'technical_elements_found': len(technical_elements),
                                    'technical_elements': technical_elements,
                                    'yolo_detections': len(result.get('yolo_detections', [])),
                                    'language_detected': language,
                                    'ocr_mode_used': ocr_mode,
                                    'combined_analysis': combined_analysis,
                                    'processing_method': 'web_pipeline'
                                },
                                'file_info': {
                                    'size': file_info['size'],
                                    'type': file_info.get('type', 'unknown')
                                }
                            })
                            
                            logger.info(f"Web pipeline processing completed for {file_info['original_name']}: {len(technical_elements)} technical elements found")
                        
                    except Exception as pipeline_error:
                        logger.error(f"Web pipeline processing failed for {file_info['original_name']}: {str(pipeline_error)}")
                        # Fall back to simulation if pipeline fails
                        use_real_ocr = False
                
                if not use_real_ocr:
                    # Enhanced simulation with realistic technical elements
                    import random
                    
                    # Simulate processing time based on file size
                    simulated_processing_time = min(file_size_mb * 0.5 + 1, 10)  # 0.5s per MB + 1s base, max 10s
                    
                    # Simulate realistic results based on filename
                    filename_lower = file_info['original_name'].lower()
                    
                    # Simulate technical elements found
                    technical_elements = []
                    if 'technical' in filename_lower or 'drawing' in filename_lower or '.pdf' in filename_lower:
                        # Simulate finding technical elements
                        element_types = ['cota', 'tolerancia', 'simbol']
                        num_elements = random.randint(2, 8)
                        
                        for _ in range(num_elements):
                            element_type = random.choice(element_types)
                            confidence = random.uniform(0.4, 0.95)
                            technical_elements.append({
                                'type': element_type,
                                'confidence': confidence,
                                'bbox': [
                                    random.randint(50, 300),
                                    random.randint(50, 300),
                                    random.randint(350, 600),
                                    random.randint(350, 600)
                                ],
                                'text_nearby': f'Text prop de {element_type}',
                                'area': random.randint(100, 1000)
                            })
                    
                    # Simulate OCR confidence and text
                    confidence = random.uniform(85, 98)
                    word_count = max(int(file_size_mb * 100 + random.randint(50, 200)), 50)
                    
                    # Create more realistic sample text
                    sample_text = f"""PLÀNOL TÈCNIC - {file_info['original_name']}

ESPECIFICACIONS:
- Dimensions principals: 250 x 150 mm
- Material: Acer inoxidable AISI 316L
- Acabat superficial: Ra 1.6 µm
- Toleràncies generals: ISO 2768-m

ELEMENTS DETECTATS:
"""
                    for element in technical_elements:
                        sample_text += f"- {element['type'].upper()}: confiança {element['confidence']:.1%}\n"
                    
                    sample_text += f"""
NOTES TÈCNIQUES:
- Verificar dimensions crítiques abans de la producció
- Aplicar tractament tèrmic segons especificació
- Control de qualitat segons ISO 9001

Fitxer processat: {file_info['original_name']}
Mida original: {file_size_mb:.2f} MB
Paraules identificades: {word_count}
Elements tècnics: {len(technical_elements)}
Confiança del reconeixement: {confidence:.1f}%

Aquest és un exemple de processament simulat.
En producció, utilitzaria el pipeline OCR + YOLOv8 real.
                    """
                    
                    # Create combined analysis
                    combined_analysis = {
                        'total_elements': len(technical_elements),
                        'element_types': {},
                        'confidence_stats': {},
                        'text_quality': 'good' if word_count > 100 else 'fair'
                    }
                    
                    # Count element types
                    for element in technical_elements:
                        element_type = element['type']
                        if element_type not in combined_analysis['element_types']:
                            combined_analysis['element_types'][element_type] = 0
                        combined_analysis['element_types'][element_type] += 1
                    
                    # Calculate confidence stats
                    if technical_elements:
                        confidences = [e['confidence'] for e in technical_elements]
                        combined_analysis['confidence_stats'] = {
                            'min': min(confidences),
                            'max': max(confidences),
                            'avg': sum(confidences) / len(confidences)
                        }
                    
                    results.append({
                        'filename': file_info['original_name'],
                        'result': {
                            'text': sample_text.strip(),
                            'confidence': confidence,
                            'processing_time': simulated_processing_time,
                            'word_count': word_count,
                            'technical_elements_found': len(technical_elements),
                            'technical_elements': technical_elements,
                            'yolo_detections': len(technical_elements),
                            'tables_found': random.randint(0, 3) if table_detection else 0,
                            'language_detected': language,
                            'ocr_mode_used': ocr_mode,
                            'combined_analysis': combined_analysis,
                            'processing_method': 'enhanced_simulation'
                        },
                        'file_info': {
                            'size': file_info['size'],
                            'type': file_info.get('type', 'unknown')
                        }
                    })
                
                logger.info(f"Processed file {i+1}/{len(files)}: {file_info['original_name']}")
                
            except Exception as e:
                logger.error(f"Error processing {file_info.get('original_name', 'unknown')}: {str(e)}")
                results.append({
                    'filename': file_info.get('original_name', 'unknown'),
                    'error': str(e)
                })
        
        total_processing_time = time.time() - processing_start
        
        # Save results to output folder
        output_filename = f"ocr_results_{int(time.time())}.{output_format}"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        try:
            if output_format == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        'timestamp': time.time(),
                        'processing_options': options,
                        'total_processing_time': total_processing_time,
                        'results': results
                    }, f, ensure_ascii=False, indent=2)
            elif output_format == 'txt':
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(f"OCR Results - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")
                    for result in results:
                        if 'result' in result:
                            f.write(f"=== {result['filename']} ===\n")
                            f.write(f"Text extret:\n{result['result']['text']}\n\n")
                            
                            # Add technical elements if found
                            if 'technical_elements' in result['result']:
                                f.write(f"Elements tècnics detectats ({result['result'].get('technical_elements_found', 0)}):\n")
                                for element in result['result']['technical_elements']:
                                    f.write(f"- {element['type']}: confiança {element['confidence']:.2f}\n")
                                f.write("\n")
                            
                            f.write(f"Confiança: {result['result']['confidence']:.1f}%\n")
                            f.write(f"Paraules: {result['result']['word_count']}\n")
                            f.write(f"Temps processament: {result['result']['processing_time']:.2f}s\n\n")
                        else:
                            f.write(f"=== {result['filename']} (ERROR) ===\n")
                            f.write(f"Error: {result.get('error', 'Unknown error')}\n\n")
            elif output_format == 'csv':
                import csv
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    # Header
                    writer.writerow([
                        'Filename', 'Text', 'Confidence', 'Word_Count', 'Processing_Time',
                        'Technical_Elements_Found', 'Technical_Elements_Detail', 'Processing_Method'
                    ])
                    
                    for result in results:
                        if 'result' in result:
                            technical_detail = '; '.join([
                                f"{elem['type']}({elem['confidence']:.2f})" 
                                for elem in result['result'].get('technical_elements', [])
                            ])
                            
                            writer.writerow([
                                result['filename'],
                                result['result']['text'].replace('\n', ' ').strip(),
                                f"{result['result']['confidence']:.1f}",
                                result['result']['word_count'],
                                f"{result['result']['processing_time']:.2f}",
                                result['result'].get('technical_elements_found', 0),
                                technical_detail or 'None',
                                result['result'].get('processing_method', 'unknown')
                            ])
                        else:
                            writer.writerow([
                                result['filename'], 
                                f"ERROR: {result.get('error', 'Unknown error')}", 
                                0, 0, 0, 0, 'Error', 'error'
                            ])
            
            logger.info(f"Results saved to: {output_path}")
        except Exception as save_error:
            logger.error(f"Error saving results: {str(save_error)}")
        
        return jsonify({
            'success': True,
            'results': results,
            'simulation': not use_real_ocr,
            'processing_time': total_processing_time,
            'output_file': output_filename,
            'download_url': f'/download/{output_filename}',
            'summary': {
                'total_files': len(files),
                'successful_files': len([r for r in results if 'result' in r]),
                'failed_files': len([r for r in results if 'error' in r]),
                'total_words': sum(r['result']['word_count'] for r in results if 'result' in r),
                'total_technical_elements': sum(r['result'].get('technical_elements_found', 0) for r in results if 'result' in r),
                'average_confidence': sum(r['result']['confidence'] for r in results if 'result' in r) / len([r for r in results if 'result' in r]) if any('result' in r for r in results) else 0,
                'processing_methods_used': list(set(r['result'].get('processing_method', 'unknown') for r in results if 'result' in r))
            }
        })
        
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        return jsonify({
            'success': False, 
            'error': f'Error de processament: {str(e)}'
        }), 500

@app.route('/preview', methods=['POST'])
def preview_files():
    """Preview uploaded files before processing"""
    try:
        data = request.get_json()
        logger.info(f"Preview request received for {len(data.get('files', [])) if data else 0} files")
        
        if not data or 'files' not in data:
            return jsonify({
                'success': False, 
                'error': 'No hi ha fitxers per previsualitzar'
            }), 400
        
        files = data['files']
        previews = []
        
        for file_info in files:
            try:
                filepath = file_info['path']
                if not os.path.exists(filepath):
                    logger.warning(f"File not found: {filepath}")
                    continue
                
                file_size_mb = file_info['size'] / (1024 * 1024)
                
                preview_info = {
                    'filename': file_info['original_name'],
                    'size': file_info['size'],
                    'size_formatted': f"{file_size_mb:.2f} MB",
                    'type': file_info.get('type', 'unknown'),
                    'path': filepath,
                    'estimated_processing_time': f"{min(file_size_mb * 0.5 + 1, 10):.1f} segons",
                    'pages_estimated': max(1, int(file_size_mb * 2)) if 'pdf' in file_info['original_name'].lower() else 1
                }
                
                previews.append(preview_info)
                
            except Exception as e:
                logger.error(f"Error previewing {file_info.get('original_name', 'unknown')}: {str(e)}")
                previews.append({
                    'filename': file_info.get('original_name', 'unknown'),
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'previews': previews,
            'total_files': len(previews),
            'total_size': sum(p.get('size', 0) for p in previews if 'size' in p),
            'estimated_total_time': sum(float(p.get('estimated_processing_time', '0').split()[0]) for p in previews if 'estimated_processing_time' in p)
        })
        
    except Exception as e:
        logger.error(f"Preview error: {str(e)}")
        return jsonify({
            'success': False, 
            'error': f'Error de previsualització: {str(e)}'
        }), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download processed results"""
    try:
        filepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': 'Fitxer no trobat'}), 404
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({'error': f'Error de descàrrega: {str(e)}'}), 500

@app.route('/cleanup', methods=['POST'])
def cleanup_files():
    """Clean up uploaded files"""
    try:
        data = request.get_json()
        files_to_remove = data.get('files', [])
        
        removed_files = []
        for file_info in files_to_remove:
            filename = file_info.get('filename')
            if filename:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
                    removed_files.append(filename)
                    logger.info(f"Removed file: {filename}")
        
        return jsonify({
            'success': True,
            'removed_files': removed_files,
            'message': f'S\'han eliminat {len(removed_files)} fitxers'
        })
        
    except Exception as e:
        logger.error(f"Cleanup error: {str(e)}")
        return jsonify({
            'success': False, 
            'error': f'Error de neteja: {str(e)}'
        }), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({
        'success': False, 
        'error': 'Fitxer massa gran. Mida màxima: 16MB'
    }), 413

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/') or request.path.startswith('/upload'):
        return jsonify({'error': 'Endpoint no trobat'}), 404
    return render_template('index.html')  # Serve the main app for any other 404

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({'error': 'Error intern del servidor'}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 STARTING OCR PRODUCTION WEB APPLICATION")
    print("=" * 60)
    print(f"📁 Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"📂 Output folder: {app.config['OUTPUT_FOLDER']}")
    print(f"📁 Upload folder exists: {os.path.exists(app.config['UPLOAD_FOLDER'])}")
    print(f"✍️  Upload folder writable: {os.access(app.config['UPLOAD_FOLDER'], os.W_OK) if os.path.exists(app.config['UPLOAD_FOLDER']) else False}")
    print("=" * 60)
    print("🌐 Application will be available at:")
    print("   • Local: http://localhost:5000")
    print("   • Network: http://0.0.0.0:5000")
    print("=" * 60)
    print("📊 Health check: http://localhost:5000/health")
    print("🔧 Debug info available in console and ocr_app.log")
    print("=" * 60)
    
    try:
        app.run(
            debug=False,  # Set to False for production
            host='0.0.0.0',
            port=5000,
            threaded=True,
            use_reloader=False  # Disable reloader for stability
        )
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        print(f"❌ Failed to start application: {str(e)}")
        sys.exit(1)
