from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import Permission
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers as decoder
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.translation import ugettext as _

from .serializers import *
from .backends import UserAccessPermission, IsAdministrator, BaseJSONWebTokenAuthentication, IsSimple, get_token_header, get_user_token

from rest_framework_jwt.utils import jwt_decode_handler
from rest_framework import exceptions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_jwt.settings import api_settings
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_202_ACCEPTED
)

import json
import jwt
import datetime
from .utils import careful_ip


class UserAccessAPI(APIView):
    """
    Clase que provee servicios de login:POST y logout:DELETE

    ...

    Attributes
    - - - - -
    permission_classes : lst
        Define los permisos para los servicios

    Methods
    - - - - -
    post(request)
        Permite a un visitante obtener credenciales para ingresar al sistema

    delete(request)
        Permite a un usuario cerrar sesion de manera segura
    """

    permission_classes = (AllowAny, )
    @csrf_exempt
    # Post equals to LOGIN.
    def post(self, request, format=None):
        """Permite a un visitante obtener credenciales para ingresar al sistema

        Parameters
        - - - - -
        request : object
            Objeto de solicitud que debe contener email y password

        Returns
        - - - - -
        JsonResponse
            Un objeto con el usuario, token y el status 200 OK

        Raises
        - - - - -
        NotFound
            Si no existe un usuario con el email y password proveidos
        """

        # TODO implements token.
        username = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if not user:
            careful_ip(request, username)
            msg = _('El usuario no existe.')
            raise exceptions.NotFound(msg)
        # Create token user.
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        # - - - - - - -
        try:
            BlackListIp.objects.get(ip=ip, email=username).delete()
        except:
            pass
        user.last_login = datetime.datetime.now()
        user.save()
        user = UserSerializer(user)
        return JsonResponse({"user": user.data, "token": token}, status=HTTP_202_ACCEPTED, content_type="application/json")

    # DELETE equals to LOGOUT.
    def delete(self, request, format=None):
        """Permite a un usuario cerrar sesion de manera segura

        Parameters
        - - - - -
        request : object
            Objeto de solicitud que debe contener email

        Returns
        - - - - -
        HttpResponse
            Un status 200 OK

        Raises
        - - - - -
        ParseError
            Si no existe un usuario con el email proveido
        """

        token = get_token_header(request)
        user = User.objects.get(email=get_user_token(request).get("email"))
        try:
            BlackListToken(token=token, user=user).save()
        except:
            msg = _('No se pudo cerrar la sesion.')
            raise exceptions.ParseError(msg)
        return HttpResponse(status=HTTP_200_OK)


class CrudUsersAPI(APIView):
    """
    Clase que provee servicios CRUD de usuarios add:POST remove:DELETE put:UPDATE read:GET

    ...

    Attributes
    - - - - -
    permission_classes : lst
        Define los permisos para los servicios

    Methods
    - - - - -
    post(request)
        Permite registrar un nuevo usuario

    put(request)
        Permite actualizar un usuario

    delete(request)
        Permite eliminar un usuario de forma permanente

    get(request, email_instance)
        Permite obtener un usuario
    """

    permission_classes = (IsAuthenticated, UserAccessPermission, )
    @csrf_exempt
    def post(self, request, format=None):
        """Permite registrar un nuevo usuario

        Parameters
        - - - - -
        request : object
            Objeto de solicitud que debe contener el objeto usuario

        Returns
        - - - - -
        JsonResponse
            Un objeto con una lista de permisos que fallaron en el registro y el status 201 CREATE

        Raises
        - - - - -
        NotAcceptable
            Si los datos solicitados no son validos
        """
        
        permissions = request.data["permissions"]
        user = request.data["user"]
        TYPE = user.get("type")
        if permissions is None or user is None or TYPE is None:
            msg = _('Ingrese los datos solicitados.')
            raise exceptions.NotAcceptable(msg)
        try:
            TYPE = int(TYPE)
        except:
            msg = _('Ingrese type como entero.')
            raise exceptions.NotAcceptable(msg)
        if TYPE is 1:
            serializer = AdministratorSerializer(data=user)
        elif TYPE is 2:
            serializer = SimpleSerializer(data=user)
        is_permission = []
        if serializer.is_valid(raise_exception=True):
            newUser = serializer.save()
            for permission in permissions:
                try:
                    newUser.user_permissions.add(
                        Permission.objects.get(codename=permission.get("name")))
                except Permission.DoesNotExist:
                    is_permission.append(permission.get("name"))
        return JsonResponse({"detail": is_permission}, status=HTTP_201_CREATED, content_type="application/json")

    def put(self, request, format=None):
        """Permite actualizar un usuario

        Parameters
        - - - - -
        request : object
            Objeto de solicitud que debe contener el email del usuario

        Returns
        - - - - -
        JsonResponse
            Un objeto con una lista de permisos que fallaron en la modificacion y el status 200 OK

        Raises
        - - - - -
        NotAcceptable
            Si los datos solicitados no son validos
        NotFound
            El usuario no existe
        """
        
        permissions_add = request.data["permissions_add"]
        permissions_remove = request.data["permissions_remove"]
        if permissions_add is None or permissions_remove is None:
            msg = _('Ingrese los datos solicitados.')
            raise exceptions.NotAcceptable(msg)
        try:
            instance = User.objects.get(email=request.data["email_instance"])
        except:
            msg = _('El usuario no existe.')
            raise exceptions.NotFound(msg)
        user = request.data["user"]
        serializer = UserSerializer(instance, data=user)
        is_permission = []
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            for permission_remove in permissions_remove:
                try:
                    user.user_permissions.remove(Permission.objects.get(
                        codename=permission_remove.get("name")))
                except:
                    is_permission.append(permission_remove.get("name"))

            for permission_add in permissions_add:
                try:
                    user.user_permissions.add(Permission.objects.get(
                        codename=permission_add.get("name")))
                except:
                    is_permission.append(permission_add.get("name"))
        return JsonResponse({"detail": is_permission}, status=HTTP_200_OK, content_type="application/json")

    @csrf_exempt
    def delete(self, request, format=None):
        """Permite eliminar un usuario de forma permanente

        Parameters
        - - - - -
        request : object
            Objeto de solicitud que debe contener el email del usuario

        Returns
        - - - - -
        HttpResponse
            Un status 200 OK

        Raises
        - - - - -
        NotFound
            El usuario no existe
        """
                
        try:
            instance = User.objects.get(
                email=request.data.get("email_instance"))
            instance.delete()
            return HttpResponse(status=HTTP_200_OK)
        except:
            msg = _('El usuario no existe.')
            raise exceptions.NotFound(msg)

    def get(self, request, email_instance, format=None):
        """Permite obtener un usuario

        Parameters
        - - - - -
        request : object
            Objeto de solicitud
        
        email_instance : str
            Correo del usuario deseado

        Returns
        - - - - -
        HttpResponse
            Un objeto con un usuario y el status 200 OK

        Raises
        - - - - -
        NotFound
            El usuario no existe
        """
              
        instance = User.objects.filter(email=email_instance).values("email", "first_name", "last_name",
                                                                    "my_center", "my_department", "my_center__name", "my_department__name", "is_staff", "is_simple")
        if list(instance).__len__() > 0:
            instance = json.dumps(list(instance), cls=DjangoJSONEncoder)
            return HttpResponse(content=instance, status=HTTP_200_OK, content_type="application/json")
        else:
            msg = _('El usuario no existe.')
            raise exceptions.NotFound(msg)


class ListUsersAPI(APIView):
    """
    Clase que provee servicios CRUD de usuarios read_all:GET

    ...

    Attributes
    - - - - -
    permission_classes : lst
        Define los permisos para los servicios

    Methods
    - - - - -
    get(request)
        Permite obtener todos los usuarios
    """

    permission_classes = (IsAuthenticated, UserAccessPermission, )

    def get(self, request, format=None):
        """Permite obtener todos los usuarios

        Parameters
        - - - - -
        request : object
            Objeto de solicitud

        Returns
        - - - - -
        HttpResponse
            Un objeto con una lista de todos los usuarios y el status 200 OK
        """
        
        instances = User.objects.all().values("email", "first_name", "last_name",
                                              "my_center__name", "my_department__name", "is_staff", "is_simple", "is_active")
        instances = json.dumps(list(instances), cls=DjangoJSONEncoder)
        return HttpResponse(content=instances, status=HTTP_200_OK, content_type="application/json")


class ActiveUserAPI(APIView):
    """
    Clase que provee servicios CRUD de usuarios put:UPDATE

    ...

    Attributes
    - - - - -
    permission_classes : lst
        Define los permisos para los servicios

    Methods
    - - - - -
    put(request)
        Permite activar o desactivar un usuario
    """

    permission_classes = (IsAuthenticated, UserAccessPermission, )

    def put(self, request, format=None):
        """Permite activar o desactivar un usuario

        Parameters
        - - - - -
        request : object
            Objeto de solicitud que contiene email_instance

        Returns
        - - - - -
        HttpResponse
            El status 200 OK
            
        Raises
        - - - - -
        NotFound
            El usuario no existe
        """
        
        try:
            instance = User.objects.get(email=request.data["email_instance"])
            is_active = request.data["is_active"]
            instance.is_active = is_active
            instance.save()
            return HttpResponse(status=HTTP_200_OK)
        except:
            msg = _('El usuario no existe.')
            raise exceptions.NotFound(msg)


class PermissionsUserAPI(APIView):
    """
    Clase que provee servicios para extraer todos los permisos de usuarios

    ...

    Attributes
    - - - - -
    permission_classes : lst
        Define los permisos para los servicios

    Methods
    - - - - -
    get(request, email_instance)
        Permite obtener todos los permisos de un usuario especifico
    """

    permission_classes = (IsAuthenticated, )

    def get(self, request, email_instance, format=None):
        """Permite obtener todos los permisos de un usuario especifico

        Parameters
        - - - - -
        request : object
            Objeto de solicitud
        
        email_instance : str
            Correo del usuario deseado

        Returns
        - - - - -
        HttpResponse
            Un objeto con una lista de todos los permisos del usuario y el status 200 OK
        """
        
        instances = User.objects.filter(email=email_instance).values(
            "user_permissions__codename")
        instances = json.dumps(list(instances), cls=DjangoJSONEncoder)
        return HttpResponse(content=instances, status=HTTP_200_OK, content_type="application/json")


class PermissionAdministratorAPI(APIView):
    """
    Clase que provee servicios de verificacion de rol usuario administrador

    ...

    Attributes
    - - - - -
    permission_classes : lst
        Define los permisos para los servicios

    Methods
    - - - - -
    post(request)
        Implicitamente verifica si es un usuario administrador mediante permission_classes:IsAdministrator
    """

    permission_classes = (IsAuthenticated, IsAdministrator, )

    def post(self, request, format=None):
        """Implicitamente verifica si es un usuario administrador mediante permission_classes:IsAdministrator

        Parameters
        - - - - -
        request : object
            Objeto de solicitud

        Returns
        - - - - -
        HttpResponse
            El status 200 OK
        """
        
        return HttpResponse(status=HTTP_200_OK)


class PermissionSimpleAPI(APIView):
    """
    Clase que provee servicios de verificacion de rol usuario simple

    ...

    Attributes
    - - - - -
    permission_classes : lst
        Define los permisos para los servicios

    Methods
    - - - - -
    post(request)
        Implicitamente verifica si es un usuario simple mediante permission_classes:IsSimple
    """
    
    permission_classes = (IsAuthenticated, IsSimple, )

    def post(self, request, format=None):
        """Implicitamente verifica si es un usuario simple mediante permission_classes:IsSimple

        Parameters
        - - - - -
        request : object
            Objeto de solicitud

        Returns
        - - - - -
        HttpResponse
            El status 200 OK
        """
        
        return HttpResponse(status=HTTP_200_OK)


class RecoveryPasswordAPI(APIView):
    """
    Clase que provee servicios para recuperacion de constraseña

    ...

    Attributes
    - - - - -
    permission_classes : lst
        Define los permisos para los servicios

    Methods
    - - - - -
    post(request, token)
        Permite modificar la contraseña de un usuario
        
    put(request)
        Permite solicitar mediante correo una nueva contraseña
    """
    
    permission_classes = (AllowAny, )

    def post(self, request, token, format=None):
        """Permite modificar la contraseña de un usuario

        Parameters
        - - - - -
        request : object
            Objeto de solicitud que contiene la nueva password
        
        token : str
            Token actual del usuario

        Returns
        - - - - -
        HttpResponse
            El status 200 OK
            
        Raises
        - - - - -
        NotFound
            El usuario no existe
        """
        
        password = request.data.get("password")
        user = jwt_decode_handler(token)
        user = User.objects.get(email=user.get("username"))
        if user is None or password is None:
            msg = _('El usuario no existe.')
            raise exceptions.NotFound(msg)
        user.set_password(password)
        user.save()
        return HttpResponse(status=HTTP_200_OK)

    def put(self, request, format=None):
        """Permite solicitar mediante correo una nueva contraseña

        Parameters
        - - - - -
        request : object
            Objeto de solicitud que contiene el correo
        
        token : str
            Token actual del usuario

        Returns
        - - - - -
        HttpResponse
            El status 200 OK
            
        Raises
        - - - - -
        NotFound
            El usuario no existe
        """
        
        email = request.data.get("email")
        user = User.objects.get(email=email)
        if user is None:
            msg = _('El usuario no existe.')
            raise exceptions.NotFound(msg)
        # Create token user.
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        # Send email user.
        user.send_recovery_password(token)
        return HttpResponse(status=HTTP_200_OK)
