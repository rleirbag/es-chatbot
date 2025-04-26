from typing import Annotated, Dict

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from google.auth.transport import requests
from google.oauth2 import id_token

from app.config.settings import Settings

security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> Dict[str, str]:
    try:
        token = credentials.credentials
        idinfo = id_token.verify_oauth2_token(
            token, requests.Request(), Settings().GOOGLE_CLIENT_ID
        )

        if idinfo['iss'] not in {
            'accounts.google.com',
            'https://accounts.google.com',
        }:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token de autenticação inválido',
            )

        return {
            'sub': idinfo['sub'],
            'email': idinfo.get('email'),
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token de autenticação inválido',
        ) from e
