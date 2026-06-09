import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from lucro_admin.infra.models.usuario import registro_tabela


@pytest.fixture
def session():
    engine = create_engine('sqlite:///:memory:')

    registro_tabela.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    registro_tabela.metadata.drop_all(engine)
