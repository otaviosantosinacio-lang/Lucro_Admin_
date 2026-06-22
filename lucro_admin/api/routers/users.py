from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from lucro_admin.api.schemas import UserList, UserPublic, UserSchema
from lucro_admin.api.security import get_current_user, get_password_hash
from lucro_admin.infra.database import get_session
from lucro_admin.infra.models.usuario import Usuario

router = APIRouter(
    prefix='/users',
    tags=['Users'],
)

Sessionn= Annotated[Session, Depends(get_session)]

@router.post('/', status_code=201, response_model=UserPublic)
def create_user(user: UserSchema, session: Sessionn):

    db_user = session.scalar(
        select(Usuario).where(
            (Usuario.nome_usuario == user.nome_usuario)
            | (Usuario.email == user.email)
        )
    )

    if db_user:
        if db_user.nome_usuario == user.nome_usuario:
            raise HTTPException(
                status_code=400, detail={'message': 'Username already exists'}
            )

        elif db_user.email == user.email:
            raise HTTPException(
                status_code=400, detail={'message': 'Email already exists'}
            )

    db_user = Usuario(
        nome_usuario=user.nome_usuario,
        email=user.email,
        senha_hash=get_password_hash(user.senha_hash),
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.get('/', response_model=UserList)
def read_users(
    limit: int = 100,
    offset: int = 0,
    session: Sessionn,
    current_user=Depends(get_current_user),
):
    users = session.scalars(select(Usuario).limit(limit).offset(offset))

    return {'users': users}


@router.put('/{user_id}', response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserSchema,
    session: Sessionn,
    current_user: Usuario = Depends(get_current_user),
):

    if current_user.id_usuario != user_id:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    valid_userdb = session.scalar(
        select(Usuario).where(
            (Usuario.nome_usuario == user.nome_usuario)
            | (Usuario.email == user.email)
        )
    )

    if valid_userdb:
        if user.nome_usuario == valid_userdb.nome_usuario:
            raise HTTPException(
                status_code=400, detail={'message': 'Username already exists'}
            )
        elif user.email == valid_userdb.email:
            raise HTTPException(
                status_code=400, detail={'message': 'Email already exists'}
            )
    try:
        current_user.nome_usuario = user.nome_usuario
        current_user.email = user.email
        current_user.senha_hash = get_password_hash(user.senha_hash)

    except IntegrityError:
        raise HTTPException(
            status_code=409, detail='Username or Email alreadry exists'
        )

    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return current_user


@router.delete('/{user_id}', status_code=200)
def delete_user(
    user_id: int,
    session: Sessionn,
    current_user: Usuario = Depends(get_current_user),
):

    if current_user.id_usuario != user_id:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    current_user.status_usuario = False
    session.add(current_user)
    session.commit()
    return {'message': 'User delete'}