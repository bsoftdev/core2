# Sistema Acadêmico — Gestão Escolar (Python-Django)

Sistema de gestão escolar sendo desenvolvido em Django, pensado para uma escola única, com áreas dedicadas para Aluno, Professor e Administrador. Cobre o ciclo acadêmico completo: cursos, disciplinas, turmas, matrículas, avaliações , notas por trimestre, chat de comunicação acadêmica, mural da escola(Blog Post) ,  modulo financeiro (Pagamento de propinas),  registo de presencas, etc.
---

## ✨ Funcionalidades atuais

### Área do Administrador (Django Admin)
- Gestão de Cursos, Disciplinas, Anos Letivos e Turmas
- Atribuição de Professores a Disciplinas/Turmas (`TeacherAssignment`)
- Criação de contas de Aluno e Professor (User + perfil, numa única página)
- Geração automática de avaliações académicas por turma/trimestre (ação em massa)
- **Pauta** por disciplina/turma/trimestre, com médias, situação e exportação para PDF (via impressão)
- Publicação/despublicação de pautas em lote

### Área do Professor
- Dashboard com indicadores (nº de disciplinas, turmas, alunos) e gráfico de alunos por turma
- Lista de alunos por turma atribuída
- Lançamento e edição de notas, filtrado por trimestre
- Só pode aceder e lançar notas em disciplinas/turmas onde tem atribuição ativa

### Área do Aluno
- Dashboard com as suas matrículas
- Consulta de notas por disciplina, com seletor de trimestre
- Média ponderada e situação (Aprovado / Recurso / Reprovado / Pendente) calculadas automaticamente

### Estrutura de avaliação
Cada disciplina, em cada trimestre, tem 3 tipos de avaliação com peso fixo:

| Tipo | Nome | Peso |
|------|------|------|
| AC | Avaliação Contínua | 30% |
| NPP | Prova do Professor | 30% |
| NPT | Prova Trimestral | 40% |

A média é aprovada com nota ≥ 10 (escala 0–20), com faixa de recurso entre 5 e 10.

---

## 🛠️ Stack técnica

- **Backend:** Django 6.x
- **Base de dados:** SQLite (desenvolvimento) — preparado para migrar para PostgreSQL em produção
- **Frontend:** Django Templates + Bootstrap 5 + Bootstrap Icons
- **Gráficos:** Chart.js
- **Autenticação:** Sistema de auth nativo do Django, com Grupos (`Professores`, `Estudantes`) para controlo de acesso

---

## 📁 Estrutura do projeto

```
schoolApp/
├── accounts/          # Autenticação, dashboards, User, Student, Teacher
├── academics/          # Curso, Disciplina, Ano Letivo, Turma, Atribuições
├── enrollments/         # Matrículas e cálculo de médias/situação
├── grades/            # Avaliações, notas, pautas
├── templates/          # base.html, base_auth.html, 404.html
└── manage.py
```

---

## 🚀 Instalação

```bash
# 1. Clonar o repositório
git clone <url-do-repositorio>
cd schoolApp

# 2. Criar e ativar ambiente virtual
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Aplicar migrations
python manage.py makemigrations
python manage.py migrate

# 5. Criar superuser (acesso ao /admin/)
python manage.py createsuperuser

# 6. Correr o servidor
python manage.py runserver
```

Depois, em `/admin/`:
1. Cria um **Ano Letivo** e marca-o como ativo
2. Cria um **Curso** e as suas **Disciplinas**
3. Cria uma **Turma**
4. Cria um **Professor** e atribui-o a Disciplina + Turma
5. Cria um **Aluno** e a respetiva **Matrícula**
6. Na página da Turma, corre a ação **"Gerar avaliações"** para o trimestre desejado

---

## ⚙️ Configuração recomendada (`settings.py`)

```python
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

DEBUG = False   # em produção — necessário para a página 404 personalizada funcionar
ALLOWED_HOSTS = ['o-teu-dominio.com']
```

---

## 🗺️ Roadmap — próximos módulos

Ideias e módulos planeados para as próximas fases do projeto:

- [ ] **API REST** (Django REST Framework) — para consumo por app mobile ou frontend separado (React/Vue)
- [ ] **Módulo Financeiro** — propinas, faturas, planos de pagamento, relatório de inadimplência
- [ ] **Módulo de Presenças** — marcação de faltas por aula, relatório de assiduidade
- [ ] **Blog / Mural de Avisos** — comunicados da escola, eventos, notícias, visível a alunos e encarregados
- [ ] **Portal do Encarregado de Educação** — acesso (só leitura) às notas e presenças do educando
- [ ] **Notificações** — email/SMS automático quando uma nota é publicada ou uma pauta é fechada
- [ ] **Integração com IA:**
  - Assistente virtual para dúvidas de alunos (FAQ académico, horários, notas)
  - Deteção precoce de risco de reprovação (análise preditiva sobre médias parciais)
  - Geração automática de relatórios/pareceres pedagógicos a partir dos dados de desempenho
- [ ] **Relatórios e exportações** — boletins em PDF, exportação de pautas/turmas para Excel
- [ ] **Multi-escola (SaaS)** — evolução do modelo de dados para suportar várias escolas na mesma instância (relacionado com o projeto [FlexEdu AI])
- [ ] **App mobile** — consulta de notas e avisos via aplicação nativa ou PWA

---

## 🔒 Notas de segurança

- Professores só acedem/lançam notas em disciplinas e turmas onde têm `TeacherAssignment` ativo — validado a nível de view, não só de UI
- Contas de aluno/professor são criadas via formulário que atribui automaticamente o utilizador ao grupo correto (`Estudantes`/`Professores`), necessário para o redirecionamento de dashboard funcionar
- Cada nota lançada regista o professor responsável (`Grade.launched_by`), para efeitos de auditoria
