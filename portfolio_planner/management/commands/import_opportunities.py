"""Management command to import opportunities from a CSV file."""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from portfolio_planner.models import Opportunity, Brand, BrandBusinessUnit, Product, FiscalYear
import csv
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Imports opportunities from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file containing opportunity data')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']

        try:
            self.stdout.write(self.style.SUCCESS(f'Importing opportunities from {csv_file_path}'))
            with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                created_count = 0
                updated_count = 0
                skipped_count = 0
                for row in reader:
                    # Check if we have a skip instruction
                    if row['Skip'] == 'True':
                        skipped_count += 1
                        self.stdout.write(self.style.WARNING(f"Skipping opportunity with ID '{row['ID']}' - Brand: {row['Brand']})"))
                        continue
                    brand = Brand.objects.get(name=row['Brand'])
                    business_unit_name = row['Brand Business Unit']
                    business_unit = BrandBusinessUnit.objects.get(name=business_unit_name, brand=brand) if business_unit_name else None
                    product = Product.objects.get(name=row['Product'])
                    fiscal_year = FiscalYear.objects.get(year=int(row['Fiscal Year']))
                    approval_user_email = row['Approval User']
                    approval_user = User.objects.get(email=approval_user_email) if approval_user_email else None

                    target_value = Decimal(row['Target Value'].replace(',', ''))
                    approved = row['Approved']

                    opportunity, created = Opportunity.objects.update_or_create(
                        id=row['ID'],
                        defaults={
                            'description': row['Description'],
                            'brand': brand,
                            'business_unit': business_unit,
                            'product': product,
                            'target': target_value,
                            'fiscal_year': fiscal_year,
                            'approved': approved,
                            'approval_user': approval_user,
                            'status': 'active'
                        }
                    )

                    action = "created" if created else "updated"

                    # Count our actions
                    if action == "created":
                        created_count += 1
                    elif action == "updated":
                        updated_count += 1

                    self.stdout.write(self.style.SUCCESS(f"Successfully {action} opportunity with ID '{row['ID']}'"))

                # Write out summary
                self.stdout.write(self.style.SUCCESS(f"Successfully created {created_count} opportunities and updated {updated_count} opportunities"))
                self.stdout.write(self.style.SUCCESS(f"Total records created/updated: {created_count + updated_count}"))
                self.stdout.write(self.style.SUCCESS(f"Total records skipped: {skipped_count}"))
                self.stdout.write(self.style.SUCCESS(f"Total rows in CSV: {reader.line_num - 1}"))
        except FileNotFoundError:
            raise CommandError(f'File "{csv_file_path}" does not exist')
        except Brand.DoesNotExist:
            raise CommandError(f"Brand {row['Brand']} not found")
        except BrandBusinessUnit.DoesNotExist:
            raise CommandError(f"Brand Business Unit {row['Brand Business Unit']} not found")
        except Product.DoesNotExist:
            raise CommandError(f"Product {row['Product']} not found")
        except FiscalYear.DoesNotExist:
            raise CommandError(f"Fiscal Year {row['Fiscal Year']} not found")
        except User.DoesNotExist:
            raise CommandError(f"Approval User {row['Approval User']} not found")
        except csv.Error as e:
            raise CommandError(f'CSV error: {e}')
