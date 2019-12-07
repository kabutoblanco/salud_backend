import jwt
import datetime

from django.contrib.auth import get_user_model
from django.utils.encoding import smart_text
from django.utils.translation import ugettext as _

from rest_framework import exceptions
from rest_framework.authentication import (
    BaseAuthentication, get_authorization_header
)

from rest_framework import permissions
from rest_framework_jwt.settings import api_settings

from users_app.models import User
from users_app.backends import get_user_token, get_token_header

DELETE = 'DELETE'

class StudyAccessPermission(permissions.BasePermission):
    """
    Clase que define permisos para los usuarios
    
    ...

    Attributes
    - - - - -
    message : str
        Define un mensaje de error en caso que el usuario no tenga los permisos

    Methods
    - - - - -
    has_permission(request, view)
        Evalua si un usuario puede manipular la tabla de usuarios
    """
    
    message = "No tiene permisos necesarios"

    def has_permission(self, request, view):
        """Evalua si un usuario puede manipular la tabla `Study`

        Parameters
        - - - - -
        request : object
            Objeto de solicitud

        Returns
        - - - - -
        True
            Si el usuario (POST, PUT, GET, DELETE) tiene permisos para esos metodos
        False
            En caso contrario
        """
        
        user_request = User.objects.get(
            email=get_user_token(request).get("email"))
        if user_request:
            if request.method in permissions.SAFE_METHODS:
                if user_request.has_perm("users_app.view_study"):
                    return True
            elif request.method is DELETE:
                if user_request.has_perm("users_app.delete_study"):
                    return True
            else:
                if user_request.has_perm("users_app.add_study") and user_request.has_perm("users_app.change_study"):
                    return True
            return False
        else:
            return False
        
class StudyCentersAccessPermission(permissions.BasePermission):
    """
    Clase que define permisos para los usuarios
    
    ...

    Attributes
    - - - - -
    message : str
        Define un mensaje de error en caso que el usuario no tenga los permisos

    Methods
    - - - - -
    has_permission(request, view)
        Evalua si un usuario puede manipular la tabla de usuarios
    """
    
    message = "No tiene permisos necesarios"

    def has_permission(self, request, view):
        """Evalua si un usuario puede manipular la tabla `User`

        Parameters
        - - - - -
        request : object
            Objeto de solicitud

        Returns
        - - - - -
        True
            Si el usuario (POST, PUT, GET, DELETE) tiene permisos para esos metodos
        False
            En caso contrario
        """
        
        user_request = User.objects.get(
            email=get_user_token(request).get("email"))
        if user_request:
            if request.method in permissions.SAFE_METHODS:
                if user_request.has_perm("users_app.view_studycenters"):
                    return True
            elif request.method is DELETE:
                if user_request.has_perm("users_app.delete_studycenters"):
                    return True
            else:
                if user_request.has_perm("users_app.add_studycenters") and user_request.has_perm("users_app.change_studycenters"):
                    return True
            return False
        else:
            return False
        
class StudyUsersAccessPermission(permissions.BasePermission):
    """
    Clase que define permisos para los usuarios
    
    ...

    Attributes
    - - - - -
    message : str
        Define un mensaje de error en caso que el usuario no tenga los permisos

    Methods
    - - - - -
    has_permission(request, view)
        Evalua si un usuario puede manipular la tabla de usuarios
    """
    
    message = "No tiene permisos necesarios"

    def has_permission(self, request, view):
        """Evalua si un usuario puede manipular la tabla `User`

        Parameters
        - - - - -
        request : object
            Objeto de solicitud

        Returns
        - - - - -
        True
            Si el usuario (POST, PUT, GET, DELETE) tiene permisos para esos metodos
        False
            En caso contrario
        """
        
        user_request = User.objects.get(
            email=get_user_token(request).get("email"))
        if user_request:
            if request.method in permissions.SAFE_METHODS:
                if user_request.has_perm("users_app.view_studyusers"):
                    return True
            elif request.method is DELETE:
                if user_request.has_perm("users_app.delete_studyusers"):
                    return True
            else:
                if user_request.has_perm("users_app.add_studyusers") and user_request.has_perm("users_app.change_studyusers"):
                    return True
            return False
        else:
            return False