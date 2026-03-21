from django.db import models

class Currency(models.Model):
    # e.g. EUR, USD, CHF, GBP
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=20, db_index=True)
    symbol = models.CharField(max_length=10)

    class Meta:
        verbose_name_plural = 'Currencies'
        
    def __str__(self):
        return self.code

class ExchangeRateProvider(models.Model):
    # e.g. CurrencyBeacon, Mock
    name = models.CharField(max_length=100)
    adapter_key = models.CharField(
        max_length=50,
        unique=True,
        help_text="Internal identifier (e.g. currency_beacon)"
    )
    priority = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['priority']

    def __str__(self):
        return f"{self.name} (Key: {self.adapter_key}, Priority: {self.priority}, Active: {self.is_active})"

class CurrencyExchangeRate(models.Model):
    # the historical exchange rate between two currencies on a given date provided by a specific source
    source_currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name='base_rates')
    exchanged_currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name='exchanged_rates')
    valuation_date = models.DateField(db_index=True)
    rate_value = models.DecimalField(db_index=True, max_digits=18, decimal_places=6)
    provider = models.ForeignKey(ExchangeRateProvider, on_delete=models.CASCADE, related_name='rates_provider')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
