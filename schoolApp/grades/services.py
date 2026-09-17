from academics.models import Subject
from .models import Evaluation, AcademicEvaluation


EVALUATION_CONFIG = {
    'AC': {
        'name': 'Avaliação Contínua',
        'weight': 30.00,
    },
    'NPP': {
        'name': 'Prova do Professor',
        'weight': 30.00,
    },
    'NPT': {
        'name': 'Prova Trimestral',
        'weight': 40.00,
    },
}


def create_default_evaluations():
    """
    Cria os três tipos globais de avaliação.
    Se já existirem, não cria duplicados.
    """

    created = 0
    existing = 0

    for evaluation_type, config in EVALUATION_CONFIG.items():
        evaluation, was_created = Evaluation.objects.get_or_create(
            type=evaluation_type,
            defaults={
                'name': config['name'],
                'gradeWeight': config['weight'],
                'is_active': True,
            }
        )

        if was_created:
            created += 1
        else:
            existing += 1

    return created, existing


def generate_evaluations_for_group(group, trimester):
    """
    Cria as avaliações académicas de uma turma
    para um determinado trimestre.
    """

    # Garante que AC, NPP e NPT existem
    create_default_evaluations()

    evaluations = Evaluation.objects.filter(
        type__in=['AC', 'NPP', 'NPT'],
        is_active=True
    )

    subjects = Subject.objects.filter(
        course=group.course,
        course_year=group.course_year,
        is_active=True
    )

    created = 0
    existing = 0

    for subject in subjects:
        for evaluation in evaluations:

            academic_evaluation, was_created = (
                AcademicEvaluation.objects.get_or_create(
                    evaluation=evaluation,
                    subject=subject,
                    group=group,
                    trimester=trimester,
                    defaults={
                        'is_active': True,
                    }
                )
            )

            if was_created:
                created += 1
            else:
                existing += 1

    return created, existing