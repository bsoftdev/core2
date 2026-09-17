from decimal import Decimal
from django.db import models
from accounts.models import Student
from academics.models import Group


class Enrollment(models.Model):

    STATUS = [
        ('ATIVA', 'Ativa'),
        ('CONCLUIDA', 'Concluída'),
        ('CANCELADA', 'Cancelada'),  
        ('TRANCADA', 'Trancada'),
    ]

    student = models.ForeignKey(
        Student, on_delete=models.PROTECT, related_name='enrollments', verbose_name='Aluno'
    )
    group = models.ForeignKey(
        Group, on_delete=models.PROTECT, related_name='enrollments', verbose_name='Turma'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Matriculado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    status = models.CharField(max_length=12, choices=STATUS, default='ATIVA', verbose_name='Status')

    class Meta:
        verbose_name = 'Matrícula'
        verbose_name_plural = 'Matrículas'
        constraints = [
            models.UniqueConstraint(fields=['student', 'group'], name='unique_student_group'),
        ]

    def calculate_average(self, subject, trimester):
        """
        Média ponderada do aluno numa disciplina, num trimestre específico.

        CORREÇÃO: agora recebe também 'trimester' (antes só recebia
        'subject' — mas uma disciplina tem 3 trimestres, cada um com a
        sua própria AC/NPP/NPT, por isso sem o trimestre era ambíguo a
        que período a média se referia).

        CORREÇÃO: usa AcademicEvaluation (não Evaluation) para filtrar
        por disciplina+turma+trimestre — é essa a informação de contexto
        que faltava no model antigo.
        """
        from grades.models import AcademicEvaluation, Grade

        academic_evaluations = AcademicEvaluation.objects.filter(
            subject=subject,
            group=self.group,
            trimester=trimester,
            is_active=True,
        ).select_related('evaluation')

        total_evaluations = academic_evaluations.count()
        if total_evaluations == 0:
            return None

        # Os pesos (AC/NPP/NPT) devem somar 100%. Se não somarem, algo
        # está mal configurado no catálogo — mais vale não calcular do
        # que mostrar uma média errada.
        total_weight = sum(
            (ae.evaluation.gradeWeight for ae in academic_evaluations),
            Decimal('0')
        )
        if total_weight != Decimal('100'):
            return None

        grades = Grade.objects.filter(
            enrollment=self,
            academic_evaluation__in=academic_evaluations,
            value__isnull=False,
        ).select_related('academic_evaluation__evaluation')

        # Se ainda faltar alguma nota (ex: NPT por lançar), a média
        # fica pendente em vez de calculada parcialmente — evita
        # mostrar ao aluno uma média que ainda vai mudar.
        if grades.count() < total_evaluations:
            return None

        total = Decimal('0')
        for grade in grades:
            weight = grade.academic_evaluation.evaluation.gradeWeight
            total += grade.value * (weight / Decimal('100'))

        return total.quantize(Decimal('0.01'))

    def situation(self, subject, trimester):
        """Situação do aluno na disciplina, no trimestre indicado."""
        average = self.calculate_average(subject, trimester)

        if average is None:
            from grades.models import AcademicEvaluation
            evaluations_exist = AcademicEvaluation.objects.filter(
                subject=subject, group=self.group, trimester=trimester, is_active=True
            ).exists()
            return 'PENDENTE' if evaluations_exist else 'SEM_NOTAS'

        if average >= Decimal('10'):
            return 'APROVADO'
        if average >= Decimal('5'):
            return 'RECURSO'
        return 'REPROVADO'

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.id}"