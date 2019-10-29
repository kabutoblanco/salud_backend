import jwt
from datetime import datetime

from django.contrib.auth import get_user_model
from django.utils.encoding import smart_text
from django.utils.translation import ugettext as _
from rest_framework import exceptions
from rest_framework.authentication import (
    BaseAuthentication, get_authorization_header
)

from rest_framework import permissions
from rest_framework_jwt.settings import api_settings

from .models import User, BlackListToken

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
        jwt_value = self.get_jwt_value(request)

        if jwt_value is None:
            return None

        token = get_token_header(request)
        user = jwt.decode(jwt_value, verify=False).get("user_id")
        is_logout = None
        
        try:
            is_logout = BlackListToken.objects.get(token=token, user=user)
        except:
            pass
        is_valid = datetime.fromtimestamp(jwt.decode(
            jwt_value, verify=False).get("exp")) >= datetime.now()
        
        if is_logout is not None and is_valid:
            msg = _('Session has expired.')
            raise exceptions.AuthenticationFailed(msg)

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
    try:
        return jwt_decode_handler(request.META.get('HTTP_AUTHORIZATION').split(' ')[1])
    except:
        return None


def get_token_header(request):
    try:
        return request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
    except:
        return None

# Permissions.


class UserAccessPermission(permissions.BasePermission):
    message = "No tiene permisos necesarios"

    def has_permission(self, request, view):
        user_request = User.objects.get(
            email=get_user_token(request).get("username"))
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
