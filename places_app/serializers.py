from rest_framework import serializers

from .models import *


class CenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Center
        fields = ("id", "name")
        
class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ("id", "name")