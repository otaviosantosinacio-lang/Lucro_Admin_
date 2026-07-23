from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from lucro_admin.api.schemas import (
    FilterPage,
    UserList,
    UserPublic,
    UserSchema,
)
from lucro_admin.api.security import get_current_user, get_password_hash
from lucro_admin.infra.database import get_session
from lucro_admin.infra.models.user import User

router = APIRouter(
    prefix='/users',
    tags=['Users'],
)

T_Session = Annotated[AsyncSession, Depends(get_session)]
current_user = Annotated[User, Depends(get_current_user)]
filter_page = Annotated[FilterPage, Query()]


@router.post('/', status_code=201, response_model=UserPublic)
async def create_user(user: UserSchema, session: T_Session):

    db_user = await session.scalar(
        select(User).where(
            (User.user_name == user.user_name)
            | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.user_name == user.user_name:
            raise HTTPException(
                status_code=400, detail={'message': 'Username already exists'}
            )

        elif db_user.email == user.email:
            raise HTTPException(
                status_code=400, detail={'message': 'Email already exists'}
            )

    db_user = User(
        user_name=user.user_name,
        email=user.email,
        password=get_password_hash(user.password),
    )

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.get('/', response_model=UserList)
async def read_users(
    session: T_Session, current_user: current_user, filter_page: filter_page
):
    users = await session.scalars(
        select(User).limit(filter_page.limit).offset(filter_page.offset)
    )

    return {'users': users}


@router.put('/{user_id}', response_model=UserPublic)
async def update_user(
    user_id: int,
    user: UserSchema,
    session: T_Session,
    current_user: current_user,
):

    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    valid_userdb = await session.scalar(
        select(User).where(
            (User.user_name == user.user_name)
            | (User.email == user.email)
        )
    )

    if valid_userdb:
        if user.user_name == valid_userdb.user_name:
            raise HTTPException(
                status_code=400, detail={'message': 'Username already exists'}
            )
        elif user.email == valid_userdb.email:
            raise HTTPException(
                status_code=400, detail={'message': 'Email already exists'}
            )
    try:
        current_user.user_name = user.user_name
        current_user.email = user.email
        current_user.password = get_password_hash(user.password)

    except IntegrityError:
        raise HTTPException(
            status_code=409, detail='Username or Email alreadry exists'
        )

    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)

    return current_user


@router.delete('/{user_id}', status_code=200)
async def delete_user(
    user_id: int,
    session: T_Session,
    current_user: current_user,
):

    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail='Not enough permissions')

    current_user.user_status = False
    session.add(current_user)
    await session.commit()
    return {'message': 'User delete'}
