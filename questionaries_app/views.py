from django.http import HttpResponse, JsonResponse

from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import *

from rest_framework import exceptions
from rest_framework.views import APIView
from django.core import serializers as decoder
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.translation import ugettext as _

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


class CrudQuestionaryAPI(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, format=None):
        questionary = request.data["questionary"]
        serializer = QuestionarySerializer(data=questionary)
        if serializer.is_valid(raise_exception=True):
            serializer = serializer.save()
        return HttpResponse(status=HTTP_201_CREATED)

    def put(self, request, format=None):
        questionary_id = request.data["questionary_id"]
        questionary = request.data["questionary"]

        try:
            instance = Questionary.objects.get(pk=questionary_id)
        except:
            msg = _('El cuestionario no existe.')
            raise exceptions.NotFound(msg)
        serializer = QuestionarySerializer(instance, data=questionary)
        if serializer.is_valid(raise_exception=True):
                study = serializer.save()
        return HttpResponse(status=HTTP_200_OK, content_type="application/json")
    
    def delete(self, request, format=None):
        questionary_id = request.data["questionary_id"]
        
        try:
            instance = Questionary.objects.get(pk=questionary_id)
            instance.is_active = not instance.is_active
            instance.save()
        except:
            msg = _('El cuestionario no existe.')
            raise exceptions.NotFound(msg)
        return HttpResponse(status=HTTP_200_OK, content_type="application/json")

    def get(self, request, questionary_id, format=None):
        try:
            instance = Questionary.objects.get(pk=questionary_id)
            instance = decoder.serialize("json", [instance])
        except:
            msg = _('El cuestionario no existe.')
            raise exceptions.NotFound(msg)
        return HttpResponse(content=instance, status=HTTP_200_OK, content_type="application/json")


class ListQuestionariesAPI(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, study_id, format=None):
        instances = Questionary.objects.filter(study_id=study_id).values()
        instances = json.dumps(list(instances), cls=DjangoJSONEncoder)
        return HttpResponse(content=instances, status=HTTP_200_OK, content_type="application/json")


class CrudPageAPI(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, format=None):
        page = request.data["page"]
        serializer = PageSerializer(data=page)
        if serializer.is_valid(raise_exception=True):
            serializer = serializer.save()
        return HttpResponse(status=HTTP_201_CREATED)


class ListPagesAPI(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, questionary_id, format=None):
        instances = Page.objects.filter(
            questionary_id=questionary_id).values().order_by('-pos_x')
        instances = json.dumps(list(instances), cls=DjangoJSONEncoder)
        return HttpResponse(content=instances, status=HTTP_200_OK, content_type="application/json")


class CrudSectionAPI(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, format=None):
        section = request.data["section"]
        serializer = SectionSerializer(data=section)
        if serializer.is_valid(raise_exception=True):
            serializer = serializer.save()
        return HttpResponse(status=HTTP_201_CREATED)


class ListSectionsAPI(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, questionary_id, format=None):
        instances = Section.objects.filter(
            page_id__questionary_id=questionary_id).values()
        instances = json.dumps(list(instances), cls=DjangoJSONEncoder)
        return HttpResponse(content=instances, status=HTTP_200_OK, content_type="application/json")


class CountQuestionariesAPI(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, study_id, format=None):
        count = Questionary.objects.filter(study_id=study_id).count()
        return HttpResponse(content=count, status=HTTP_200_OK, content_type="application/json")
