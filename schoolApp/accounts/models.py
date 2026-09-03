from django.db import models
from django.contrib.auth.models import User

# Create your models here.

#MODEL STUDENT (student 1 - 1 User => relation)
class Student(models.Model):  
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='students', blank=True)
    birthdate = models.DateField(verbose_name='Data de Nascimento')
    phone = models.CharField(max_length=9, blank=True, verbose_name='Telefone')
    address = models.CharField(verbose_name='Morada')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
              verbose_name ='Estudante'

    def __str__(self):
        return (
            f"{self.user.get_full_name()} - "
            f"Nº De Estudante : {self.id}"
            
         )

#TEACHER MODEL (Teacher 1 - 1 User => Relation)
class Teacher(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE, related_name='teachers', verbose_name='Nome')
    #employee_number = models.CharField(max_length=30, unique=True, verbose_name='Número de Funciorio')
    specialty = models.CharField(max_length=150,blank=True, verbose_name='Especialidade')
    phone = models.CharField(max_length=9,blank=True, verbose_name='Telefone')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
              verbose_name ='Professor'
              verbose_name_plural = "Professores"
              
    def __str__(self):
        return (
            f"{self.user.get_full_name()} - "
            f"Nº de Funcionário : {self.id}"
        )


