from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers as decoder
from django.core.serializers.json import DjangoJSONEncoder

from .serializers import *
from .backends import CenterAccessPermission, DepartmentAccessPermission

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK,
    HTTP_201_CREATED
)

import json

class CrudCentersAPI(APIView):
    permission_classes = (IsAuthenticated, CenterAccessPermission, )
    serializer_class = CenterSerializer
    @csrf_exempt
    def post(self, request, format=None):
        center = request.data["center"]
        serializer = self.serializer_class(data=center)
        if serializer.is_valid(raise_exception=True):
            newCenter = serializer.save()
        return HttpResponse(status=HTTP_201_CREATED)
    
class ListCentersAPI(APIView):
    permission_classes = (IsAuthenticated, CenterAccessPermission, )
    def get(self, request, format=None):
        instances = Center.objects.all()
        instances = decoder.serialize("json", instances)
        return HttpResponse(content=instances, status=HTTP_200_OK, content_type="JSON")
    
class CrudDepartmentsAPI(APIView):
    permission_classes = (IsAuthenticated, DepartmentAccessPermission, )
    serializer_class = DepartmentSerializer
    @csrf_exempt
    def post(self, request, format=None):
        department = request.data["department"]
        serializer = self.serializer_class(data=department)
        if serializer.is_valid(raise_exception=True):
            newDepartment = serializer.save()
        return HttpResponse(status=HTTP_201_CREATED)
    
class ListDeparmentsAPI(APIView):
    permission_classes = (IsAuthenticated, DepartmentAccessPermission, )
    def get(self, request, format=None):
        instances = Department.objects.all()
        instances = decoder.serialize("json", instances)
        return HttpResponse(content=instances, status=HTTP_200_OK, content_type="JSON")
    