from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import ugettext_lazy as _
from .models import *


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('user_id', 'username', 'email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'my_center', 'my_department')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user_id', 'email', 'username', 'password1', 'password2', 'is_superuser', 'is_staff', 'is_simple', 'my_center', 'my_department'),
        }),
    )
    list_display = ('id', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)


admin.site.register(Administrator, UserAdmin)
admin.site.register(Simple, UserAdmin)
admin.site.register(BlackListToken)
admin.site.register(BlackListIp)
admin.site.register(Permission)
