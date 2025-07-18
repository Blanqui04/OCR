from google.cloud import documentai_v1 as documentai
from google.api_core.client_options import ClientOptions
import os

def process_document_sample(
    project_id: str,
    location: str,
    processor_id: str,
    file_path: str,
    mime_type: str,
    credentials_path: str = None
):
    # Set credentials if provided
    if credentials_path and os.path.exists(credentials_path):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    
    try:
        # Instantiates a client
        opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")

        client = documentai.DocumentProcessorServiceClient(client_options=opts)

        # The full resource name of the processor
        name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"

        # Read the file into memory
        with open(file_path, "rb") as image:
            image_content = image.read()

        # Load binary data into a Document object
        raw_document = documentai.RawDocument(content=image_content, mime_type=mime_type)

        # Configure the process request
        request = documentai.ProcessRequest(
            name=name,
            raw_document=raw_document
        )

        result = client.process_document(request=request)

        document = result.document

        # Imprimeix el text complet del document
        print("Processament del document completat.")
        print("Text:")
        print(document.text)
        
    except Exception as e:
        print(f"Error en processar el document: {e}")
        print("\nPer solucionar problemes d'autenticació:")
        print("1. Instal·la Google Cloud SDK: https://cloud.google.com/sdk/docs/install")
        print("2. Executa: gcloud auth application-default login")
        print("3. Executa: gcloud config set project natural-bison-465607-b6")
        print("4. O proporciona la ruta del fitxer de la clau del compte de servei com a paràmetre credentials_path")
        return None

# Use this to call your processor
process_document_sample(
    project_id="natural-bison-465607-b6",
    location="eu",
    processor_id="4369d16f70cb0a26",
    file_path=r"C:\Users\eceballos\OneDrive - SOME, S.A\Desktop\OCR\6555945_003.pdf",  
    mime_type="application/pdf"
)
