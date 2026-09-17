from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # DASHBOARD DO PROFESSOR
    path('teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher/assignment/<int:assignment_id>/students/', views.teacher_students, name='teacher_students'),

    path(
        'teacher/assignment/<int:assignment_id>/student/<int:student_id>/grades/<int:trimester>/',
        views.teacher_student_grades,
        name='teacher_student_grades'
    ),

    path(
        'teacher/assignment/<int:assignment_id>/student/<int:student_id>/evaluation/<int:evaluation_id>/grade/add/',
        views.teacher_add_grade,
        name='teacher_add_grade'
    ),

    # DASHBOARD DO ALUNO
    path('student/', views.student_dashboard, name='student_dashboard'),

    #  'sudent' -> 'student' (typo no path) + <int:trimester>/
    path(
        'student/enrollment/<int:enrollment_id>/grades/<int:trimester>/',
        views.student_grades,
        name='student_grades'
    ),
]