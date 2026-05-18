<<<<<<< HEAD
# backend/app/modules/scrapers/__init__.py
from .base import AbstractScraper, VesselRecord
from .registry import ScraperRegistry

# Auto-discover plugins when the scrapers module is first imported
ScraperRegistry.discover()

__all__ = [
    "AbstractScraper",
    "VesselRecord",
    "ScraperRegistry"
]
=======
# backend/app/scrapers/__init__.py
# placeholder for initialising scraper related items
>>>>>>> dev
