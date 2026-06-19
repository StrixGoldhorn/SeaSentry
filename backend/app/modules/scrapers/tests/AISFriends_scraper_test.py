# backend/app/modules/scrapers/tests/AISFriends_scraper_test.py

'''
Unit + Integration tests for AISFriends_scraper.py
'''

import pytest
import logging
from datetime import datetime, timezone
from requests.exceptions import RequestException, Timeout

from app.modules.scrapers.registry import ScraperRegistry
from app.core.schemas import ScrapedVesselRecord

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

@pytest.mark.live
class TestWithScraperBase:
    '''
    Class to do integration testing
    for backend/app/modules/scrapers/plugins/AISFriends_scraper.py
    with backend/app/modules/scrapers/base.py
    '''
    # Generic test area, usually populated with vessels.
    _predefined_coords = {
        "long_min": 103.82335160632802,
        "long_max": 103.85594676548685,
        "lat_min": 1.2535264424975803,
        "lat_max": 1.266477533544827
    }

    def test_live_scraper_returns_valid_records(self, scraper_name="AISFriends_Scraper"):
        '''
        Scrape site once, test records
        '''
        # Instantiate via registry
        try:
            scraper = ScraperRegistry.instantiate(scraper_name)
        except ValueError as e:
            pytest.skip(f"Scraper '{scraper_name}' not registered. Error: {e}")

        # Run live scrape with retry protection
        try:
            records = scraper.run(TestWithScraperBase._predefined_coords)
        except (RequestException, Timeout) as e:
            pytest.fail(f"Live network request failed after retries: {e}")

        # Basic shape assertions
        assert isinstance(records, list), "Scraper must return a list"
        if len(records) == 0:
            pytest.skip("Live API returned empty dataset (maintenance/rate limit).")

        assert len(records) >= 5, "Expected at least 5 record from a live maritime feed"

        # Schema & domain validation
        for rec in records:
            assert isinstance(rec, ScrapedVesselRecord), f"Expected ScrapedVesselRecord, got {type(rec)}, raw: {rec.raw}"
            assert rec.source == scraper_name, f"Source mismatch: expected {scraper_name}, got {rec.source}, raw: {rec.raw}"

            # assert null fields
            assert rec.ship_type is None, f"Expected None, got {type(rec.ship_type)}, raw: {rec.raw}"
            assert rec.rate_of_turn_deg_per_sec is None, f"Expected None, got {type(rec.rate_of_turn_deg_per_sec)}, raw: {rec.raw}"

            # mmsi
            assert isinstance(rec.mmsi, (str, type(None))), f"Expected string, got {type(rec.mmsi)}, raw: {rec.raw}"
            if isinstance(rec.mmsi, str):
                assert len(rec.mmsi) == 9, f"Invalid MMSI length: {rec.mmsi}, raw: {rec.raw}"
                assert rec.mmsi.isdigit(), f"Non-numeric MMSI: {rec.mmsi}, raw: {rec.raw}"

            # imo
            assert isinstance(rec.imo, (str, type(None))), f"Expected string, got {type(rec.imo)}, raw: {rec.raw}"
            if isinstance(rec.imo, str):
                assert len(rec.imo) == 7, f"Invalid IMO length: {rec.imo}"
                assert rec.imo.isdigit(), f"Non-numeric IMO: {rec.imo}"

            # flag
            assert isinstance(rec.flag, (str, type(None))), f"Expected string, got {type(rec.flag)}, raw: {rec.raw}"

            # length_meters
            assert isinstance(rec.length_meters, (int, type(None))), f"Expected int, got {type(rec.length_meters)}, raw: {rec.raw}"
            if isinstance(rec.length_meters, int):
                assert rec.length_meters < 600, f"Vessel length too long: {rec.length_meters}, raw: {rec.raw}"

            # beam_meters
            assert isinstance(rec.beam_meters, (int, type(None))), f"Expected int, got {type(rec.beam_meters)}, raw: {rec.raw}"
            if isinstance(rec.beam_meters, int):
                assert rec.beam_meters < 600, f"Vessel beam too wide: {rec.beam_meters}, raw: {rec.raw}"

            # coordinates
            assert isinstance(rec.lat, (int, float)), f"Expected float, got {type(rec.lat)}, raw: {rec.raw}"
            assert -90 <= rec.lat <= 90, f"Invalid latitude: {rec.lat}, raw: {rec.raw}"

            assert isinstance(rec.lon, (int, float)), f"Expected float, got {type(rec.lon)}, raw: {rec.raw}"
            assert -180 <= rec.lon <= 180, f"Invalid longitude: {rec.lon}, raw: {rec.raw}"

            # speed
            assert isinstance(rec.speed_knots, (int, float, type(None))), f"Expected float, got {type(rec.speed_knots)}, raw: {rec.raw}"
            if isinstance(rec.speed_knots, (int, float)):
                assert -500 <= rec.speed_knots <= 500, f"Invalid speed: {rec.speed_knots}, raw: {rec.raw}"

            # course
            assert isinstance(rec.course_deg, (int, float, type(None))), f"Expected float, got {type(rec.course_deg)}, raw: {rec.raw}"
            if isinstance(rec.course_deg, (int, float)):
                assert 0 <= rec.course_deg <= 360, f"Invalid course: {rec.course_deg}, raw: {rec.raw}"

            # heading
            assert isinstance(rec.heading_deg, (int, float, type(None))), f"Expected float, got {type(rec.heading_deg)}, raw: {rec.raw}"
            if isinstance(rec.heading_deg, (int, float)):
                assert -0 <= rec.heading_deg <= 360, f"Invalid heading: {rec.heading_deg}, raw: {rec.raw}"

            # nav status
            assert isinstance(rec.nav_status, (int, type(None))), f"Expected int, got {type(rec.nav_status)}, raw: {rec.raw}"
            if isinstance(rec.nav_status, int):
                assert 0 <= rec.nav_status <= 15, f"Invalid nav status: {rec.nav_status}, raw: {rec.raw}"

            # timestamp
            assert rec.timestamp is not None, "Timestamp must not be none, raw: {rec.raw}"
            
        logger.info("%s Tests successful", type(self).__name__)

    def test_live_scraper_inserts_vessel_data_to_db(self, scraper_name="AISFriends_Scraper"):
        '''
        Scrape site once, insert vessel data into db
        '''
        from app.ingest.ingest import ScraperToIngest
        # Instantiate via registry (injects config if scraper supports it)
        try:
            scraper = ScraperRegistry.instantiate(scraper_name)
        except ValueError as e:
            pytest.skip(f"Scraper '{scraper_name}' not registered. Error: {e}")

        # Run live scrape with retry protection
        try:
            records = scraper.run(TestWithScraperBase._predefined_coords)
        except (RequestException, Timeout) as e:
            pytest.fail(f"Live network request failed after retries: {e}")

        # Basic shape assertions
        assert isinstance(records, list), "Scraper must return a list"

        # Schema & domain validation
        for rec in records:
            ScraperToIngest.processVesselRecord(rec)

if __name__ == "__main__":
    a = TestWithScraperBase()
    # a.test_live_scraper_returns_valid_records()
    a.test_live_scraper_inserts_vessel_data_to_db()
