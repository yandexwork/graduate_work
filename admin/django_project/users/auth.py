import http
import json

import requests
from requests.exceptions import ConnectionError
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model


User = get_user_model()


class CustomBackend(BaseBackend):

    def authenticate(self, request, username=None, password=None):
        login_url = settings.AUTH_API_LOGIN_URL
        payload = {'login': username, 'password': password}
        try:
            response = requests.post(login_url, data=json.dumps(payload))
        except ConnectionError:
            return None
        if response.status_code != http.HTTPStatus.OK:
            return None

        data = response.json()

        access_token = data['access_token']
        user_info_url = "https://9a2a-46-138-8-149.ngrok-free.app/api/v1/users/me"
        response = requests.get(user_info_url, cookies={'access_token': access_token})
        if response.status_code != http.HTTPStatus.OK:
            return None

        data = response.json()

        try:
            user, created = User.objects.get_or_create(id=data['id'],)
            user.email = data.get('login')
            user.last_name = data.get('login')
            user.first_name = data.get('first_name')
            user.last_name = data.get('last_name')
            user.is_admin = data.get('is_admin')
            if data.get('is_admin'):
                user.is_staff = True
            user.save()
        except Exception:
            return None

        return user

    def get_user(self, user_id):
        return User.objects.get(pk=user_id)
