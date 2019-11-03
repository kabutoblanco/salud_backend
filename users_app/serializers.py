from rest_framework import serializers
from rest_framework_jwt.utils import jwt_decode_handler

from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("user_id", "username", "first_name",
                  "last_name", "email", "my_center", "my_department", "is_active", "is_staff", "is_simple")

    def update(self, instance, validated_data):
        instance.email = validated_data.get("email", instance.email)
        instance.first_name = validated_data.get(
            "first_name", instance.first_name)
        instance.last_name = validated_data.get(
            "last_name", instance.last_name)
        instance.save()
        return instance


class AdministratorSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(default=0)
    email = serializers.EmailField(max_length=50)

    def create(self, validated_data):
        return Administrator.objects.create_administrator(**validated_data)

    def update(self, instance, validated_data):
        instance.email = validated_data.get("email", instance.email)
        instance.first_name = validated_data.get(
            "first_name", instance.first_name)
        instance.last_name = validated_data.get(
            "last_name", instance.last_name)
        instance.save()
        return instance

    class Meta:
        model = Administrator
        fields = ("user_id", "first_name", "last_name",
                  "email", "my_center", "my_department")


class SimpleSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(default=0)
    email = serializers.EmailField(max_length=50)

    class Meta:
        model = Simple
        fields = ("user_id", "first_name", "last_name",
                  "email", "my_center", "my_department")

    def create(self, validated_data):
        return Simple.objects.create_simple(**validated_data)

    def update(self, instance, validated_data):
        instance.email = validated_data.get("email", instance.email)
        instance.first_name = validated_data.get(
            "first_name", instance.first_name)
        instance.last_name = validated_data.get(
            "last_name", instance.last_name)
        instance.save()
        return instance
