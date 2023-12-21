"""Management command to import brands from a CSV file"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from portfolio_planner.models import Brand, Agency, OrgBusinessUnit
import csv

User = get_user_model()


class Command(BaseCommand):
    help = 'Imports brands from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file containing brand data')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']

        try:
            self.stdout.write(self.style.SUCCESS(f'Importing brands from {csv_file_path}'))
            with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    user_email = row['Email']
                    user = User.objects.get(email=user_email)

                    agency_name = row['Agency']
                    agency = Agency.objects.get(name=agency_name) if agency_name else None

                    org_business_unit_name = row['Org BU']
                    org_business_unit = OrgBusinessUnit.objects.get(name=org_business_unit_name)

                    brand, created = Brand.objects.update_or_create(
                        name=row['Name'],
                        defaults={
                            'description': row['Description'],
                            'client_code': row['Client Code'],
                            'status': 'active',
                            'user': user,
                            'agency': agency,
                            'org_business_unit': org_business_unit,
                        }
                    )

                    action = "created" if created else "updated"
                    self.stdout.write(self.style.SUCCESS(f"Successfully {action} brand '{brand.name}'"))
        except FileNotFoundError:
            raise CommandError(f'File "{csv_file_path}" does not exist')
        except User.DoesNotExist:
            raise CommandError(f'User with email {user_email} does not exist')
        except Agency.DoesNotExist:
            raise CommandError(f'Agency with name {agency_name} does not exist')
        except OrgBusinessUnit.DoesNotExist:
            raise CommandError(f'Organisation Business Unit with name {org_business_unit_name} does not exist')
        except csv.Error as e:
            raise CommandError(f'CSV error: {e}')
