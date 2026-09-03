from django.db import models
from accounts.models import Teacher
from django.core.exceptions import ValidationError

# Create your models here.

#Course Model
class Course(models.Model):
    name = models.CharField(max_length=150, null=False, unique=True, verbose_name='Nome')
    code = models.CharField(max_length=30,unique=True, null=False, verbose_name='Codigo do Curso')
    description = models.TextField(blank=True,verbose_name='Descrição')
    duration = models.PositiveBigIntegerField(verbose_name='Duração do Curso')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')

    class Meta:
              verbose_name ='Curso'

    def __str__(self):
        return f"{self.code}-{self.name}"


    #SUBJECT MODEL (Subject 1 -N Course =>Relation)
class Subject(models.Model):
    course = models.ForeignKey(Course,on_delete=models.PROTECT, related_name='subjects', verbose_name='Curso')
    name = models.CharField(max_length=150, unique=True,null=False,verbose_name='Nome')
    code = models.CharField(max_length=30,unique=True,null=False, verbose_name='Codigo da Disciplina')
    course_year = models.PositiveIntegerField(verbose_name='Ano do Curso')
    trimester = models.PositiveIntegerField(verbose_name='trimeste')
    workload = models.PositiveIntegerField(default=0, verbose_name='Caraga Horária')
    is_active = models.BooleanField(default=True,null=False, verbose_name='Ativo')

    class Meta:
              verbose_name ='Disciplina'

    def __str__(self):
        return f"{self.code} - {self.name}"

#ACDEMY YEAR MODEL
class AcademicYear(models.Model):
     designation = models.CharField(max_length=20,null=False, unique=True, verbose_name='Ano Letivo')
     start_date = models.DateField(null=False,verbose_name='Data de Inicio')
     end_date = models.DateField(null=False,verbose_name='Data de fim')
     is_active = models.BooleanField(default=False, verbose_name='Ativo')

     class Meta:
              verbose_name ='Ano Letivo'

     def __str__(self):
         return self.designation

#Class or Group Model => Turma
class Group(models.Model):
    SHIFTS = [
        ('MANHA','Manhã'),
        ('TARDE', 'Tarde'),
        ('NOITE','Noite'),
        ]
    course = models.ForeignKey(Course, on_delete=models.PROTECT,null=False, related_name='groups', verbose_name='Curso')
    academic_year = models.ForeignKey(AcademicYear, null=False, on_delete=models.PROTECT, related_name='groups', verbose_name='Ano Letivo')
    designation = models.CharField(max_length=50, verbose_name='Designação')
    course_year =models.PositiveIntegerField(verbose_name='Ano do curso')
    shit= models.CharField(max_length=10, choices=SHIFTS, verbose_name='Turno')

    class Meta:
              verbose_name ='Turma'

    def __str__(self):
        return (
                f"{self.designation}-"
                f"{self.course.name}-"#poderemos pegar nome  do curso
                f"{self.academic_year}-" #poderemos pegar a designacao do ano
        )

# TEACHER - SUBJECT - GROUP (AtribuicaoProfessor)
#WITCH TEACHER GIVES CLASSES TO WITCH GROUP

class TeacherAssignment(models.Model):
    teacher = models.ForeignKey(Teacher,  on_delete=models.PROTECT, related_name='teacherassignments',verbose_name='Professor')
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name='teacherassignments', verbose_name='Dsiciplina')
    group = models.ForeignKey(Group,on_delete=models.PROTECT, related_name='teacherassignments', verbose_name='Turma')
    date_assignment = models.DateField(auto_now_add=True,verbose_name='Data Atribuição')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')

    class Meta:
        verbose_name = 'Atribuições a Professor'
        verbose_name_plural = 'Atribuições a Professores'
        constraints = [
            models.UniqueConstraint(
                fields=[
                    'teacher',
                    'subject',
                    'group',
                ],
                name='unique_assignment_teacher'
            )   
        ]

        
    #METHODO professor só pode ser atribuído a uma disciplina que pertença ao curso da turma.
    def clean(self):

        if self.group_id and self.subject_id:

            if self.subject.course_id != self.group.course_id:

                raise ValidationError({
                    'subject': (
                        'Esta disciplina não pertence '
                        'ao curso desta turma.'
                    )
                })

        
    def __str__(self):
        return (
            f"{self.teacher} - "
            f"{self.subject} - "
            f"{self.group} - "

        )

   


    

    