# backend/app/modules/scrapers/registry.py
import importlib
import pkgutil
import logging
from typing import Dict, Type, List
from .base import AbstractScraper

logger = logging.getLogger(__name__)

class ScraperRegistry:
    '''
    Class to register all scrapers.

    Attributes:
        _plugins (Dict[str, Type[AbstractScraper]]):
            Dict of all the Scrapers detected, with their name as key.
    '''
    _plugins: Dict[str, Type[AbstractScraper]] = {}

    @classmethod
    def register(cls, scraper_cls: Type[AbstractScraper]) -> Type[AbstractScraper]:
        '''
        Attempts to registers classes with the @ScraperRegistry.register decorator
        '''

        # Class must be a subclass of AbstractScraper
        if not issubclass(scraper_cls, AbstractScraper):
            raise TypeError(f"{scraper_cls.__name__} must inherit from AbstractScraper")

        # In case of 2 classes with the same
        name = scraper_cls.name
        if name in cls._plugins:
            logger.warning("Overwriting existing scraper: %s", name)

        cls._plugins[name] = scraper_cls
        logger.info("Registered scraper plugin: %s", name)
        return scraper_cls

    @classmethod
    def discover(cls, package_path: str = "app.modules.scrapers.plugins"):
        '''
        Auto-import all modules in backend/app/modules/scrapers/plugins/.
        This populates this class's _plugins dict.
        '''
        try:
            package = importlib.import_module(package_path)
            for _, modname, _ in pkgutil.iter_modules(package.__path__, prefix=f"{package_path}."):

                # Any files starting with _ is skipped
                if modname.startswith("_"):
                    continue
                importlib.import_module(modname)

        except ImportError as e:
            logger.warning("Could not auto-discover plugins: %s", e)

    @classmethod
    def list(cls) -> List[str]:
        ''' List detected scrapers. '''
        return list(cls._plugins.keys())

    @classmethod
    def get(cls, name: str) -> Type[AbstractScraper]:
        '''
        Returns specified scraper.
        Raises ValueError if not found.

        Args:
            name (str): Name of scraper to be returned.
        '''
        plugin = cls._plugins.get(name)
        if not plugin:
            raise ValueError(f"Scraper '{name}' not found. Available: {cls.list()}")
        return plugin

    @classmethod
    def instantiate(cls, name: str, **config_overrides) -> AbstractScraper:
        '''
        Creates new instance of specified scraper.
        
        Args:
            name (str): Name of scraper to be instantiated.
        '''
        cls_obj = cls.get(name)

        instance = cls_obj()
        if hasattr(instance, "config"):
            instance.config.update(config_overrides)
        return instance
