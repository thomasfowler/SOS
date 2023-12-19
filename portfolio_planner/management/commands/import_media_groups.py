"""Management command to import media groups from a CSV file."""
from django.core.management.base import BaseCommand, CommandError
from portfolio_planner.models import MediaGroup
import csv


class Command(BaseCommand):
    """Imports users from a CSV file."""
    help = 'Imports media groups from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file containing media group data')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']

        try:
            self.stdout.write(self.style.SUCCESS(f'Importing media groups from {csv_file_path}'))
            with open(csv_file_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    media_group = MediaGroup.objects.create(
                        name=row['Name'],
                        description=row['Description']
                    )

                    self.stdout.write(self.style.SUCCESS(f'Successfully created media group {media_group.name}'))
        except FileNotFoundError:
            raise CommandError(f'File "{csv_file_path}" does not exist')