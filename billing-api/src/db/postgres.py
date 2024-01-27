from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession, Session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from core.config import settings


engine: AsyncEngine | None = None
Base = declarative_base()


async def get_async_session() -> AsyncSession:
    async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


def get_sync_session() -> Session:
    sync_engine = create_engine(settings.dsn_sync, future=True)
    sync_session = sessionmaker(bind=sync_engine, class_=Session, expire_on_commit=False)
    with sync_session() as session:
        return session
