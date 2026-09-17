from django.db import models
from django.core.exceptions import ValidationError
from accounts.models import Teacher


# COURSE MODEL
class Course(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name='Nome')
    code = models.CharField(max_length=30, unique=True, verbose_name='Código do Curso')
    description = models.TextField(blank=True, verbose_name='Descrição')
    duration = models.PositiveSmallIntegerField(verbose_name='Duração do Curso (anos)')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        ordering = ['name']

    def __str__(self):
        return f"{self.code} - {self.name}"


# SUBJECT MODEL (Subject N - 1 Course)
class Subject(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.PROTECT, related_name='subjects', verbose_name='Curso'
    )
    name = models.CharField(max_length=150, verbose_name='Nome')
    code = models.CharField(max_length=30, unique=True, verbose_name='Código da Disciplina')
    course_year = models.PositiveSmallIntegerField(verbose_name='Ano do Curso')
    workload = models.PositiveIntegerField(default=0, verbose_name='Carga Horária')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')

    class Meta:
        verbose_name = 'Disciplina'
        verbose_name_plural = 'Disciplinas'
        ordering = ['course_year', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['course', 'name'], name='unique_subject_name_per_course'
            ),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


# ACADEMIC YEAR MODEL
class AcademicYear(models.Model):
    designation = models.CharField(max_length=20, unique=True, verbose_name='Ano Letivo')
    start_date = models.DateField(verbose_name='Data de Início')
    end_date = models.DateField(verbose_name='Data de Fim')
    is_active = models.BooleanField(default=False, verbose_name='Ativo')

    class Meta:
        verbose_name = 'Ano Letivo'
        verbose_name_plural = 'Anos Letivos'
        ordering = ['-start_date']

    def clean(self):
        # Validação nova: evita datas invertidas por engano no admin.
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError(
                {'end_date': 'A data de fim deve ser posterior à data de início.'}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.designation


# CLASS/GROUP MODEL => Turma
class Group(models.Model):
    SHIFTS = [
        ('MANHA', 'Manhã'),
        ('TARDE', 'Tarde'),
        ('NOITE', 'Noite'),
    ]
    course = models.ForeignKey(
        Course, on_delete=models.PROTECT, related_name='groups', verbose_name='Curso'
    )
    academic_year = models.ForeignKey(
        AcademicYear, on_delete=models.PROTECT, related_name='groups', verbose_name='Ano Letivo'
    )
    designation = models.CharField(max_length=50, verbose_name='Designação')
    course_year = models.PositiveSmallIntegerField(verbose_name='Ano do Curso')
    shift = models.CharField(max_length=10, choices=SHIFTS, verbose_name='Turno')

    class Meta:
        verbose_name = 'Turma'
        verbose_name_plural = 'Turmas'
        ordering = ['academic_year', 'course', 'designation']
        constraints = [
            models.UniqueConstraint(
                fields=['course', 'academic_year', 'designation'],
                name='unique_group_per_course_year'
            ),
        ]

    def __str__(self):
        return f"{self.designation} - {self.course.name} - {self.academic_year}"


# TEACHER - SUBJECT - GROUP (Atribuição de Professor)
class TeacherAssignment(models.Model):
    teacher = models.ForeignKey(
        Teacher, on_delete=models.PROTECT, related_name='teacherassignments', verbose_name='Professor'
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.PROTECT, related_name='teacherassignments', verbose_name='Disciplina'
    )
    group = models.ForeignKey(
        Group, on_delete=models.PROTECT, related_name='teacherassignments', verbose_name='Turma'
    )
    date_assignment = models.DateField(auto_now_add=True, verbose_name='Data de Atribuição')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')

    class Meta:
        verbose_name = 'Atribuição de Professor'
        verbose_name_plural = 'Atribuições de Professores'
        constraints = [
            models.UniqueConstraint(
                fields=['teacher', 'subject', 'group'], name='unique_assignment_teacher'
            )
        ]

    def clean(self):
        # Um professor só pode ser atribuído a uma disciplina que
        # pertença ao curso da turma.
        if self.group_id and self.subject_id:
            if self.subject.course_id != self.group.course_id:
                raise ValidationError({
                    'subject': 'Esta disciplina não pertence ao curso desta turma.'
                })

    def save(self, *args, **kwargs):
        # ull_clean() garante que o clean() acima corre
        # sempre, mesmo fora de um ModelForm (ex: scripts, shell, admin
        # com bulk actions). Sem isto, a validação existe no código mas
        # nunca é realmente executada em muitos cenários.
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.teacher} - {self.subject} - {self.group}"