from django.db import models

# Create your models here.
class Center(models.Model):
    name = models.CharField(max_length=36)
    
    class Meta:
        verbose_name = 'Center'
        verbose_name_plural = 'Centers'
        
    def __str__(self):
        return '{}'.format(self.name)


class Department(models.Model):
    name = models.CharField(max_length=36)
    
    class Meta:
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        
    def __str__(self):
        return '{}'.format(self.name)