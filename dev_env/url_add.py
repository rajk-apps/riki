from .urls import *
from django.urls import include
import os

urlpatterns += [path("%s/" % r, include("%s.urls" % r))
                for r in [os.environ.get('APP_NAME')]]
