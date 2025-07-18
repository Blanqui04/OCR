"""
Google Cloud Authentication Setup for Document AI OCR
This script helps set up authentication for Google Cloud Document AI
"""

import os
import json
from pathlib import Path

class GoogleCloudAuth:
    def __init__(self):
        self.project_id = "natural-bison-465607-b6"
        self.keys_dir = Path(r"C:\Users\eceballos\keys")
        self.expected_key_file = "natural-bison-465607-b6-a638a05f2638.json"
        
    def check_authentication(self):
        """Check current authentication status"""
        print("🔍 Comprovant l'autenticació de Google Cloud...")
        
        # Check for service account key file
        key_path = self.keys_dir / self.expected_key_file
        if key_path.exists():
            print(f"✅ Fitxer de clau trobat: {key_path}")
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(key_path)
            return True
        
        # Check for application default credentials
        if 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
            creds_path = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
            if os.path.exists(creds_path):
                print(f"✅ Credencials d'aplicació per defecte: {creds_path}")
                return True
            else:
                print(f"⚠️ Variable GOOGLE_APPLICATION_CREDENTIALS apunta a un fitxer inexistent: {creds_path}")
        
        print("❌ No s'han trobat credencials vàlides")
        return False
    
    def setup_instructions(self):
        """Display setup instructions"""
        print("\n🔧 INSTRUCCIONS PER CONFIGURAR L'AUTENTICACIÓ:")
        print("=" * 60)
        
        print("\n📋 OPCIÓ 1: Fitxer de clau de compte de servei")
        print("-" * 45)
        print(f"1. Baixa el fitxer de clau del compte de servei de Google Cloud Console")
        print(f"2. Anomena'l: {self.expected_key_file}")
        print(f"3. Guarda'l a: {self.keys_dir}")
        print(f"4. Assegura't que el directori existeix: {self.keys_dir}")
        
        print("\n📋 OPCIÓ 2: Google Cloud SDK (Recomanat)")
        print("-" * 42)
        print("1. Instal·la Google Cloud SDK:")
        print("   https://cloud.google.com/sdk/docs/install")
        print("2. Autentica't:")
        print("   gcloud auth application-default login")
        print(f"3. Configura el projecte:")
        print(f"   gcloud config set project {self.project_id}")
        
        print("\n📋 OPCIÓ 3: Variable d'entorn")
        print("-" * 32)
        print("Configura la variable d'entorn GOOGLE_APPLICATION_CREDENTIALS")
        print("apuntant al teu fitxer de credencials JSON")
        
    def create_keys_directory(self):
        """Create keys directory if it doesn't exist"""
        if not self.keys_dir.exists():
            try:
                self.keys_dir.mkdir(parents=True, exist_ok=True)
                print(f"✅ Directori de claus creat: {self.keys_dir}")
                return True
            except Exception as e:
                print(f"❌ Error creant el directori de claus: {e}")
                return False
        else:
            print(f"✅ Directori de claus ja existeix: {self.keys_dir}")
            return True
    
    def test_connection(self):
        """Test Google Cloud Document AI connection"""
        try:
            from google.cloud import documentai_v1 as documentai
            from google.api_core.client_options import ClientOptions
            
            print("\n🧪 Provant la connexió a Document AI...")
            
            opts = ClientOptions(api_endpoint="eu-documentai.googleapis.com")
            client = documentai.DocumentProcessorServiceClient(client_options=opts)
            
            # Try to list processors to test authentication
            parent = f"projects/{self.project_id}/locations/eu"
            
            try:
                processors = client.list_processors(parent=parent)
                print("✅ Connexió a Document AI exitosa!")
                print(f"Processadors disponibles: {len(list(processors))}")
                return True
            except Exception as e:
                print(f"❌ Error de connexió: {e}")
                return False
                
        except ImportError:
            print("❌ La llibreria google-cloud-documentai no està instal·lada")
            print("Instal·la-la amb: pip install google-cloud-documentai")
            return False
    
    def interactive_setup(self):
        """Interactive setup wizard"""
        print("🚀 CONFIGURADOR D'AUTENTICACIÓ GOOGLE CLOUD")
        print("=" * 50)
        
        # Check current status
        if self.check_authentication():
            print("\n✅ L'autenticació ja està configurada!")
            test = input("\n❓ Vols provar la connexió? (s/n): ").lower().strip()
            if test in ['s', 'si', 'sí', 'y', 'yes']:
                self.test_connection()
            return
        
        print("\n❌ L'autenticació no està configurada.")
        
        # Create keys directory
        self.create_keys_directory()
        
        # Show instructions
        self.setup_instructions()
        
        print("\n" + "=" * 60)
        print("Després de seguir una de les opcions anteriors,")
        print("executa aquest script de nou per verificar la configuració.")

def main():
    auth = GoogleCloudAuth()
    auth.interactive_setup()

if __name__ == "__main__":
    main()
