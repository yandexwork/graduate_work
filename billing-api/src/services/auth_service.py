import uuid
from http import HTTPStatus
from uuid import UUID

import requests
from requests.exceptions import Timeout, TooManyRedirects, RequestException

from core.config import settings
from core.exceptions import AuthServiceNoResponse, AuthServiceBadResponse


def auth_subscribe(user_id: UUID, tariff_id: UUID):
    url = settings.AUTH_API_SUBSCRIBE_URL
    headers = {"x-api-key": "11111"}
    payload = {"tariff_id": str(tariff_id)}
    try:
        response = requests.put(url + f'/{str(user_id)}', headers=headers, params=payload)
        print(response)
    except (TooManyRedirects, RequestException, Timeout):
        raise AuthServiceNoResponse
    if response.status_code != HTTPStatus.OK:
        raise AuthServiceBadResponse


def auth_unsubscribe(user_id):
    url = settings.AUTH_API_UNSUBSCRIBE_URL
    headers = {"x-api-key": "11111"}
    try:
        response = requests.put(url + f'/{str(user_id)}', headers=headers)
        print(response)
    except (TooManyRedirects, RequestException, Timeout):
        raise AuthServiceNoResponse
    if response.status_code != HTTPStatus.OK:
        raise AuthServiceBadResponse
