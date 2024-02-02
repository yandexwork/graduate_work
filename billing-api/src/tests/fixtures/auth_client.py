import json

import pytest_asyncio
from httpx import AsyncClient

from app.tests.settings import auth_client_settings as settings


class AuthClient(AsyncClient):

    async def get_auth_headers(self) -> dict:
        auth_response = await self.post(
            settings.login_path,
            json={
                'login': settings.login,
                'password': settings.password
            }
        )
        content = json.loads(auth_response.content.decode('utf-8'))
        access_token = content["access_token"]
        cookies = {"cookie": f"access_token={access_token};"}
        headers = {"Accept": "application/json", **cookies}
        return headers


@pytest_asyncio.fixture()
async def auth_client():
    async with AuthClient(base_url=settings.base_url) as auth_client:
        yield auth_client
