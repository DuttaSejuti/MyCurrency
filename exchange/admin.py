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
    change_list_template = "admin/exchange_rates_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('currency_converter/', self.admin_site.admin_view(self.convert_view), name='backoffice_convert'),
        ]
        return custom_urls + urls

    def convert_view(self, request):
        currencies = Currency.objects.all()
        results = []
        source_curr = None
        amount = Decimal("1.00")
        
        if request.method == "POST":
            from_id = request.POST.get("from_currency")
            to_ids = request.POST.getlist("to_currencies")
            amount_val = request.POST.get("amount", "1")
            
            try:
                source_curr = Currency.objects.get(id=from_id)
                amount = Decimal(amount_val)
                
                for to_id in to_ids:
                    target_curr = Currency.objects.get(id=to_id)
                    # Use our adapter-based service!
                    rate_obj = get_exchange_rate_data(source_curr, target_curr, datetime.date.today())
                    
                    results.append({
                        "to": target_curr.code,
                        "rate": rate_obj.rate_value,
                        "provider": rate_obj.provider.name,
                        "converted": amount * rate_obj.rate_value,
                    })
            except Exception as e:
                messages.error(request, f"Conversion failed: {str(e)}")

        context = {
            **self.admin_site.each_context(request),
            "title": "Backoffice Multi-Converter",
            "currencies": currencies,
            "results": results,
            "source": source_curr,
            "amount": amount,
            "opts": self.model._meta,
        }
        return render(request, "admin/currency_converter.html", context)
