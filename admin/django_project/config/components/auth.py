import os


AUTH_USER_MODEL = "users.User"
AUTH_API_URL = os.environ.get('AUTH_API_URL')
AUTH_LOGIN_PATH = os.environ.get('AUTH_LOGIN_PATH')
AUTH_USER_INFO_PATH = os.environ.get('AUTH_USER_INFO_PATH')
AUTHENTICATION_BACKENDS = [
    'users.auth.CustomBackend',
    'django.contrib.auth.backends.ModelBackend'
]
