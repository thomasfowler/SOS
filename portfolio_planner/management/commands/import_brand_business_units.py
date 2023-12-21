"""Management command to import brand business units from a CSV file."""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from portfolio_planner.models import Brand, BrandBusinessUnit
import csv

User = get_user_model()


class Command(BaseCommand):
    """Imports brand business units from a CSV file."""
    help = 'Imports brand business units from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file containing brand business unit data')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']

        try:
            self.stdout.write(self.style.SUCCESS(f'Importing brand business units from {csv_file_path}'))
            with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                created_count = 0
                updated_count = 0
                for row in reader:
                    brand_name = row['Brand']
                    brand = Brand.objects.get(name=brand_name)

                    user_email = row['Email']
                    user = User.objects.get(email=user_email)

                    # Delete the default business unit if it exists
                    BrandBusinessUnit.objects.filter(brand=brand, name='Default Business Unit').delete()

                    # Create the new BrandBusinessUnit
                    brand_bu, created = BrandBusinessUnit.objects.update_or_create(
                        name=row['Name'],
                        description=row['Description'],
                        status='active',
                        user=user,
                        brand=brand
                    )

                    action = "created" if created else "updated"

                    # Count our actions
                    if action == "created":
                        created_count += 1
                    elif action == "updated":
                        updated_count += 1

                    self.stdout.write(self.style.SUCCESS(f"Successfully {action} business unit '{brand_bu.name}' for brand '{brand.name}'"))

                # Write out summary
                self.stdout.write(self.style.SUCCESS(f"Imported {created_count} business units, updated {updated_count} business units"))
                self.stdout.write(self.style.SUCCESS(f"Total records created/updated: {created_count + updated_count}"))
                self.stdout.write(self.style.SUCCESS(f"Total rows in CSV: {reader.line_num - 1}"))
        except FileNotFoundError:
            raise CommandError(f'File "{csv_file_path}" does not exist')
        except Brand.DoesNotExist:
            raise CommandError(f'Brand with name {brand_name} does not exist')
        except User.DoesNotExist:
            raise CommandError(f'User with email {user_email} does not exist')
        except csv.Error as e:
            raise CommandError(f'CSV error: {e}')
