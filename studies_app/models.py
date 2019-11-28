from django.db import models
# from places_app import models as places
from django.contrib.auth.models import Permission

# from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string

# Create your models here.
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings

class StudyManager(BaseUserManager):
    

# Create your models here.

class Study(models.Model):
    study_id = models.CharField(max_length=50)
    title_little = models.CharField(max_length=50)
    title_long = models.CharField(max_length=120)
    date_reg = models.DateTimeField(auto_now=True)
    date_in_study = models.DateField(auto_now=True)
    date_prevout_end = modesl.DateField(auto_now=True)
    date_actout_end = modesl.DateField(auto_now=True)
    date_trueaout_end = modesl.DateField(auto_now=True)    
    description = models.CharField(max_length=524)
    promoter = models.CharField(max_length=50, blank=True)
    financial_entity = models.CharField(max_length=50, blank=True)
    amount = models.FloatField(default=0)
    manager_reg = models.ForeignKey(User, on_delete=models.CASCADE)
    principal_inv = models.ForeignKey(User, on_delete=models.CASCADE)
    manager_1 = models.ForeignKey(User, on_delete=models.CASCADE)
    manager_2 = models.ForeignKey(User, on_delete=models.CASCADE)
    is_valid = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ("manager_reg", "principal_inv", "manager_1", "manager_2")
