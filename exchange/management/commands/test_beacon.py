from django.core.management.base import BaseCommand
import datetime
from exchange.models import Currency, ExchangeRateProvider
from exchange.services import get_exchange_rate_data

class Command(BaseCommand):
    help = "Test CurrencyBeaconProvider via the service"

    def handle(self, *args, **kwargs):
        usd = Currency.objects.get(code="USD")
        eur = Currency.objects.get(code="EUR")
        provider = ExchangeRateProvider.objects.get(adapter_key="currency_beacon")

        rate = get_exchange_rate_data(usd, eur, datetime.date.today(), provider)
        self.stdout.write(f"USD -> EUR rate: {rate}")
