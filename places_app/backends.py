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
from users_app.serializers import get_user_token
from users_app.models import User

DELETE = 'DELETE'


class CenterAccessPermission(permissions.BasePermission):
    message = "No tiene permisos necesarios"

    def has_permission(self, request, view):
        user_request = User.objects.get(
            email=get_user_token(request).get("username"))
        if user_request is not None:
            if request.method in permissions.SAFE_METHODS:
                if user_request.has_perm("users_app.view_center"):
                    return True
            elif request.method is DELETE:
                if user_request.has_perm("users_app.delete_center"):
                    return True
            else:
                if user_request.has_perm("users_app.add_center") and user_request.has_perm("users_app.change_center"):
                    return True
            return False
        else:
            return False

class DepartmentAccessPermission(permissions.BasePermission):
    message = "No tiene permisos necesarios"

    def has_permission(self, request, view):
        user_request = User.objects.get(
            email=get_user_token(request).get("username"))
        if user_request is not None:
            if request.method in permissions.SAFE_METHODS:
                if user_request.has_perm("users_app.view_department"):
                    return True
            elif request.method is DELETE:
                if user_request.has_perm("users_app.delete_department"):
                    return True
            else:
                if user_request.has_perm("users_app.add_department") and user_request.has_perm("users_app.change_department"):
                    return True
            return False
        else:
            return False
