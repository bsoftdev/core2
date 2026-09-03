from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


#CLASS PARA CRIA GROUPO NO DJANGO ADMIN, MAS PODE SER FEITO MANUALMENTE
class Command(BaseCommand):

    help = "Cria os grupos padrao do sistema"

    def handle(self, *args, **kwarges):
        groupos = [
            'Administradores',
            'Professores',
            'Estudantes',
        ]

        for nameGroup in groupos:
            group, created = Group.objects.get_or_create(
                name = nameGroup
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Grupo criado {group}'
                    )
                )
            else:
                self.stdout.write(
                        self.style.SUCCESS(
                            f'Grupo ja existe {group}'
                        )
                    )
        self.stdout.write(
                    self.style.SUCCESS(
                        'Grupos configurados com sucesso'
                    )
                )