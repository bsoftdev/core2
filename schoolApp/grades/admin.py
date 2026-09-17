from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import render, get_object_or_404
from django.utils.html import format_html
from django.utils import timezone

from .models import Evaluation, AcademicEvaluation, Grade, GradeBook


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('type', 'name', 'gradeWeight', 'is_active')
    list_filter = ('type', 'is_active')
    search_fields = ('name', 'type')
    ordering = ('type',)


@admin.register(AcademicEvaluation)
class AcademicEvaluationAdmin(admin.ModelAdmin):
    list_display = ('evaluation', 'subject', 'group', 'trimester', 'date', 'is_active')
    list_filter = ('evaluation', 'subject', 'group', 'trimester', 'is_active')
    search_fields = ('subject__name', 'subject__code', 'group__designation')
    autocomplete_fields = ('evaluation', 'subject', 'group')
    ordering = ('group', 'subject', 'trimester', 'evaluation')


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    # CORREÇÃO: 'avaluation' -> 'academic_evaluation' em todo o lado
    # abaixo, porque o campo do model foi renomeado (Grade agora liga-se
    # a AcademicEvaluation, não a Evaluation).
    list_display = ('enrollment', 'academic_evaluation', 'value', 'created_at', 'updated_at')

    # CORREÇÃO ADICIONAL: como agora há dois saltos
    # (Grade -> AcademicEvaluation -> Evaluation), 'type'/'name'/'gradeWeight'
    # deixaram de estar diretamente em 'academic_evaluation' — estão em
    # 'academic_evaluation__evaluation'.
    list_filter = (
        'academic_evaluation__evaluation__type',
        'academic_evaluation__trimester',
        'academic_evaluation__group',
    )

    search_fields = (
        'enrollment__student__user__first_name',
        'enrollment__student__user__last_name',
        'enrollment__student__user__username',
        'academic_evaluation__subject__name',
    )

    autocomplete_fields = ('enrollment', 'academic_evaluation')

    ordering = (
        'academic_evaluation__group',
        'academic_evaluation__subject',
        'academic_evaluation__trimester',
    )


@admin.action(description="Publicar Pautas Selecionadas")
def post_gradebooks(modeladmin, request, queryset):
    # CORREÇÃO: 'created_at' -> 'posted_at' (o campo foi renomeado para
    # refletir melhor o que representa: a data em que a pauta foi publicada).
    updated = queryset.filter(posted=False).update(
        posted=True,
        posted_at=timezone.now(),
    )
    modeladmin.message_user(request, f"{updated} pauta(s) publicada(s) com sucesso.")


@admin.action(description="Despublicar Pautas Selecionadas")
def unpost_gradebooks(modeladmin, request, queryset):
    updated = queryset.filter(posted=True).update(
        posted=False,
        posted_at=None,
    )
    modeladmin.message_user(request, f"{updated} pauta(s) despublicada(s) com sucesso.")


@admin.register(GradeBook)
class GradeBookAdmin(admin.ModelAdmin):

    actions = (post_gradebooks, unpost_gradebooks)

    list_display = (
        'group', 'subject', 'academic_year', 'trimester',
        'posted', 'posted_at', 'generated_at', 'view_gradebook_button',
    )
    search_fields = ('group__designation', 'subject__name', 'subject__code', 'academic_year__designation')
    list_filter = ('posted', 'academic_year', 'trimester', 'group', 'subject')
    autocomplete_fields = ('group', 'subject', 'academic_year')
    readonly_fields = ('generated_at',)
    list_editable = ('posted',)

    def view_gradebook_page(self, request, object_id):
        gradebook = get_object_or_404(GradeBook, pk=object_id)

        enrollments = gradebook.group.enrollments.select_related(
            'student__user'
        ).order_by('student__user__first_name', 'student__user__last_name')

        # CORREÇÃO: usa AcademicEvaluation (que tem subject/group/trimester),
        # não Evaluation. E agora filtra também pelo trimestre da pauta —
        # uma pauta é sempre de UM trimestre específico.
        academic_evaluations = AcademicEvaluation.objects.filter(
            subject=gradebook.subject,
            group=gradebook.group,
            trimester=gradebook.trimester,
            is_active=True,
        ).select_related('evaluation').order_by('evaluation__type')

        # Todas as notas da turma/disciplina/trimestre numa única query.
        all_grades = Grade.objects.filter(
            enrollment__in=enrollments,
            academic_evaluation__in=academic_evaluations,
        ).select_related('academic_evaluation__evaluation')

        grades_lookup = {
            (g.enrollment_id, g.academic_evaluation_id): g
            for g in all_grades
        }

        results = []
        for enrollment in enrollments:
            average = enrollment.calculate_average(gradebook.subject, gradebook.trimester)
            situation = enrollment.situation(gradebook.subject, gradebook.trimester)

            ordered_grades = [
                grades_lookup.get((enrollment.id, ae.id))
                for ae in academic_evaluations
            ]

            results.append({
                'enrollment': enrollment,
                'student': enrollment.student,
                'grades': ordered_grades,
                'average': average,
                'situation': situation,
            })

        context = {
            **self.admin_site.each_context(request),
            'gradebook': gradebook,
            'academic_evaluations': academic_evaluations,
            'results': results,
            'title': f'{gradebook.subject.name} - {gradebook.group.designation} - {gradebook.get_trimester_display()}',
        }

        return render(request, 'admin/grades/gradebook.html', context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/ver-pauta/',
                self.admin_site.admin_view(self.view_gradebook_page),
                name='gradebook_view'
            )
        ]
        return custom_urls + urls

    @admin.display(description='Ações')
    def view_gradebook_button(self, obj):
        url = reverse('admin:gradebook_view', args=[obj.pk])
        return format_html('<a class="button" href="{}">Ver Pauta</a>', url)