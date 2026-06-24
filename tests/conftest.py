import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from lucro_admin.api.app import app
from lucro_admin.api.security import get_password_hash
from lucro_admin.infra import models
from lucro_admin.infra.database import get_session
from lucro_admin.infra.models.usuario import Usuario
from lucro_admin.settings import Settings


@pytest.fixture
def client(session: AsyncSession):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override

        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        'sqlite+aiosqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine.sync_engine, 'connect')
    def ativar_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.close()

    async with engine.begin() as conn:
        await conn.run_sync(models.registro_tabela.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(models.registro_tabela.metadata.drop_all)


@pytest_asyncio.fixture
async def user(session: AsyncSession):
    password: str = 'lucro_admin_test'
    user = Usuario(
        nome_usuario='lucroadmintest',
        email='test@lucroadmin.com',
        senha_hash=get_password_hash(password),
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = password
    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    return response.json()['access_token']


@pytest.fixture
def settings():
    return Settings()
