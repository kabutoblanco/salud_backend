from places_app.models import Center
from users_app.models import User

from django.conf import settings
from django.contrib.auth.models import Permission, AbstractUser, BaseUserManager
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string


class StudyManager(BaseUserManager):
    """
    Clase usada para prestar servicios a `Study`, `StudyCenters` y `StudyUsers`

    ...

    Methods
    - - - - -
    create_study(study_id, title_little, title_long, status, date_in_study, date_prevout_end, date_actout_end, date_trueaout_end, description, promoter, financial_entity, amount, manager_reg, principal_inv, manager_1, manager_2)
        Crea un nuevo estudio

    create_studyCenters(study_id, center_id)
        Crea un nuevo usuario simple

    create_studyUsers(self, study_id, user_id)
        Crea un nuevo usuario simple
    """

    def create_study(self, study_id, title_little, title_long, status, date_in_study, date_prevout_end, date_actout_end, date_trueaout_end, description, promoter, financial_entity, amount, manager_reg, principal_inv, manager_1, manager_2):
        """Crea un nuevo estudio

        Parameters
        - - - - -
        study_id : int
            Número de identificación
        title_little : str
            Nombre corto
        title_long : str
            Nombre largo
        status : int
            Estado del proyecto
            1 : REGISTRO
            2 : DISEÑO
            3 : FINALIZADO
        date_reg : DateTimeField
            Fecha de registro
        date_in_study : DateTimeField
            Fecha de inicio del estudio
        date_prevout_end : DateTimeField
            Fecha de previa de finalización del estudio
        date_actout_end : DateTimeField
            Fecha de actual de finalización del estudio
        date_trueaout_end : DateTimeField
            Fecha de verdadera de finalización del estudio
        description : str
            Descripción del proyecto
        promoter : str
            Promotor que financia el estudio
        financial_entity : str
            Entidad financiadora del estudio
        amount : float
            Monto total de financiamiento
        manager_reg : int
            Usuario encargado del registro
        principal_inv : int
            Investigador principal
        manager_1 : int
            Primer encargado
        manager_2 : int
            Segundo encargado
        is_active : boolean
            Indica si esta activo

        Returns
        - - - - -
        `Study`
            Un estudio
        """

        study = Study(study_id=study_id, title_little=title_little, title_long=title_long, status=status, date_in_study=date_in_study,
                      date_prevout_end=date_prevout_end, date_actout_end=date_actout_end, date_trueaout_end=date_trueaout_end, description=description, promoter=promoter, financial_entity=financial_entity, amount=amount, manager_reg=manager_reg, principal_inv=principal_inv, manager_1=manager_1, manager_2=manager_2)
        study.save()
        return study

    def create_studyCenters(self, study_id, center_id):
        """Crea una relación entre `Study` y `Center`"""

        study = StudyCenters(study_id=study_id, center_id=center_id)
        study.save()
        return study

    def create_studyUsers(self, study_id, user_id, date_maxAccess, role, is_manager):
        """Crea una relación entre `Study` y `User`"""

        study = StudyUsers(study_id=study_id, user_id=user_id,
                           date_maxAccess=date_maxAccess, role=role)
        study.save()     
        if is_manager:
            user_id.user_permissions.add(
                Permission.objects.get(codename="change_parameterization"))
            user_id.user_permissions.add(
                Permission.objects.get(codename="change_questionnaire"))
            user_id.user_permissions.add(
                Permission.objects.get(codename="change_analysis"))
            user_id.user_permissions.add(
                Permission.objects.get(codename="chage_control"))
            user_id.user_permissions.add(
                Permission.objects.get(codename="change_observer"))
            user_id.user_permissions.add(
                Permission.objects.get(codename="change_registry"))
            user_id.user_permissions.add(
                Permission.objects.get(codename="change_member"))
            user_id.user_permissions.add(
                Permission.objects.get(codename="change_centerStudy"))
        return study


class Study(models.Model):
    """
    Clase usada para representar un `Study`

    ...

    Attributes
    - - - - -
    study_id : int
        Número de identificación
    title_little : str
        Nombre corto
    title_long : str
        Nombre largo
    status : int
        Estado del proyecto
        1 : REGISTRO
        2 : DISEÑO
        3 : FINALIZADO
    date_reg : DateTimeField
        Fecha de registro
    date_in_study : DateTimeField
        Fecha de inicio del estudio
    date_prevout_end : DateTimeField
        Fecha de previa de finalización del estudio
    date_actout_end : DateTimeField
        Fecha de actual de finalización del estudio
    date_trueaout_end : DateTimeField
        Fecha de verdadera de finalización del estudio
    description : str
        Descripción del proyecto
    promoter : str
        Promotor que financia el estudio
    financial_entity : str
        Entidad financiadora del estudio
    amount : float
        Monto total de financiamiento
    manager_reg : int
        Usuario encargado del registro
    principal_inv : int
        Investigador principal
    manager_1 : int
        Primer encargado
    manager_2 : int
        Segundo encargado
    is_active : boolean
        Indica si esta activo
    """

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
        return '{} - {}'.format(self.id, self.title_little)

    class Meta:
        verbose_name = 'Estudio'
        verbose_name_plural = 'Estudios'


class StudyCenters(models.Model):
    """
    Clase usada para representar la relación entre un `Study` y `Center`

    ...

    Attributes
    - - - - -
    study_id : int
        Pk usuario asociado
    center_id : int
        Pk centro asociado
    is_active : boolean
        Indica si esta activo
    """

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
    """
    Clase usada para representar la relación entre un `Study` y `User`

    ...

    Attributes
    - - - - -
    study_id : int
        Pk usuario asociado
    user_id : int
        Pk usuario asociado
    date_maxAccess : date
        Fecha máxima de acceso
    role : int
        Role del participante
        1 : GESTOR
        2 : INVESTIGADOR
        3 : TECNICO
    is_active : boolean
        Indica si esta activo
    """

    ACCESS_CHOICES = (
        (1, _("GESTOR")),
        (2, _("INVESTIGADOR")),
        (3, _("TECNICO"))
    )

    study_id = models.ForeignKey(Study, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    date_maxAccess = models.DateField(auto_now=False, blank=True, null=True)
    role = models.IntegerField(choices=ACCESS_CHOICES, default=1)
    is_manager = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = StudyManager()

    def __str__(self):
        return '{}'.format(self.user_id)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

        unique_together = ("study_id", "user_id")
