import os
from .settings import *

INSTALLED_APPS = [
    os.environ.get("APP_NAME"),
    "django_extensions",
] + INSTALLED_APPS

ROOT_URLCONF = "{}.url_add".format(os.environ.get("DJANGO_PROJECT"))

ALLOWED_HOSTS += [os.environ.get("DJANGO_HOST"), "localhost"]

NOTEBOOK_ARGUMENTS = ["--ip", "0.0.0.0", "--port", "8888", "--allow-root"]
