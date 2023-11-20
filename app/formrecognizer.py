from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import os

def analyze_pdf_document(pdf_file_path):
    # Replace with your actual Azure Form Recognizer service endpoint and key
    SERVICE_ENDPOINT = os.environ.get("SERVICE_ENDPOINT")
    SERVICE_KEY = os.environ.get("SERVICE_KEY")
    # Initialize DocumentAnalysisClient
    document_analysis_client = DocumentAnalysisClient(
        endpoint=SERVICE_ENDPOINT, credential=AzureKeyCredential(SERVICE_KEY)
    )
    # Open the PDF file and begin document analysis
    with open(pdf_file_path, "rb") as f:
        poller = document_analysis_client.begin_analyze_document(
            "prebuilt-document", document=f
        )
    # Wait for the analysis to complete and get the result
    result = poller.result()
    return result.to_dict()


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    import warnings

    warnings.filterwarnings(
        "ignore",
        category=UserWarning,
        module="streamlit.runtime.caching.cache_data_api",
    )
    load_dotenv("./app/.env")

    filepath = "app/data/LT E-BillPDF_231119_145147.pdf"
    result = analyze_pdf_document(filepath)
    result