from django.contrib.auth.decorators import user_passes_test

# FUNÇÕES AUXILIARES PARA IDENTIFICAR PERFIS NA HORA DE AUTENTICAR

def is_admin(user):
    return user.is_superuser


def is_teacher(user):
    return user.groups.filter(name='Professores').exists()


def is_student(user):
    return user.groups.filter(name='Estudantes').exists()


# DECORATORES = PROTEGER AS NOSSAS VIEWS

def teacher_required(view_func):
    return user_passes_test(is_teacher, login_url='login')(view_func)


def student_required(view_func):
    return user_passes_test(is_student, login_url='login')(view_func)


def admin_required(view_func):
    return user_passes_test(is_admin, login_url='login')(view_func)


# CORREÇÃO: estavam comentadas e usavam 'user.teacher' (não existe).
# Reativei-as com o related_name correto ('teacher_profile') — evitam
# repetir a mesma query em várias views e centralizam a regra de
# "o professor só acede às suas próprias atribuições", que é a base
# da segurança de todo o módulo de notas.

def get_teacher_assignments(user):
    return user.teacher_profile.teacherassignments.select_related('subject', 'group')


def teacher_has_access_to(user, subject, group):
    if not is_teacher(user):
        return False
    return user.teacher_profile.teacherassignments.filter(
        subject=subject, group=group, is_active=True
    ).exists()