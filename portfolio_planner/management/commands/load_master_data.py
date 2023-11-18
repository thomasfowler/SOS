"""Loads Test Data from Fixtures."""
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Loads Master Data from Fixtures.

    Provides minimal data for running the Portfolio Planner.
    """

    help = 'Loads minimum config data from fixtures and synchronise roles to groups.'

    def handle(self, *args, **kwargs):
        """Load Test Data from Fixtures."""
        fixture_files = [
            'portfolio_planner/fixtures/master_data/org_business_unit.json',
            'portfolio_planner/fixtures/master_data/fiscal_year.json',
            'portfolio_planner/fixtures/master_data/media_group.json',
            'portfolio_planner/fixtures/master_data/product.json',
            'portfolio_planner/fixtures/master_data/agency.json',
        ]

        print('Synchronising roles to groups')
        call_command('sync_roles')

        for fixture_file in fixture_files:
            print(f'Loading master data from {fixture_file}')  # noqa: T201
            call_command('loaddata', fixture_file)
