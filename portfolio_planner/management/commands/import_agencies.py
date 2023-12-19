"""Management command to import agencies from a CSV file."""
from django.core.management.base import BaseCommand, CommandError
from portfolio_planner.models import Agency, MediaGroup
import csv


class Command(BaseCommand):
    """Imports agencies from a CSV file."""
    help = 'Imports agencies from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file containing agency data')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']

        try:
            self.stdout.write(self.style.SUCCESS(f'Importing agencies from {csv_file_path}'))
            with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Find or create the media group
                    media_group_name = row['Media Group']
                    media_group = MediaGroup.objects.get(
                        name=media_group_name) if media_group_name else (None, False)

                    # Update or create the Agency
                    agency, created = Agency.objects.update_or_create(
                        name=row['Name'],
                        defaults={
                            'description': row['Description'] or '',
                            'media_group': media_group
                        }
                    )

                    action = "created" if created else "updated"
                    self.stdout.write(self.style.SUCCESS(f"Successfully {action} agency '{row['Name']}'"))
        except FileNotFoundError:
            raise CommandError(f'File "{csv_file_path}" does not exist')
        except csv.Error as e:
            raise CommandError(f'CSV error: {e}')
