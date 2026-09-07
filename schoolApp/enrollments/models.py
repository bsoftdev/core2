from decimal import Decimal
from django.db import models
from accounts.models import Student
from academics.models import Group

# CORREÇÃO 1: Removido o import de Grade e Evaluation do topo do ficheiro!

class Enrollment(models.Model):

    STATUS = [
        ('ATIVA','Ativo'),
        ('CONCLUIDA','Concluída'),
        ('CANCELEDA','Cancelada'),
        ('TRANCADA','Trancada'),
    ]

    student = models.ForeignKey(Student, on_delete=models.PROTECT, null=False, related_name='enrollments', verbose_name='Aluno')
    group = models.ForeignKey(Group, on_delete=models.PROTECT, null=False, related_name='enrollments', verbose_name='Turma')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Matriculado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    status = models.CharField(max_length=12, choices=STATUS, default='ATIVA', verbose_name='Status')

    class Meta:
        verbose_name = 'Matricula'
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'group'],
                name='unique_student_group'
            )
        ]
    def calculate_avarage(self, subject):
        from grades.models import Evaluation, Grade

        evaluations = Evaluation.objects.filter(
            subject=subject,
            group=self.group,
            is_active=True,
            type__in=['TESTE', 'TRABALHO', 'PROVA']
        )

        total_evaluations = evaluations.count()

        if total_evaluations == 0:
            return None

        # Verificar se os pesos totalizam 100%
        total_weight = sum(
            (evaluation.gradeWeight for evaluation in evaluations),
            Decimal('0')
        )

        if total_weight != Decimal('100'):
            return None

        grades = Grade.objects.filter(
            enrollment=self,
            avaluation__in=evaluations,
            value__isnull=False
        ).select_related('avaluation')

        # Se faltar alguma nota, a média fica pendente
        if grades.count() < total_evaluations:
            return None

        total = Decimal('0')

        for grade in grades:
            value = grade.value
            weight = grade.avaluation.gradeWeight

            total += value * (weight / Decimal('100'))

        return total.quantize(Decimal('0.01'))


    def situation(self, subject):
        average = self.calculate_avarage(subject)

        if average is None:
            from grades.models import Evaluation

            evaluations_exist = Evaluation.objects.filter(
                subject=subject,
                group=self.group,
                is_active=True,
                type__in=['TESTE', 'TRABALHO', 'PROVA']
            ).exists()

            if evaluations_exist:
                return 'PENDENTE'

            return 'SEM_NOTAS'

        if average >= Decimal('10'):
            return 'APROVADO'

        if average >= Decimal('5'):
            return 'RECURSO'

        return 'REPROVADO'