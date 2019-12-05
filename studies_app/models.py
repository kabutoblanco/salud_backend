from django.db import models
# from places_app import models as places
from django.contrib.auth.models import Permission
from django.utils.translation import ugettext_lazy as _

# from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string

# Create your models here.
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
from users_app.models import User
from places_app.models import Center


class StudyManager(BaseUserManager):

    # Create your models here.
    def create_study(self, study_id, title_little, title_long, status, date_in_study, date_prevout_end, date_actout_end, date_trueaout_end, description, promoter, financial_entity, amount, manager_reg, principal_inv, manager_1, manager_2):
        study = Study(study_id=study_id, title_little=title_little, title_long=title_long, status=status, date_in_study=date_in_study,
                      date_prevout_end=date_prevout_end, date_actout_end=date_actout_end, date_trueaout_end=date_trueaout_end, description=description, promoter=promoter, financial_entity=financial_entity, amount=amount, manager_reg=manager_reg, principal_inv=principal_inv, manager_1=manager_1, manager_2=manager_2)
        study.save()
        return study

    def create_studyCenters(self, study_id, center_id):
        study = StudyCenters(study_id=study_id, center_id=center_id)
        study.save()
        return study

    def create_studyUsers(self, study_id, user_id):
        study = StudyUsers(study_id=study_id, user_id=user_id)
        study.save()
        return study


class Study(models.Model):
    STATUS_CHOICES = (
        (1, _("REGISTRO")),
        (2, _("DISEÑO")),
        (3, _("FINALIZADO"))
    )

    study_id = models.CharField(max_length=50)
    title_little = models.CharField(max_length=50)
    title_long = models.CharField(max_length=120, blank=True, null=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)
    date_reg = models.DateTimeField(auto_now=True)
    date_in_study = models.DateField(auto_now=False)
    date_prevout_end = models.DateField(auto_now=False, blank=True, null=True)
    date_actout_end = models.DateField(auto_now=False, blank=True, null=True)
    date_trueaout_end = models.DateField(auto_now=False, blank=True, null=True)
    description = models.CharField(max_length=524, blank=True, null=True)
    promoter = models.CharField(max_length=50, blank=True, null=True)
    financial_entity = models.CharField(max_length=50, blank=True, null=True)
    amount = models.FloatField(default=0, blank=True, null=True)
    manager_reg = models.ForeignKey(
        User, related_name="manager_reg", on_delete=models.CASCADE)
    principal_inv = models.ForeignKey(
        User, related_name="principal_inv", on_delete=models.CASCADE)
    manager_1 = models.ForeignKey(
        User, related_name="manager_1", on_delete=models.CASCADE, blank=True, null=True)
    manager_2 = models.ForeignKey(
        User, related_name="manager_2", on_delete=models.CASCADE, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    objects = StudyManager()

    def __str__(self):
        return '{}'.format(self.title_little)

    class Meta:
        verbose_name = 'Estudio'
        verbose_name_plural = 'Estudios'

        unique_together = ("manager_reg", "principal_inv",
                           "manager_1", "manager_2")


class StudyCenters(models.Model):
    study_id = models.ForeignKey(Study, on_delete=models.CASCADE)
    center_id = models.ForeignKey(Center, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    objects = StudyManager()

    def __str__(self):
        return '{}'.format(self.center_id)

    class Meta:
        verbose_name = 'Centro'
        verbose_name_plural = 'Centros'

        unique_together = ("study_id", "center_id")


class StudyUsers(models.Model):
    study_id = models.ForeignKey(Study, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    objects = StudyManager()

    def __str__(self):
        return '{}'.format(self.user_id)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

        unique_together = ("study_id", "user_id")
