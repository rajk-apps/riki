import os
from .settings import *

INSTALLED_APPS = [os.environ.get("APP_NAME")] + INSTALLED_APPS

ROOT_URLCONF = "{}.url_add".format(os.environ.get("DJANGO_PROJECT"))

ALLOWED_HOSTS += [os.environ.get("DJANGO_HOST"), "localhost"]
