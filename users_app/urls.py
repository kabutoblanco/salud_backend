from django.urls import path, include
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token, refresh_jwt_token
from rest_framework.urlpatterns import format_suffix_patterns

from .views import *

extra_patterns = [
    path('all/', ListUsersAPI.as_view(), name="read_all"),
    path('active/', ActiveUserAPI.as_view(), name="change_active"),
]

urlpatterns = [    
    # TOKENS
    path('token/auth/', obtain_jwt_token),
    path('token/verificate/', verify_jwt_token),
    path('token/refresh/', refresh_jwt_token),
    # - - - - -    
    # CRUD USERS
    path('login/', UserAccessAPI.as_view(), name="login"),
    path('', include(extra_patterns)),
    path('', CrudUsersAPI.as_view(), name="crud_write"),
    path('<str:email_instance>/', CrudUsersAPI.as_view(), name="crud_read"),
    # - - - - -
]