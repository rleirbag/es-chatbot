import requests
from fastapi import APIRouter, status
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer

from app.config.settings import Settings

router = APIRouter()
oauth2_scheme = HTTPBearer()


@router.get("/login")
async def login_google():
    return RedirectResponse(url=f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={Settings().GOOGLE_CLIENT_ID}&redirect_uri={Settings().GOOGLE_REDIRECT_URI}&scope=openid%20profile%20email%20https://www.googleapis.com/auth/drive.file&access_type=offline&prompt=consent", status_code=302)


@router.get("/callback")
async def auth_google(code: str):
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "code": code,
        "client_id": Settings().GOOGLE_CLIENT_ID,
        "client_secret": Settings().GOOGLE_SECRET_KEY,
        "redirect_uri": Settings().GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    response = requests.post(token_url, data=data)
    token_data = response.json()

    # Verificar se temos o refresh token
    if 'refresh_token' not in token_data:
        return {"error": "Não foi possível obter o refresh token."}

    return {
        "access_token": token_data.get("access_token"),
        "refresh_token": token_data.get("refresh_token"),
        "expires_in": token_data.get("expires_in"),
        "token_type": token_data.get("token_type"),
        "id_token": token_data.get("id_token")
    }


@router.post("/refresh")
async def refresh_google_token(refresh_token):
    params = {
        'client_id': Settings().GOOGLE_CLIENT_ID,
        'client_secret': Settings().GOOGLE_SECRET_KEY,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }

    response = requests.post('https://oauth2.googleapis.com/token', data=params)

    if response.status_code == status.HTTP_200_OK:
        tokens = response.json()
        return tokens
    else:
        return None
