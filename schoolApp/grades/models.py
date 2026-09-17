from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from enrollments.models import Enrollment
from academics.models import Subject, Group, AcademicYear


# EVALUATION MODEL — catálogo fixo dos TIPOS de avaliação e o peso de cada um
# (ex: AC=40%, NPP=30%, NPT=30% — os pesos devem somar 100%).
class Evaluation(models.Model):
    TYPES = [
        ('AC', 'Avaliação Contínua'),
        ('NPP', 'Prova do Professor'),
        ('NPT', 'Prova Trimestral'),
    ]

    type = models.CharField(max_length=10, choices=TYPES, unique=True, verbose_name='Tipo')
    name = models.CharField(max_length=100, verbose_name='Nome da Avaliação')
    gradeWeight = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Peso da Nota (%)')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')

    class Meta:
        verbose_name = 'Tipo de Avaliação'
        verbose_name_plural = 'Tipos de Avaliação'

    def __str__(self):
        return self.get_type_display()


# ACADEMIC EVALUATION — a "ocorrência" concreta: esta disciplina, nesta
# turma, neste trimestre, tem uma avaliação deste tipo.
class AcademicEvaluation(models.Model):
    TRIMESTERS = [
        (1, '1º Trimestre'),
        (2, '2º Trimestre'),
        (3, '3º Trimestre'),
    ]

    evaluation = models.ForeignKey(
        Evaluation, on_delete=models.PROTECT, related_name='academic_evaluations',
        verbose_name='Tipo de Avaliação'
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.PROTECT, related_name='academic_evaluations', verbose_name='Disciplina'
    )
    group = models.ForeignKey(
        Group, on_delete=models.PROTECT, related_name='academic_evaluations', verbose_name='Turma'
    )
    trimester = models.PositiveSmallIntegerField(choices=TRIMESTERS, verbose_name='Trimestre')
    date = models.DateField(null=True, blank=True, verbose_name='Data da Realização')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')

    class Meta:
        verbose_name = 'Avaliação Académica'
        verbose_name_plural = 'Avaliações Académicas'
        ordering = ['trimester', 'subject']
        constraints = [
            models.UniqueConstraint(
                fields=['evaluation', 'subject', 'group', 'trimester'],
                name='unique_academic_evaluation'
            )
        ]

    def clean(self):
        # a disciplina tem de pertencer
        # ao curso da turma (o mesmo que já faz em TeacherAssignment).
        if self.subject_id and self.group_id:
            if self.subject.course_id != self.group.course_id:
                raise ValidationError({
                    'subject': 'Esta disciplina não pertence ao curso desta turma.'
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.evaluation.get_type_display()} - {self.subject} - "
            f"{self.group.designation} - {self.get_trimester_display()}"
        )


# GRADE MODEL — a nota de UM aluno numa avaliação concreta.
class Grade(models.Model):
    enrollment = models.ForeignKey(
        Enrollment, on_delete=models.CASCADE, related_name='grades', verbose_name='Matrícula'
    )
    
    academic_evaluation = models.ForeignKey(
        AcademicEvaluation, on_delete=models.CASCADE, related_name='grades', verbose_name='Avaliação'
    )
    value = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
        verbose_name='Nota'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Data de Lançamento')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    launched_by = models.ForeignKey(
        'accounts.Teacher', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='launched_grades', verbose_name='Lançada por'
    )
    observation = models.TextField(blank=True, verbose_name='Observação')

    class Meta:
        verbose_name = 'Nota'
        verbose_name_plural = 'Notas'
        constraints = [
            models.UniqueConstraint(
                fields=['enrollment', 'academic_evaluation'], name='unique_grade_academic_evaluation'
            )
        ]

    def clean(self):
        super().clean()
        if self.academic_evaluation_id and self.enrollment_id:
            # O aluno tem de pertencer à mesma turma da avaliação.
            if self.enrollment.group_id != self.academic_evaluation.group_id:
                raise ValidationError({
                    'academic_evaluation': 'Esta avaliação pertence a uma turma diferente da turma deste aluno.'
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.enrollment.student.user.get_full_name()} - {self.academic_evaluation} - {self.value}"


# GRADEBOOK => Pauta
class GradeBook(models.Model):
    group = models.ForeignKey(Group, on_delete=models.PROTECT, related_name='gradebooks', verbose_name='Turma')
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name='gradebooks', verbose_name='Disciplina')
    academic_year = models.ForeignKey(
        AcademicYear, on_delete=models.PROTECT, related_name='gradebooks', verbose_name='Ano Letivo'
    )
   
    trimester = models.PositiveSmallIntegerField(
        choices=AcademicEvaluation.TRIMESTERS, verbose_name='Trimestre'
    )
    posted = models.BooleanField(default=False, verbose_name='Publicada')
    posted_at = models.DateTimeField(null=True, blank=True, verbose_name='Pauta Publicada em')
    generated_at = models.DateTimeField(auto_now=True, verbose_name='Data Gerada')

    class Meta:
        verbose_name = 'Pauta'
        verbose_name_plural = 'Pautas'
        constraints = [
            models.UniqueConstraint(
                fields=['group', 'subject', 'academic_year', 'trimester'],
                name='unique_gradebook_group_subject_year_trimester'
            )
        ]

    def __str__(self):
        return f"Pauta - {self.subject} - {self.group} - {self.get_trimester_display()}"