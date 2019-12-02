from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import ugettext_lazy as _
from .models import *

admin.site.register(Study)
admin.site.register(StudyCenters)
admin.site.register(StudyUsers)