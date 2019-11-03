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
    def create_administrator(self, user_id, first_name, last_name, email, my_center, my_department):
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
    objects = UserManager()

    class Meta:
        verbose_name = 'Administrator'
        verbose_name_plural = 'Administrators'


class Simple(User):
    objects = UserManager()

    class Meta:
        verbose_name = 'Simple'
        verbose_name_plural = 'Simples'


class BlackListToken(models.Model):
    token = models.CharField(max_length=500)
    user = models.ForeignKey(
        User, related_name="token_user", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("token", "user")


class BlackListIp(models.Model):
    ip = models.CharField(max_length=500)
    email = models.EmailField(max_length=50)
    timestamp = models.DateTimeField(auto_now=True)
    country = models.IntegerField(default=0)

    class Meta:
        unique_together = ("ip", "email")

# - - - - - - - - - - - - - - - - - -
