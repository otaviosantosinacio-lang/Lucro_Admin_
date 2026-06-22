from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from lucro_admin.infra.models.usuario import Usuario
from lucro_admin.infra.database import get_session
from lucro_admin.api.security import (
    create_access_token,
    verify_password,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/token')
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.scalar(
        select(Usuario).where(Usuario.email == form_data.username)
    )

    if not user:
        raise HTTPException(
            status_code=401, detail={'message': 'Incorrect email or password'}
        )

    if not verify_password(form_data.password, user.senha_hash):
        raise HTTPException(
            status_code=401, detail={'message': 'Incorrect email or password'}
        )

    access_token = create_access_token({'sub': user.email})

    return {'access_token': access_token, 'token_type': 'Bearer'}
