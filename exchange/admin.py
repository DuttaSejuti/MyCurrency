from django.contrib import admin
from .models import Currency, ExchangeRateProvider, CurrencyExchangeRate

@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'symbol')
    search_fields = ('code', 'name')

@admin.register(ExchangeRateProvider)
class ExchangeRateProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'adapter_key', 'priority', 'is_active')
    list_editable = ('priority', 'is_active')
    search_fields = ('name', 'adapter_key')
    list_filter = ('is_active',)
    ordering = ('priority',)

@admin.register(CurrencyExchangeRate)
class CurrencyExchangeRateAdmin(admin.ModelAdmin):
    list_display = (
        'source_currency', 'exchanged_currency', 'valuation_date',
        'rate_value', 'provider', 'created_at', 'updated_at'
    )
    list_filter = ('valuation_date', 'provider', 'source_currency', 'exchanged_currency')
    date_hierarchy = 'valuation_date'
    readonly_fields = ('created_at', 'updated_at')
