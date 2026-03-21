from abc import ABC, abstractmethod
import datetime
from decimal import Decimal

class BaseProvider(ABC):
    @abstractmethod
    def get_exchange_rate(
        self, 
        source_currency: str, 
        exchanged_currency: str, 
        valuation_date: datetime.date
    ) -> Decimal:
        # rate = provider.get_exchange_rate('EUR', 'USD', datetime.date(2026, 3, 21))
        pass
