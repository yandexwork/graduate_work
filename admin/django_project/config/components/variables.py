from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = True
ALLOWED_HOSTS = [os.environ.get("SITE_HOST"), 'localhost', '0.0.0.0']
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'
LANGUAGE_CODE = 'ru-RU'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = os.path.join(BASE_DIR, 'static/')
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
LOCALE_PATHS = ['movies/locale']
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
