from django.db import models
from enrollments.models import Enrollment
from academics.models import Subject, Group, AcademicYear
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

# Create your models here.

# Evaluation Model
class Evaluation(models.Model):
    TYPES = [
        ('TESTE', 'Teste'),
        ('TRABALHO', 'Trabalho'),
        ('PROVA', 'Prova'),
        ('EXAME', 'Exame'),
        ('RECURSO', 'Recurso'),  # Corrigido: 'Reucrso' -> 'Recurso'
    ]

    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name='evaluations', verbose_name='Disciplina')  # Corrigido: related_name
    group = models.ForeignKey(Group, on_delete=models.PROTECT, related_name='evaluations', verbose_name='Turma')          # Corrigido: related_name
    name = models.CharField(max_length=100, verbose_name='Nome da Avaliação')  # Corrigido: 'Avalição'
    type = models.CharField(max_length=20, choices=TYPES, verbose_name='Tipo de Avaliação')
    gradeWeight = models.DecimalField(max_digits=5, validators=[MinValueValidator(0), MaxValueValidator(100)], decimal_places=2, default=0.00, verbose_name='Peso da Nota (%)')
    date = models.DateField(null=True, blank=True, verbose_name='Data da realização')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')

    class Meta:
        verbose_name = 'Avaliação'        # Corrigido singular
        verbose_name_plural = 'Avaliações' # Adicionado plural correto

    def __str__(self):
        # Proteção caso group ou subject sejam nulos por algum motivo na memória
        designation = self.group.designation if self.group else "Sem Turma"
        return f"{self.subject} - {self.name} - {designation}"


# GRADE MODEL
class Grade(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='grades', verbose_name='Aluno')
    avaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE, related_name='grades', verbose_name='Avaliação') # Corrigido verbose_name
    value = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(20)], verbose_name='Nota')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Data de Lançamento') # Invertido com updated_at
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')        # Invertido com created_at
    observation = models.TextField(blank=True, verbose_name='Observação')

    class Meta:
        verbose_name = 'Nota'
        verbose_name_plural = 'Notas'
        constraints = [
            models.UniqueConstraint(
                fields=['enrollment', 'avaluation'],
                name='unique_grade_avaluation'
            )
        ]

   
    def clean(self):
        super().clean() # Boa prática chamar o clean do pai

        # Verifica se ambos os relacionamentos foram selecionados no form
        if hasattr(self, 'avaluation') and hasattr(self, 'enrollment') and self.avaluation and self.enrollment:
            
            # Validação 1: Aluno e Avaliação devem ser da mesma turma
            if self.enrollment.group_id != self.avaluation.group_id:
                raise ValidationError({
                    'avaluation': 'Esta avaliação pertence a uma turma diferente da turma desse aluno.'
                })

            # Validação 2: A disciplina da avaliação deve existir no curso da turma do aluno
            # Nota: Certifique-se de que self.enrollment.group.course existe no seu app 'academics'
            if hasattr(self.enrollment.group, 'course') and self.enrollment.group.course:
                course_subjects = self.enrollment.group.course.subjects.values_list('id', flat=True)
                if self.avaluation.subject_id not in course_subjects:
                    raise ValidationError({
                        'avaluation': 'A disciplina desta avaliação não pertence ao curso da turma.'
                    })

   
    def __str__(self):
        # Certifique-se de que o model Enrollment possui o relacionamento 'student'
        student_name = getattr(self.enrollment, 'student', self.enrollment)
        return f"{student_name} - {self.avaluation} - {self.value}"


# GRADEBOOK => PAUTA
class GradeBook(models.Model):
    group = models.ForeignKey(Group, on_delete=models.PROTECT, related_name='gradebooks', verbose_name='Turma')
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name='gradebooks', verbose_name='Disciplina')
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.PROTECT, related_name='gradebooks', verbose_name='Ano Letivo')
    posted = models.BooleanField(default=False, verbose_name='Publicada')
    created_at = models.DateTimeField(null=True, blank=True, verbose_name='Pauta Publicada em')
    genareted_at = models.DateTimeField(auto_now=True, verbose_name='Data Gerada')

    class Meta:
        verbose_name = 'Pauta'
        verbose_name_plural = 'Pautas' 

        # Evitar duplicidade de dados 
        constraints = [
            models.UniqueConstraint(
                fields= ['group', 'subject', 'academic_year'], 
                name='unique_gradebook_group_subject_academic_year'
            )
        ]
        

    def __str__(self):
        return f"Pauta - {self.subject} - {self.group}"

