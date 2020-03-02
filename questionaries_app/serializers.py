from rest_framework import serializers
from rest_framework_jwt.utils import jwt_decode_handler

from .models import *


class QuestionarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Questionary
        fields = "__all__"

    def create(self, validated_data):
        questionary = Questionary.objects.create_questionary(**validated_data)
        return questionary


class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = "__all__"

    def create(self, validated_data):
        page = Page.objects.create_page(**validated_data)
        return page


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = "__all__"

    def create(self, validated_data):
        section = Section.objects.create_questionary(**validated_data)
        return section
