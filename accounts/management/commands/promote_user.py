from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

class Command(BaseCommand):
    help = 'Promotes a user to staff status'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the user to promote')

    def handle(self, *args, **options):
        username = options['username']
        try:
            user = User.objects.get(username=username)
            user.is_staff = True
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully promoted user "{username}" to staff status')
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" does not exist')
            ) 