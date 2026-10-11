import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create a Django superuser using environment variables."

    def handle(self, *args, **options):
        username = os.environ.get("LIVE_ADMIN_USERNAME")
        password = os.environ.get("LIVE_ADMIN_PASSWORD")
        email = os.environ.get("LIVE_ADMIN_EMAIL", "")

        if not username or not password:
            raise CommandError(
                "Set LIVE_ADMIN_USERNAME and LIVE_ADMIN_PASSWORD first."
            )

        User = get_user_model()

        if User.objects.filter(username=username).exists():
            raise CommandError(
                "That username already exists. Choose a different username."
            )

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )

        self.stdout.write(
            self.style.SUCCESS("Superuser created successfully.")
        )
