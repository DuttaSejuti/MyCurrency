from django.db import models

class Currency(models.Model):
    # e.g. EUR, USD, CHF, GBP
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=50, blank=True)
        
    def __str__(self):
        return self.code

class ExchangeRateProvider(models.Model):
    # e.g. CurrencyBeacon, Mock
    name = models.CharField(max_length=100)
    adapter_key = models.CharField(max_length=50, unique=True, help_text="Internal identifier (e.g. currency_beacon")
    priority = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['priority']

    def __str__(self):
        return f"{self.name} (Key: {self.adapter_key}, Priority: {self.priority}, Active: {self.is_active})"

class CurrencyExchangeRate(models.Model):
    # the historical exchange rate between two currencies on a given date provided by a specific source
    source_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='rates_as_source')
    exchanged_currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='rates_as_exchanged')
    valuation_date = models.DateField(db_index=True)
    rate_value = models.DecimalField(max_digits=9, decimal_places=4)
    provider = models.ForeignKey(ExchangeRateProvider, on_delete=models.CASCADE, related_name='rates_provider')

    class Meta:
        indexes = [models.Index(fields=['source_currency', 'exchanged_currency', 'valuation_date'])]
        constraints = [
            models.UniqueConstraint(
                fields=['source_currency', 'exchanged_currency', 'valuation_date', 'provider'],
                name='unique_exchange_rate'
            )
        ]

    def __str__(self):
        return f"1 {self.source_currency.code} = {self.rate_value} {self.exchanged_currency.code} on {self.valuation_date} via {self.provider.name}"
