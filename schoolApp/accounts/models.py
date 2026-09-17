from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

# Validador simples para números angolanos (9 dígitos, começa por 9)
phone_validator = RegexValidator(
    regex=r'^9\d{8}$',
    message='O telefone deve ter 9 dígitos e começar por 9 (ex: 923456789).'
)


# MODEL STUDENT (Student 1 - 1 User => Relation)
class Student(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='student_profile'
    )
    birthdate = models.DateField(verbose_name='Data de Nascimento')
    phone = models.CharField(
        max_length=9, blank=True, validators=[phone_validator],
        verbose_name='Telefone'
    )
    address = models.CharField(max_length=255, verbose_name='Morada')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Estudante'
        verbose_name_plural = 'Estudantes'
        ordering = ['user__first_name']

    def __str__(self):
        return f"{self.user.get_full_name()} - Nº de Estudante: {self.id}"


# TEACHER MODEL (Teacher 1 - 1 User => Relation)
class Teacher(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='teacher_profile',
        verbose_name='Utilizador'
    )
    specialty = models.CharField(max_length=150, blank=True, verbose_name='Especialidade')
    phone = models.CharField(
        max_length=9, blank=True, validators=[phone_validator],
        verbose_name='Telefone'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    class Meta:
        verbose_name = 'Professor'
        verbose_name_plural = 'Professores'
        ordering = ['user__first_name']

    def __str__(self):
        return f"{self.user.get_full_name()} - Nº de Funcionário: {self.id}"


def get_user_role(user):
    """
    Função central para determinar o papel (role) de um utilizador logado.
    Usa is_staff/is_superuser para Admin (via Django auth nativo) e os
    perfis OneToOne para Professor/Aluno. Usada pelos mixins de acesso
    às dashboards — assim a lógica de "quem é quem" vive num único sítio.
    """
    if not user.is_authenticated:
        return None
    if user.is_superuser or user.is_staff:
        return 'ADMIN'
    if hasattr(user, 'teacher_profile'):
        return 'TEACHER'
    if hasattr(user, 'student_profile'):
        return 'STUDENT'
    return None