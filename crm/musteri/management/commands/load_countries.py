from django.core.management.base import BaseCommand
from musteri.models import Country
import pandas as pd
class Command(BaseCommand):
    help = 'Load country data from Excel file into Database'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='The path to the Excel file.')

    def handle(self, *args, **options):
        excel_file = options['excel_file']

        # Read the Excel file
        df = pd.read_excel(excel_file)

        # Iterate over the rows of the DataFrame
        for index, row in df.iterrows():
            # Create a new Country object for each row and save it to the database
            Country.objects.create(
                name=row['name'],
                fee_first_year=row['fee_first_year'],
                fee_next_year=row['fee_next_year']
            )

        self.stdout.write(self.style.SUCCESS('Successfully loaded country data!'))