# OCR Viewer - Professional Document Analysis

A modern, professional OCR (Optical Character Recognition) application built from scratch with Python and Google Cloud Document AI integration.

## 🚀 Features

### Core Functionality
- **PDF Visualization**: High-quality PDF rendering with zoom and navigation
- **Google Cloud OCR**: Integration with Google Cloud Document AI for accurate text extraction
- **Interactive Overlays**: Visual text block overlays with confidence level color coding
- **Modern UI**: Clean, professional interface with modern theme
- **Multi-format Export**: Export results to TXT, JSON, CSV, and PDF formats

### Advanced Features
- **Confidence Analysis**: Color-coded confidence levels (High/Medium/Low)
- **Text Search**: Search functionality within extracted text
- **Statistics**: Comprehensive analysis and statistics
- **Batch Processing**: Process multiple documents
- **Zoom Controls**: Zoom in/out, fit to window
- **Page Navigation**: Easy navigation through multi-page documents

## 📋 Requirements

- Python 3.7 or later
- Windows 10/11 (tested)
- Google Cloud account with Document AI enabled (optional but recommended)

## 🛠️ Installation

### Quick Setup

1. **Clone or Download** this repository
2. **Run the setup script**:
   ```bash
   setup_new.bat
   ```
3. **Start the application**:
   ```bash
   run_ocr_viewer.bat
   ```

### Manual Setup

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements_new.txt
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

## 🔧 Google Cloud Setup (Optional)

1. **Create a Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one

2. **Enable Document AI API**:
   - Navigate to APIs & Services → Library
   - Search for "Document AI API" and enable it

3. **Create a Processor**:
   - Go to Document AI → Processors
   - Create a new processor (choose "Form Parser" or "OCR")
   - Note the Processor ID

4. **Create Service Account**:
   - Go to IAM & Admin → Service Accounts
   - Create new service account
   - Download the JSON key file
   - Place it in the `docs/` folder

5. **Configure the Application**:
   - Open the Settings tab in the application
   - Enter your Project ID, Location, and Processor ID
   - Test the connection

## 📁 Project Structure

```
OCR/
├── main.py                    # Application entry point
├── ocr_viewer.py             # Main application class
├── ui_theme.py               # Modern UI theme
├── pdf_handler.py            # PDF operations
├── google_ocr.py             # Google Cloud Document AI integration
├── data_exporter.py          # Export functionality
├── requirements_new.txt      # Python dependencies
├── setup_new.bat            # Setup script
├── run_ocr_viewer.bat       # Launch script
├── config_template.json     # Configuration template
└── docs/                    # Documentation and credentials
    └── [your-credentials].json
```

## 🎯 Usage

### Basic Usage

1. **Open a PDF**:
   - Click "Open PDF" or use File → Open PDF
   - Select your PDF file

2. **Process with OCR**:
   - Click "Process Page" to analyze current page
   - Or "Process All" for all pages

3. **View Results**:
   - See extracted text in the "Extracted Text" tab
   - View text blocks with coordinates in "Text Blocks" tab
   - Check statistics in "Statistics" tab

4. **Export Results**:
   - Use File menu to export as TXT, JSON, or CSV
   - Generate PDF reports with analysis

### Advanced Features

- **Confidence Overlay**: Toggle visual overlays showing text detection confidence
- **Zoom Controls**: Use zoom buttons or mouse wheel
- **Search**: Find text within extracted content
- **Settings**: Configure Google Cloud credentials and display options

## 🎨 UI Components

### Main Interface
- **PDF Viewer**: Left panel with PDF display and overlays
- **Analysis Panel**: Right panel with tabs for different views
- **Toolbar**: Quick access to common functions
- **Status Bar**: Shows current operation status

### Analysis Tabs
1. **Extracted Text**: Full text with search functionality
2. **Text Blocks**: Detailed block information with coordinates
3. **Statistics**: Document analysis and confidence metrics
4. **Settings**: Configuration for Google Cloud and display options

## 📊 Export Formats

### Text (.txt)
- Plain text extraction
- Header with metadata
- Statistics summary

### JSON (.json)
- Complete OCR results
- Structured data with coordinates
- Confidence levels and metadata

### CSV (.csv)
- Text blocks in tabular format
- Coordinates and confidence data
- Easy import into spreadsheets

### PDF Report (.pdf)
- Professional analysis report
- Statistics and confidence distribution
- Sample text blocks

## 🔧 Configuration

The application supports configuration through:
- **Settings Tab**: UI-based configuration
- **config.json**: File-based configuration (auto-generated)
- **Environment Variables**: For Google Cloud credentials

### Sample Configuration
```json
{
  "project_id": "your-project-id",
  "location": "eu",
  "processor_id": "your-processor-id",
  "settings": {
    "confidence_threshold": 0.7,
    "default_zoom": 1.0,
    "show_overlays": true
  }
}
```

## 🚨 Troubleshooting

### Common Issues

1. **"Module not found" errors**:
   - Ensure virtual environment is activated
   - Run `pip install -r requirements_new.txt`

2. **PDF not loading**:
   - Check if PyMuPDF is installed: `pip install PyMuPDF`
   - Ensure PDF file is not corrupted

3. **Google Cloud errors**:
   - Verify credentials file location
   - Check project ID and processor ID
   - Ensure Document AI API is enabled

4. **UI looks incorrect**:
   - Update to latest Python version
   - Try different Windows theme

### Error Logs
Check `ocr_viewer.log` for detailed error information.

## 🔄 Updates from Previous Version

This is a complete rewrite with:
- ✅ Cleaner, modular code architecture
- ✅ Better error handling and logging
- ✅ Modern UI with professional theme
- ✅ Improved PDF handling
- ✅ Enhanced export capabilities
- ✅ Better Google Cloud integration
- ✅ Comprehensive documentation

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review the logs (`ocr_viewer.log`)
- Create an issue with detailed error information

---

**OCR Viewer v2.0** - Professional Document Analysis Made Simple
