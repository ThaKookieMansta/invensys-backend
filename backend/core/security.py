from typing import Optional
from jose import jwt
from datetime import datetime, timezone, timedelta

from core.config import Settings as settings


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRY_MINUTES)

    to_encode.update({'exp': expire})

    encoded_jwt = jwt.encode(to_encode,settings.SECRET_KEY, settings.ALGORITHM)
    return encoded_jwt

