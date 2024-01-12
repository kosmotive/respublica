import os

from backend.settings.common import *


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-vg-s)f30%m&e%)=$g7_(@l47q9g2&39#@myofzsx(2op$eqoq8'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Add random delays via middleware to simulate network jitter
SIMUL_NETWORK_JITTER = bool(os.environ.get('SIMUL_NETWORK_JITTER', False))
