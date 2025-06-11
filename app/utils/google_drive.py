import logging
import json

from google.oauth2 import service_account
from googleapiclient.discovery import build
from app.config.settings import Settings

logger = logging.getLogger(__name__)


def authenticate_google_drive():
    """
    Autentica e retorna um serviço do Google Drive.
    Returns:
        googleapiclient.discovery.Resource: Serviço autenticado do Google Drive
    """
    json_credentials = json.loads(Settings.GOOGLE_CREDENTIALS_JSON)

    if not Settings.GOOGLE_CREDENTIALS_JSON:
        credentials = service_account.Credentials.from_service_account_file(
            json_credentials,
            scopes=["https://www.googleapis.com/auth/drive"]
        )


    service = build('drive', 'v3', credentials=credentials)
    return service
