from django.urls import path, include
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token, refresh_jwt_token
from rest_framework.urlpatterns import format_suffix_patterns

from .views import *

extra_patterns = [
    path('all/', ListUsersAPI.as_view(), name="read_all"),
    path('active/', ActiveUserAPI.as_view(), name="change_active")
]

urlpatterns = [    
    # TOKENS
    path('token/auth/', obtain_jwt_token),
    path('token/verificate/', verify_jwt_token),
    path('token/refresh/', refresh_jwt_token),
    # - - - - -    
    # CRUD USERS
    path('login/', UserAccessAPI.as_view(), name="login"),
    path('logout/', UserAccessAPI.as_view(), name="logout"),
    path('', include(extra_patterns)),
    path('', CrudUsersAPI.as_view(), name="crud_write"),
    path('<str:email_instance>/', CrudUsersAPI.as_view(), name="crud_read"),
    # - - - - -
    # VERIFICATE PERMISSIONS URL
    path('permissions/all/<str:email_instance>/', PermissionsUserAPI.as_view(), name="my_permissions"),
    path('verificate/administrator/', PermissionAdministratorAPI.as_view(), name="administrator"),
    path('verificate/simple/', PermissionSimpleAPI.as_view(), name="simple"),
    # - - - - -
    # RECOVERY PASSWORD
    path('password/recovery/', RecoveryPasswordAPI.as_view(), name="send_link"),
    path('password/<str:token>/', RecoveryPasswordAPI.as_view(), name="recovery"),
    
    path('user/<str:email_instance>/', UserPublicAPI.as_view(), name="info_user")
    # - - - - -
]