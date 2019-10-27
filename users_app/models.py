from django.db import models
from places_app import models as places

# Create your models here.
from django.contrib.auth.models import AbstractUser, BaseUserManager


# Manager models.
# - - - - - - - - - - - - - - - - - -
class UserManager(BaseUserManager):
    def create_administrator(self, username, user_id, first_name, last_name, email, password, my_center, my_department):
        administrator = Administrator(user_id=user_id, username=username, first_name=first_name, last_name=last_name, email=self.normalize_email(
            email), my_center=my_center, my_department=my_department)
        administrator.set_password(password)
        administrator.is_staff = True
        administrator.save()
        return administrator

    def create_simple(self, username, user_id, first_name, last_name, email, password, my_center, my_department):
        simple = Simple(user_id=user_id, username=username, first_name=first_name, last_name=last_name, email=self.normalize_email(
            email), my_center=my_center, my_department=my_department)
        simple.set_password(password)
        simple.is_simple = True
        simple.save()
        return simple

# - - - - - - - - - - - - - - - - - -


# Models.
# - - - - - - - - - - - - - - - - - -
class User(AbstractUser):
    user_id = models.IntegerField(default=0, unique=True)
    username = models.CharField(max_length=23, blank=True)
    email = models.EmailField(max_length=50, unique=True)
    password = models.CharField(max_length=236)
    is_simple = models.BooleanField(default=False)

    my_center = models.ForeignKey(
        places.Center, on_delete=models.CASCADE, blank=True, null=True)
    my_department = models.ForeignKey(
        places.Department, on_delete=models.CASCADE, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_id', 'username']


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

# - - - - - - - - - - - - - - - - - -
