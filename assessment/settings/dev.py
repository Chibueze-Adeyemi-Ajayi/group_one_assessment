from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

# Additional dev-only apps
INSTALLED_APPS += [
]

# The following configuration is only needed for Django apps.
DJANGO_ALLOW_ASYNC_UNSAFE = "true"
