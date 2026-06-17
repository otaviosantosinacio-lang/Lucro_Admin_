from http import HTTPStatus

from fastapi import FastAPI, HTTPException, Depends

from lucro_admin.api.schemas import UserPublic, UserSchema, UserList
from lucro_admin.infra.models.usuario import Usuario
from lucro_admin.infra.database import get_session

from sqlalchemy import select
from sqlalchemy.orm import Session

app = FastAPI()


@app.get('/')
def home():
    boas_vindas = {
        'Olá usuário, seja bem-vindo ao Lucro Admin, um sistema financeiro'
        ' para gerenciamento das suas vendas'
    }
    return boas_vindas


@app.post('/users', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema, session: Session= Depends(get_session)):
    
    db_user= session.scalar(
        select(Usuario).where(
            (Usuario.nome_usuario == user.nome_usuario) | 
            (Usuario.email == user.email)
        )
    )

    if db_user:
        if db_user.nome_usuario == user.nome_usuario:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, 
                detail='Username alreadry exists'
            )
        
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, 
                detail='Email alreadry exists'
            )
    
    db_user= Usuario(
        nome_usuario= user.nome_usuario,
        email= user.email,
        senha_hash= user.senha_hash
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user

@app.get('/users/', response_model=UserList)
def read_users(
    limit: int= 100,
    offset: int= 0,
    session: Session= Depends(get_session)
):
    users= session.scalars(
        select(Usuario).limit(limit).offset(offset) 
    )

    return {'users': users}

@app.put('/users/{user_id}', response_model=UserPublic)
def update_user(
    user_id: int, 
    user: UserSchema,
    session: Session= Depends(get_session)
    ):
    
@app.delete('/user/{user_id}')
def delete_user(
    user_id: int,
    session: Session= Depends(get_session)
)