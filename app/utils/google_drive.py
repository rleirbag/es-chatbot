import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

def authenticate_google_drive():
    """
    Autentica e retorna um serviço do Google Drive.
    
    Returns:
        googleapiclient.discovery.Resource: Serviço autenticado do Google Drive
    """
    credentials = service_account.Credentials.from_service_account_file(
        "credentials.json",
        scopes=["https://www.googleapis.com/auth/drive"]
    )

    service = build('drive', 'v3', credentials=credentials)
    return service 