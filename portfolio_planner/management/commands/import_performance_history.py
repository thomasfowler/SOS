"""Management command to import opportunity performance data from a CSV file"""
from django.core.management.base import BaseCommand, CommandError
from portfolio_planner.models import OpportunityPerformance, Opportunity, FiscalYear, PeriodPerformance
from django.core.exceptions import ValidationError
import csv
from decimal import Decimal


class Command(BaseCommand):
    help = 'Imports opportunity performance data from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file containing opportunity performance data')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']

        try:
            self.stdout.write(self.style.SUCCESS(f'Importing opportunity performance data from {csv_file_path}'))
            with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                created_count = 0
                updated_count = 0
                skipped_count = 0

                for row in reader:
                    opportunity_id = row['Opportunity']
                    fiscal_year_int = row['Fiscal year']

                    try:
                        opportunity = Opportunity.objects.get(id=opportunity_id)
                        fiscal_year = FiscalYear.objects.get(year=fiscal_year_int)

                        # Create or update OpportunityPerformance
                        opp_perf, created = OpportunityPerformance.objects.update_or_create(
                            opportunity=opportunity,
                            fiscal_year=fiscal_year
                            # Add other fields and defaults if necessary
                        )

                        for period_num in range(1, 13):  # There are 12 periods in a fiscal year
                            revenue = row.get(f'Period {period_num}', '0').replace(',', '')
                            if revenue:
                                revenue = Decimal(revenue)
                                PeriodPerformance.objects.update_or_create(
                                    opportunity_performance=opp_perf,
                                    period=period_num,
                                    fiscal_year=fiscal_year,
                                    defaults={'revenue': revenue}
                                )

                        action = "created" if created else "updated"
                        if action == "created":
                            created_count += 1
                        else:
                            updated_count += 1

                        self.stdout.write(self.style.SUCCESS(f"Successfully {action} opportunity performance with Opportunity ID '{opportunity_id}'"))

                    except Opportunity.DoesNotExist:
                        skipped_count += 1
                        self.stdout.write(self.style.WARNING(f"Skipping: Opportunity with ID '{opportunity_id}' not found"))

                self.stdout.write(self.style.SUCCESS(f"Summary: Created {created_count}, Updated {updated_count}, Skipped {skipped_count}"))
        except FileNotFoundError:
            raise CommandError(f'File "{csv_file_path}" does not exist')
        except FiscalYear.DoesNotExist:
            raise CommandError(f"Fiscal Year {row['Fiscal year']} not found")
        except ValidationError as e:
            raise CommandError(f'Validation error: {e}')
        except csv.Error as e:
            raise CommandError(f'CSV error: {e}')
