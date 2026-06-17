from lucro_admin.settings import Settings
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

engine= create_engine(Settings().DATABASE_URL)

def get_session():
    with Session(engine) as session:
        return session