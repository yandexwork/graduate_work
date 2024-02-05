from http import HTTPStatus
from uuid import uuid4

import pytest


pytestmark = pytest.mark.asyncio


async def test_subscribe_unauthorized(billing_client):
    response = await billing_client.subscribe()
    assert response.status_code == HTTPStatus.UNAUTHORIZED


async def test_subscribe(auth_client, billing_client):
    tariff_id = await billing_client.get_first_tariff_id()
    auth_headers = await auth_client.get_auth_headers()
    response = await billing_client.subscribe(
        tariff_id=tariff_id, headers=auth_headers
    )
    assert response.status_code == HTTPStatus.CREATED


async def test_subscribe_invalid_tariff(auth_client, billing_client):
    invalid_tariff_id = str(uuid4())
    auth_headers = await auth_client.get_auth_headers()
    response = await billing_client.subscribe(
        tariff_id=invalid_tariff_id, headers=auth_headers
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
