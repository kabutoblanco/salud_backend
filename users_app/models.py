from django.db import models
from places_app import models as places
from django.contrib.auth.models import Permission

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string

# Create your models here.
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings

URL_System = "http://localhost:3000/"
URL_RecoveryPassword = "http://localhost:3000/user/recovery/"

# Manager models.
# - - - - - - - - - - - - - - - - - -


class UserManager(BaseUserManager):
    """
    Clase que provee de servicios a las clase Administrator y Simple

    ...

    Methods
    - - - - -
    create_administrator(user_id, first_name, last_name, email, my_center, my_department)
        Crea un nuevo usuario administrador

    create_simple(user_id, first_name, last_name, email, my_center, my_department)
        Crea un nuevo usuario simple
    """

    def create_administrator(self, user_id, first_name, last_name, email, my_center, my_department):
        """Crea un nuevo usuario administrador
        
        Parameters
        - - - - -
        user_id : int
            Numero de identificacion
        first_name : str
            Nombres
        last_name : str
            Apellidos
        email : str
            Correo electronico
        my_center : int
            Centro al que el usuario pertenece
        my_department : int
            Departamento al que el usuario pertence
            
        Returns
        - - - - -
        object
            Un usuario administrador
        """
        
        administrator = Administrator(user_id=user_id, first_name=first_name, last_name=last_name, email=self.normalize_email(
            email), my_center=my_center, my_department=my_department)
        administrator.username = email
        password = get_random_string(length=6)
        administrator.set_password(password)
        administrator.is_staff = True
        administrator.save()
        administrator.send_create_password(password)
        administrator.user_permissions.add(
            Permission.objects.get(codename="view_user"))
        return administrator

    def create_simple(self, user_id, first_name, last_name, email, my_center, my_department):
        """Crea un nuevo usuario simple
        
        Parameters
        - - - - -
        user_id : int
            Numero de identificacion
        first_name : str
            Nombres
        last_name : str
            Apellidos
        email : str
            Correo electronico
        my_center : int
            Centro al que el usuario pertenece
        my_department : int
            Departamento al que el usuario pertence
            
        Returns
        - - - - -
        object
            Un usuario simple
        """
        
        simple = Simple(user_id=user_id, first_name=first_name, last_name=last_name, email=self.normalize_email(
            email), my_center=my_center, my_department=my_department)
        simple.username = email
        password = get_random_string(length=6)
        simple.set_password(password)
        simple.is_simple = True
        simple.save()
        simple.send_create_password(password)
        return simple


# - - - - - - - - - - - - - - - - - -


# Models.
# - - - - - - - - - - - - - - - - - -
class User(AbstractUser):
    """
    Clase que representa la redefinición de un Usuario en Django

    ...

    Attributes
    - - - - -
    user_id : int
        Numero de identificacion
    username : str
        Nombre de usuario, nickname, apodo
    email : str
        Correo electronico
    password : str
        Contraseña encriptada
    is_simple : boolean
        Indica si es un usuario simple
    my_center : int
        Centro al que el usuario pertenece
    my_department : int
        Departamento al que el usuario pertence

    Methods
    - - - - - 
    send_recovery_password(token)
        Envia un correo para recuperación de contraseña

    send_create_password(password)
        Envia un correo al recien creado usuario con las credenciales de acceso
    """

    user_id = models.IntegerField(default=0, unique=True)
    username = models.CharField(max_length=50, blank=True)
    email = models.EmailField(max_length=50, unique=True)
    password = models.CharField(max_length=236)
    is_simple = models.BooleanField(default=False)

    my_center = models.ForeignKey(
        places.Center, on_delete=models.CASCADE, blank=True, null=True)
    my_department = models.ForeignKey(
        places.Department, on_delete=models.CASCADE, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_id', 'username']

    def send_recovery_password(self, token):
        body = render_to_string('recovery_password.html', {
                                'first_name': self.first_name, 'last_name': self.last_name, 'url_recovery': '{}{}/'.format(URL_RecoveryPassword, token), 'url_page': URL_System},)
        email_message = EmailMessage(
            subject='Recuperación contraseña Clinapsis Unicauca',
            body=body,
            from_email=settings.EMAIL_HOST_USER,
            to=[self.email],
        )
        email_message.content_subtype = 'html'
        email_message.send()

    def send_create_password(self, password):
        body = render_to_string('new_user.html', {
                                'email': self.email, 'first_name': self.first_name, 'last_name': self.last_name, 'password': password, 'url_page': URL_System, 'url_recovery':  URL_RecoveryPassword},)
        email_message = EmailMessage(
            subject='Registro en la plataforma Clinapsis Unicauca',
            body=body,
            from_email=settings.EMAIL_HOST_USER,
            to=[self.email],
        )
        email_message.content_subtype = 'html'
        email_message.send()


class Administrator(User):
    """
    Clase que representa un usuario tipo Administrador

    ...

    Methods
    - - - - - 
    """

    objects = UserManager()

    class Meta:
        verbose_name = 'Administrator'
        verbose_name_plural = 'Administrators'


class Simple(User):
    """
    Clase que representa un usuario tipo Simple

    ...

    Methods
    - - - - - 
    """

    objects = UserManager()

    class Meta:
        verbose_name = 'Simple'
        verbose_name_plural = 'Simples'


class BlackListToken(models.Model):
    """
    Clase que representa la lista negra de Tokens

    ...

    Attributes
    - - - - -
    token : str
        Token de un usuario
    user : int
        Pk de un usuario
    timestamp : datetime
        Momento exacto cuando se dispara el evento
    """

    token = models.CharField(max_length=500)
    user = models.ForeignKey(
        User, related_name="token_user", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return '{} {}'.format(self.user, self.timestamp)

    class Meta:
        verbose_name = 'Token baneado'
        verbose_name_plural = 'Tokens baneados'
        
        unique_together = ("token", "user")


class BlackListIp(models.Model):
    """
    Clase que representa la lista negra de ip's

    ...

    Attributes
    - - - - - 
    ip : str
        Ip proveniente de la cabecera HTTP
    email : str
        Correo de un usuario
    timestamp : datetime
        Momento exacto cuando se dispara el evento
    country : int
        Numero de intentos provenientes de la misma ip e email
    """

    ip = models.CharField(max_length=500)
    email = models.EmailField(max_length=50)
    timestamp = models.DateTimeField(auto_now=True)
    country = models.IntegerField(default=0)
    
    def __str__(self):
        return '{} {}'.format(self.email, self.timestamp)

    class Meta:
        verbose_name = 'Ip baneada'
        verbose_name_plural = 'Ips baneadas'
        
        unique_together = ("ip", "email")

# - - - - - - - - - - - - - - - - - -
