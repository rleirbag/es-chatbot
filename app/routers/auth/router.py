import requests
from fastapi import (
    APIRouter,
    HTTPException,
    Security,
    status,
)
from fastapi.responses import RedirectResponse

from app.config.database import DbSession
from app.config.settings import Settings
from app.schemas.user import UserCreate
from app.services.users.create_user_use_case import CreateUserUseCase
from app.utils.security import get_current_user

router = APIRouter(tags=['Auth'])


@router.get('/login')
async def login_google():
    scopes = [
        'openid',
        'profile',
        'email',
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/userinfo.profile',
        'https://www.googleapis.com/auth/userinfo.email',
    ]
    scope_string = '%20'.join(scopes)
    return RedirectResponse(
        url=f'https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={Settings().GOOGLE_CLIENT_ID}&redirect_uri={Settings().GOOGLE_REDIRECT_URI}&scope={scope_string}&access_type=offline&prompt=consent',
        status_code=302,
    )


@router.get('/callback')
async def auth_google(code: str, db: DbSession):
    token_url = 'https://accounts.google.com/o/oauth2/token'
    data = {
        'code': code,
        'client_id': Settings().GOOGLE_CLIENT_ID,
        'client_secret': Settings().GOOGLE_SECRET_KEY,
        'redirect_uri': Settings().GOOGLE_REDIRECT_URI,
        'grant_type': 'authorization_code',
    }
    response = requests.post(token_url, data=data)
    token_data = response.json()

    if 'refresh_token' not in token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Não foi possível obter o refresh token.',
        )

    user_info = requests.get(
        'https://www.googleapis.com/oauth2/v3/userinfo',
        headers={'Authorization': f'Bearer {token_data.get("access_token")}'},
    )
    user_info = user_info.json()

    user = UserCreate(
        name=user_info.get('name'),
        email=user_info.get('email'),
        refresh_token=token_data.get('refresh_token'),
        avatar_url=user_info.get('picture'),
    )

    user, error = CreateUserUseCase.execute(db, user)  # type: ignore

    if error:
        raise HTTPException(
            status_code=error.error_code, detail=error.error_message
        )

    return {
        'access_token': token_data.get('access_token'),
        'refresh_token': token_data.get('refresh_token'),
        'expires_in': token_data.get('expires_in'),
        'token_type': token_data.get('token_type'),
        'id_token': token_data.get('id_token'),
        'picture': user_info.get('picture', ''),
    }


# TODO: Implementar refresh token pelo usuário logado
@router.post('/refresh')
async def refresh_google_token(refresh_token):
    params = {
        'client_id': Settings().GOOGLE_CLIENT_ID,
        'client_secret': Settings().GOOGLE_SECRET_KEY,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token',
    }

    response = requests.post(
        'https://oauth2.googleapis.com/token', data=params
    )

    if response.status_code == status.HTTP_200_OK:
        tokens = response.json()
        return tokens
    else:
        return None


@router.get('/protected')
async def protected_route(user_info: dict = Security(get_current_user)):
    return {'user_info': user_info}
