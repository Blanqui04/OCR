"""
Simple OCR Test Script
Test Google Cloud Document AI processing without GUI
"""

import warnings
warnings.filterwarnings("ignore", message="Your application has authenticated using end user credentials")

from google.cloud import documentai_v1 as documentai
from google.api_core.client_options import ClientOptions
import os

def test_document_processing():
    """Test document processing with improved error handling"""
    
    # Configuration
    project_id = "natural-bison-465607-b6"
    location = "eu"
    processor_id = "4369d16f70cb0a26"
    file_path = r"C:\Users\eceballos\OneDrive - SOME, S.A\Desktop\OCR\6555945_003.pdf"
    
    print("🔍 Testing Google Cloud Document AI processing...")
    print(f"📄 File: {os.path.basename(file_path)}")
    print(f"🏗️ Project: {project_id}")
    print(f"📍 Location: {location}")
    print(f"⚙️ Processor: {processor_id}")
    print("-" * 50)
    
    try:
        # Set up client
        print("🔗 Connecting to Google Cloud Document AI...")
        opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
        client = documentai.DocumentProcessorServiceClient(client_options=opts)
        
        # Read file
        print("📖 Reading PDF file...")
        with open(file_path, "rb") as pdf_file:
            content = pdf_file.read()
        
        print(f"📏 File size: {len(content):,} bytes")
        
        # Create request
        print("📤 Sending request to Document AI...")
        raw_document = documentai.RawDocument(content=content, mime_type="application/pdf")
        name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"
        request = documentai.ProcessRequest(name=name, raw_document=raw_document)
        
        # Process document
        result = client.process_document(request=request)
        document = result.document
        
        print("✅ Document processed successfully!")
        print(f"📝 Text length: {len(document.text):,} characters")
        print(f"📄 Pages: {len(document.pages)}")
        
        # Analyze structure
        print("\n📊 Document Structure Analysis:")
        for page_num, page in enumerate(document.pages):
            print(f"  Page {page_num + 1}:")
            
            # Check what's available on this page
            elements = []
            if hasattr(page, 'paragraphs'):
                elements.append(f"paragraphs: {len(page.paragraphs)}")
            if hasattr(page, 'blocks'):
                elements.append(f"blocks: {len(page.blocks)}")
            if hasattr(page, 'lines'):
                elements.append(f"lines: {len(page.lines)}")
            if hasattr(page, 'words'):
                elements.append(f"words: {len(page.words)}")
            if hasattr(page, 'tokens'):
                elements.append(f"tokens: {len(page.tokens)}")
                
            print(f"    Available: {', '.join(elements) if elements else 'basic text only'}")
        
        # Show first 500 characters of extracted text
        print(f"\n📝 Text Preview (first 500 chars):")
        print("-" * 50)
        preview_text = document.text[:500].replace('\n', '\\n')
        print(f"{preview_text}...")
        print("-" * 50)
        
        print("\n🎉 Test completed successfully!")
        print("✅ The Document AI processing is working correctly")
        print("✅ You can now use the GUI application to visualize the results")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        print("\n🔧 Troubleshooting suggestions:")
        print("1. Check your Google Cloud authentication")
        print("2. Verify the processor ID is correct")
        print("3. Ensure the PDF file exists and is readable")
        print("4. Check your internet connection")
        return False

if __name__ == "__main__":
    print("🧪 Simple OCR Test")
    print("=" * 50)
    
    success = test_document_processing()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All tests passed! The OCR system is ready to use.")
    else:
        print("❌ Tests failed. Please check the error messages above.")
    
    input("\nPress Enter to exit...")
