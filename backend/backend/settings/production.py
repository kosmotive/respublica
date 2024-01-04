import os

from backend.settings.common import *


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['respublica.evoid.de']

STATIC_ROOT = BASE_DIR / 'static-deployed'
