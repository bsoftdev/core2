from django.contrib import admin
from .models import Enrollment
from grades.models import Grade
from grades.models import Evaluation

# Register your models here.

#VAMOS CRIAR O NotaInline para quando abrir a matricula de um aluno conisgamos visualizar a turma dele e as suas notas
#GRADEINLINE

 #METHOD PARA PARA fazer com que o Admin mostre apenas avaliações pertencentes à turma da matrícula.
class GradeInline(admin.TabularInline):
        model = Grade
        extra = 0
        fields = ('avaluation', 'value', 'observation', 'created_at')
        readonly_fields = ('observation', 'created_at')
        # REMOVE o autocomplete_fields, pois ele entra em conflito com o filtro manual abaixo
        # autocomplete_fields = ('avaluation',) 

        def formfield_for_foreignkey(self, db_field, request, **kwargs):
            """Filtra as avaliações para mostrar apenas as da turma da matrícula"""
            if db_field.name == "avaluation":
                # Recupera o ID da matrícula a partir da URL do admin
                resolved = request.resolver_match
                if resolved and resolved.kwargs.get('object_id'):
                    enrollment_id = resolved.kwargs['object_id']
                    
                    # Ajusta os filtros abaixo de acordo com os teus modelos reais:
                    # Exemplo: Buscar avaliações que pertencem à mesma turma (group) da matrícula
                    kwargs["queryset"] = Evaluation.objects.filter(
                        group__enrollments__id=enrollment_id, # Substitui pela tua relação real
                        is_active=True
                    )
                else:
                    # Se for uma nova matrícula (ainda sem ID), esconde as avaliações
                    kwargs["queryset"] = Evaluation.objects.none()

            return super().formfield_for_foreignkey(db_field, request, **kwargs)

    

#ENROLLMENT MODEL ADMIN
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):

    #INCLUINDO GradeInline (Inline de notas) para aparecer na matricula
    inlines = [
        GradeInline,
    ]

    list_display = ('student','enrollment_number','group','status','created_at',)
    search_fields = ('id','student__user__first_name' ,'student__user__last_name','group__designation',)
    list_filter = ('status','group','group__course','group__academic_year',)
    ordering = ('-created_at',)
    autocomplete_fields = ('student', 'group',)
    readonly_fields = ('created_at',)
    list_per_page = 20

    @admin.display(description='Nº de Matricula')
    def enrollment_number(self, obj):
        return obj.id

