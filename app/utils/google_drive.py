import json
import base64
from google.oauth2 import service_account
from googleapiclient.discovery import build
from app.config.settings import Settings

def authenticate_google_drive():
    """
    Autentica e retorna um serviço do Google Drive usando credenciais
    de uma variável de ambiente.

    Returns:
        googleapiclient.discovery.Resource: Serviço autenticado do Google Drive.
    """
    str_b64_raw = Settings().GOOGLE_CREDENTIALS_B64
    str_b64=str_b64_raw.strip()
    print(Settings().GOOGLE_CREDENTIALS_B64)
    creds_json_str = base64.b64decode(str_b64).decode('utf-8')
    if not creds_json_str:
        raise ValueError("A variável GOOGLE_CREDENTIALS_JSON não foi encontrada.")

    creds_info = json.loads(creds_json_str)

    credentials = service_account.Credentials.from_service_account_info(
        creds_info,
        scopes=["https://www.googleapis.com/auth/drive"]
    )

    # 4. Constrói e retorna o serviço.
    service = build('drive', 'v3', credentials=credentials)
    return service