from django.db import models

from studies_app.models import Study
from django.contrib.auth.models import BaseUserManager

# Create your models here.


class QuestionaryManager(BaseUserManager):

    def create_questionary(self, code, title, description, num_minRegistry, num_maxRegistry, is_read, is_accessExternal, study_id):
        questionary = Questionary(code=code, title=title, description=description, num_minRegistry=num_minRegistry,
                                  is_read=is_read, is_accessExternal=is_accessExternal, study_id=study_id)
        questionary.save()
        return questionary
    
    def create_page(self, name, pos_x):
        page = Page(name=name, pos_x=pos_x)
        page.save()
        return page
    
    def create_section(self, name, pos_y):
        section = Section(name=name, pos_y=pos_y)
        section.save()
        return section


class Questionary(models.Model):
    code = models.CharField(max_length=10)
    title = models.CharField(max_length=36)
    description = models.CharField(max_length=125, blank=True)
    num_minRegistry = models.IntegerField(default=0)
    num_maxRegistry = models.IntegerField(default=0)
    is_read = models.BooleanField(default=False)
    is_accessExternal = models.BooleanField(default=False)

    study_id = models.ForeignKey(
        Study, related_name="study_questionary", on_delete=models.CASCADE)
    
    objects = QuestionaryManager()

    class Meta:
        verbose_name = 'Cuestionario'
        verbose_name_plural = 'Cuestionarios'

    def __str__(self):
        return '{}'.format(self.title)


class Page(models.Model):
    name = models.CharField(max_length=36)
    pos_x = models.IntegerField(default=0)

    questionary_id = models.ForeignKey(
        Questionary, related_name="questionary_page", on_delete=models.CASCADE)
    
    objects = QuestionaryManager()

    class Meta:
        verbose_name = 'Pagina'
        verbose_name_plural = 'Paginas'

    def __str__(self):
        return '{}'.format(self.name)


class Section(models.Model):
    name = models.CharField(max_length=36)
    pos_y = models.IntegerField(default=0)

    page_id = models.ForeignKey(
        Page, related_name="questionary_section", on_delete=models.CASCADE)
    
    objects = QuestionaryManager()

    class Meta:
        verbose_name = 'Seccion'
        verbose_name_plural = 'Secciones'

    def __str__(self):
        return '{}'.format(self.name)


class Question(models.Model):
    name = models.CharField(max_length=36)
    pos_x = models.IntegerField(default=0)
    pos_y = models.IntegerField(default=0)
    width = models.IntegerField(default=1)

    section_id = models.ForeignKey(
        Study, related_name="questionary_question", on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Pregunta'
        verbose_name_plural = 'Preguntas'

    def __str__(self):
        return '{}'.format(self.name)
