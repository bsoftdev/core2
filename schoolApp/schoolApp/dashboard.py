import json
from django.db.models import Count
from unfold.components import BaseComponent, register_component

from academics.models import Course, Group
from enrollments.models import Enrollment
from grades.models import Grade, GradeBook
from accounts.models import Student, Teacher


@register_component
class EnrollmentsByCourseChart(BaseComponent):
    """Gráfico de barras: nº de alunos com matrícula ativa, por curso."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        courses = Course.objects.filter(is_active=True).order_by('name')
        labels, data = [], []
        for course in courses:
            count = Enrollment.objects.filter(
                group__course=course, status='ATIVA'
            ).count()
            labels.append(course.name)
            data.append(count)

        context.update({
            "height": 280,
            "data": json.dumps({
                "labels": labels,
                "datasets": [
                    {
                        "label": "Alunos matriculados",
                        "data": data,
                        "backgroundColor": "var(--color-primary-600)",
                        # CORREÇÃO: controla a "espessura" das barras —
                        # sem isto, o Chart.js decide sozinho e as barras
                        # ficam finas quando há poucas categorias.
                        "borderRadius": 6,
                        "maxBarThickness": 42,
                        "borderSkipped": False,
                    },
                ],
            }),
        })
        return context


@register_component
class GradeDistributionChart(BaseComponent):
    """Gráfico de barras: distribuição das notas lançadas por faixa (0-20)."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        buckets = [
            ("0 - 9 (Reprovado)", 0, 9.99),
            ("10 - 13 (Suficiente)", 10, 13.99),
            ("14 - 16 (Bom)", 14, 16.99),
            ("17 - 20 (Excelente)", 17, 20),
        ]
        labels, data = [], []
        for label, low, high in buckets:
            count = Grade.objects.filter(value__gte=low, value__lte=high).count()
            labels.append(label)
            data.append(count)

        context.update({
            "height": 280,
            "data": json.dumps({
                "labels": labels,
                "datasets": [
                    {
                        "label": "Notas",
                        "data": data,
                        "backgroundColor": "var(--color-primary-500)",
                        "borderRadius": 6,
                        "maxBarThickness": 56,
                        "borderSkipped": False,
                    },
                ],
            }),
        })
        return context


def dashboard_callback(request, context):
    """Injeta os KPIs e os dados do gráfico de doughnut no admin/index.html."""

    # --- Matrículas por estado, para o gráfico de doughnut (Chart.js puro) ---
    status_labels = dict(Enrollment.STATUS)
    counts = Enrollment.objects.values('status').annotate(total=Count('id'))
    counts_map = {row['status']: row['total'] for row in counts}

    # Cores semânticas: verde=ativa, azul=concluída, vermelho=cancelada, âmbar=trancada
    status_colors_map = {
        'ATIVA': '#16a34a',
        'CONCLUIDA': '#2563eb',
        'CANCELADA': '#dc2626',
        'TRANCADA': '#f59e0b',
    }

    status_display_labels = list(status_labels.values())
    status_data = [counts_map.get(code, 0) for code in status_labels.keys()]
    status_colors = [status_colors_map.get(code, '#94a3b8') for code in status_labels.keys()]

    context.update({
        "total_students": Student.objects.count(),
        "total_teachers": Teacher.objects.count(),
        "total_groups": Group.objects.count(),
        "total_active_enrollments": Enrollment.objects.filter(status='ATIVA').count(),
        "total_grades": Grade.objects.filter(value__isnull=False).count(),
        "pending_gradebooks": GradeBook.objects.filter(posted=False).count(),

        "enrollment_status_labels": status_display_labels,
        "enrollment_status_data": status_data,
        "enrollment_status_colors": status_colors,
    })
    return context