import asyncio
import datetime
from decimal import Decimal
import logging

from asgiref.sync import sync_to_async
from .models import Currency, ExchangeRateProvider, CurrencyExchangeRate
from .providers.manager import ProviderManager

logger = logging.getLogger(__name__)

async def fetch_and_store_rate(source, target, date, provider):
    """
    Fetch a single exchange rate from a provider and store it in the DB.
    """
    # Pre-check to avoid unnecessary API calls and UniqueConstraint errors
    exists = await sync_to_async(
        CurrencyExchangeRate.objects.filter(
            source_currency=source,
            exchanged_currency=target,
            valuation_date=date,
            provider=provider
        ).exists
    )()
    
    if exists:
        return

    try:
        adapter = ProviderManager.get_adapter(provider.adapter_key)

        # Use async method if provider supports it, else fallback to sync
        if hasattr(adapter, 'async_get_exchange_rate'):
            rate_value = await adapter.async_get_exchange_rate(
                source_currency=source.code,
                exchanged_currency=target.code,
                valuation_date=date
            )
        else:
            # Run sync get_exchange_rate in executor
            loop = asyncio.get_running_loop()
            rate_value = await loop.run_in_executor(
                None,
                adapter.get_exchange_rate,
                source.code,
                target.code,
                date
            )

        # Save to DB (run sync ORM in thread)
        await sync_to_async(CurrencyExchangeRate.objects.create)(
            source_currency=source,
            exchanged_currency=target,
            valuation_date=date,
            rate_value=rate_value,
            provider=provider
        )
        logger.info(f"Stored {source.code}/{target.code} on {date} from {provider.name}")

    except Exception as e:
        logger.warning(f"Provider {provider.name} failed for {source.code}/{target.code} on {date}: {e}")

async def load_historical_rates(start_date: datetime.date, end_date: datetime.date):
    """
    Load historical rates for all currencies and active providers asynchronously.
    """
    # Load currencies from DB safely in async context
    currencies = await sync_to_async(list)(Currency.objects.all())
    providers = await sync_to_async(list)(ExchangeRateProvider.objects.filter(is_active=True))

    if not currencies or not providers:
        logger.warning("No currencies or providers found for historical loading.")
        return

    current_date = start_date
    while current_date <= end_date:
        tasks = []
        for source in currencies:
            for target in currencies:
                if source == target:
                    continue
                for provider in providers:
                    tasks.append(fetch_and_store_rate(source, target, current_date, provider))
        await asyncio.gather(*tasks)
        current_date += datetime.timedelta(days=1)


def run_load_historical_rates(start_date: str, end_date: str):
    """
    Entry point for management command.
    Converts string dates to datetime.date objects and runs the async loader.
    """
    start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    logger.info(f"Loading rates from {start_dt} to {end_dt}...")
    asyncio.run(load_historical_rates(start_dt, end_dt))
    logger.info("Historical loading completed.")
