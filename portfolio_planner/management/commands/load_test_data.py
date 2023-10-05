"""Loads Test Data from Fixtures."""
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Loads Test Data from Fixtures."""

    help = 'Loads test data from fixtures'

    def handle(self, *args, **kwargs):
        """Load Test Data from Fixtures."""
        fixture_files = [
        ]

        for fixture_file in fixture_files:
            print(f'Loading test data from {fixture_file}')  # noqa: T201
            call_command('loaddata', fixture_file)


