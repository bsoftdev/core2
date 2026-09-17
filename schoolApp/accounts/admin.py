from django.contrib import admin
from .models import Student, Teacher
from enrollments.models import Enrollment
from .forms import StudentUserFormAdmin, TeacherUserFormAdmin
from academics.models import TeacherAssignment


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 0
    fields = ('id', 'group', 'status', 'created_at')
    readonly_fields = ('created_at',)
    autocomplete_fields = ('group',)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):

    form = StudentUserFormAdmin

    inlines = [EnrollmentInline]

    list_display = ('full_name', 'student_number', 'username', 'birthdate', 'phone', 'created_at')
    search_fields = ('id', 'user__first_name', 'user__last_name', 'user__username')
    list_filter = ('created_at',)
    ordering = ('user__first_name', 'user__last_name')
    readonly_fields = ('created_at',)
    list_per_page = 20

    @admin.display(description='Nome completo', ordering='user__first_name')
    def full_name(self, obj):
        return obj.user.get_full_name()

    @admin.display(description='Nº de Estudante')
    def student_number(self, obj):
        return obj.id

    def username(self, obj):
        return obj.user.username


class TeacherAssignmentInline(admin.TabularInline):
    model = TeacherAssignment
    extra = 0
    fields = ('subject', 'group', 'date_assignment', 'is_active')
    readonly_fields = ('date_assignment',)
    autocomplete_fields = ('subject', 'group')


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):

    form = TeacherUserFormAdmin

    inlines = [TeacherAssignmentInline]

    list_display = ('full_name', 'username', 'employee_number', 'specialty', 'phone', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'user__username')
    list_filter = ('specialty', 'created_at')
    ordering = ('user__first_name', 'user__last_name')
    readonly_fields = ('created_at',)
    autocomplete_fields = ('user',)
    list_per_page = 20

    @admin.display(description='Nome completo', ordering='user__first_name')
    def full_name(self, obj):
        return obj.user.get_full_name()

    @admin.display(description='Nº de Funcionário')
    def employee_number(self, obj):
        return obj.id


    @admin.display(description='Nome de Usuário')
    def username(self, obj):
        return obj.user.username


admin.site.site_header = "KIBACO'S CENTER"
admin.site.site_title = 'BSOFT TECHNOLOGIES'
admin.site.index_title = 'Painel Administrativo'