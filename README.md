# Professional OCR Viewer

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Google Cloud](https://img.shields.io/badge/Google%20Cloud-Document%20AI-4285F4.svg)](https://cloud.google.com/document-ai)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A professional Windows desktop application for visualizing Google Cloud Document AI results with PDF rendering and interactive text bounding boxes overlay, similar to the Google Cloud Document AI demo interface.

![OCR Viewer Screenshot](docs/screenshot.png)

## 🚀 Features

### 📄 PDF Visualization
- High-quality PDF rendering using PyMuPDF
- Zoom controls (in, out, fit-to-window)
- Multi-page navigation
- Interactive canvas with smooth scrolling

### 🤖 Document AI Integration
- Google Cloud Document AI processing
- Real-time text extraction
- Confidence scoring for extracted text
- Robust error handling and fallback methods

### 🎯 Interactive Text Analysis
- **Bounding box overlays** on PDF (just like Google's demo!)
- **Color-coded confidence levels:**
  - 🟢 Green: High confidence (>90%)
  - 🟠 Orange: Medium confidence (70-90%)
  - 🔴 Red: Low confidence (<70%)
  - 🔵 Blue: Selected text block
- Click-to-select text blocks
- Hover effects and cursor changes

### 📊 Comprehensive Analysis Views
- **Full Text Tab:** Complete extracted text with search functionality
- **Text Blocks Tab:** Detailed listing with confidence scores and coordinates
- **Statistics Tab:** Document metrics and analysis

### 💾 Export Capabilities
- Export full text to .txt files
- Export structured data to JSON with coordinates and confidence scores
- **Export to CSV** with detailed metrics (coordinates, confidence, dimensions)
- **Export PDF reports** with professional tables, statistics, and analysis
- Professional file dialogs

### 🎨 Professional Interface
- Modern Windows tkinter GUI
- Tabbed content organization
- Toolbar with intuitive controls
- Status bar with progress updates
- Keyboard shortcuts for efficiency

## 📋 Requirements

- **Operating System:** Windows 10/11
- **Python:** 3.7 or higher
- **Google Cloud:** Authentication configured
- **Internet:** Required for Document AI processing

## 🛠️ Installation

### Option 1: Quick Setup (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/professional-ocr-viewer.git
   cd professional-ocr-viewer
   ```

2. **Run the setup script:**
   ```bash
   setup.bat
   ```

3. **Configure Google Cloud:**
   - Install [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
   - Run: `gcloud auth application-default login`
   - Set project: `gcloud config set project YOUR_PROJECT_ID`

4. **Launch the application:**
   ```bash
   OCR_Viewer.bat
   ```

### Option 2: Manual Setup

1. **Create virtual environment:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your project settings** in `ocr_viewer_app.py`:
   ```python
   self.project_id = "your-project-id"
   self.location = "your-location"  # e.g., "us" or "eu"
   self.processor_id = "your-processor-id"
   ```

4. **Run the application:**
   ```bash
   python launch_ocr_viewer.py
   ```

## 🎯 Quick Start

1. **Launch the application** using `OCR_Viewer.bat`

2. **Open a PDF file:**
   - Click "Open PDF" button or use `Ctrl+O`
   - Select your PDF file from the dialog

3. **Process with Document AI:**
   - Click "Process Document" button or use `Ctrl+P`
   - Wait for Google Cloud processing to complete

4. **Explore the results:**
   - View text overlays on the PDF
   - Click on text blocks to select them
   - Browse through different analysis tabs
   - Search within extracted text
   - Export results as needed

## 🖥️ Interface Overview

### Main Window Layout

- **Left Panel**: PDF Viewer with interactive overlay visualization
- **Right Panel**: Tabbed analysis view
  - **Full Text**: Complete extracted text with search functionality
  - **Text Blocks**: Detailed block listing with confidence scores
  - **Statistics**: Document metrics and analysis

### Toolbar Controls

- **Open PDF**: Load PDF file for processing
- **Process Document**: Send to Google Cloud Document AI
- **Zoom In/Out**: Adjust PDF display size
- **Fit Window**: Auto-fit PDF to window size
- **Page Navigation**: Navigate through multi-page documents

### Color Coding System

- **🟢 Green**: High confidence text (>90%)
- **🟠 Orange**: Medium confidence text (70-90%)
- **🔴 Red**: Low confidence text (<70%)
- **🔵 Blue**: Currently selected text block

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Open PDF file |
| `Ctrl+P` | Process document |
| `Ctrl++` | Zoom in |
| `Ctrl+-` | Zoom out |
| `Ctrl+0` | Fit to window |

## 📂 Project Structure

```
professional-ocr-viewer/
├── 📄 OCR_Viewer.bat          # Main application launcher
├── 📄 launch_ocr_viewer.py    # Application launcher with checks
├── 📄 ocr_viewer_app.py       # Main application code
├── 📄 test_ocr.py             # Simple testing script
├── 📄 requirements.txt        # Python dependencies
├── 📄 setup.bat               # Automated setup script
├── 📄 README.md               # This file
├── 📄 LICENSE                 # MIT License
├── 📁 docs/                   # Documentation
│   ├── 📄 setup-guide.md      # Detailed setup instructions
│   ├── 📄 troubleshooting.md  # Common issues and solutions
│   └── 🖼️ screenshot.png      # Application screenshot
└── 📁 examples/               # Example files
    └── 📄 sample.pdf          # Sample PDF for testing
```

## 🔧 Configuration

### Google Cloud Settings

Edit the configuration in `ocr_viewer_app.py`:

```python
# Google Cloud settings
self.project_id = "your-project-id"
self.location = "eu"  # or "us", "asia-northeast1", etc.
self.processor_id = "your-processor-id"
```

### Supported Document Types

- PDF files (`.pdf`)
- Images (`.png`, `.jpg`, `.jpeg`, `.tiff`, `.bmp`)
- Other formats supported by Google Cloud Document AI

## 💾 Export Options

### Text Export
- **Format**: Plain text (`.txt`)
- **Content**: All extracted text organized by pages
- **Use case**: Simple text analysis, copy-paste operations

### JSON Export
- **Format**: Structured JSON (`.json`)
- **Content**: Complete data including:
  - Text content for each block
  - Confidence scores
  - Bounding box coordinates
  - Page numbers
- **Use case**: Further processing, integration with other tools

## 🔍 Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Ensure Google Cloud SDK is installed
   - Run `gcloud auth application-default login`
   - Verify project ID is correct

2. **Import Errors**
   - Check virtual environment is activated
   - Install missing dependencies: `pip install -r requirements.txt`

3. **PDF Loading Issues**
   - Verify file permissions
   - Check file format is supported
   - Ensure file is not corrupted

4. **Processing Failures**
   - Check internet connection
   - Verify Google Cloud quotas
   - Ensure Document AI API is enabled

See [docs/troubleshooting.md](docs/troubleshooting.md) for detailed solutions.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Cloud Document AI** for the powerful OCR capabilities
- **PyMuPDF** for excellent PDF rendering
- **tkinter** for the cross-platform GUI framework
- **Pillow** for image processing capabilities

## 📞 Support

If you encounter any issues or have questions:

1. Check the [troubleshooting guide](docs/troubleshooting.md)
2. Search existing [GitHub issues](https://github.com/your-username/professional-ocr-viewer/issues)
3. Create a new issue with detailed information

## 🔄 Changelog

### v1.0.0 (2025-01-17)
- Initial release
- PDF viewing with zoom and navigation
- Google Cloud Document AI integration
- Interactive text block visualization
- Professional Windows interface
- Export capabilities (TXT, JSON)
- Comprehensive error handling

---

**Professional OCR Viewer v1.0**  
*Powered by Google Cloud Document AI*
