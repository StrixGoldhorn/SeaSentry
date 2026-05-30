# backend/app/modules/scrapers/__init__.py
from .base import AbstractScraper
from app.core.schemas import ScrapedVesselRecord
from .registry import ScraperRegistry

# Auto-discover plugins when the scrapers module is first imported
ScraperRegistry.discover()

__all__ = [
    "AbstractScraper",
    "ScrapedVesselRecord",
    "ScraperRegistry"
]
