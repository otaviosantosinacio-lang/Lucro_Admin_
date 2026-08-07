from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from lucro_admin.settings import DataBaseSettings

engine = create_async_engine(
    DataBaseSettings().DATABASE_URL
)

SessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)