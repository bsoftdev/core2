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

    # CALCULATING THE AVERAGE MARK => MEDIA
          # CALCULATING THE AVERAGE MARK => MEDIA
    def calculate_avarage(self, subject):
        from grades.models import Evaluation, Grade

        # 1. Buscar todas as avaliações que DEVERIAM ter nota nesta disciplina e turma
        avaluations = Evaluation.objects.filter(
            subject=subject,
            group=self.group,
            is_active=True,
            type__in=['TESTE', 'TRABALHO', 'PROVA']
        )

        total_avaliacoes = avaluations.count()

        # Se não há nenhuma avaliação criada no sistema, não há média
        if total_avaliacoes == 0:
            return None

        # 2. Buscar apenas as notas que o aluno REALMENTE tem para essas avaliações
        grades = Grade.objects.filter(
            enrollment=self,
            avaluation__in=avaluations,
            value__isnull=False # Garante que a nota não está vazia/nula
        ).select_related('avaluation')

        total_notas_lancadas = grades.count()

        # SEGURANÇA MÁXIMA: Se o número de notas for menor que o número de avaliações,
        # significa que há notas em falta. O sistema para imediatamente aqui.
        if total_notas_lancadas < total_avaliacoes:
            return None

        # 3. Se passou na validação (tem todas as notas), faz o cálculo ponderado
        total_sum = Decimal('0')
        sum_weight = Decimal('0')

        for grade in grades:
            # Aceder ao peso diretamente através da nota relacionada
            weight = Decimal(str(grade.avaluation.gradeWeight))
            total_sum += Decimal(str(grade.value)) * weight
            sum_weight += weight

        if sum_weight == 0:
            return None

        return round(total_sum / sum_weight, 2)

    # METHOD TO SEE IF SOMEONE IS APPROVED OR NOT
    def situation(self, subject):
        avarage = self.calculate_avarage(subject)

        # Se a média retornou None, significa que faltam notas ou não há avaliações
        if avarage is None:
            from grades.models import Evaluation

            existe_avaluation = Evaluation.objects.filter(
                subject=subject,
                group=self.group,
                is_active=True,
                type__in=[
                    'TESTE',
                    'TRABALHO',
                    'PROVA',
                ]
            ).exists()

            if existe_avaluation:
                # Se existem avaliações criadas, mas o aluno não tem todas as notas
                return 'PENDENTE'
            
            # Se nem sequer existem avaliações criadas para a disciplina
            return 'SEM_NOTAS' 

        # CORREÇÃO DA LÓGICA DE NOTAS (Ordem de exclusão estrita)
        if avarage >= 9.5:  # Na realidade angolana, 9.5 arredonda para 10 (Aprovado)
            return 'APROVADO'
        
        if avarage >= 4.5:  # De 4.5 a 9.4 vai a Exame de Recurso
            return 'RECURSO'
        
        return 'REPROVADO' # Abaixo de 4.5 reprova direto sem direito a recurso

    def __str__(self):
        return f"{self.student}"