from users_app.models import User

# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import Permission
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers as decoder
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.translation import ugettext as _

from .models import PermissionStudy
from .serializers import *
from .backends import StudyAccessPermission, StudyCentersAccessPermission, StudyUsersAccessPermission

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


class CrudStudiesAPI(APIView):
    """
    Clase que provee servicios CRUD de usuarios add:POST remove:DELETE put:UPDATE read:GET

    ...

    Attributes
    - - - - -
    permission_classes : lst
        Define los permisos para los servicios

    Methods
    - - - - -
    post(request)
        Permite registrar un nuevo estudio

    put(request)
        Permite actualizar un estudio

    delete(request, study_id)
        Permite activar o desactivar un estudio segun sea el caso

    get(request, study_id)
        Permite obtener un estudio
    """

    permission_classes = (StudyAccessPermission, )

    def post(self, request, format=None):
        """Permite registrar un nuevo estudio
        """

        study = request.data["study"]
        print(study)
        serializer = StudySerializer(data=study)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return HttpResponse(status=HTTP_201_CREATED)

    def put(self, request, format=None):
        """Permite actualizar un estudio
        """

        study = request.data["study"]
        study_id = request.data["study_id"]
        try:
            instance = Study.objects.get(id=study_id)
        except:
            msg = _('El estudio no existe.')
            raise exceptions.NotFound(msg)
        serializer = StudySerializer(instance, data=study)
        if serializer.is_valid(raise_exception=True):
            study = serializer.save()
        return HttpResponse(status=HTTP_200_OK)

    def delete(self, request, study_id, format=None):
        """Permite activar o desactivar un estudio segun sea el caso
        """

        try:
            instance = Study.objects.get(id=study_id)
            instance.is_active = not instance.is_active
            instance.save()
            return HttpResponse(status=HTTP_200_OK)
        except:
            msg = _('El estudio no existe.')
            raise exceptions.NotFound(msg)

    def get(self, request, study_id, format=None):
        """Permite obtener un estudio
        """

        try:
            instance = Study.objects.get(id=study_id)
            instance = decoder.serialize("json", [instance])
        except:
            msg = _('El estudio no existe.')
            raise exceptions.NotFound(msg)
        return HttpResponse(content=instance, status=HTTP_200_OK, content_type="application/json")


class ListStudiesAPI(APIView):
    permission_classes = (StudyAccessPermission, )

    def get(self, request, format=None):
        instances = Study.objects.all().values("id", "study_id", "title_little", "status", "date_reg", "date_in_study",
                                               "date_trueaout_end", "manager_reg", "manager_reg__first_name", "principal_inv", "principal_inv__first_name", "is_active")
        instances = json.dumps(list(instances), cls=DjangoJSONEncoder)
        return HttpResponse(content=instances, status=HTTP_200_OK, content_type="application/json")


class CrudStudyCentersAPI(APIView):
    """Clase que provee funciones para la relacion entre un estudio y varios centros
    """

    permission_classes = (StudyCentersAccessPermission, )

    def post(self, request, format=None):
        """Permite registrar un centro al estudio
        """

        study = request.data["study"]
        serializer = StudyCentersSerializer(data=study)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return HttpResponse(status=HTTP_201_CREATED)

    def put(self, request, format=None):
        """Permite modificar una tupla estudio centro
        """

        study = request.data["study"]
        study_id = request.data["study_instance"]
        try:
            instance = StudyCenters.objects.get(id=study_id)
        except:
            msg = _('El estudio no existe.')
            raise exceptions.NotFound(msg)
        serializer = StudyCentersSerializer(instance, data=study)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return HttpResponse(status=HTTP_200_OK)

    def delete(self, request, study_id, format=None):
        """Permite desactivar una tupla estudio centro
        """

        try:
            instance = StudyCenters.objects.get(id=study_id)
            instance.is_active = not instance.is_active
            instance.save()
            return HttpResponse(status=HTTP_200_OK)
        except:
            msg = _('El estudio no existe.')
            raise exceptions.NotFound(msg)

    def get(self, request, study_id, format=None):
        """Permite obtener todas las tuplas estudio centro
        """

        instances = StudyCenters.objects.filter(study_id=study_id).values(
            "study_id", "center_id", "study_id__title_little", "center_id__name")
        instances = json.dumps(list(instances), cls=DjangoJSONEncoder)
        return HttpResponse(content=instances, status=HTTP_200_OK, content_type="application/json")


class CrudStudyUsersAPI(APIView):
    """Clase que provee funciones para la relacion entre un estudio y varios usuarios
    """

    permission_classes = (StudyUsersAccessPermission, )

    def post(self, request, format=None):
        study = request.data["study"]
        permissions = request.data["permissions"]
        serializer = StudyUsersSerializer(data=study)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        is_permission = []
        if not study.get("is_manager"):
            for permission in permissions:
                try:
                    permission = PermissionStudy(studyUser_id=study.get("user_id"), permission_id=Permission.objects.get(
                        codename=permission.get("name")))
                    permission.save()
                except Permission.DoesNotExist:
                    is_permission.append(permission.get("name"))
        return JsonResponse({"detail": is_permission}, status=HTTP_201_CREATED, content_type="application/json")

    def put(self, request, format=None):
        study = request.data["study"]
        study_id = request.data["study_instance"]
        permissions_add = request.data["permissions_add"]
        permissions_remove = request.data["permissions_remove"]
        try:
            instance = StudyUsers.objects.get(pk=study_id)
        except:
            msg = _('El estudio no existe.')
            raise exceptions.NotFound(msg)
        serializer = StudyUsersSerializer(instance, data=study)
        is_permission = []
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            for permission_remove in permissions_remove:
                try:
                    permission = PermissionStudy.objects.get(studyUser_id=study_id, permission_id=Permission.objects.get(
                        codename=permission_remove.get("name")))
                    print(permission)
                    permission.delete()
                except:
                    is_permission.append(permission_remove.get("name"))

            for permission_add in permissions_add:
                try:
                    permission = PermissionStudy(studyUser_id=study_id, permission_id=Permission.objects.get(
                        codename=permission_add.get("name")))
                    permission.save()
                except:
                    is_permission.append(permission_add.get("name"))
        return HttpResponse(status=HTTP_200_OK)

    def delete(self, request, study_id, format=None):
        try:
            instance = StudyUsers.objects.get(id=study_id)
            instance.is_active = not instance.is_active
            instance.save()
            return HttpResponse(status=HTTP_200_OK)
        except:
            msg = _('El estudio no existe.')
            raise exceptions.NotFound(msg)

    def get(self, request, study_id, format=None):
        instances = StudyUsers.objects.filter(study_id=study_id).values(
            "id", "study_id", "user_id", "study_id__title_little", "user_id__email", "role", "is_manager")
        instances = json.dumps(list(instances), cls=DjangoJSONEncoder)
        return HttpResponse(content=instances, status=HTTP_200_OK, content_type="application/json")


class CrudUserStudiesAPI(APIView):
    """Clase que provee funciones para la relacion entre un usuario y varios estudios
    """

    permission_classes = (StudyUsersAccessPermission, )

    def get(self, request, user_id, format=None):
        instances = StudyUsers.objects.filter(user_id=user_id).values(
            "id", "study_id", "user_id", "study_id__title_little", "user_id__email", "role", "is_manager")
        instances = json.dumps(list(instances), cls=DjangoJSONEncoder)
        return HttpResponse(content=instances, status=HTTP_200_OK, content_type="application/json")


class CrudPermissionsAPI(APIView):
    """Clase que provee funciones para la relación entre el usuario de un estudio y sus permisos"""

    def get(self, request, study_id, format=None):
        instances = PermissionStudy.objects.filter(
            studyUser_id=study_id).values("id", "permission_id", "permission_id__codename")
        instances = json.dumps(list(instances), cls=DjangoJSONEncoder)
        return HttpResponse(content=instances, status=HTTP_200_OK, content_type="application/json")


class CrudStudyUserViewAPI(APIView):
    """Clase que provee la vista para traer la información completa de los detalles del usuario"""

    def get(self, request, study_id, format=None):
        try:
            instance = StudyUsers.objects.filter(id=study_id).values("id", "user_id__first_name", "user_id__last_name", "date_maxAccess", "is_active")
            instance = json.dumps(list(instance), cls=DjangoJSONEncoder)
        except:
            msg = _('El estudio no existe.')
            raise exceptions.NotFound(msg)
        return HttpResponse(content=instance, status=HTTP_200_OK, content_type="application/json")

