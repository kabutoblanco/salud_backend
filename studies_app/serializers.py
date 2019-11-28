from rest_framework import serializers
from rest_framework_jwt.utils import jwt_decode_handler

from .models import *


class StudySerializer(serializers.ModelSerializer):
    class Meta:
        model = Study
        
    def create(self, validated_data):
        return Study.objects.create_administrator(**validated_data)