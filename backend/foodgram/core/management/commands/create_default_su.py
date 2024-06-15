import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


def_su_name = os.getenv('DEFAULT_SU_NAME')
def_su_mail = os.getenv('DEFAULT_SU_MAIL')
def_su_password = os.getenv('DEFAULT_SU_PASSWORD')


class Command(BaseCommand):
    def handle(self, *args, **options):
        if not User.objects.filter(username=def_su_name).exists():
            User.objects.create_superuser(
                def_su_name,
                def_su_mail,
                def_su_password
            )

            self.stdout.write(self.style.SUCCESS(
                'Superuser created successfully!'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                'Superuser already exists. Skipping creation.'
            ))
