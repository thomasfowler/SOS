"""Imports business units from a CSV file"""
from django.core.management.base import BaseCommand, CommandError
from portfolio_planner.models import OrgBusinessUnit
from django.contrib.auth import get_user_model
import csv

User = get_user_model()


class Command(BaseCommand):
    """Imports business units from a CSV file"""
    help = 'Imports business units from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file containing business unit data')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']

        try:
            self.stdout.write(self.style.SUCCESS(f'Importing business units from {csv_file_path}'))
            with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Find or create the business unit manager user
                    email = row['Manager']
                    manager = User.objects.get(
                        email=email
                    )

                    # Create the OrgBusinessUnit
                    OrgBusinessUnit.objects.create(
                        name=row['Name'],
                        status='active',  # Assuming default status is 'active'
                        business_unit_manager=manager
                    )

                    self.stdout.write(self.style.SUCCESS(f"Successfully created business unit '{row['Name']}'"))
        except FileNotFoundError:
            raise CommandError(f'File "{csv_file_path}" does not exist')
        except csv.Error as e:
            raise CommandError(f'CSV error: {e}')
