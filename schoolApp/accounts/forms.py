from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth import password_validation
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Student, Teacher

# Este formulário cria o User + os dados de Estudante/Professor de uma
# só vez, já que Student/Teacher dependem de um User associado.


class _BaseUserProfileForm(forms.ModelForm):
    """
    Lógica partilhada entre StudentUserFormAdmin e TeacherUserFormAdmin,
    para não repetir o mesmo save() duas vezes.
    Subclasses definem `group_name` ('Estudantes' ou 'Professores').
    """
    username = forms.CharField(max_length=150, label='Nome de usuário')
    password = forms.CharField(
        widget=forms.PasswordInput(), label='Senha', required=False,
        help_text='Deixa em branco para manter a senha atual (ao editar).'
    )
    first_name = forms.CharField(max_length=100, label='Nome')
    last_name = forms.CharField(max_length=100, label='Sobrenome')
    email = forms.EmailField(max_length=254, required=False, label='E-mail')

    group_name = None  # definido nas subclasses

    # CAMPOS PARTILHADOS DE PersonalInfoMixin — comuns aos dois forms.
    # Definidos aqui, na base, para não repetir em Student e Teacher.
    base_fields_common = [
        'id_card_number', 'gender', 'birthdate', 'place_of_birth',
        'province', 'father_name', 'mother_name', 'phone',
    ]

    def clean_username(self):
        username = self.cleaned_data['username']
        existing = User.objects.filter(username=username)
        if self.instance.pk and self.instance.user_id:
            existing = existing.exclude(pk=self.instance.user_id)
        if existing.exists():
            raise ValidationError('Já existe um utilizador com este nome de usuário.')
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            password_validation.validate_password(password)
        elif not self.instance.pk:
            raise ValidationError('A senha é obrigatória para criar uma nova conta.')
        return password

    def save(self, commit=True):
        with transaction.atomic():
            profile = super().save(commit=False)

            if profile.pk:
                user = profile.user
                user.username = self.cleaned_data['username']
                user.first_name = self.cleaned_data['first_name']
                user.last_name = self.cleaned_data['last_name']
                user.email = self.cleaned_data['email']
                password = self.cleaned_data.get('password')
                if password:
                    user.set_password(password)
                user.save()
            else:
                user = User.objects.create_user(
                    username=self.cleaned_data['username'],
                    password=self.cleaned_data['password'],
                    first_name=self.cleaned_data['first_name'],
                    last_name=self.cleaned_data['last_name'],
                    email=self.cleaned_data['email'],
                )
                profile.user = user

            group, _ = Group.objects.get_or_create(name=self.group_name)
            user.groups.add(group)

            if commit:
                profile.save()

            return profile


class StudentUserFormAdmin(_BaseUserProfileForm):
    group_name = 'Estudantes'

    class Meta:
        model = Student
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name',
            'id_card_number', 'gender', 'birthdate', 'place_of_birth',
            'province', 'father_name', 'mother_name', 'phone',
            'address',
        ]


class TeacherUserFormAdmin(_BaseUserProfileForm):
    group_name = 'Professores'

    class Meta:
        model = Teacher
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name',
            'id_card_number', 'gender', 'birthdate', 'place_of_birth',
            'province', 'father_name', 'mother_name', 'phone',
            'specialty',
        ]


# =========================================================
# FORMS DE AUTOATUALIZAÇÃO DE PERFIL (usados pelo próprio
# aluno/professor nas suas páginas de Perfil — diferente dos
# forms do admin acima, que servem para criar/editar contas).
# =========================================================

class StudentContactForm(forms.ModelForm):
    """Permite ao próprio aluno atualizar e-mail e telefone."""
    email = forms.EmailField(
        required=False, label='E-mail',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Student
        fields = ['phone']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user is not None:
            self.fields['email'].initial = self.user.email

    def save(self, commit=True):
        student = super().save(commit=commit)
        if self.user is not None:
            self.user.email = self.cleaned_data.get('email', '')
            if commit:
                self.user.save(update_fields=['email'])
        return student


class TeacherContactForm(forms.ModelForm):
    """Permite ao próprio professor atualizar e-mail e telefone."""
    email = forms.EmailField(
        required=False, label='E-mail',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Teacher
        fields = ['phone']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user is not None:
            self.fields['email'].initial = self.user.email

    def save(self, commit=True):
        teacher = super().save(commit=commit)
        if self.user is not None:
            self.user.email = self.cleaned_data.get('email', '')
            if commit:
                self.user.save(update_fields=['email'])
        return teacher


class BootstrapPasswordChangeForm(PasswordChangeForm):
    """
    O PasswordChangeForm nativo do Django não sabe nada de Bootstrap —
    esta subclasse só acrescenta a classe 'form-control' a cada campo,
    para não teres de o fazer campo a campo em cada template.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'