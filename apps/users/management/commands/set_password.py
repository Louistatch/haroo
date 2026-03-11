"""Set password for an existing user by email."""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Set password for a user by email'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str)
        parser.add_argument('password', type=str)

    def handle(self, *args, **options):
        email = options['email'].lower()
        password = options['password']
        try:
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save(update_fields=['password'])
            self.stdout.write(self.style.SUCCESS(
                f'Password set for {email} (id={user.id}, type={user.user_type})'
            ))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {email} not found'))
