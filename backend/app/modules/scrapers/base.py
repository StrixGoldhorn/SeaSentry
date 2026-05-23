# backend/app/modules/scrapers/base.py

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import List, Dict, Any

from app.core.schemas import ScrapedVesselRecord
from app.ingest.ingest import ScraperToIngest

logger = logging.getLogger(__name__)

class AbstractScraper(ABC):
    ''' Base class all scrapers must inherit from. '''

    @property
    @abstractmethod
    def name(self) -> str:
        ''' Returns name of this scraper. '''

    @property
    @abstractmethod
    def default_interval_seconds(self) -> int:
        ''' Returns default interval between every scans. '''

    def get_config(self) -> Dict[str, Any]:
        ''' Override or load from .env / app config.'''

    @abstractmethod
    def fetch_data(self, coords: Dict) -> Any:
        '''
        Fetches data from the site, querying for locations of vessels within the specified coords.

        Args:
            coords (Dict[str, float]): A dict containing the queried coords.
        '''

    @abstractmethod
    def parse_data(self, raw: Any) -> List[Dict[str, Any]]:
        ''' Convert raw response to list of dicts. '''

    def normalise(self, parsed: List[Dict[str, Any]]) -> List[ScrapedVesselRecord]:
        ''' Map source-specific fields to ScrapedVesselRecord schema. '''
        records = []
        for item in parsed:
            try:

                records.append(ScrapedVesselRecord(
                    mmsi = str(item.get("mmsi") if item.get("mmsi") is not None else 0).zfill(9),
                    imo = str(item.get("imo") if item.get("imo") is not None else 0).zfill(7),
                    ship_name = item.get("ship_name"),
                    ship_type = item.get("ship_type"),
                    flag = item.get("flag"),
                    length_meters = item.get("length_meters"),
                    beam_meters = item.get("beam_meters"),

                    lat = item.get("lat"),
                    lon = item.get("lon"),
                    timestamp = item.get("timestamp") or datetime.now(timezone.utc),
                    speed_knots = item.get("speed_knots"),
                    course_deg = item.get("course_deg"),
                    heading_deg = item.get("heading_deg"),
                    rate_of_turn_deg_per_sec = item.get("rate_of_turn_deg_per_sec"),
                    nav_status = item.get("nav_status"),

                    source = self.name,
                    raw = str(item)
                ))

            except Exception as e:
                logger.warning("[%s] Failed to normalise record: %s", self.name, e)

        return records

    def run(self, coords=dict) -> List[ScrapedVesselRecord]:
        ''' Fetch -> parse -> normalise -> pass to data ingest. '''
        logger.info("[%s] Starting scrape cycle...", self.name)

        try:
            raw = self.fetch_data(coords)
            logger.info("[%s] Fetch successful", self.name)

            parsed = self.parse_data(raw)
            logger.info("[%s] Parse successful", self.name)

            normalised = self.normalise(parsed)
            logger.info("[%s] Normalisation successful", self.name)

            logger.info("[%s] Successfully processed %d records.", self.name, len(normalised))

            for rec in normalised:
                ScraperToIngest.processVesselRecord(rec)

            return normalised

        except Exception as e:
            # If fail for whatever unforseen reason.
            logger.error("[%s] Scraping failed: %s", self.name, e, exc_info=True)
            return []
