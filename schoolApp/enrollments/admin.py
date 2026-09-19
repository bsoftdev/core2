from django.contrib import admin
from .models import Enrollment
from grades.models import Grade, AcademicEvaluation
from unfold.admin import ModelAdmin


# GRADEINLINE — mostra as notas de um aluno dentro da página da matrícula
class GradeInline(admin.TabularInline):
    model = Grade
    extra = 0
    # CORREÇÃO: 'avaluation' -> 'academic_evaluation' (nome do campo mudou).
    fields = ('academic_evaluation', 'value', 'observation', 'created_at')
    readonly_fields = ('observation', 'created_at')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filtra as avaliações para mostrar apenas as da turma da matrícula."""
        
        if db_field.name == "academic_evaluation":
            resolved = request.resolver_match
            if resolved and resolved.kwargs.get('object_id'):
                enrollment_id = resolved.kwargs['object_id']
                kwargs["queryset"] = AcademicEvaluation.objects.filter(
                    group__enrollments__id=enrollment_id,
                    is_active=True,
                )
            else:
                kwargs["queryset"] = AcademicEvaluation.objects.none()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Enrollment)
class EnrollmentAdmin(ModelAdmin):

    inlines = [GradeInline]

    list_display = ('student', 'enrollment_number', 'group', 'status', 'created_at')
    search_fields = ('id', 'student__user__first_name', 'student__user__last_name', 'group__designation')
    list_filter = ('status', 'group', 'group__course', 'group__academic_year')
    ordering = ('-created_at',)
    autocomplete_fields = ('student', 'group')
    readonly_fields = ('created_at',)
    list_editable = ('status',)
    list_per_page = 20

    @admin.display(description='Nº de Matrícula')
    def enrollment_number(self, obj):
        return obj.id

   