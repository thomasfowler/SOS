"""Management command to import users from a CSV file."""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group
from portfolio_planner.models import User
import csv


class Command(BaseCommand):
    """Imports users from a CSV file."""
    help = 'Imports users from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file containing user data')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']

        try:
            self.stdout.write(self.style.SUCCESS(f'Importing users from {csv_file_path}'))
            with open(csv_file_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    user = User.objects.create_user(
                        email=row['Email Address'],
                        password=row['Password'],
                        first_name=row['First Name'],
                        last_name=row['Last Name']
                    )

                    # Assign user to group
                    group_name = row['Role']
                    group = Group.objects.get(name=group_name)
                    user.groups.add(group)

                    self.stdout.write(self.style.SUCCESS(f'Successfully created user {user.email}'))
        except FileNotFoundError:
            raise CommandError(f'File "{csv_file_path}" does not exist')
