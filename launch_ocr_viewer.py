"""
OCR Viewer Application Launcher
Professional Windows desktop application for Google Cloud Document AI
"""

import sys
import os
import warnings

# Suppress Google Cloud warnings
warnings.filterwarnings("ignore", message="Your application has authenticated using end user credentials")

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def check_dependencies():
    """Check if all required dependencies are available"""
    missing_deps = []
    
    try:
        import tkinter
    except ImportError:
        missing_deps.append("tkinter")
        
    try:
        from PIL import Image
    except ImportError:
        missing_deps.append("Pillow")
        
    try:
        import fitz
    except ImportError:
        missing_deps.append("PyMuPDF")
        
    try:
        from google.cloud import documentai_v1
    except ImportError:
        missing_deps.append("google-cloud-documentai")
        
    return missing_deps

if __name__ == "__main__":
    print("🚀 Professional OCR Viewer")
    print("=" * 50)
    print("📋 Features:")
    print("   • PDF viewing with zoom and navigation")
    print("   • Google Cloud Document AI integration") 
    print("   • Interactive text block visualization")
    print("   • Text search and export capabilities")
    print("   • Professional Windows interface")
    print("=" * 50)
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    missing = check_dependencies()
    
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("\n📦 Please install missing packages:")
        for dep in missing:
            print(f"   pip install {dep}")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    print("✅ All dependencies found!")
    
    try:
        print("\n🎯 Launching application...")
        from ocr_viewer_app import main
        main()
        
    except ImportError as e:
        print(f"❌ Error importing application: {e}")
        print("\n🔧 Troubleshooting:")
        print("   • Ensure all files are in the same directory")
        print("   • Check file permissions")
        print("   • Verify Python environment")
        input("\nPress Enter to exit...")
        
    except KeyboardInterrupt:
        print("\n🛑 Application interrupted by user")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("\n📞 If this problem persists, please check:")
        print("   • Google Cloud authentication is working")
        print("   • Internet connection is available")
        print("   • No antivirus blocking the application")
        input("\nPress Enter to exit...")
