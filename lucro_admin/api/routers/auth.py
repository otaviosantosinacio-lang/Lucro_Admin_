from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from lucro_admin.api.security import (
    create_access_token,
    verify_password,
)
from lucro_admin.infra.database import get_session
from lucro_admin.infra.models.usuario import Usuario

router = APIRouter(prefix='/auth', tags=['Auth'])

T_Session = Annotated[AsyncSession, Depends(get_session)]
form_data = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post('/token')
async def login_for_access_token(
    session: T_Session,
    form_data: form_data,
):
    user = await session.scalar(
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
