from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.contrib import messages
from .models import Currency, ExchangeRateProvider, CurrencyExchangeRate
from .services import get_exchange_rate_data
from decimal import Decimal
import datetime

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

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('currency_converter/', self.admin_site.admin_view(self.convert_view), name='backoffice_convert'),
        ]
        return custom_urls + urls

    def convert_view(self, request):
        currencies = Currency.objects.all()
        result = None
        
        if request.method == "POST":
            from_id = request.POST.get("from_currency")
            to_id = request.POST.get("to_currency")
            amount_val = request.POST.get("amount", "1")
            
            try:
                from_curr = Currency.objects.get(id=from_id)
                to_curr = Currency.objects.get(id=to_id)
                amount = Decimal(amount_val)
                
                # Use our adapter-based service!
                rate_obj = get_exchange_rate_data(from_curr, to_curr, datetime.date.today())
                
                result = {
                    "from": from_curr.code,
                    "to": to_curr.code,
                    "amount": amount,
                    "rate": rate_obj.rate_value,
                    "provider": rate_obj.provider.name,
                    "converted": amount * rate_obj.rate_value,
                }
            except Exception as e:
                messages.error(request, f"Conversion failed: {str(e)}")

        context = {
            **self.admin_site.each_context(request),
            "title": "Backoffice Converter",
            "currencies": currencies,
            "result": result,
            "opts": self.model._meta,
        }
        return render(request, "admin/currency_converter.html", context)
