from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import traceback

class Command(BaseCommand):
    help = 'Create default superuser if it does not exist'

    def handle(self, *args, **options):
        try:
            User = get_user_model()
            email = 'admin@oldmoneyalgeria.dz'
            username = 'admin'
            password = 'Password123!'

            if not User.objects.filter(email=email).exists():
                User.objects.create_superuser(username=username, email=email, password=password)
                self.stdout.write(self.style.SUCCESS('Admin created'))
            else:
                self.stdout.write(self.style.WARNING('Admin already exists'))
        except Exception as e:
            # We catch all exceptions so the build command never fails
            self.stderr.write(self.style.ERROR(f'Failed to create admin: {e}'))
            traceback.print_exc()
