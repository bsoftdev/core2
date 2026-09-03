from django.contrib import admin
from .models import (Evaluation,Grade,GradeBook)
from decimal import Decimal
from .forms import GradeAdminForm

#IMPORTES PARA CRIAR PAGINAS PERSONALIZADAS
from django.urls import path, reverse
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from django.utils.html import format_html
# Register your models here.

#AVALUATION ADMIN
@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('name','subject','group','type','gradeWeight','date','is_active',)
    search_fields = ('name','subject__name','group__name','subject__code',)
    list_filter =('type','subject','group','is_active',)
    ordering = ('subject','date',)
    autocomplete_fields = ('subject','group',)
    list_editable = ('is_active',)


#GRADE ADMIN
@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):

    form = GradeAdminForm #Incluindo o formulario personalizado de NOTA

    list_display = ('student','subject','group','avaluation','value',)
    search_fields =('enrollment__student__user__first_name','enrollment__student__user__last_name','avaluation__name','avaluation__subject__name','avaluation__group__designation')
    list_filter = ('avaluation__subject','avaluation__type','avaluation__group','created_at',)
    autocomplete_fields = ('enrollment','avaluation',)
    readonly_fields = ('created_at',)
    list_per_page = 20



   #Decorators for student and subject display 
    @admin.display(description='Nome de Estudante')
    def student(self,obj):
        return obj.enrollment.student

    @admin.display(description="Disciplina")
    def subject(self,obj):
        return obj.avaluation.subject
    
    @admin.display(description="Turma")
    def group(self,obj):
        return obj.avaluation.group

#_________________________________________________________________________
#FUNÇÃO PARA PUBLICAR PAUTAS DE UMA UNICA VEZ DE DISCCIPLINAS SELECIONADAS
@admin.action(description="Publicar Pautas Selecionadas")
def post_gradebooks(modeladmin, request, queryset):
    from django.utils import timezone
    updated = queryset.filter(posted=False).update(
                        posted=True,
                        created_at = timezone.now()
                        ) 
    modeladmin.message_user(request,f"{updated} pauata(s) publicada(s) com sucesso")

#FUNÇÃO PARA DESPUBLICAR PAUTAS DE UMA UNICA VEZ DE DISCCIPLINAS SELECIONADAS
@admin.action(description="Despublicar Pautas Selecionadas")
def unpost_gradebooks(modeladmin, request, queryset):
    from django.utils import timezone
    updated = queryset.filter(posted=True).update(
                        posted=False,
                        created_at = timezone.now()
                        ) 
    modeladmin.message_user(request,f"{updated} pauata(s) despublicada(s) com sucesso")



#GRADEBOOK ADMIN => PAUTA
@admin.register(GradeBook)
class GradeBookAdmin(admin.ModelAdmin):

    #incluindo a funcao de publicar e funcao de despublicar pautas de uma vez
    actions = [
         post_gradebooks,
         unpost_gradebooks,
    ]

    #MÉTODO PARA CALCULAR AS MEDIAS DAS DISCI´PLINA
    def calculate_avarage_student(self, gradebook, enrollment):
        return enrollment.calculate_avarage(gradebook.subject)

    list_display = ('group','subject','academic_year','posted','created_at','genareted_at','view_gradebook_button',)
    search_fields = ('group__designation','subject__name','subject__code','academic_year__designation',)
    list_filter = ('posted','academic_year','group', 'subject',)
    autocomplete_fields = ('group','subject','academic_year',)
    readonly_fields = ('genareted_at',)
    list_editable = ('posted',)

    #METHOD TO VIEW GRADEBOOK(PAUTA)
    def view_gradebook_page(self, request, object_id):

        gradebook = get_object_or_404(
            GradeBook,
            pk=object_id
        )

        enrollments = gradebook.group.enrollments.select_related(
            'student__user'
        ).order_by(
            'student__user__first_name',
            'student__user__last_name'
        )

        # Lista fixa de avaliações, igual para TODOS os alunos — define as colunas
        avaliations = Evaluation.objects.filter(
            subject=gradebook.subject,
            group=gradebook.group,
            is_active=True
        ).order_by('date')

        # Todas as notas da turma/disciplina numa única query (evita N+1)
        all_grades = Grade.objects.filter(
            enrollment__in=enrollments,
            avaluation__in=avaliations
        ).select_related('avaluation')

        # Mapa: (enrollment_id, avaluation_id) -> grade
        grades_lookup = {   
            (g.enrollment_id, g.avaluation_id): g
            for g in all_grades
        }

        results = []
        for enrollment in enrollments:
            avarage = enrollment.calculate_avarage(gradebook.subject)
            situation = enrollment.situation(gradebook.subject)

            # Mesma ordem, mesmo tamanho para todos os alunos — None onde faltar nota
            ordered_grades = [
                grades_lookup.get((enrollment.id, av.id))
                for av in avaliations
            ]

            results.append({
                'enrollment': enrollment,
                'student': enrollment.student,
                'grades': ordered_grades,
                'avarage': avarage,
                'situation': situation,
            })

        context = {
            **self.admin_site.each_context(request),
            'gradebook': gradebook,
            'avaliations': avaliations,   # <-- novo: para o cabeçalho da tabela
            'results': results,
            'title': f'{gradebook.subject.name} - {gradebook.group.designation}',
        }

        return render(request, 'admin/grades/gradebook.html', context)

    # 2. CRIAÇÃO DA URL (CORRIGIDA)
    def get_urls(self):
        urls = super().get_urls()
        
        # Correção no padrão da tag da URL (<path:object_id>)
        custom_urls = [
            path(
                '<path:object_id>/ver-pauta/',
                self.admin_site.admin_view(self.view_gradebook_page), # Aponta para o nome correto
                name='gradebook_view'    
            )
        ]
        return custom_urls + urls


    # 3. O BOTÃO NO ADMIN (NOME ALTERADO PARA NÃO CONFLITUAR)
    @admin.display(description='Ações')
    def view_gradebook_button(self, obj):
        url = reverse(
            'admin:gradebook_view',
            args=[obj.pk]
        )
        return format_html('<a class="button" href="{}">Ver Pauta</a>', url)


    