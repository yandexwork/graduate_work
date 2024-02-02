import uuid
from http import HTTPStatus
from uuid import UUID

import requests
from requests.exceptions import Timeout, TooManyRedirects, RequestException
import httpx

from core.config import settings
from core.exceptions import AuthServiceNoResponse, AuthServiceBadResponse


def auth_subscribe(user_id: UUID, tariff_id: UUID):
    url = settings.AUTH_API_SUBSCRIBE_URL
    headers = {settings.header_key: settings.header_value}
    payload = {"tariff_id": str(tariff_id)}
    try:
        response = requests.put(url + f'/{str(user_id)}', headers=headers, params=payload)
    except (TooManyRedirects, RequestException, Timeout):
        raise AuthServiceNoResponse
    if response.status_code != HTTPStatus.OK:
        raise AuthServiceBadResponse


def auth_unsubscribe(user_id):
    url = settings.AUTH_API_UNSUBSCRIBE_URL
    headers = {settings.header_key: settings.header_value}
    try:
        response = requests.put(url + f'/{str(user_id)}', headers=headers)
    except (TooManyRedirects, RequestException, Timeout):
        raise AuthServiceNoResponse
    if response.status_code != HTTPStatus.OK:
        raise AuthServiceBadResponse


async def auth_async_unsubscribe(user_id: UUID):
    url = settings.AUTH_API_UNSUBSCRIBE_URL
    headers = {settings.header_key: settings.header_value}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(url + f'/{str(user_id)}', headers=headers)
        except (TooManyRedirects, RequestException, Timeout):
            raise AuthServiceNoResponse
        if response.status_code != HTTPStatus.OK:
            raise AuthServiceBadResponse
