import jwt

from django.contrib.auth import get_user_model
from django.utils.encoding import smart_text
from django.utils.translation import ugettext as _
from rest_framework import exceptions
from rest_framework.authentication import (
    BaseAuthentication, get_authorization_header
)

from rest_framework import permissions

from .serializers import *

DELETE = 'DELETE'

# Permissions.
class UserAccessPermission(permissions.BasePermission):
    message = "No tiene permisos necesarios"
    
    def has_permission(self, request, view):
        user_request = User.objects.get(email=get_user_token(request).get("username"))
        if user_request is not None:
            if request.method in permissions.SAFE_METHODS:
                if user_request.has_perm("users_app.view_user"):
                    return True
            elif request.method is DELETE:
                if user_request.has_perm("users_app.delete_user"):
                    return True
            else:
                if user_request.has_perm("users_app.add_user") and user_request.has_perm("users_app.change_user"):
                    return True
            return False
        else:
            return False