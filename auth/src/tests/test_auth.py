import sys
import json
sys.path[0] = '/app'

import pytest

from src.core.config import admin_settings


@pytest.mark.asyncio
async def test_login(test_client):
    tokens_response = await test_client.post(
        "/auth/login",
        json={
            'login': admin_settings.ADMIN_LOGIN,
            'password': admin_settings.ADMIN_PASSWORD
        }
    )
    assert tokens_response.status_code == 200


@pytest.mark.asyncio
async def test_login(test_client):
    tokens_response = await test_client.post(
        "/auth/login",
        json={
            'login': admin_settings.ADMIN_LOGIN,
            'password': admin_settings.ADMIN_PASSWORD
        }
    )
    assert tokens_response.status_code == 200


@pytest.mark.asyncio
async def test_refresh(test_client):
    tokens_response = await test_client.post(
        "/auth/login",
        json={
            'login': admin_settings.ADMIN_LOGIN,
            'password': admin_settings.ADMIN_PASSWORD
        }
    )
    content = json.loads(tokens_response.content.decode('utf-8'))
    access_token = content["access_token"]
    cookies = {"access_token": access_token}
    refresh_response = await test_client.post(
        "/auth/refresh",
        headers={"Accept": "application/json", **cookies}
    )
    assert refresh_response.status_code == 200


@pytest.mark.asyncio
async def test_logout(test_client):
    tokens_response = await test_client.post(
        "/auth/login",
        json={
            'login': admin_settings.ADMIN_LOGIN,
            'password': admin_settings.ADMIN_PASSWORD
        }
    )
    content = json.loads(tokens_response.content.decode('utf-8'))
    access_token = content["access_token"]
    cookies = {"access_token": access_token}
    refresh_response = await test_client.get(
        "/auth/logout",
        headers={"Accept": "application/json", **cookies}
    )
    assert refresh_response.status_code == 204
