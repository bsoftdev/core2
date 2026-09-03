from django.urls import path
from . import views  

from django.urls import path
from . import views

urlpatterns = [
    path(
        'login/',
        views.login_view,
        name='login'
    ),

    path(
        'logout/',
        views.logout_view,
        name='logout'
    ),

    path(
        'dashboard/',
        views.dashboard,
        name='dashboard'
    ),

    path(
        'teacher/',
        views.teacher_dashboard,
        name='teacher_dashboard'
    ),

    path(
        'teacher/assignment/<int:assignment_id>/students/',
        views.teacher_students,
        name='teacher_students'
    ),

    path(
        'teacher/assignment/<int:assignment_id>/student/<int:student_id>/grades/',
        views.teacher_student_grades,
        name='teacher_student_grades'
    ),

    path(
        'student/',
        views.student_dashboard,
        name='student_dashboard'
    ),
]