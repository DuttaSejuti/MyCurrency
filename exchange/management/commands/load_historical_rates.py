from django.core.management.base import BaseCommand
from exchange.async_tasks import run_load_historical_rates

# python manage.py load_historical_rates 2026-02-10 2026-02-12 (YYYY-MM-DD)
class Command(BaseCommand):
    help = "Load historical currency exchange rates"

    def add_arguments(self, parser):
        parser.add_argument('start_date', type=str)
        parser.add_argument('end_date', type=str)

    def handle(self, *args, **options):
        run_load_historical_rates(options['start_date'], options['end_date'])
