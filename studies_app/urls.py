from django.urls import path, include
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token, refresh_jwt_token
from rest_framework.urlpatterns import format_suffix_patterns

from .views import *

urlpatterns = [
    # TOKENS
    path('token/auth/', obtain_jwt_token),
    path('token/verificate/', verify_jwt_token),
    path('token/refresh/', refresh_jwt_token),
]
