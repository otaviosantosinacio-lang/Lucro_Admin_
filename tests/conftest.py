import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from lucro_admin.infra import models


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool
        )

    @event.listens_for(engine, 'connect')
    def ativar_foreign_keys(dbapi_connection, connection_record):
        cursor= dbapi_connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.close()

    models.registro_tabela.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    models.registro_tabela.metadata.drop_all(engine)
