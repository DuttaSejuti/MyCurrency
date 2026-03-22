import datetime
import logging
from decimal import Decimal
from typing import Optional
from .models import Currency, ExchangeRateProvider, CurrencyExchangeRate
from .providers.manager import ProviderManager

logger = logging.getLogger(__name__)

def _get_cached_rate(
    source: Currency, 
    target: Currency, 
    date: datetime.date, 
    provider: Optional[ExchangeRateProvider] = None
) -> Optional[CurrencyExchangeRate]:
    # Checks if the rate is already in the database
    query = CurrencyExchangeRate.objects.filter(
        source_currency=source,
        exchanged_currency=target,
        valuation_date=date
    )
    if provider:
        query = query.filter(provider=provider)
    
    return query.first()

def _get_active_providers_sorted(
    specific_provider: Optional[ExchangeRateProvider] = None
) -> list[ExchangeRateProvider]:
    # determine which providers to use in terms of priority and active status
    # if a specific provider is provided, use it, else use active providers sorted by priority
    if specific_provider:
        return [specific_provider]
    return list(ExchangeRateProvider.objects.filter(is_active=True).order_by('priority'))

def _try_fetch_from_providers(
    source: Currency, 
    target: Currency, 
    date: datetime.date, 
    providers: list[ExchangeRateProvider]
) -> tuple[Decimal, ExchangeRateProvider]:
    # Fetch the rate from providers, using fallback if a providcer fails
    last_error = None
    for prov in providers:
        try:
            adapter = ProviderManager.get_adapter(prov.adapter_key)
            rate_value = adapter.get_exchange_rate(
                source_currency=source.code,
                exchanged_currency=target.code,
                valuation_date=date
            )
            return rate_value, prov
            
        except Exception as e:
            logger.warning(f"Provider {prov.name} failed: {str(e)}. Falling back...")
            last_error = e
            continue

    raise RuntimeError(
        f"All providers failed for {source.code}/{target.code} on {date}. "
        f"Last error: {str(last_error)}"
    )

def get_exchange_rate_data(
    source_currency: Currency, 
    exchanged_currency: Currency, 
    valuation_date: datetime.date, 
    provider: Optional[ExchangeRateProvider] = None
) -> CurrencyExchangeRate:
    # save fetched rate to the database and provider fallback orchestration

    # 1. Check database cache
    cached_obj = _get_cached_rate(source_currency, exchanged_currency, valuation_date, provider)
    if cached_obj:
        return cached_obj

    # 2. get the list of providers to try
    providers_to_try = _get_active_providers_sorted(provider)
    if not providers_to_try:
        raise ValueError("No active exchange rate providers found.")

    # 3. fallback to the providers
    rate_value, provider_used = _try_fetch_from_providers(
        source_currency, exchanged_currency, valuation_date, providers_to_try
    )

    # 4. Save to DB
    return CurrencyExchangeRate.objects.create(
        source_currency=source_currency,
        exchanged_currency=exchanged_currency,
        valuation_date=valuation_date,
        rate_value=rate_value,
        provider=provider_used
    )
