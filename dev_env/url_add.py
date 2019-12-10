from .urls import *
from django.urls import include
import os

from django.contrib.admin.sites import site

urlpatterns += [
    path(
        "{}/".format(os.environ.get("APP_NAME")),
        include("{}.urls".format(os.environ.get("APP_NAME"))),
    ),
    path("accounts/login/", site.login),
    path("accounts/logout/", site.logout, name="logout"),
]
