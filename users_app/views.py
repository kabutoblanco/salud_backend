from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import Permission
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers as decoder
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.translation import ugettext as _

from .serializers import *
from .backends import UserAccessPermission, IsAdministrator, IsSimple, get_token_header, get_user_token    

from rest_framework_jwt.utils import jwt_decode_handler
from rest_framework import exceptions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_jwt.settings import api_settings
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_202_ACCEPTED
)

import json
import jwt
import datetime
from .utils import careful_ip


class UserAccessAPI(APIView):
    permission_classes = (AllowAny, )
    @csrf_exempt
    # Post equals to LOGIN.
    def post(self, request, format=None):
        # TODO implements token.
        username = request.data.get("email")
        password = request.data.get("password")
        if username is None or password is None:
            msg = _('Ingrese usuario y contraseña.')
            raise exceptions.NotAcceptable(msg)
        user = authenticate(username=username, password=password)        
        if not user:
            careful_ip(request, username)
            msg = _('El usuario no existe.')
            raise exceptions.NotFound(msg)
        # Create token user.
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)        
        # - - - - - - - 
        try:
            BlackListIp.objects.get(ip=ip, email=username).delete()   
        except:
            pass
        user.last_login = datetime.datetime.now()
        user.save()
        user = UserSerializer(user)
        return JsonResponse({"user": user.data, "token": token}, status=HTTP_202_ACCEPTED, content_type="application/json")

    # DELETE equals to LOGOUT.
    def delete(self, request, format=None):
        token = get_token_header(request)
        user = User.objects.get(email=get_user_token(request).get("username"))
        try:
            BlackListToken(token=token, user=user).save()
        except:
            msg = _('No se pudo cerrar la sesion.')
            raise exceptions.ParseError(msg)
        return HttpResponse(status=HTTP_200_OK)


class CrudUsersAPI(APIView):
    permission_classes = (IsAuthenticated, UserAccessPermission, )
    @csrf_exempt
    def post(self, request, format=None):
        permissions = request.data["permissions"]
        user = request.data["user"]
        TYPE = user.get("type")
        if permissions is None or user is None or TYPE is None:
            msg = _('Ingrese los datos solicitados.')
            raise exceptions.NotAcceptable(msg)
        try:
            TYPE = int(TYPE)
        except:
            msg = _('Ingrese type como entero.')
            raise exceptions.NotAcceptable(msg)
        if TYPE is 1:
            serializer = AdministratorSerializer(data=user)
        elif TYPE is 2:
            serializer = SimpleSerializer(data=user)
        is_permission = ""
        if serializer.is_valid(raise_exception=True):
            newUser = serializer.save()
            for permission in permissions:
                try:
                    newUser.user_permissions.add(
                        Permission.objects.get(codename=permission.get("name")))
                except Permission.DoesNotExist:
                    is_permission = is_permission + permission.get("name") + "|"
        return JsonResponse({"detail": is_permission}, status=HTTP_201_CREATED, content_type="application/json")

    def put(self, request, format=None):
        permissions_add = request.data["permissions_add"]
        permissions_remove = request.data["permissions_remove"]
        if permissions_add is None or permissions_remove is None:
            msg = _('Ingrese los datos solicitados.')
            raise exceptions.NotAcceptable(msg)
        try:
            instance = User.objects.get(email=request.data["email_instance"])
        except:
            msg = _('El usuario no existe.')
            raise exceptions.NotFound(msg)
        user = request.data["user"]
        serializer = UserSerializer(instance, data=user)
        is_permission = ""
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            try:
                for permission_remove in permissions_remove:
                    user.user_permissions.remove(Permission.objects.get(
                        codename=permission_remove.get("name")))
            except:
                is_permission = is_permission + permission_remove.get("name") + "|"
            try:
                for permission_add in permissions_add:
                    user.user_permissions.add(Permission.objects.get(
                        codename=permission_add.get("name")))
            except:
                is_permission = is_permission + permission_add.get("name") + "|"
        return JsonResponse({"detail": is_permission}, status=HTTP_200_OK, content_type="application/json")        

    @csrf_exempt
    def delete(self, request, format=None):
        try:
            instance = User.objects.get(
                email=request.data.get("email_instance"))
            instance.delete()
            return HttpResponse(status=HTTP_200_OK)
        except:
            msg = _('El usuario no existe.')
            raise exceptions.NotFound(msg)

    def get(self, request, email_instance, format=None):
        try:
            instance = User.objects.filter(email=email_instance).values("first_name", "last_name", "my_center__name", "my_department__name", "is_staff", "is_simple", "user_permissions")
            instance = json.dumps(list(instance), cls=DjangoJSONEncoder)
            return HttpResponse(content=instance, status=HTTP_200_OK, content_type="application/json")
        except User.DoesNotExist:
            msg = _('El usuario no existe.')
            raise exceptions.NotFound(msg)


class ListUsersAPI(APIView):
    permission_classes = (IsAuthenticated, UserAccessPermission, )

    def get(self, request, format=None):
        instances = User.objects.all().values("first_name", "last_name", "my_center__name", "my_department__name", "is_staff", "is_simple", "user_permissions")
        instances = json.dumps(list(instances), cls=DjangoJSONEncoder)
        return HttpResponse(content=instances, status=HTTP_200_OK, content_type="application/json")


class ActiveUserAPI(APIView):
    permission_classes = (IsAuthenticated, UserAccessPermission, )

    def put(self, request, format=None):
        try:
            instance = User.objects.get(email=request.data["email_instance"])
            is_active = request.data["is_active"]
            instance.is_active = is_active
            instance.save()
            return HttpResponse(status=HTTP_200_OK)
        except:
            msg = _('El usuario no existe.')
            raise exceptions.NotFound(msg)
        
class PermissionAdministratorAPI(APIView):
    permission_classes = (IsAuthenticated, IsAdministrator, )
    
    def post(self, request, format=None):
        return HttpResponse(status=HTTP_200_OK)

class PermissionSimpleAPI(APIView):
    permission_classes = (IsAuthenticated, IsSimple, )
    
    def post(self, request, format=None):
        return HttpResponse(status=HTTP_200_OK)
    
class RecoveryPasswordAPI(APIView):
    permission_classes = (AllowAny, )
    
    def post(self, request, token, format=None):
        password = request.data.get("password")
        user = jwt_decode_handler(token)
        user = User.objects.get(email=user.get("username"))
        if user is None or password is None:
            msg = _('El usuario no existe.')
            raise exceptions.NotFound(msg)
        user.set_password(password)
        user.save()
        return HttpResponse(status=HTTP_200_OK)
    
    def put(self, request, format=None):
        email = request.data.get("email")
        user = User.objects.get(email=email)
        if user is None:
            msg = _('El usuario no existe.')
            raise exceptions.NotFound(msg)
        # Create token user.
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        # Send email user.
        user.send_recovery_password(token)
        return HttpResponse(status=HTTP_200_OK)
    
    