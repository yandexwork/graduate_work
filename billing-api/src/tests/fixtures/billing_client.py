from uuid import UUID
import json

import pytest_asyncio
from httpx import AsyncClient, Response

from app.tests.settings import billing_client_settings as settings


class BillingClient(AsyncClient):

    async def get_first_tariff_id(self) -> str:
        response = await self.get(settings.tariff_path)
        content = json.loads(response.content.decode('utf-8'))
        return content[0]['id']

    async def subscribe(self, tariff_id: UUID = None, headers=None) -> Response:
        payload = {"tariff_id": tariff_id}
        response = await self.post(
            settings.subscribe_path,
            json=payload,
            headers=headers
        )
        return response


@pytest_asyncio.fixture()
async def billing_client():
    async with BillingClient(base_url=settings.base_url) as billing_client:
        yield billing_client
