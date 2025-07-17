# Troubleshooting Guide

This guide helps you resolve common issues with the Professional OCR Viewer application.

## 🔧 Installation Issues

### Python Not Found
**Error:** `'python' is not recognized as an internal or external command`

**Solution:**
1. Install Python 3.7+ from [python.org](https://www.python.org/downloads/)
2. During installation, check "Add Python to PATH"
3. Restart your command prompt/terminal
4. Verify with: `python --version`

### Virtual Environment Creation Failed
**Error:** `Failed to create virtual environment`

**Solution:**
1. Ensure you have sufficient disk space
2. Run as administrator if necessary
3. Try manually: `python -m venv .venv`
4. Check Python installation integrity

### Dependency Installation Errors
**Error:** `Failed to install dependencies`

**Solutions:**
1. **Update pip first:**
   ```bash
   python -m pip install --upgrade pip
   ```

2. **Install packages individually:**
   ```bash
   pip install google-cloud-documentai
   pip install Pillow
   pip install PyMuPDF
   ```

3. **Use alternative index (if behind firewall):**
   ```bash
   pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt
   ```

## 🔐 Authentication Issues

### Default Credentials Not Found
**Error:** `Your default credentials were not found`

**Solution:**
1. **Install Google Cloud SDK:**
   - Download from [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
   - Follow installation instructions for Windows

2. **Authenticate:**
   ```bash
   gcloud auth application-default login
   ```

3. **Set project:**
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

4. **Verify authentication:**
   ```bash
   gcloud auth list
   ```

### Invalid Project ID
**Error:** `Project not found` or `Permission denied`

**Solution:**
1. Verify project ID in Google Cloud Console
2. Ensure you have access to the project
3. Update project ID in `ocr_viewer_app.py`:
   ```python
   self.project_id = "your-correct-project-id"
   ```

### Processor Not Found
**Error:** `Processor not found` or `Invalid processor ID`

**Solution:**
1. Go to Google Cloud Console > Document AI
2. Find your processor and copy the ID
3. Update processor ID in `ocr_viewer_app.py`:
   ```python
   self.processor_id = "your-processor-id"
   ```

### Quota Exceeded
**Error:** `Quota exceeded` or `Rate limit exceeded`

**Solutions:**
1. Check quotas in Google Cloud Console
2. Request quota increase if needed
3. Wait before retrying (rate limits reset)
4. Consider using a different project

## 📄 PDF Processing Issues

### PDF Won't Load
**Error:** `Failed to load PDF`

**Solutions:**
1. **Check file format:**
   - Ensure file is actually a PDF
   - Try with a different PDF file

2. **File permissions:**
   - Ensure file is not open in another program
   - Check read permissions on the file
   - Try copying file to a different location

3. **File corruption:**
   - Try opening PDF in Adobe Reader
   - Use a different PDF if original is corrupted

### Blank or Missing Text
**Error:** PDF loads but no text is extracted

**Solutions:**
1. **Scanned PDFs:**
   - Document may be image-based
   - OCR processing should still work via Document AI

2. **Font issues:**
   - Some fonts may not be recognized properly
   - Try with a standard PDF with common fonts

3. **Language settings:**
   - Ensure Document AI processor supports the document language

## 🖥️ Interface Issues

### Application Won't Start
**Error:** Application closes immediately or doesn't open

**Solutions:**
1. **Check error messages:**
   - Run from command line to see errors:
     ```bash
     python launch_ocr_viewer.py
     ```

2. **Graphics issues:**
   - Update graphics drivers
   - Try running on different display

3. **Dependencies:**
   - Verify all packages installed:
     ```bash
     python -c "import tkinter, fitz, PIL, google.cloud.documentai_v1"
     ```

### Bounding Boxes Not Visible
**Issue:** PDF displays but no overlay boxes appear

**Solutions:**
1. **Process document first:**
   - Click "Process Document" button
   - Wait for processing to complete

2. **Zoom level:**
   - Try different zoom levels
   - Use "Fit Window" option

3. **Color visibility:**
   - Boxes may be same color as background
   - Try selecting text blocks from the right panel

### Slow Performance
**Issue:** Application is slow or unresponsive

**Solutions:**
1. **Large files:**
   - Try with smaller PDF files first
   - Consider splitting large documents

2. **Memory issues:**
   - Close other applications
   - Restart the OCR Viewer

3. **Network speed:**
   - Document AI processing requires internet
   - Check network connection speed

## 🌐 Network Issues

### Connection Timeout
**Error:** `Connection timeout` or `Network error`

**Solutions:**
1. **Check internet connection**
2. **Firewall/antivirus:**
   - Temporarily disable to test
   - Add exceptions for Python and the application

3. **Proxy settings:**
   - Configure proxy if behind corporate firewall
   - Set environment variables if needed

4. **VPN issues:**
   - Try disconnecting VPN
   - Some VPNs may block Google services

## 📊 Data Export Issues

### Export Failed
**Error:** `Failed to export` or permission errors

**Solutions:**
1. **File permissions:**
   - Choose a different export location
   - Ensure write permissions to target folder

2. **File in use:**
   - Close exported file if open in another program
   - Choose different filename

3. **Disk space:**
   - Ensure sufficient disk space
   - Clean up temporary files

## 🔄 General Troubleshooting Steps

### Reset Application
1. Close the application completely
2. Delete `.venv` folder
3. Run `setup.bat` again
4. Reconfigure Google Cloud settings

### Clean Installation
1. Delete all application files
2. Download fresh copy from GitHub
3. Follow installation guide step by step
4. Test with sample PDF

### Check System Requirements
- **OS:** Windows 10/11
- **Python:** 3.7 or higher
- **RAM:** 4GB minimum, 8GB recommended
- **Disk:** 500MB free space minimum
- **Internet:** Required for Document AI processing

## 📞 Getting Additional Help

If you're still experiencing issues:

1. **Check GitHub Issues:**
   - Search for similar problems
   - Check closed issues for solutions

2. **Create New Issue:**
   - Include error messages
   - Describe steps to reproduce
   - Include system information
   - Attach relevant files if possible

3. **Diagnostic Information:**
   When reporting issues, include:
   - Operating system version
   - Python version (`python --version`)
   - Error messages (full text)
   - Steps that led to the error
   - PDF file characteristics (if relevant)

## 📝 Diagnostic Commands

Run these commands to gather system information:

```bash
# Python version
python --version

# Installed packages
pip list

# Google Cloud authentication status
gcloud auth list

# System information
systeminfo | findstr "OS"
```

Remember to never share sensitive information like API keys or authentication tokens when reporting issues.
