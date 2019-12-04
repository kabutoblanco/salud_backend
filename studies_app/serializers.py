from rest_framework import serializers
from rest_framework_jwt.utils import jwt_decode_handler

from .models import *

class StudySerializer(serializers.ModelSerializer):
    class Meta:
        model = Study
        fields = "__all__"
        
    def create(self, validated_data):
        return Study.objects.create_study(**validated_data)
    
    def update(self, instance, validated_data):
        instance.title_little = validated_data.get("title_little", instance.title_little)
        instance.title_long = validated_data.get("title_long", instance.title_long)
        instance.date_trueaout_end = validated_data.get("date_trueaout_end", instance.date_trueaout_end)
        instance.description = validated_data.get("description", instance.description)
        instance.promoter = validated_data.get("promoter", instance.promoter)
        instance.financial_entity = validated_data.get("financial_entity", instance.financial_entity)
        instance.amount = validated_data.get("amount", instance.amount)
        instance.principal_inv = validated_data.get("principal_inv", instance.principal_inv)
        instance.manager_1 = validated_data.get("manager_1", instance.manager_1)
        instance.manager_2 = validated_data.get("manager_2", instance.manager_2)
        instance.save()
        return instance
    
class StudyCentersSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyCenters
        fields = "__all__"
        
    def create(self, validated_data):
        return StudyCenters.objects.create_studyCenters(**validated_data)
    
    def update(self, instance, validated_data):
        instance.study_id = validated_data.get("study_id", instance.study_id)
        instance.center_id = validated_data.get("center_id", instance.center_id)
        instance.save()
        return instance
    
class StudyUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyUsers
        fields = "__all__"
        
    def create(self, validated_data):
        return StudyUsers.objects.create_studyUsers(**validated_data)
    
    def update(self, instance, validated_data):
        instance.study_id = validated_data.get("study_id", instance.study_id)
        instance.user_id = validated_data.get("user_id", instance.user_id)
        instance.save()
        return instance
        