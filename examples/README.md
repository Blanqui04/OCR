# Example Files

This directory contains example files for testing the Professional OCR Viewer application.

## 📄 Sample Files

### sample.pdf
A sample PDF document for testing OCR functionality. This file demonstrates:
- Mixed text and graphics
- Various font sizes and styles
- Technical drawings (if available)
- Multi-column layouts

## 🧪 Testing Instructions

1. **Launch the OCR Viewer:**
   ```bash
   python launch_ocr_viewer.py
   ```

2. **Open the sample file:**
   - Click "Open PDF" or press Ctrl+O
   - Navigate to this examples folder
   - Select `sample.pdf`

3. **Process the document:**
   - Click "Process Document" or press Ctrl+P
   - Wait for processing to complete

4. **Explore the results:**
   - View bounding boxes on the PDF
   - Check the text extraction quality
   - Try different zoom levels
   - Test the export functions

## 📝 Expected Results

When processing the sample file, you should see:
- Green bounding boxes for high-confidence text
- Orange boxes for medium-confidence text
- Red boxes for low-confidence areas
- Clickable text blocks for selection

## 🔄 Adding Your Own Test Files

To test with your own documents:

1. Copy PDF files to this directory
2. Use the application to open them
3. Compare results with different document types:
   - Scanned documents
   - Text-based PDFs
   - Documents with images
   - Multi-language content

## 📊 Performance Benchmarks

Use these files to test performance:
- Small documents (< 1MB): Should process in 2-5 seconds
- Medium documents (1-5MB): Should process in 5-15 seconds
- Large documents (> 5MB): May take 15+ seconds

Note: Processing time depends on:
- Document complexity
- Image quality
- Network speed
- Google Cloud processing load
