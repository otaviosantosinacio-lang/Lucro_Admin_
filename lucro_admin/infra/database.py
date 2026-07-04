from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from lucro_admin.settings import DataBaseSettings

engine = create_async_engine(DataBaseSettings().DATABASE_URL)


async def get_session():  # pragma: no cover
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
