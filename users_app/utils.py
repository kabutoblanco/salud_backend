from rest_framework import exceptions
from django.utils.translation import ugettext as _

from .models import User, BlackListIp

import datetime

def careful_ip(request, username):
    user = None
    try:                
        user = User.objects.get(email=username)                
        if user:
            ip = request.META.get("REMOTE_ADDR")                                
            try:                        
                ip_black = BlackListIp.objects.get(ip=ip, email=username)
                ip_black.country = ip_black.country + 1
                my_timezone = datetime.datetime.now() - datetime.timedelta(hours=5)
                ip_black.timestamp = my_timezone
                ip_black.save()
            except:
                BlackListIp(ip=ip, email=username).save()                                   
    except:
        pass
    
    if user:
        msg = _('Contraseña incorrecta.')
        raise exceptions.PermissionDenied(msg)