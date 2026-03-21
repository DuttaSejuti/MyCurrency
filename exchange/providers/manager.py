from typing import Dict, Type
from .base import BaseProvider
from .mock import MockProvider
from .currency_beacon import CurrencyBeaconProvider

class ProviderManager:
    # Maps database 'adapter_key' strings to python classes
    _registry: Dict[str, Type[BaseProvider]] = {
        'mock': MockProvider,
        'currency_beacon': CurrencyBeaconProvider,
    }

    @classmethod
    def get_adapter(cls, adapter_key: str) -> BaseProvider:
        # Returns an instance of the requested adapter
        adapter_class = cls._registry.get(adapter_key)
        if not adapter_class:
            raise ValueError(f"No adapter implementation found for key: {adapter_key}")
        return adapter_class()
