import os


AUTH_USER_MODEL = "users.User"
AUTH_API_LOGIN_URL = os.environ.get('AUTH_API_LOGIN_URL')
AUTHENTICATION_BACKENDS = [
    'users.auth.CustomBackend',
    'django.contrib.auth.backends.ModelBackend'
]
