
from django.contrib.auth.decorators import user_passes_test 

#FUNCOES AUXILIARES PARA IDENTIFICAR PERFIS NA HORA DE AUTENTICAR

def is_admin(user):
    return user.is_superuser

def is_teacher(user):
    return user.groups.filter(name='Professores').exists()

def is_student(user):
    return user.groups.filter(name='Estudantes').exists()


#DECORATORES = CRIANDO FUNCOES PARA PROTEJER AS NOSSAS VIEWS
def teacher_required(view_func):
    return user_passes_test(is_teacher,login_url='login')(view_func)

def student_required(view_func):
    return user_passes_test(is_student, login_url='login')(view_func)

def admin_required(view_func):
    return user_passes_test(is_admin, login_url='login')(view_func)


#FUNCAO PARA PEGAR AS ATRIBUICOES DO PROFESSOR
#def get_teacher_assignments(user):
 #   return user.teacher.teacherassignments.select_related(
  #      'subject',
   #     'group'
    #)



#FUNCAOPARA PROTEJER AS ATRIBUICOES

#FUNCAO PARA VERIFICAR A ATRIBUICAO, O PROF NAO PODE ACESSAR TURMAS NEM DISCIPLINAS FORA DA SUA TURMA
#def teacher_has_access_to(user,subject, group):

 #   if not is_teacher(user):
  #      return False

   # return user.teacher.teacherassignments.filter(
    #    subject = subject,
     #   group = group
    #)


