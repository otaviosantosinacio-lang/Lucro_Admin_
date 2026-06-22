from pwdlib import PasswordHash
from jwt import encode, decode, DecodeError
from lucro_admin.utils.time import somandosecs
from lucro_admin.infra.database import get_session
from lucro_admin.infra.models.usuario import Usuario

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session
from sqlalchemy import select

SECRET_KEY = 'your-secret-key'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_SECONDS = 1800
oauth2_scheme= OAuth2PasswordBearer(tokenUrl= 'token')
pwd_context = PasswordHash.recommended()


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = somandosecs(ACCESS_TOKEN_EXPIRE_SECONDS)

    to_encode.update({'exp': expire})

    encode_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encode_jwt

def get_current_user(
    session: Session = Depends(get_session),
    token: str= Depends(oauth2_scheme)
):
    
    credentials_exception = HTTPException(
        status_code= 401,
        detail= 'Could not validate credentials',
        headers= {'WWW-Authenticate': 'Bearer'}
    )

    try:
        payload= decode(token, SECRET_KEY, algorithms=ALGORITHM)
        subject_email= payload.get('sub')
        if not subject_email:
            raise credentials_exception
    except DecodeError:
        raise credentials_exception
    
    user= session.scalar(
        select(Usuario).where(
            Usuario.email == subject_email
        )
    )

    if not user:
        raise credentials_exception
    
    return user