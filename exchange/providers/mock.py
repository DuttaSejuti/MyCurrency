import datetime
from decimal import Decimal
from .base import BaseProvider

class MockProvider(BaseProvider):
    def get_exchange_rate(
        self, 
        source_currency: str, 
        exchanged_currency: str, 
        valuation_date: datetime.date
    ) -> Decimal:
        if source_currency == exchanged_currency:
            return Decimal('1.000000')
        # Ex:(length of currency codes + day of month) / 10
        day_factor = valuation_date.day
        rate = (len(source_currency) + len(exchanged_currency) + day_factor) / 10

        return Decimal(str(rate)).quantize(Decimal('0.000001'))
