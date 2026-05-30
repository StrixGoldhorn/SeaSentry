# backend/app/modules/scrapers/scrape.py

import logging
from threading import Event, Thread
from typing import Dict, List
from datetime import datetime
from requests.exceptions import RequestException, Timeout

from app.modules.scrapers.registry import ScraperRegistry
from app.utils.geo_helpers import get_all_aois, get_aoi_polygon_corners
from app.utils.audit_log_helpers import write_audit_log

logger = logging.getLogger(__name__)

def run_single_scraper(scraper_name: str, stop_event: Event, interval_seconds: int,  scraper_config: dict = None):
    logger.info("[%s] Thread started. Interval: %ss", scraper_name, interval_seconds)

    while not stop_event.is_set():
        aoi_list = get_all_aois()

        for aoi in aoi_list:
            try:
                logger.info("[%s] [%s] Starting scrape cycle. Scraping %s", scraper_name, datetime.now().isoformat(), aoi.area_of_interest_name)
                write_audit_log("Starting scrape cycle", __name__, {"Scraper name": scraper_name, "AOI": aoi.area_of_interest_name, "Time": str(datetime.now())}, "INFO")

                scraper = ScraperRegistry.instantiate(scraper_name, config=scraper_config or {})

                coords = get_aoi_polygon_corners(aoi)
                records = scraper.run(coords)

                logger.info("[%s] Cycle complete. Processed %s location records.", scraper_name, len(records))
                write_audit_log("Finished scrape cycle", __name__, {"Scraper name": scraper_name, "AOI": aoi.area_of_interest_name, "Time": str(datetime.now()), "Number of records": len(records)}, "INFO")

            except (RequestException, Timeout) as e:
                logger.warning("[%s] Network error: %s. Retrying next cycle...", scraper_name, e)
                write_audit_log("Network error during scrape cycle", __name__, {"Scraper name": scraper_name, "AOI": aoi.area_of_interest_name, "Time": str(datetime.now())}, "ERROR")

            except Exception as e:
                logger.error("[%s] Unexpected error: %s", scraper_name, e, exc_info=True)
                write_audit_log("Unexpected error", __name__, {"Scraper name": scraper_name, "AOI": aoi.area_of_interest_name, "Info": str(e)}, "ERROR")

            logger.info("[%s] [%s] Pausing for %ss.", scraper_name, datetime.now().isoformat(), interval_seconds)

            # Wait for interval or shutdown signal
            stop_event.wait(interval_seconds)

    logger.info("[%s] Thread shutting down.", scraper_name)

def run_all_scrapers(stop_event: Event, scraper_configs: Dict[str, dict] = None) -> List[Thread]:
    '''
    Spawns one thread per registered scraper.
    '''

    scraper_configs = scraper_configs or {}
    threads = []

    for scraper_name in ScraperRegistry.list():
        config = scraper_configs.get(scraper_name, {})

        # Skip if disabled
        if config.get('enabled') is False:
            logger.info("Disabled %s. Skipping.", scraper_name)
            continue

        interval = config.get('interval_seconds', 300)

        thread = Thread(
            target = run_single_scraper,
            args = (scraper_name, stop_event, interval, config),
            name = f"SeaSentry-Scraper-{scraper_name}",
            daemon = True
        )
        thread.start()
        threads.append(thread)
        logger.info("[%s] Scraper thread launched (interval: %ss)", scraper_name, interval)

    return threads
