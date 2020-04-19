from django.db import models

from studies_app.models import Study
from django.contrib.auth.models import BaseUserManager

# Create your models here.


class QuestionaryManager(BaseUserManager):
    """
    Clase usada para prestar servicios a `Questionary` `Page` `Section`y `Question`

    ...

    Methods
    - - - - -
    create_questionary(code, title, description, num_minRegistry, num_maxRegistry, is_read, is_accessExternal, study_id)
        Crea un nuevo cuestionario

    create_page(name, pos_x)
        Crea una nueva pagina

    create_section(name, pos_y)
        Crea una nueva seccion
    """

    def create_questionary(self, code, title, description, num_minRegistry, num_maxRegistry, is_read, is_accessExternal, study_id):
        """Crea un nuevo cuestionario

        Parameters
        - - - - -
        code : int
            Codigo de identificacion
        title : str
            Titulo del cuestionario
        description : str
            Descripción breve del cuestionario
        num_minRegistry : int
            Número minimo de registros
        num_maxRegistry : int
            Número máximo de registros
        is_read : boolean
            Indica si permite la lectura del cuestionario o no
        is_accessExternal : boolean
            Indica si puede ser accedido por un usuario externo
        study_id : int 
            Relación para indicar a cual estudio pertenece el cuestionario

        Returns
        - - - - -
        `Questionary`
            Un objeto cuestionario
        """

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
    """Clase usada para representar la definicíón del modelo `Questionary` en Django

    ...

    Attributes
    - - - - -
    code : int
        Codigo de identificacion
    title : str
        Titulo del cuestionario
    description : str
        Descripción breve del cuestionario
    num_minRegistry : int
        Número minimo de registros
    num_maxRegistry : int
        Número máximo de registros
    is_read : boolean
        Indica si permite la lectura del cuestionario o no
    is_accessExternal : boolean
        Indica si puede ser accedido por un usuario externo
    is_active : boolean
        Establece si el registro permance activo o no
    study_id : int 
        Relación para indicar a cual estudio pertenece el cuestionario
    """
    code = models.CharField(max_length=10)
    title = models.CharField(max_length=36)
    description = models.CharField(max_length=125, blank=True)
    num_minRegistry = models.IntegerField(default=0)
    num_maxRegistry = models.IntegerField(default=0)
    is_read = models.BooleanField(default=False)
    is_accessExternal = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    study_id = models.ForeignKey(
        Study, related_name="study_questionary", on_delete=models.CASCADE)
    
    objects = QuestionaryManager()

    class Meta:
        verbose_name = 'Cuestionario'
        verbose_name_plural = 'Cuestionarios'

    def __str__(self):
        return '{}'.format(self.title)


class Page(models.Model):
    """Clase usada para representar la definicíón del modelo `Page` en Django

    ...

    Attributes
    - - - - -
    
    questionary_id : int 
        Relación para indicar a cual cuestionario pertenece la pagina
    name : str
        Nombre que identifica la pagina
    pos_x : int
        Indica en que posición de la grilla ira ubicado en el frontend
    """

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
    """Clase usada para representar la definicíón del modelo `Section` en Django

    ...

    Attributes
    - - - - -
    
    page_id : int 
        Relación para indicar a cual pagina pertenece la seccion
    name : str
        Nombre que identifica la seccion
    pos_x : int
        Indica en que posición de la grilla ira ubicado en el frontend
    """

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
    """Clase usada para representar la definicíón del modelo `Question` en Django

    ...

    Attributes
    - - - - -
    
    questionary_id : int 
        Relación para indicar a cual seccion  pertenece la pregunta
    name : str
        Nombre que identifica la pregunta
    pos_x : int
        Indica en que posición x de la grilla ira ubicado en el frontend
    pos_y : int
        Indica en que posición y de la grilla ira ubicado en el frontend
    width : int
        Indica el tamaño horizontal del elemento en la grilla del frontend
    """

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
