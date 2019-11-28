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
# from .backends import UserAccessPermission, IsAdministrator, BaseJSONWebTokenAuthentication, IsSimple, get_token_header, get_user_token

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

class StudiesCrudAPI(APIView):
    permission_classes(AllowAny, )
    
    def post(self, request, format=None):
        """Permite registrar un nuevo estudio
        """
        
        study = request.date["study"]
        serializer = StudySerializer(data=study)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return HttpResponse(status=HTTP_200_OK)
        