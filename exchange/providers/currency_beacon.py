import datetime
import requests
from decimal import Decimal
from django.conf import settings
from .base import BaseProvider

class CurrencyBeaconProvider(BaseProvider):
    BASE_URL = "https://api.currencybeacon.com/v1/historical"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or getattr(settings, "CURRENCY_BEACON_API_KEY", "")

    def get_exchange_rate(
        self, 
        source_currency: str, 
        exchanged_currency: str, 
        valuation_date: datetime.date
    ) -> Decimal:
        if not self.api_key:
            raise ValueError("CurrencyBeacon API Key is missing. Please configure CURRENCY_BEACON_API_KEY.")

        params = {
            'api_key': self.api_key,
            'base': source_currency,
            'date': valuation_date.strftime('%Y-%m-%d'),
            'symbols': exchanged_currency
        }

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            response_coe = data.get('meta', {}).get('code', {})
            if response_coe != 200:
                raise ValueError(f"CurrencyBeacon API error: {response_coe}")
            
            rates = data.get('response', {}).get('rates', {})
            rate = rates.get(exchanged_currency)
            
            if rate is None:
                raise ValueError(f"Rate for {exchanged_currency} not found in CurrencyBeacon response.")
                
            return Decimal(str(rate))
            
        except requests.RequestException as e:
            raise RuntimeError(f"CurrencyBeacon API error: {str(e)}")
