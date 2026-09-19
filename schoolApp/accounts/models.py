from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

# Validador simples para números angolanos (9 dígitos, começa por 9)
phone_validator = RegexValidator(
    regex=r'^9\d{8}$',
    message='O telefone deve ter 9 dígitos e começar por 9 (ex: 923456789).'
)

# Validador básico do Bilhete de Identidade angolano (9 dígitos + 2 letras +
# 3 dígitos, ex: 003267618LA047). Ajusta o regex se o formato usado for outro.
id_card_validator = RegexValidator(
    regex=r'^\d{9}[A-Z]{2}\d{3}$',
    message='Formato de Bilhete de Identidade inválido (ex: 003267618LA047).'
)


class PersonalInfoMixin(models.Model):
    """
    Campos pessoais partilhados entre Student e Teacher — extraídos para
    aqui em vez de repetidos nos dois models. Qualquer ajuste futuro
    (ex: tornar 'province' uma lista de choices) faz-se só aqui.
    """
    GENDERS = [
        ('MASCULINO', 'Masculino'),
        ('FEMININO', 'Feminino'),
    ]

    id_card_number = models.CharField(
        max_length=20, unique=True, blank=True, null=True, validators=[id_card_validator],
        verbose_name='Nº do Bilhete de Identidade'
    )
    gender = models.CharField(max_length=10, choices=GENDERS, blank=True, verbose_name='Género')
    birthdate = models.DateField(blank=True, null=True, verbose_name='Data de Nascimento')
    place_of_birth = models.CharField(max_length=100, blank=True, verbose_name='Naturalidade')
    province = models.CharField(max_length=100, blank=True, verbose_name='Província')
    father_name = models.CharField(max_length=150, blank=True, verbose_name='Nome do Pai')
    mother_name = models.CharField(max_length=150, blank=True, verbose_name='Nome da Mãe')
    phone = models.CharField(max_length=9, blank=True, validators=[phone_validator], verbose_name='Telefone')
    address = models.CharField(max_length=255, verbose_name='Morada')

    class Meta:
        abstract = True


# MODEL STUDENT (Student 1 - 1 User => Relation)
class Student(PersonalInfoMixin):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='student_profile'
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
class Teacher(PersonalInfoMixin):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='teacher_profile',
        verbose_name='Utilizador'
    )
    specialty = models.CharField(max_length=150, blank=True, verbose_name='Especialidade')
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
    perfis OneToOne para Professor/Aluno.
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