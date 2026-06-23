from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, decode, encode
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from lucro_admin.infra.database import get_session
from lucro_admin.infra.models.usuario import Usuario
from lucro_admin.utils.time import somandosecs
from lucro_admin.settings import Settings

settings = Settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')
pwd_context = PasswordHash.recommended()


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = somandosecs(settings.ACCESS_TOKEN_EXPIRE_SECONDS)

    to_encode.update({'exp': expire})

    encode_jwt = encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return encode_jwt


def get_current_user(
    settings,
    session: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme),
):

    credentials_exception = HTTPException(
        status_code=401,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = decode(
            token, settings.SECRET_KEY, algorithms=settings.ALGORITHM
        )
        subject_email = payload.get('sub')
        if not subject_email:
            raise credentials_exception
    except DecodeError:
        raise credentials_exception

    user = session.scalar(
        select(Usuario).where(Usuario.email == subject_email)
    )

    if not user:
        raise credentials_exception

    return user
