from rest_framework import serializers
from rest_framework_jwt.utils import jwt_decode_handler

from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("user_id", "username", "first_name",
                  "last_name", "email", "my_center", "my_department", "is_active")
    
    def update(self, instance, validated_data):
        instance.email = validated_data.get("email", instance.email)
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.save()
        return instance
        

class AdministratorSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(default=0)
    username = serializers.CharField(max_length=23)
    email = serializers.EmailField(max_length=50)
    password = serializers.CharField(max_length=236)

    def create(self, validated_data):
        return Administrator.objects.create_administrator(**validated_data)

    def update(self, instance, validated_data):
        instance.email = validated_data.get("email", instance.email)
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.save()
        return instance

    class Meta:
        model = Administrator
        fields = ("user_id", "username", "first_name",
                  "last_name", "email", "password", "my_center", "my_department")


class SimpleSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(default=0)
    username = serializers.CharField(max_length=23)
    email = serializers.EmailField(max_length=50)
    password = serializers.CharField(max_length=236)
    
    class Meta:
        model = Simple
        fields = ("user_id", "username", "first_name",
                  "last_name", "email", "password", "my_center", "my_department")

    def create(self, validated_data):
        return Simple.objects.create_administrator(**validated_data) 

    def update(self, instance, validated_data):
        instance.email = validated_data.get("email", instance.email)
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.save()
        return instance

def get_user_token(request):
    try:
        return jwt_decode_handler(request.META.get('HTTP_AUTHORIZATION').split(' ')[1])
    except:
        return None
