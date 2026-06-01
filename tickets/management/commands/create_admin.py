import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Crea el superusuario desde variables de entorno (para Railway)"

    def handle(self, *args, **kwargs):
        User = get_user_model()
        username = os.environ.get("ADMIN_USERNAME", "admin")
        email    = os.environ.get("ADMIN_EMAIL", "admin@example.com")
        password = os.environ.get("ADMIN_PASSWORD", "")

        if not password:
            self.stdout.write(self.style.WARNING(
                "ADMIN_PASSWORD no definido — se omite la creación del superusuario."
            ))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(f"  · Superusuario '{username}' ya existe.")
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"  ✓ Superusuario '{username}' creado."))
