from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth import password_validation
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError
from django.db import transaction
from unfold.widgets import (
    UnfoldAdminTextInputWidget,
    UnfoldAdminEmailInputWidget,
    UnfoldAdminSelectWidget,
    UnfoldAdminSingleDateWidget,
)
from .models import Student, Teacher

# Este formulário cria o User + os dados de Estudante/Professor de uma
# só vez, já que Student/Teacher dependem de um User associado.


class UnfoldAdminPasswordInputWidget(UnfoldAdminTextInputWidget):
    """
    O Unfold não tem um widget de password dedicado — esta subclasse
    herda todas as classes CSS do UnfoldAdminTextInputWidget e só troca
    o tipo do input para 'password', para o campo não aparecer em
    texto simples mas manter o mesmo visual dos outros campos.
    """
    input_type = "password"


class _BaseUserProfileForm(forms.ModelForm):
    """
    Lógica partilhada entre StudentUserFormAdmin e TeacherUserFormAdmin,
    para não repetir o mesmo save() duas vezes.
    Subclasses definem `group_name` ('Estudantes' ou 'Professores').
    """
    username = forms.CharField(
        max_length=150, label='Nome de usuário',
        widget=UnfoldAdminTextInputWidget
    )
    password = forms.CharField(
        widget=UnfoldAdminPasswordInputWidget(), label='Senha', required=False,
        help_text='Deixa em branco para manter a senha atual (ao editar).'
    )
    first_name = forms.CharField(
        max_length=100, label='Nome',
        widget=UnfoldAdminTextInputWidget
    )
    last_name = forms.CharField(
        max_length=100, label='Sobrenome',
        widget=UnfoldAdminTextInputWidget
    )
    email = forms.EmailField(
        max_length=254, required=False, label='E-mail',
        widget=UnfoldAdminEmailInputWidget
    )

    group_name = None  # definido nas subclasses

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # CORREÇÃO: username/email/first_name/last_name pertencem ao
        # User, não ao Student/Teacher — o ModelForm não os preenche
        # sozinho a partir da instância. Sem isto, ao abrir para editar,
        # estes campos apareciam sempre vazios mesmo já tendo valor.
        if self.instance and self.instance.pk and self.instance.user_id:
            user = self.instance.user
            self.fields['username'].initial = user.username
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email

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
        widgets = {
            'id_card_number': UnfoldAdminTextInputWidget(),
            'gender': UnfoldAdminSelectWidget(),
            'birthdate': UnfoldAdminSingleDateWidget(),
            'place_of_birth': UnfoldAdminTextInputWidget(),
            'province': UnfoldAdminTextInputWidget(),
            'father_name': UnfoldAdminTextInputWidget(),
            'mother_name': UnfoldAdminTextInputWidget(),
            'phone': UnfoldAdminTextInputWidget(),
            'address': UnfoldAdminTextInputWidget(),
        }


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
        widgets = {
            'id_card_number': UnfoldAdminTextInputWidget(),
            'gender': UnfoldAdminSelectWidget(),
            'birthdate': UnfoldAdminSingleDateWidget(),
            'place_of_birth': UnfoldAdminTextInputWidget(),
            'province': UnfoldAdminTextInputWidget(),
            'father_name': UnfoldAdminTextInputWidget(),
            'mother_name': UnfoldAdminTextInputWidget(),
            'phone': UnfoldAdminTextInputWidget(),
            'specialty': UnfoldAdminTextInputWidget(),
        }


# =========================================================
# FORMS DE AUTOATUALIZAÇÃO DE PERFIL (usados pelo próprio
# aluno/professor nas suas páginas de Perfil no site — não são
# do Django Admin, por isso continuam com widgets simples/Bootstrap,
# aplicados diretamente nos templates).
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
    para o site do aluno/professor (fora do Admin).
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'