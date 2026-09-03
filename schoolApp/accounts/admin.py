from django.contrib import admin
from .models import Student, Teacher
from enrollments.models import Enrollment
from .forms import StudentUserFormAdmin, TeacherUserFormAdmin
from academics.models import TeacherAssignment



# Register your models here.


#O QUE É ««INLINE»» é o mecanisco que nos permite editar objectos relacionado dentro de outro objecto, em uma unica pagina (ex.: Student - Enrollment) 

#INLINE DE «Student - User»
class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 0
    fields = ('id','group','status','created_at',)
    readonly_fields = ('created_at',)
    autocomplete_fields = ('group',)


#student admin

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):

    form = StudentUserFormAdmin #incluindo o formulario personalizado (Student - User)
    
    #INCLUINDO O INLINE MATRICULA NO ESTUDANTE PARA A MATRICULA POSSA TAMBEM SER FEITO NA PAGINA DE ESTUDANTE
    inlines = [          
        EnrollmentInline, 
    ]

    list_display = ('full_name','student_number','username','birthdate','phone','created_at',)
    search_fields =('id','user__first_name','user__last_name','user__username',)
    list_filter = ('created_at',)
    ordering =('user__first_name', 'user__last_name',)
    readonly_fields =('created_at',)
    list_per_page = 20
    

    @admin.display( description='Nome completo',ordering='user__first_name')
    def full_name(self, obj):
        return obj.user.get_full_name()

    @admin.display(description='Nº de Estudante')
    def student_number(self, obj):
        return obj.id
    
    def username(self, obj):
        return obj.user.username



#Este é ««INLINE de profssor»», onde vai mostrar  e editar(Disciplinas e Turmas) o professor e as suas atribuicoes (Turmas e Disciplinas) quando abrimos um professor

class TeacherAssignmentInline(admin.TabularInline):

    model = TeacherAssignment

    extra = 0
    fields = ('subject','group','date_assignment','is_active')
    readonly_fields = ('date_assignment',)
    autocomplete_fields = ('subject','group',)


#TECHAER ADMIN
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):

    form = TeacherUserFormAdmin #Incluindo o formulario personalizado

    #INCLUINDO O INLINE DE ATRIBUICOES DE PROFESSOR(Turmas e Disciplinas)
    inlines = [
        TeacherAssignmentInline,
    ]

    list_display = ('full_name','username','employee_number','specialty','phone','created_at',)
    search_fields =('employee_number','user__first_name','user__last_name','user__username',)
    list_filter = ('specialty','created_at',)
    ordering =('user__first_name', 'user__last_name',)
    readonly_fields =('created_at',)
    autocomplete_fields = ('user',)
    list_per_page = 20

    @admin.display( description='Nome completo',ordering='user__first_name')
    def full_name(self, obj):
        return obj.user.get_full_name()

    #personalyzing teacher.id to employee_number
    @admin.display( description='Nº de Funcionário',ordering='speciality')
    def employee_number(self, obj):
        return obj.id

    #personalyzing teacher.username
    @admin.display( description='Nome de Usuário',ordering='teacher__user__username')
    def username(self, obj):
        return obj.user.username

    

    #CONFIGUIRNG THE SITE
admin.site.site_header = "KIBACO'S CENTER"
admin.site.site_title = 'BSOFT TECHNOLOGIES'
admin.site.index_title = 'Painel Administrativo'