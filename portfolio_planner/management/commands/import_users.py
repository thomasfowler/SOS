"""Management command to import users from a CSV file."""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group
from django.db import IntegrityError, transaction
from portfolio_planner.models import User
import csv

class Command(BaseCommand):
    """Imports users from a CSV file."""
    help = 'Imports users from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file containing user data')

    @transaction.atomic
    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']

        try:
            self.stdout.write(self.style.SUCCESS(f'Importing users from {csv_file_path}'))
            with open(csv_file_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        # Update or create the user based on email
                        user, created = User.objects.update_or_create(
                            email=row['Email Address'],
                            defaults={
                                'first_name': row['First Name'],
                                'last_name': row['Last Name'],
                                # Don't set password here; handle it after user creation/update
                            }
                        )

                        # Set password securely
                        if created:
                            user.set_password(row['Password'])
                            user.save()

                        # Assign user to group
                        group_name = row['Role']
                        try:
                            group = Group.objects.get(name=group_name)
                            user.groups.add(group)
                        except Group.DoesNotExist:
                            self.stdout.write(self.style.ERROR(f'Group {group_name} does not exist'))

                        action = "created" if created else "updated"
                        self.stdout.write(self.style.SUCCESS(f'Successfully {action} user {user.email}'))

                    except IntegrityError as e:
                        self.stdout.write(self.style.ERROR(f'Error importing user {row["Email Address"]}: {e}'))
                        continue

        except FileNotFoundError:
            raise CommandError(f'File "{csv_file_path}" does not exist')
