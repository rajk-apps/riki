from .urls import *
from django.urls import include
import os

urlpatterns += [path("{}/".format(os.environ.get('APP_NAME')),
                     include("{}.urls".format(os.environ.get('APP_NAME')))),
                path('accounts/login/', include('django.contrib.auth.views.login'))]
