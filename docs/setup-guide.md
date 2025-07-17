# Setup Guide

Detailed step-by-step instructions for setting up the Professional OCR Viewer application.

## 📋 Prerequisites

Before starting the installation, ensure you have:

- **Windows 10 or 11** (64-bit recommended)
- **Python 3.7 or higher** installed
- **Internet connection** for downloading dependencies and Document AI processing
- **Google Cloud account** with Document AI enabled
- **Administrator privileges** (may be required for some installations)

## 🚀 Quick Setup (Recommended)

### Step 1: Download the Application

```bash
git clone https://github.com/your-username/professional-ocr-viewer.git
cd professional-ocr-viewer
```

### Step 2: Run Automated Setup

Double-click `setup.bat` or run from command line:

```bash
setup.bat
```

This will:
- Check Python installation
- Create virtual environment
- Install all dependencies
- Test the installation

### Step 3: Configure Google Cloud

1. **Install Google Cloud SDK:**
   - Download from [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
   - Run the installer and follow instructions
   - Restart command prompt after installation

2. **Authenticate:**
   ```bash
   gcloud auth application-default login
   ```

3. **Set your project:**
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

### Step 4: Configure Application Settings

Edit `ocr_viewer_app.py` and update these lines:

```python
# Google Cloud settings
self.project_id = "your-project-id"
self.location = "your-location"  # e.g., "us", "eu", "asia-northeast1"
self.processor_id = "your-processor-id"
```

### Step 5: Launch Application

Double-click `OCR_Viewer.bat` or run:

```bash
python launch_ocr_viewer.py
```

## 🔧 Manual Setup

If you prefer manual installation or the automated setup fails:

### Step 1: Install Python

1. Download Python 3.7+ from [python.org](https://www.python.org/downloads/)
2. During installation:
   - ✅ Check "Add Python to PATH"
   - ✅ Check "Install for all users" (if administrator)
3. Verify installation:
   ```bash
   python --version
   pip --version
   ```

### Step 2: Create Project Directory

```bash
mkdir professional-ocr-viewer
cd professional-ocr-viewer
```

### Step 3: Download Application Files

Download or copy these files to your project directory:
- `ocr_viewer_app.py`
- `launch_ocr_viewer.py`
- `OCR_Viewer.bat`
- `requirements.txt`
- `README.md`

### Step 4: Create Virtual Environment

```bash
python -m venv .venv
```

Activate the environment:
```bash
.venv\Scripts\activate
```

### Step 5: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Or install packages individually:
```bash
pip install google-cloud-documentai
pip install Pillow
pip install PyMuPDF
```

### Step 6: Verify Installation

Test all dependencies:
```bash
python -c "import tkinter; import fitz; from PIL import Image; from google.cloud import documentai_v1; print('All dependencies installed successfully!')"
```

## ☁️ Google Cloud Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Note your Project ID

### Step 2: Enable Document AI API

1. Go to "APIs & Services" > "Library"
2. Search for "Document AI API"
3. Click "Enable"

### Step 3: Create Document AI Processor

1. Go to "Document AI" in the Console
2. Click "Create Processor"
3. Choose processor type (e.g., "Document OCR")
4. Select region (e.g., "us", "eu")
5. Note the Processor ID

### Step 4: Set Up Authentication

Choose one of these methods:

#### Option A: Application Default Credentials (Recommended)

1. Install Google Cloud SDK
2. Run authentication:
   ```bash
   gcloud auth application-default login
   ```
3. Set project:
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

#### Option B: Service Account Key

1. Go to "IAM & Admin" > "Service Accounts"
2. Create new service account
3. Download JSON key file
4. Set environment variable:
   ```bash
   set GOOGLE_APPLICATION_CREDENTIALS=path\to\your\key.json
   ```

## ⚙️ Configuration

### Application Settings

Edit `ocr_viewer_app.py` to configure:

```python
class OCRViewerApp:
    def __init__(self, root):
        # ... other code ...
        
        # Google Cloud settings - UPDATE THESE
        self.project_id = "your-project-id"           # Your Google Cloud Project ID
        self.location = "eu"                          # Processor location: "us", "eu", etc.
        self.processor_id = "your-processor-id"       # Your Document AI Processor ID
```

### Default File Paths

The application will look for PDFs in the same directory by default. You can change this by modifying the `open_pdf()` function.

### UI Customization

You can customize the interface by modifying these settings in `ocr_viewer_app.py`:

```python
# Window size
self.root.geometry("1400x900")

# Colors for confidence levels
color = "green"    # High confidence (>90%)
color = "orange"   # Medium confidence (70-90%)
color = "red"      # Low confidence (<70%)
color = "blue"     # Selected block
```

## 🧪 Testing Installation

### Step 1: Test Basic Functionality

Run the test script:
```bash
python test_ocr.py
```

This will verify:
- Google Cloud connection
- Document AI processing
- PDF file reading

### Step 2: Test GUI Application

1. Launch the application:
   ```bash
   python launch_ocr_viewer.py
   ```

2. Try opening a sample PDF
3. Process with Document AI
4. Verify bounding boxes appear

### Step 3: Test Export Functions

1. Process a document
2. Try exporting to TXT format
3. Try exporting to JSON format

## 📁 Directory Structure After Setup

```
professional-ocr-viewer/
├── .venv/                     # Virtual environment (created by setup)
│   ├── Scripts/
│   │   ├── python.exe
│   │   └── pip.exe
│   └── Lib/
├── docs/                      # Documentation
│   ├── setup-guide.md
│   └── troubleshooting.md
├── OCR_Viewer.bat            # Main launcher
├── launch_ocr_viewer.py      # Python launcher
├── ocr_viewer_app.py         # Main application
├── test_ocr.py              # Test script
├── requirements.txt          # Dependencies
├── setup.bat                # Setup script
├── README.md                # Main documentation
└── LICENSE                  # License file
```

## 🔄 Updating the Application

To update to a newer version:

1. **Backup your configuration:**
   - Copy your modified `ocr_viewer_app.py` settings

2. **Download new version:**
   ```bash
   git pull origin main
   ```

3. **Update dependencies:**
   ```bash
   .venv\Scripts\activate
   pip install --upgrade -r requirements.txt
   ```

4. **Restore configuration:**
   - Update the new `ocr_viewer_app.py` with your settings

## 🚨 Common Setup Issues

### Python Not Found
- Ensure Python is in your PATH
- Try `py` instead of `python` command
- Reinstall Python with "Add to PATH" option

### Virtual Environment Issues
- Delete `.venv` folder and recreate
- Ensure sufficient disk space
- Run as administrator if needed

### Google Cloud Authentication
- Verify internet connection
- Check firewall/antivirus settings
- Ensure correct project permissions

### Permission Errors
- Run command prompt as administrator
- Check file/folder permissions
- Temporarily disable antivirus

For more detailed troubleshooting, see [troubleshooting.md](troubleshooting.md).

## ✅ Verification Checklist

Before using the application, verify:

- [ ] Python 3.7+ installed and in PATH
- [ ] Virtual environment created successfully
- [ ] All dependencies installed without errors
- [ ] Google Cloud SDK installed and authenticated
- [ ] Project ID, location, and processor ID configured
- [ ] Test script runs successfully
- [ ] GUI application launches without errors
- [ ] Sample PDF can be loaded and processed
- [ ] Bounding boxes are visible on processed documents
- [ ] Export functions work correctly

## 📞 Support

If you encounter issues during setup:

1. Check [troubleshooting.md](troubleshooting.md)
2. Search GitHub issues
3. Create new issue with setup details

Include this information when reporting setup issues:
- Operating system version
- Python version
- Error messages (complete text)
- Steps that led to the error
