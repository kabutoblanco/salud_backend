from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import Permission
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers as decoder
from django.core.serializers.json import DjangoJSONEncoder

from .serializers import *
from .backends import UserAccessPermission

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_jwt.settings import api_settings
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK,
    HTTP_201_CREATED
)

import json


class UserAccessAPI(APIView):
    permission_classes = (AllowAny, )
    @csrf_exempt
    # Post equals to LOGIN.
    def post(self, request, format=None):
        # TODO implements token.
        username = request.data.get("email")
        password = request.data.get("password")
        if username is None or password is None:
            return HttpResponse({"Ingrese usuario y contraseña"}, status=HTTP_400_BAD_REQUEST)
        user = authenticate(username=username, password=password)
        if not user:
            return HttpResponse({"El usuario no existe"}, status=HTTP_404_NOT_FOUND)
        # Create token user.
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        user = UserSerializer(user)
        return JsonResponse({"user": user.data, "token": token}, status=HTTP_200_OK)

    # DELETE equals to LOGOUT.
    def delete(self, request, format=None):
        pass


class CrudUsersAPI(APIView):
    permission_classes = (IsAuthenticated, UserAccessPermission, )
    @csrf_exempt
    def post(self, request, format=None):
        permissions = request.data["permissions"]
        user = request.data["user"]
        if user.get("type") is 1:
            serializer = AdministratorSerializer(data=user)
        elif user.get("type") is 2:
            serializer = SimpleSerializer(data=user)
        if serializer.is_valid(raise_exception=True):
            newUser = serializer.save()
            for permission in permissions:
                newUser.user_permissions.add(
                    Permission.objects.get(codename=permission.get("name")))
        return HttpResponse(status=HTTP_201_CREATED)

    def put(self, request, format=None):
        permissions_add = request.data["permissions_add"]
        permissions_remove = request.data["permissions_remove"]
        try:
            instance = User.objects.get(email=request.data["email_instance"])  
            user = request.data["user"]
            serializer = UserSerializer(instance, data=user)         
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()
                for permission_remove in permissions_remove:
                    user.user_permissions.remove(Permission.objects.get(
                        codename=permission_remove.get("name")))
                for permission_add in permissions_add:
                    user.user_permissions.add(Permission.objects.get(
                        codename=permission_add.get("name")))
            return HttpResponse(status=HTTP_200_OK)
        except:
            return HttpResponse({"El usuario no existe"}, status=HTTP_400_BAD_REQUEST)

    @csrf_exempt
    def delete(self, request, format=None):
        try:
            instance = User.objects.get(email=request.data.get("email_instance"))
            instance.delete()
            return HttpResponse(status=HTTP_200_OK)
        except:
            return HttpResponse({"El usuario no existe"}, status=HTTP_400_BAD_REQUEST)

    def get(self, request, email_instance, format=None):
        try:
            instance = User.objects.get(email=email_instance)
            instance = UserSerializer(instance)
            return JsonResponse({"user": instance.data}, status=HTTP_200_OK)
        except:
            return HttpResponse({"El usuario no existe"}, status=HTTP_400_BAD_REQUEST)

class ListUsersAPI(APIView):
    permission_classes = (IsAuthenticated, UserAccessPermission, )
    def get(self, request, format=None):
        instances = User.objects.all()
        instances = decoder.serialize("json", instances, fields=(
            "first_name", "last_name", "my_center", "my_department", "is_staff", "is_simple", "user_permissions"))
        return HttpResponse(instances, status=HTTP_200_OK)
    
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
            return HttpResponse({"El usuario no existe"}, status=HTTP_400_BAD_REQUEST)                    