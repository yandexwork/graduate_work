from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.core.config import settings


Base = declarative_base()

engine = create_async_engine(settings.DB_URL, echo=True, future=True)
async_session = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def create_database() -> None:
    """Создание таблиц, в случае наличия Alembic странная вещь"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def purge_database() -> None:
    """Удаление всех таблиц, тоже странная вещь"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def get_session() -> AsyncSession:
    """Получение сессии"""
    async with async_session() as session:
        yield session
