import sys
sys.path[0] = '/app'

import pytest
import asyncio
from sqlalchemy import select, delete

from src.main import app
from httpx import AsyncClient
from src.db.postgres import async_session
from src.models.users import User
from src.models.history import LoginHistory
from src.models.tokens import RefreshTokens


@pytest.fixture(scope="session")
def event_loop():
    # Кринге штука, которая делает новый event loop для теста
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()

    yield loop

    loop.close()


@pytest.fixture(scope="function")
async def clear_data():
    yield
    async with async_session() as session:
        sql_request = await session.execute(select(User).where(User.login == 'testuser'))
        user: User = sql_request.scalar()
        await session.execute(delete(LoginHistory).where(LoginHistory.user_id == user.id))
        await session.execute(delete(RefreshTokens).where(RefreshTokens.user_id == user.id))
        await session.delete(user)
        await session.commit()


@pytest.fixture()
async def test_client():
    async with AsyncClient(app=app, base_url="http://localhost/api/v1") as ac:
        yield ac
