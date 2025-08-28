#!/usr/bin/env python3
"""
Simple HTTP Server for Testing File Upload
"""

import http.server
import socketserver
import json
import os
from urllib.parse import parse_qs
import cgi

class UploadHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Test Upload</title>
                <style>
                    body { font-family: Arial; margin: 40px; }
                    .upload-area { 
                        border: 2px dashed #ccc; 
                        padding: 40px; 
                        text-align: center;
                        margin: 20px 0;
                    }
                    .file-list { margin: 20px 0; }
                </style>
            </head>
            <body>
                <h1>Test d'Upload de Fitxers</h1>
                
                <div class="upload-area" id="uploadArea">
                    <p>Arrossega fitxers aquí o fes clic per seleccionar</p>
                    <input type="file" id="fileInput" multiple accept=".pdf,.png,.jpg,.jpeg">
                </div>
                
                <div class="file-list" id="fileList"></div>
                <button onclick="uploadFiles()">Pujar Fitxers</button>
                
                <div id="result"></div>
                
                <script>
                    let selectedFiles = [];
                    
                    document.getElementById('uploadArea').onclick = () => {
                        document.getElementById('fileInput').click();
                    };
                    
                    document.getElementById('fileInput').onchange = (e) => {
                        selectedFiles = Array.from(e.target.files);
                        displayFiles();
                    };
                    
                    document.getElementById('uploadArea').ondragover = (e) => {
                        e.preventDefault();
                        e.target.style.backgroundColor = '#f0f0f0';
                    };
                    
                    document.getElementById('uploadArea').ondragleave = (e) => {
                        e.target.style.backgroundColor = '';
                    };
                    
                    document.getElementById('uploadArea').ondrop = (e) => {
                        e.preventDefault();
                        e.target.style.backgroundColor = '';
                        selectedFiles = Array.from(e.dataTransfer.files);
                        displayFiles();
                    };
                    
                    function displayFiles() {
                        const fileList = document.getElementById('fileList');
                        fileList.innerHTML = '<h3>Fitxers seleccionats:</h3>';
                        selectedFiles.forEach((file, index) => {
                            fileList.innerHTML += `<p>${index + 1}. ${file.name} (${(file.size/1024).toFixed(1)} KB)</p>`;
                        });
                    }
                    
                    function uploadFiles() {
                        if (selectedFiles.length === 0) {
                            alert('Selecciona fitxers primer');
                            return;
                        }
                        
                        const formData = new FormData();
                        selectedFiles.forEach(file => {
                            formData.append('files', file);
                        });
                        
                        document.getElementById('result').innerHTML = 'Pujant fitxers...';
                        
                        fetch('/upload', {
                            method: 'POST',
                            body: formData
                        })
                        .then(response => response.json())
                        .then(data => {
                            document.getElementById('result').innerHTML = 
                                '<h3>Resultat:</h3><pre>' + JSON.stringify(data, null, 2) + '</pre>';
                        })
                        .catch(error => {
                            document.getElementById('result').innerHTML = 
                                '<h3>Error:</h3><p style="color: red;">' + error + '</p>';
                        });
                    }
                </script>
            </body>
            </html>
            '''
            self.wfile.write(html.encode())
            
        elif self.path == '/debug':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            upload_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'uploads')
            debug_info = {
                'upload_directory': os.path.abspath(upload_dir),
                'upload_directory_exists': os.path.exists(upload_dir),
                'upload_directory_writable': os.access(upload_dir, os.W_OK) if os.path.exists(upload_dir) else False,
                'current_directory': os.getcwd(),
                'python_version': os.sys.version
            }
            
            self.wfile.write(json.dumps(debug_info, indent=2).encode())
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/upload':
            try:
                # Parse the form data
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST'}
                )
                
                upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'uploads'))
                os.makedirs(upload_dir, exist_ok=True)
                
                uploaded_files = []
                
                if 'files' in form:
                    files = form['files']
                    if not isinstance(files, list):
                        files = [files]
                    
                    for file_item in files:
                        if file_item.filename:
                            filename = file_item.filename
                            filepath = os.path.join(upload_dir, filename)
                            
                            with open(filepath, 'wb') as f:
                                f.write(file_item.file.read())
                            
                            uploaded_files.append({
                                'filename': filename,
                                'size': os.path.getsize(filepath),
                                'path': filepath
                            })
                
                response = {
                    'success': True,
                    'message': f'Uploaded {len(uploaded_files)} files successfully',
                    'files': uploaded_files,
                    'upload_directory': upload_dir
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response, indent=2).encode())
                
            except Exception as e:
                error_response = {
                    'success': False,
                    'error': str(e),
                    'type': type(e).__name__
                }
                
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(error_response, indent=2).encode())

if __name__ == '__main__':
    PORT = 8000
    
    # Ensure upload directory exists
    upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'uploads'))
    os.makedirs(upload_dir, exist_ok=True)
    
    print(f"Starting simple upload test server on port {PORT}")
    print(f"Upload directory: {upload_dir}")
    print(f"Go to: http://localhost:{PORT}")
    print(f"Debug info: http://localhost:{PORT}/debug")
    
    with socketserver.TCPServer(("", PORT), UploadHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped by user")
