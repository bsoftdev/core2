from decimal import Decimal, InvalidOperation

from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count

from .utils import teacher_required, student_required
from .forms import StudentContactForm, TeacherContactForm, BootstrapPasswordChangeForm

from academics.models import TeacherAssignment, Subject
from enrollments.models import Enrollment
from grades.models import AcademicEvaluation, Grade
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

        messages.error(request, 'Usuário ou senha incorretos.')

    return render(request, 'accounts/login.html')


# LOGOUT
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


# REDIRECIONAR PARA A DASHBOARD CERTA
@login_required
def dashboard(request):
    user = request.user

    if user.is_superuser:
        return redirect('/admin/')

    if user.groups.filter(name='Professores').exists():
        return redirect('teacher_dashboard')

    if user.groups.filter(name='Estudantes').exists():
        return redirect('student_dashboard')

    logout(request)
    messages.error(
        request,
        'Este usuário não possui um perfil válido. Contacte o administrador do sistema.'
    )
    return redirect('login')


# DASHBOARD DO PROFESSOR
@teacher_required
def teacher_dashboard(request):
    # CORREÇÃO: related_name mudou de 'teachers' para 'teacher_profile'
    teacher = request.user.teacher_profile
    assignments = teacher.teacherassignments.select_related('subject', 'group')

    # CORREÇÃO: no template original, "Disciplinas" e "Turmas" mostravam
    # o mesmo número (assignments|length) — mas uma atribuição não é o
    # mesmo que uma disciplina nem que uma turma (um professor pode ter
    # 3 atribuições em apenas 2 turmas, por exemplo). Contamos os
    # valores distintos.
    total_subjects = assignments.values('subject').distinct().count()
    total_groups = assignments.values('group').distinct().count()

    # Dados para o gráfico: nº de alunos ativos por turma do professor.
    groups_summary = list(
        Enrollment.objects.filter(
            group__in=assignments.values('group'), status='ATIVA'
        )
        .values('group__designation')
        .annotate(total=Count('id'))
        .order_by('group__designation')
    )

    return render(request, 'teacher/dashboard.html', {
        'teacher': teacher,
        'assignments': assignments,
        'total_subjects': total_subjects,
        'total_groups': total_groups,
        'groups_summary': groups_summary,
    })


# PERFIL DO PROFESSOR
@teacher_required
def teacher_profile(request):
    teacher = request.user.teacher_profile
    contact_form = TeacherContactForm(instance=teacher, user=request.user)
    password_form = BootstrapPasswordChangeForm(user=request.user)

    if request.method == 'POST':
        if 'update_contact' in request.POST:
            contact_form = TeacherContactForm(request.POST, instance=teacher, user=request.user)
            if contact_form.is_valid():
                contact_form.save()
                messages.success(request, 'Dados de contacto atualizados com sucesso!')
                return redirect('teacher_profile')

        elif 'change_password' in request.POST:
            # SEGURANÇA: PasswordChangeForm exige a senha atual antes de
            # aceitar a nova — evita que alguém com a sessão aberta
            # (mas sem saber a senha) a troque sem mais nem menos.
            password_form = BootstrapPasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                # Sem isto, o Django invalidava a sessão atual ao mudar
                # a senha, e o professor era deslogado logo a seguir.
                update_session_auth_hash(request, user)
                messages.success(request, 'Senha alterada com sucesso!')
                return redirect('teacher_profile')

    return render(request, 'teacher/profile.html', {
        'teacher': teacher,
        'contact_form': contact_form,
        'password_form': password_form,
    })


# DASHBOARD DO ALUNO
@student_required
def student_dashboard(request):
    # CORREÇÃO: related_name mudou de 'students' para 'student_profile'
    student = request.user.student_profile

    enrollments = Enrollment.objects.filter(student=student).select_related('group', 'group__course')

    return render(request, 'student/dashboard.html', {'student': student, 'enrollments': enrollments})


# PERFIL DO ALUNO
@student_required
def student_profile(request):
    student = request.user.student_profile
    contact_form = StudentContactForm(instance=student, user=request.user)
    password_form = BootstrapPasswordChangeForm(user=request.user)

    if request.method == 'POST':
        if 'update_contact' in request.POST:
            contact_form = StudentContactForm(request.POST, instance=student, user=request.user)
            if contact_form.is_valid():
                contact_form.save()
                messages.success(request, 'Dados de contacto atualizados com sucesso!')
                return redirect('student_profile')

        elif 'change_password' in request.POST:
            password_form = BootstrapPasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Senha alterada com sucesso!')
                return redirect('student_profile')

    return render(request, 'student/profile.html', {
        'student': student,
        'contact_form': contact_form,
        'password_form': password_form,
    })


# NOTAS DO ALUNO — POR DISCIPLINA E TRIMESTRE
@student_required
def student_grades(request, enrollment_id, trimester):
    student = request.user.student_profile

    enrollment = get_object_or_404(
        Enrollment.objects.select_related('group', 'group__course', 'student'),
        id=enrollment_id,
        student=student,
    )

    # Disciplinas que têm avaliações académicas para esta turma/trimestre
    subjects = Subject.objects.filter(
        academic_evaluations__group=enrollment.group,
        academic_evaluations__trimester=trimester,
        academic_evaluations__is_active=True,
    ).distinct()

    subject_data = []

    for subject in subjects:
        academic_evaluations = AcademicEvaluation.objects.filter(
            subject=subject,
            group=enrollment.group,
            trimester=trimester,
            is_active=True,
        ).select_related('evaluation').order_by('evaluation__type')

        grades = Grade.objects.filter(
            enrollment=enrollment,
            academic_evaluation__in=academic_evaluations,
        ).select_related('academic_evaluation')

        grades_by_evaluation = {g.academic_evaluation_id: g for g in grades}

        evaluation_data = [
            {'evaluation': ae, 'grade': grades_by_evaluation.get(ae.id)}
            for ae in academic_evaluations
        ]

        average = enrollment.calculate_average(subject, trimester)
        situation = enrollment.situation(subject, trimester)

        subject_data.append({
            'subject': subject,
            'evaluation_data': evaluation_data,
            'average': average,
            'situation': situation,
        })

    return render(request, 'student/grades.html', {
        'student': student,
        'enrollment': enrollment,
        'trimester': trimester,
        'subject_data': subject_data,
    })


# ALUNOS DE UMA TURMA/DISCIPLINA ATRIBUÍDA AO PROFESSOR
@teacher_required
def teacher_students(request, assignment_id):
    teacher = request.user.teacher_profile

    assignment = get_object_or_404(
        TeacherAssignment.objects.select_related('group', 'subject'),
        id=assignment_id,
        teacher=teacher,
    )

    enrollments = Enrollment.objects.filter(group=assignment.group).select_related('student', 'student__user')

    return render(request, 'teacher/students.html', {
        'teacher': teacher,
        'assignment': assignment,
        'enrollments': enrollments,
    })


# NOTAS DE UM ALUNO ESPECÍFICO (VISÃO DO PROFESSOR) — POR TRIMESTRE
@teacher_required
def teacher_student_grades(request, assignment_id, student_id, trimester):
    teacher = request.user.teacher_profile

    assignment = get_object_or_404(
        TeacherAssignment.objects.select_related('group', 'subject'),
        id=assignment_id,
        teacher=teacher,
    )

    enrollment = get_object_or_404(Enrollment, student_id=student_id, group=assignment.group)

    average = enrollment.calculate_average(assignment.subject, trimester)
    situation = enrollment.situation(assignment.subject, trimester)

    academic_evaluations = AcademicEvaluation.objects.filter(
        group=assignment.group,
        subject=assignment.subject,
        trimester=trimester,
        is_active=True,
    ).select_related('evaluation').order_by('evaluation__type')

    grades = Grade.objects.filter(
        enrollment=enrollment,
        academic_evaluation__in=academic_evaluations,
    ).select_related('academic_evaluation')

    grades_by_evaluation = {g.academic_evaluation_id: g for g in grades}

    evaluation_data = [
        {'evaluation': ae, 'grade': grades_by_evaluation.get(ae.id)}
        for ae in academic_evaluations
    ]

    return render(request, 'teacher/student_grades.html', {
        'teacher': teacher,
        'assignment': assignment,
        'enrollment': enrollment,
        'trimester': trimester,
        'evaluation_data': evaluation_data,
        'average': average,
        'situation': situation,
    })


# LANÇAR/EDITAR NOTA
@teacher_required
def teacher_add_grade(request, assignment_id, student_id, evaluation_id):
    teacher = request.user.teacher_profile

    # SEGURANÇA: o professor só pode lançar notas na sua própria
    # atribuição — isto já estava bem feito no teu código original.
    assignment = get_object_or_404(
        TeacherAssignment.objects.select_related('group', 'subject'),
        id=assignment_id,
        teacher=teacher,
    )

    enrollment = get_object_or_404(Enrollment, student_id=student_id, group=assignment.group)

    # CORREÇÃO: 'Evaluation' -> 'AcademicEvaluation' (Evaluation não tem
    # 'group'/'subject' — isto rebentava sempre com FieldError).
    academic_evaluation = get_object_or_404(
        AcademicEvaluation,
        id=evaluation_id,
        group=assignment.group,
        subject=assignment.subject,
        is_active=True,
    )

    existing_grade = Grade.objects.filter(
        enrollment=enrollment,
        academic_evaluation=academic_evaluation,
    ).first()

    if request.method == 'POST':
        value = request.POST.get('value')
        observation = request.POST.get('observation', '')

        def _redirect_back():
            # CORREÇÃO: o parâmetro estava com typo ('assignmnet_id'),
            # o que causava NoReverseMatch sempre que caías aqui.
            return redirect(
                'teacher_add_grade',
                assignment_id=assignment.id,
                student_id=enrollment.student.id,
                evaluation_id=academic_evaluation.id,
            )

        if not value:
            messages.error(request, 'Informe a nota do aluno.')
            return _redirect_back()

        # CORREÇÃO: usa Decimal (como o model), em vez de float — evita
        # imprecisões de ponto flutuante numa nota académica.
        try:
            value = Decimal(value)
        except InvalidOperation:
            messages.error(request, 'Informe uma nota válida.')
            return _redirect_back()

        if value < 0 or value > 20:
            messages.error(request, 'A nota deve estar entre 0 e 20.')
            return _redirect_back()

        if existing_grade:
            existing_grade.value = value
            existing_grade.observation = observation
            existing_grade.launched_by = teacher
            existing_grade.save()
            messages.success(request, 'Nota atualizada com sucesso!')
        else:
            Grade.objects.create(
                enrollment=enrollment,
                academic_evaluation=academic_evaluation,
                value=value,
                observation=observation,
                launched_by=teacher,
            )
            messages.success(request, 'Nota lançada com sucesso!')

        return redirect(
            'teacher_student_grades',
            assignment_id=assignment.id,
            student_id=enrollment.student.id,
            trimester=academic_evaluation.trimester,
        )

    return render(request, 'teacher/add_grade.html', {
        'teacher': teacher,
        'assignment': assignment,
        'enrollment': enrollment,
        'evaluation': academic_evaluation,
        'existing_grade': existing_grade,
    })