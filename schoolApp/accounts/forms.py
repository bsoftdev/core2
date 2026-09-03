from django import forms
from django.contrib.auth.models import User 
from .models import Student, Teacher

#Este formulario vai ser usado para que possamos criar de um unica vez o User + Dados de estudante de uma vez só, ou seja, vamos criar um formulário que vai ter os campos do User e os campos do Estudante  ja que estamos usando o User como base para o Estudante, ou seja, o Estudante vai ter um User associado a ele.

class StudentUserFormAdmin(forms.ModelForm):
    username = forms.CharField(max_length=100, label='Nome de usuário')
    password = forms.CharField(widget=forms.PasswordInput(), label='Senha')
    first_name = forms.CharField(max_length=100, label='Nome')
    last_name = forms.CharField(max_length=100, label='Sobrenome')
    email = forms.EmailField(max_length=100, required=False, label='E-mail')

    class Meta:
        model = Student
        fields = [
            'username', 
            'email', 
            'password',
            'first_name', 
            'last_name',
            'address',
            'birthdate',
            'phone',
            ]
        
    def save(self, commit=True):

        student = super().save(commit=False)
        if student.pk:

            user = student.user
            user.username = self.cleaned_data['username']
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            password = self.cleaned_data['password']
            if password:
                user.set_password(password)
            user.save()
        else:
            user = User.objects.create_user(

                username=self.cleaned_data['username'],
                password= self.cleaned_data['password'],
                first_name = self.cleaned_data['first_name'],
                last_name = self.cleaned_data['last_name'],
                email = self.cleaned_data['email'],

                )
            student.user = user
        if commit:
            student.save()
        return student


class TeacherUserFormAdmin(forms.ModelForm):
    username = forms.CharField(max_length=100, label='Nome de usuário')
    password = forms.CharField(widget=forms.PasswordInput(), label='Senha')
    first_name = forms.CharField(max_length=100, label='Nome')
    last_name = forms.CharField(max_length=100, label='Sobrenome')
    email = forms.EmailField(max_length=100, required=False, label='Email')

    class Meta:
        model = Teacher
        fields = [
            'username', 
            'email', 
            'password',
            'first_name', 
            'last_name',
            'specialty',
            'phone',
            ]
        
    def save(self, commit=True):

        teacher = super().save(commit=False)
        if teacher.pk:

            user = teacher.user
            user.username = self.cleaned_data['username']
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            password = self.cleaned_data['password']
            if password:
                user.set_password(password)
            user.save()
        else:
            user = User.objects.create_user(

                username=self.cleaned_data['username'],
                password= self.cleaned_data['password'],
                first_name = self.cleaned_data['first_name'],
                last_name = self.cleaned_data['last_name'],
                email = self.cleaned_data['email'],

                )
            teacher.user = user
        if commit:
            teacher.save()
        return teacher


        