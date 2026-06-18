from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from lucro_admin.api.schemas import UserPublic, UserSchema, UserList
from lucro_admin.infra.models.usuario import Usuario
from lucro_admin.infra.database import get_session
from lucro_admin.api.security import get_password_hash, verify_password

from sqlalchemy import select
from sqlalchemy.orm import Session

app = FastAPI(title='Lucro Admin API')


@app.get('/')
def home():
    boas_vindas = {
        'Olá usuário, seja bem-vindo ao Lucro Admin, um sistema financeiro'
        ' para gerenciamento das suas vendas'
    }
    return boas_vindas


@app.post('/users', status_code=201, response_model=UserPublic)
def create_user(user: UserSchema, session: Session = Depends(get_session)):

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


@app.get('/users/', response_model=UserList)
def read_users(
    limit: int = 100, offset: int = 0, session: Session = Depends(get_session)
):
    users = session.scalars(select(Usuario).limit(limit).offset(offset))

    return {'users': users}


@app.put('/users/{user_id}', response_model=UserPublic)
def update_user(
    user_id: int, user: UserSchema, session: Session = Depends(get_session)
):

    user_db = session.scalar(
        select(Usuario).where(Usuario.id_usuario == user_id)
    )

    if not user_db:
        raise HTTPException(
            status_code=404, detail={'message': 'User Not Found'}
        )

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

    user_db.nome_usuario = user.nome_usuario
    user_db.email = user.email
    user_db.senha_hash = get_password_hash(user.senha_hash)

    session.add(user_db)
    session.commit()
    session.refresh(user_db)

    return user_db


@app.delete('/users/{user_id}', status_code=200)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
):
    user_db = session.scalar(
        select(Usuario).where(Usuario.id_usuario == user_id)
    )

    if not user_db:
        raise HTTPException(
            status_code=404, detail={'message': 'User not found'}
        )

    user_db.status_usuario = False
    session.add(user_db)
    session.commit()
    return {'message': 'User delete'}


@app.post('/token')
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
): 
    user= session.scalar(
        select(Usuario).where(
            Usuario.email == form_data.username
        )
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail={'message': 'Incorrect email or password'}
        )

    if not verify_password(form_data.password, user.senha_hash):
        raise HTTPException(
            status_code=401,
            detail={'message': 'Incorrect email or password'}
        )
        
