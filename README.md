# Professional OCR Viewer Application

A professional Windows desktop application for visualizing Google Cloud Document AI results with PDF rendering and interactive text bounding boxes overlay.

## Features

🔍 **PDF Viewing**
- High-quality PDF rendering with zoom controls
- Multi-page navigation
- Fit-to-window functionality

📄 **Document AI Integration**
- Google Cloud Document AI processing
- Real-time text extraction
- Confidence scoring for extracted text

🎯 **Interactive Visualization**
- Text block bounding boxes overlay
- Color-coded confidence indicators
- Click-to-select text blocks
- Hover effects and cursor changes

📊 **Text Analysis**
- Full text view with search functionality
- Detailed text blocks listing
- Document statistics and metrics
- Export capabilities (TXT, JSON)

🎨 **Professional UI**
- Modern Windows interface
- Tabbed content organization
- Keyboard shortcuts
- Status bar with progress updates

## Quick Start

1. **Launch the application:**
   ```
   python launch_ocr_viewer.py
   ```

2. **Open a PDF file:**
   - Click "Open PDF" button or use Ctrl+O
   - Select your PDF file

3. **Process with Document AI:**
   - Click "Process Document" button or use Ctrl+P
   - Wait for processing to complete

4. **Explore the results:**
   - View text overlays on the PDF
   - Browse text blocks in the right panel
   - Search through extracted text
   - Export results as needed

## Interface Overview

### Main Window Layout

- **Left Panel**: PDF Viewer with overlay visualization
- **Right Panel**: Tabbed analysis view
  - **Full Text**: Complete extracted text with search
  - **Text Blocks**: Detailed block listing with confidence scores
  - **Statistics**: Document metrics and analysis

### Toolbar Controls

- **Open PDF**: Load PDF file for processing
- **Process Document**: Send to Google Cloud Document AI
- **Zoom In/Out**: Adjust PDF display size
- **Fit Window**: Auto-fit PDF to window size
- **Page Navigation**: Navigate through multi-page documents

### Color Coding

- **Green**: High confidence text (>90%)
- **Orange**: Medium confidence text (70-90%)
- **Red**: Low confidence text (<70%)
- **Blue**: Currently selected text block

## Keyboard Shortcuts

- `Ctrl+O`: Open PDF file
- `Ctrl+P`: Process document
- `Ctrl++`: Zoom in
- `Ctrl+-`: Zoom out
- `Ctrl+0`: Fit to window

## Export Options

- **Text Export**: Save all extracted text to .txt file
- **JSON Export**: Save structured data with coordinates and confidence scores

## System Requirements

- Windows 10/11
- Python 3.7+
- Google Cloud authentication configured
- Internet connection for Document AI processing

## Configuration

The application is pre-configured with your Google Cloud settings:
- Project ID: `natural-bison-465607-b6`
- Location: `eu`
- Processor ID: `4369d16f70cb0a26`

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed via pip
2. **Authentication Errors**: Verify Google Cloud SDK setup
3. **PDF Loading Issues**: Check file permissions and format
4. **Processing Failures**: Verify internet connection and API quotas

### Support

For technical support or feature requests, please refer to the Google Cloud Document AI documentation or contact your system administrator.

---

**Professional OCR Viewer v1.0**  
*Powered by Google Cloud Document AI*
