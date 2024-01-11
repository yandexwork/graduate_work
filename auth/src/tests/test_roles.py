import json
import sys
import time
sys.path[0] = '/app'

import pytest
from sqlalchemy import select

from src.core.config import admin_settings
from src.db.postgres import async_session
from src.models.users import User


@pytest.mark.asyncio
async def test_roles(test_client):
    response = await test_client.get(
        "/roles/?page_size=20&page_number=1"
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_user_roles(test_client):
    async with async_session() as session:
        sql_request = await session.execute(select(User).where(User.login == admin_settings.ADMIN_LOGIN))
        user: User = sql_request.scalar()
    response = await test_client.get(
        f"/roles/user_roles/{user.id}"
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_roles_create(test_client):
    time.sleep(1)
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
    response = await test_client.post(
        "/roles/",
        headers={"Accept": "application/json", **cookies},
        json={
            "name": "test_roles"
        }
    )
    global role_id
    content = json.loads(response.content.decode('utf-8'))
    role_id = content['id']
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_roles_update(test_client):
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
    response = await test_client.put(
        f"/roles/{role_id}",
        headers={"Accept": "application/json", **cookies},
        json={
            "name": "new_test_roles"
        }
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_roles_attach(test_client):
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
    async with async_session() as session:
        sql_request = await session.execute(select(User).where(User.login == admin_settings.ADMIN_LOGIN))
        user: User = sql_request.scalar()
        payload = {
                "user_id": str(user.id),
                "role_id": role_id
            }
    response = await test_client.post(
        "/roles/attach_role",
        headers={"Accept": "application/json", **cookies},
        json=payload
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_roles_detach(test_client):
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
    async with async_session() as session:
        sql_request = await session.execute(select(User).where(User.login == admin_settings.ADMIN_LOGIN))
        user: User = sql_request.scalar()
    response = await test_client.delete(
        f"/roles/detach_role/?user_id={user.id}&role_id={role_id}",
        headers={"Accept": "application/json", **cookies},
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_roles_delete(test_client):
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
    response = await test_client.delete(
        f"/roles/{role_id}",
        headers={"Accept": "application/json", **cookies},
    )
    assert response.status_code == 204
