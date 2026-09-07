from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages #mensagens de alerta
from django.shortcuts import render, redirect, get_object_or_404 #pegar objecto ou nao encontre
from django.http import HttpResponseForbidden

from .utils import teacher_required, student_required

from academics.models import Group,TeacherAssignment
from enrollments.models import Enrollment
from grades.models import Evaluation, Grade
from .models import Student, Teacher


# LOGIN
def login_view(request):


    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:

            login(request, user)

            return redirect('dashboard')

        messages.error(
            request,
            'Usuário ou senha incorretos.'
        )

    return render(request,'accounts/login.html')


# LOGOUT
@login_required
def logout_view(request):

    logout(request)
 
    return redirect('login')


# REDIRECTING TO THE RIGHT DASHBOARD
@login_required
def dashboard(request):

    user = request.user

    # ADMIN
    if user.is_superuser:

        return redirect('/admin/')


    # PROFESSOR
    if user.groups.filter(name='Professores').exists():

        return redirect(
            'teacher_dashboard'
        )

    # ESTUDANTE
    if user.groups.filter(name='Estudantes').exists():

        return redirect(
            'student_dashboard'
        )


    # Usuário sem perfil
    logout(request)

    messages.error(request, 'Este usuário não possui um perfil válido.Contactar o Adminastrador do Sistema')

    return redirect('login')


# DASHBOARD OF TEACHER
@teacher_required
def teacher_dashboard(request):

    teacher = request.user.teachers #pegando o prof logado
    assignments = teacher.teacherassignments.select_related(
        'subject',
        'group'
    )

    return render(request,'teacher/dashboard.html',{'teacher': teacher, 'assignments':assignments})


# DASHBOARD OF STUDENT
@student_required
def student_dashboard(request):

    student = request.user.students

    return render( request, 'student/dashboard.html', {'student': student})


#VIEW PARA PROFESSOR PODER VISUALIZAR APENAS ALUNOS PERTECENTES AS SUAS TURMAS
@teacher_required
def teacher_students(request, assignment_id):

    teacher = request.user.teachers

    # Buscar a atribuição específica do professor
    assignment = get_object_or_404(
        TeacherAssignment.objects.select_related(
            'group',
            'subject'
        ),
        id=assignment_id,
        teacher=teacher
    )

    # Buscar alunos matriculados na turma dessa atribuição
    enrollments = Enrollment.objects.filter(
        group=assignment.group
    ).select_related(
        'student',
        'student__user'
    )

    return render(
        request,
        'teacher/students.html',
        {
            'teacher': teacher,
            'assignment': assignment,
            'enrollments': enrollments,
        }
    )


#view para tela de lancar nota de aluno
@teacher_required
def teacher_student_grades(request, assignment_id, student_id):

    teacher = request.user.teachers

    # Buscar a atribuição EXATA
    assignment = get_object_or_404(
        TeacherAssignment.objects.select_related(
            'group',
            'subject'
        ),
        id=assignment_id,
        teacher=teacher
    )

    # Verificar se o aluno pertence à turma
    enrollment = get_object_or_404(
        Enrollment,
        student_id=student_id,
        group=assignment.group
    )
    
    avarage = enrollment.calculate_avarage(assignment.subject)
    situation = enrollment.situation(assignment.subject)
    

    # Buscar somente avaliações da disciplina
    # e da turma dessa atribuição
    evaluations = Evaluation.objects.filter(
        group=assignment.group,
        subject=assignment.subject,
        is_active=True
    ).order_by('date')

    # Buscar notas do aluno somente dessas avaliações
    grades = Grade.objects.filter(
        enrollment=enrollment,
        avaluation__in=evaluations
        
    ).select_related(
        'avaluation'
    )
    
    # Organizar notas por avaliação
    grades_by_evaluation = {
        grade.avaluation_id: grade
        for grade in grades
    }
    evaluation_data = []

    for evaluation in evaluations:

        grade = grades_by_evaluation.get(evaluation.id)

        evaluation_data.append({
            'evaluation': evaluation,
            'grade': grade,
    })

    return render(
        request,
        'teacher/student_grades.html',
        {
            'teacher': teacher,
            'assignment': assignment,
            'enrollment': enrollment,
            'evaluations': evaluations,
            'evaluation_data': evaluation_data,
            'avarage': avarage,
            'situation': situation,
        }
    )

#view para lançar notas
@teacher_required
def teacher_add_grade(request, assignment_id, student_id, evaluation_id):

    teacher = request.user.teachers

    #buscar atribuição exata do professor
    assignment = get_object_or_404(
        TeacherAssignment.objects.select_related('group','subject'),
        id=assignment_id,
        teacher = teacher
    )
    #verificar de o aluno pertence a turma 
    enrollment = get_object_or_404(
        Enrollment,
        student_id=student_id,
        group=assignment.group
    )

    #buscar avaliacão exata
    evaluation = get_object_or_404(
        Evaluation,
        id = evaluation_id,
        group = assignment.group,
        subject = assignment.subject,
        is_active = True
    )

    #verificar se o estudante já tem  uma nota para essa avaliação
    existing_grade = Grade.objects.filter(
        enrollment = enrollment,
        avaluation = evaluation
    ).first()

    if request.method == 'POST':
        value = request.POST.get('value')
        observation = request.POST.get('observation')

        #verificar se foi informado uma nota no formulario
        if value == '' or value is None:

            messages.error(request,'Informe a nota do aluno')
            
            return redirect(
                    'teacher_add_grade',
                    assignmnet_id = assignment.id,
                    student_id = enrollment.student.id,
                    evaluation_id = evaluation.id
            )
        try:
            value = float(value)

        except ValueError:
            messages.error(request,'Informe uma nota válida')

            return redirect(
                    'teacher_add_grade',
                    assignmnet_id = assignment.id,
                    student_id = enrollment.student.id,
                    evaluation_id = evaluation.id
            )

        #validadar intervalo da nota [0,20]
        if value < 0 or value > 20:

            messages.error(request,'A nota deve estar entre 0 e 20')

            return redirect(
                    'teacher_add_grade',
                    assignmnet_id = assignment.id,
                    student_id = enrollment.student.id,
                    evaluation_id = evaluation.id
            )

        #CRIAR OU ATUALIZAR A NOTA
        if existing_grade:
            existing_grade.value = value
            existing_grade.observation = observation
            existing_grade.save()

            messages.success(request, 'Nota atualizada com sucesso!')
        else:
            Grade.objects.create(
                enrollment = enrollment,
                avaluation = evaluation,
                value = value,
                observation = observation
            )

            messages.success(request, 'Nota lançada com sucesso!')

        return redirect(
            'teacher_student_grades',
            assignment_id = assignment.id,
            student_id = enrollment.student.id
        )
    return render(
        request,
        'teacher/add_grade.html',{
            'teacher':teacher,
            'assignment':assignment,
            'enrollment':enrollment,
            'evaluation':evaluation,
            'existing_grade':existing_grade,
        }
    )
    

