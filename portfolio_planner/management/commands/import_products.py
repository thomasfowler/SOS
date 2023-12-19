"""Management command to import products from a CSV file."""
from django.core.management.base import BaseCommand, CommandError
from portfolio_planner.models import Product
import csv


class Command(BaseCommand):
    """Imports products from a CSV file."""
    help = 'Imports media groups from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file containing product data')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']

        try:
            self.stdout.write(self.style.SUCCESS(f'Importing media groups from {csv_file_path}'))
            with open(csv_file_path, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    product = Product.objects.create(
                        name=row['Name'],
                        description=row['Description']
                    )

                    self.stdout.write(self.style.SUCCESS(f'Successfully created product {product.name}'))
        except FileNotFoundError:
            raise CommandError(f'File "{csv_file_path}" does not exist')
