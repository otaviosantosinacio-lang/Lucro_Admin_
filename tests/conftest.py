import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from lucro_admin.infra import models
from lucro_admin.infra.models.usuario import Usuario
from lucro_admin.infra.database import get_session
from lucro_admin.api.app import app

@pytest.fixture
def client(session):
    def get_session_override():
        return session
    
    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override

        yield client
    
    app.dependency_overrides.clear()

@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, 'connect')
    def ativar_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.close()

    models.registro_tabela.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    models.registro_tabela.metadata.drop_all(engine)

@pytest.fixture
def user(session):
    user= Usuario(
        nome_usuario='lucroadmintest',
        email='test@lucroadmin.com',
        senha_hash='lucro_admin_test',
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user