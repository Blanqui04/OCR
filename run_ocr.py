"""
🚀 EXECUTAR OCR TECHNICAL ANALYZER
Script principal per llançar el sistema de producció
"""

import sys
import os
from pathlib import Path
import subprocess
import time

class OCRLauncher:
    """Llançador principal del sistema OCR"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.production_dir = self.base_dir / "production"
        
    def show_welcome(self):
        """Mostra el missatge de benvinguda"""
        print("🚀 OCR TECHNICAL ANALYZER - SISTEMA DE PRODUCCIÓ")
        print("=" * 60)
        print("📋 Sistema d'anàlisi OCR amb detecció IA d'elements tècnics")
        print("🎯 Detecta cotes, toleràncies i símbols en plànols tècnics")
        print("=" * 60)
    
    def check_environment(self):
        """Verifica l'entorn d'execució"""
        print("\n🔍 Verificant entorn...")
        
        # Verificar Python
        try:
            import sys
            print(f"  ✅ Python {sys.version}")
        except:
            print("  ❌ Error amb Python")
            return False
        
        # Verificar directori de producció
        if self.production_dir.exists():
            print(f"  ✅ Directori de producció: {self.production_dir}")
        else:
            print("  ❌ Directori de producció no trobat")
            print("  🔧 Executa primer: python deploy_production.py")
            return False
        
        # Verificar dependències bàsiques
        try:
            import loguru
            print("  ✅ Loguru disponible")
        except:
            print("  ⚠️ Loguru no trobat, instal·lant...")
            subprocess.run([sys.executable, "-m", "pip", "install", "loguru"])
        
        try:
            import cv2
            print("  ✅ OpenCV disponible")
        except:
            print("  ⚠️ OpenCV no trobat")
        
        return True
    
    def show_menu(self):
        """Mostra el menú principal"""
        print("\n📋 OPCIONS D'EXECUCIÓ:")
        print("1. 🧪 Test ràpid del sistema")
        print("2. 🎬 Demo amb exemple")
        print("3. 📄 Processar documents (input/)")
        print("4. 🎯 Només detecció YOLOv8")
        print("5. ⚙️ Configuració del sistema")
        print("6. 📊 Consultar resultats")
        print("7. 🚪 Sortir")
        
        choice = input("\n➤ Selecciona opció (1-7): ").strip()
        return choice
    
    def run_quick_test(self):
        """Executa test ràpid"""
        print("\n🧪 Executant test ràpid...")
        os.chdir(self.production_dir)
        result = subprocess.run([sys.executable, "quick_test.py"])
        return result.returncode == 0
    
    def run_demo(self):
        """Executa demo amb exemple"""
        print("\n🎬 Executant demo...")
        os.chdir(self.production_dir)
        result = subprocess.run([sys.executable, "demo_production.py"])
        return result.returncode == 0
    
    def run_document_processing(self):
        """Processa documents del directori input"""
        print("\n📄 Processant documents...")
        
        input_dir = self.production_dir / "data" / "input"
        
        # Verificar si hi ha documents
        pdf_files = list(input_dir.glob("*.pdf"))
        image_files = list(input_dir.glob("*.png")) + list(input_dir.glob("*.jpg"))
        
        if not pdf_files and not image_files:
            print(f"📁 No hi ha documents a {input_dir}")
            print("💡 Copia documents PDF o imatges al directori data/input/")
            return False
        
        print(f"📋 Trobats: {len(pdf_files)} PDFs, {len(image_files)} imatges")
        
        os.chdir(self.production_dir)
        
        # Processar amb pipeline complet
        print("🔄 Executant processament...")
        result = subprocess.run([sys.executable, "process_documents.py"])
        
        if result.returncode == 0:
            print("✅ Documents processats!")
            print("📁 Consulta resultats a production/data/output/")
        
        return result.returncode == 0
    
    def run_yolo_only(self):
        """Executa només detecció YOLOv8"""
        print("\n🎯 Detecció YOLOv8...")
        
        input_path = input("📁 Path a imatge o directori: ").strip()
        if not input_path:
            input_path = str(self.production_dir / "data" / "input")
        
        confidence = input("🎚️ Confiança (0.1-1.0, per defecte 0.3): ").strip()
        if not confidence:
            confidence = "0.3"
        
        os.chdir(self.base_dir)
        cmd = [
            sys.executable, 
            "src/technical_element_detector.py",
            "--input", input_path,
            "--confidence", confidence
        ]
        
        result = subprocess.run(cmd)
        return result.returncode == 0
    
    def show_config(self):
        """Mostra configuració del sistema"""
        print("\n⚙️ Configuració del Sistema:")
        
        config_file = self.production_dir / "config" / "production_config.json"
        if config_file.exists():
            import json
            with open(config_file) as f:
                config = json.load(f)
            
            print(f"📛 Nom: {config['system']['name']}")
            print(f"🔢 Versió: {config['system']['version']}")
            print(f"🌍 Entorn: {config['system']['environment']}")
            print(f"🎯 Confiança YOLOv8: {config['yolo']['confidence_threshold']}")
            print(f"📁 Directori base: {self.production_dir}")
        else:
            print("❌ Fitxer de configuració no trobat")
    
    def show_results(self):
        """Mostra resultats recents"""
        print("\n📊 Resultats Recents:")
        
        output_dir = self.production_dir / "data" / "output"
        if output_dir.exists():
            files = sorted(output_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
            
            if files:
                print(f"📋 Últims {min(5, len(files))} resultats:")
                for i, file in enumerate(files[:5], 1):
                    size = file.stat().st_size
                    mtime = time.ctime(file.stat().st_mtime)
                    print(f"  {i}. {file.name} ({size} bytes, {mtime})")
                
                # Mostrar contingut de l'últim
                if input("\n👁️ Veure contingut de l'últim? (y/N): ").lower() == 'y':
                    import json
                    with open(files[0]) as f:
                        data = json.load(f)
                    print(json.dumps(data, indent=2, ensure_ascii=False)[:1000] + "...")
            else:
                print("📁 No hi ha resultats encara")
        else:
            print("❌ Directori de resultats no trobat")
    
    def run(self):
        """Executa el llançador principal"""
        self.show_welcome()
        
        if not self.check_environment():
            print("\n❌ L'entorn no està preparat")
            print("🔧 Executa primer: python deploy_production.py")
            return
        
        while True:
            choice = self.show_menu()
            
            if choice == "1":
                self.run_quick_test()
            elif choice == "2":
                self.run_demo()
            elif choice == "3":
                self.run_document_processing()
            elif choice == "4":
                self.run_yolo_only()
            elif choice == "5":
                self.show_config()
            elif choice == "6":
                self.show_results()
            elif choice == "7":
                print("\n👋 Fins aviat!")
                break
            else:
                print("\n❌ Opció no vàlida")
            
            input("\n⏎ Prem Enter per continuar...")

def main():
    """Funció principal"""
    launcher = OCRLauncher()
    launcher.run()

if __name__ == "__main__":
    main()
