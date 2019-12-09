from .models import User, BlackListIp

from django.utils.translation import ugettext as _

from rest_framework import exceptions

import datetime


def careful_ip(request, username):
    """Agrega una ip a la lista negra

    ... 

    Parameters
    - - - - -
    username : str
        Correo del usuario

    Raises
    - - - - -
    PermissionDenied
        Si la contraseña es incorrecta
    """

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
    
def translate(e):
    string = "{}".format(e.__cause__).split(" ")[3].split(".")[1]
    if string == 'email':
        return "correo"
    elif string == 'user_id':
        return 'identificación'
