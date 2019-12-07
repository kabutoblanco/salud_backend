from django.db import models

# Create your models here.
class Center(models.Model):
    name = models.CharField(max_length=36, unique=True)
    
    class Meta:
        verbose_name = 'Centro'
        verbose_name_plural = 'Centros'
        
    def __str__(self):
        return '{}'.format(self.name)


class Department(models.Model):
    name = models.CharField(max_length=36, unique=True)
    
    class Meta:
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'
        
    def __str__(self):
        return '{}'.format(self.name)