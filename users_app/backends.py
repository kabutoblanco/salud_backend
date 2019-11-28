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

from .models import User, Administrator, Simple, BlackListToken, BlackListIp

DELETE = 'DELETE'


jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER


class BaseJSONWebTokenAuthentication(BaseAuthentication):
    """
    Token based authentication using the JSON Web Token standard.
    """

    def authenticate(self, request):
        """
        Returns a two-tuple of `User` and token if a valid signature has been
        supplied using JWT-based authentication.  Otherwise returns `None`.
        """
        user = request.data.get("email")
        ip = request.META.get("REMOTE_ADDR")
        self.validate_ip(ip, user)
        
        jwt_value = self.get_jwt_value(request)

        if jwt_value is None:
            return None
        
        token = get_token_header(request)        
        user = jwt.decode(jwt_value, verify=False).get("user_id")             
        self.validate_token(token, user, jwt_value)
        
        try:
            payload = jwt_decode_handler(jwt_value)
        except jwt.ExpiredSignature:
            token = get_token_header(request)
            try:
                BlackListToken.objects.get(token=token, user=user).delete()
            except:
                pass
            msg = _('Signature has expired.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.DecodeError:
            msg = _('Error decoding signature.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed()

        user = self.authenticate_credentials(payload)

        return (user, jwt_value)

    def authenticate_credentials(self, payload):
        """
        Returns an active user that matches the payload's user id and email.
        """
        User = get_user_model()
        username = jwt_get_username_from_payload(payload)

        if not username:
            msg = _('Invalid payload.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = User.objects.get_by_natural_key(username)
        except User.DoesNotExist:
            msg = _('Invalid signature.')
            raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = _('User account is disabled.')
            raise exceptions.AuthenticationFailed(msg)

        return user
    
    def validate_token(self, token, user, jwt_value):
        """Verifica que el token no se encuentre en la lista negra
        
        Parameters
        - - - - -
        token : str
            Token de un usuario
        
        user : str
            Pk de un usuario
            
        Raises
        - - - - -
        AuthenticationFailed
            Si el token se encuetra en la lista negra y ha expirado
        """
        
        is_logout = False
        try:
            is_logout = BlackListToken.objects.get(token=token, user=user) is not None
        except:
            pass
        is_valid = datetime.datetime.fromtimestamp(jwt.decode(
            jwt_value, verify=False).get("exp")) >= datetime.datetime.now()
        
        if is_logout and is_valid:
            msg = _('Session has expired.')
            raise exceptions.AuthenticationFailed(msg)
    
    def validate_ip(self, ip, user):
        """Verifica que la ip ha sido bloqueada
        
        Parameters
        - - - - -
        ip : str
            Ip de la cabecera de una solicitud
        
        user : str
            Correo de un usuario
            
        Raises
        - - - - -
        AuthenticationFailed
            Si la ip esta en la lista negra, el tiempo de espera a un es menor a 1 hora y el número de intentos supera los 10
        """
        
        status_time = False
        status_count = False
        ip_black = None
        try:
            ip_black = BlackListIp.objects.get(ip=ip, email=user)
            Y = int(ip_black.timestamp.strftime("%Y"))
            m = int(ip_black.timestamp.strftime("%m"))
            d = int(ip_black.timestamp.strftime("%d"))
            H = int(ip_black.timestamp.strftime("%H"))
            M = int(ip_black.timestamp.strftime("%M"))
            S = int(ip_black.timestamp.strftime("%S"))
            date1 = datetime.datetime(Y, m, d, H, M, S)
                                    
            status_time = datetime.datetime.now() - date1 < datetime.timedelta(seconds=40)
            status_count = ip_black.country > 7        
        except:
            pass
        if status_time and status_count:
            msg = _('Ip bloqueada, intentelo de nuevo mas tarde.')
            raise exceptions.AuthenticationFailed(msg)
        elif not status_time and ip_black:
            ip_black.delete()


class JSONWebTokenAuthentication(BaseJSONWebTokenAuthentication):
    """
    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string specified in the setting
    `JWT_AUTH_HEADER_PREFIX`. For example:

        Authorization: JWT eyJhbGciOiAiSFMyNTYiLCAidHlwIj
    """
    www_authenticate_realm = 'api'

    def get_jwt_value(self, request):
        auth = get_authorization_header(request).split()
        auth_header_prefix = api_settings.JWT_AUTH_HEADER_PREFIX.lower()

        if not auth:
            if api_settings.JWT_AUTH_COOKIE:
                return request.COOKIES.get(api_settings.JWT_AUTH_COOKIE)
            return None

        if smart_text(auth[0].lower()) != auth_header_prefix:
            return None

        if len(auth) == 1:
            msg = _('Invalid Authorization header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _('Invalid Authorization header. Credentials string '
                    'should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        return auth[1]

    def authenticate_header(self, request):
        """
        Return a string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response, or `None` if the
        authentication scheme should return `403 Permission Denied` responses.
        """
        return '{0} realm="{1}"'.format(api_settings.JWT_AUTH_HEADER_PREFIX, self.www_authenticate_realm)


def get_user_token(request):
    """Extrae el username:correo de la cabecera de la solicitud
    
    Parameters
    - - - - -
    request : object
        Objeto de solicitud
    
    Returns
    - - - - -
    str
        Correo del token
    None
        Si no existe la variable correo en el token
    """
    
    try:
        return jwt_decode_handler(request.META.get('HTTP_AUTHORIZATION').split(' ')[1])
    except:
        return None


def get_token_header(request):
    """Extrae el token de la cabecera de la solicitud
    
    Parameters
    - - - - -
    request : object
        Objeto de solicitud
    
    Returns
    - - - - -
    str
        Token
    None
        Si no existe el token en la solicitud
    """
    
    try:
        return request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
    except:
        return None

# Permissions.


class UserAccessPermission(permissions.BasePermission):
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
        
class IsAdministrator(permissions.BasePermission):
    message = "No tiene permisos de administrador"

    def has_permission(self, request, view):
        """Evalua si un usuario es de tipo usuario administrador

        Parameters
        - - - - -
        request : object
            Objeto de solicitud

        Returns
        - - - - -
        True
            Si el usuario es is_staff
        False
            En caso contrario
            
        Raises
        - - - - -
        DoesNotExist
            El usuario no existe
        """
        
        try:
            user_request = User.objects.get(
                email=get_user_token(request).get("email"))
            if user_request.is_superuser or user_request.is_staff:
                return True
            else:
                return False
        except Administrator.DoesNotExist:
            msg = _('No tiene credenciales de administrador.')
            raise exceptions.AuthenticationFailed(msg)
        
class IsSimple(permissions.BasePermission):
    message = "No tiene permisos de usuario simple"

    def has_permission(self, request, view):
        """Evalua si un usuario puede manipular la tabla de usuarios simples

        Parameters
        - - - - -
        request : object
            Objeto de solicitud

        Returns
        - - - - -
        True
            Si el usuario es existe en la tabla Simple
        False
            En caso contrario
            
        Raises
        - - - - -
        DoesNotExist
            El usuario no existe en la tabla Simple
        """
        
        try:
            user_request = Simple.objects.get(
                email=get_user_token(request).get("email"))
            if user_request:
                return True
            else:
                return False
        except Simple.DoesNotExist:
            msg = _('No tiene credenciales de usuario simple.')
            raise exceptions.AuthenticationFailed(msg)