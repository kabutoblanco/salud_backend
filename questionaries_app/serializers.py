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
    
    def update(self, instance, validated_data):
        instance.code = validated_data.get("code", instance.code)
        instance.title = validated_data.get("title", instance.title)
        instance.description = validated_data.get("descriptio", instance.description)
        instance.num_minRegistry = validated_data.get("num_minRegistry", instance.num_minRegistry)
        instance.num_maxRegistry = validated_data.get("num_maxRegistry", instance.num_maxRegistry)
        instance.is_read = validated_data.get("is_read", instance.is_read)
        instance.is_accessExternal = validated_data.get("is_accessExternal", instance.is_accessExternal)
        
        instance.save()
        return instance


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
