import json

import pytest


@pytest.mark.asyncio
async def test_create_user(test_client):
    response = await test_client.post(
        "/users/signup",
        json={
            'login': 'testuser',
            'password': 'qwerty12345',
            'first_name': 'testuser`',
            'last_name': 'testuser'
        })
    assert response.status_code == 200


def get_content(content):
    return json.loads(content.decode('utf-8'))


async def get_access_token(test_client, password):
    tokens_response = await test_client.post(
        "/auth/login",
        json={
            'login': 'testuser',
            'password': password
        }
    )
    content = get_content(tokens_response.content)
    access_token = content["access_token"]
    return access_token


@pytest.mark.asyncio
async def test_change_password(test_client):
    access_token = await get_access_token(test_client, 'qwerty12345')
    cookies = {"access_token": access_token}
    response = await test_client.put(
        "/users/change_password",
        headers={"Accept": "application/json", **cookies},
        json={
            "previous_password": "qwerty12345",
            "new_password": "qwerty123456"
        })
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_login_history(test_client):
    access_token = await get_access_token(test_client, 'qwerty123456')
    cookies = {"access_token": access_token}
    response = await test_client.get(
        "/users/get_user_history?page_size=20&page_number=1",
        headers={"Accept": "application/json", **cookies},
    )
    assert response.status_code == 200
    assert 1 <= len(get_content(response.content)) <= 20


@pytest.mark.asyncio
async def test_user_information(test_client, clear_data):
    access_token = await get_access_token(test_client, 'qwerty123456')
    cookies = {"access_token": access_token}
    response = await test_client.get(
        "/users/me",
        headers={"Accept": "application/json", **cookies},
    )
    assert response.status_code == 200
