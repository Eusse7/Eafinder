import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Crea el administrador inicial desde variables DJANGO_SUPERUSER_*."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "").strip()
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "").strip()

        if not username and not password:
            self.stdout.write("No se configuró el administrador inicial; no se creó ningún usuario.")
            return
        if not username or not password:
            raise CommandError(
                "Configura DJANGO_SUPERUSER_USERNAME y DJANGO_SUPERUSER_PASSWORD juntos."
            )

        user_model = get_user_model()
        existing_user = user_model.objects.filter(username=username).first()
        if existing_user:
            if not existing_user.is_staff or not existing_user.is_superuser:
                raise CommandError(
                    f"El usuario '{username}' existe, pero no es administrador."
                )
            existing_user.email = email
            existing_user.set_password(password)
            existing_user.save(update_fields=["email", "password"])
            self.stdout.write(
                f"Credenciales del administrador '{username}' actualizadas desde el entorno."
            )
            return

        user_model.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        self.stdout.write(self.style.SUCCESS(f"Administrador inicial '{username}' creado."))
