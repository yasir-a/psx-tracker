from __future__ import annotations

from functools import lru_cache
from src.config import Settings, get_settings
from src.domain.market.provider_interface import IMarketDataProvider
from src.infrastructure.market.cached_market_service import CachedMarketService
from src.infrastructure.market.mock_provider import MockMarketDataProvider
from src.infrastructure.market.psx_scraper_provider import PSXScraperMarketDataProvider


def get_market_provider(settings: Settings | None = None) -> IMarketDataProvider:
    """Resolve the market data provider from configuration."""
    cfg = settings or get_settings()
    if cfg.MARKET_DATA_PROVIDER == "psx_scraper":
        return PSXScraperMarketDataProvider(timeout=cfg.PSX_SCRAPER_TIMEOUT_SECONDS)
    return MockMarketDataProvider()


@lru_cache(maxsize=1)
def get_market_service() -> CachedMarketService:
    """Return the cached market service singleton."""
    provider = get_market_provider()
    return CachedMarketService(provider)