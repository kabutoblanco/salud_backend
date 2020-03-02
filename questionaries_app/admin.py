from django.contrib import admin

from django.utils.translation import ugettext_lazy as _
from .models import *

admin.site.register(Questionary)
admin.site.register(Page)
admin.site.register(Section)
admin.site.register(Question)
