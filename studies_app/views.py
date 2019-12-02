from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import Permission
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers as decoder
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.translation import ugettext as _

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
    permission_classes = (StudyAccessPermission, )
    
    def post(self, request, format=None):
        """Permite registrar un nuevo estudio
        """
        
        study = request.data["study"]
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
        """Permite activar o desactivar segun sea el estado actual del objeto
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
        instances = Study.objects.all()
        instances = decoder.serialize("json", instances)
        return HttpResponse(content=instances, status=HTTP_200_OK, content_type="application/json")
    
class CrudStudyCentersAPI(APIView):
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
        
        instances = StudyCenters.objects.filter(study_id=study_id).values("study_id", "center_id", "study_id__title_little", "center_id__name")
        instances = json.dumps(list(instances), cls=DjangoJSONEncoder)
        return HttpResponse(content=instances, status=HTTP_200_OK, content_type="application/json")

class CrudStudyUsersAPI(APIView):
    permission_classes = (StudyUsersAccessPermission, )
    
    def post(self, request, format=None):
        study = request.data["study"]
        serializer = StudyUsersSerializer(data=study)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return HttpResponse(status=HTTP_201_CREATED)
    
    def put(self, request, format=None):
        study = request.data["study"]
        study_id = request.data["study_instance"]
        try:
            instance = StudyUsers.objects.get(id=study_id)
        except:
            msg = _('El estudio no existe.')
            raise exceptions.NotFound(msg)
        serializer = StudyUsersSerializer(instance, data=study)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
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
        instances = StudyUsers.objects.filter(study_id=study_id).values("study_id", "user_id", "study_id__title_little", "user_id__email")
        instances = json.dumps(list(instances), cls=DjangoJSONEncoder)
        return HttpResponse(content=instances, status=HTTP_200_OK, content_type="application/json")
        