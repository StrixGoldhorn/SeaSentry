# backend/app/modules/scrapers/tests/udp_scraper_test.py

'''
Unit tests for udp_scraper.py
'''

import pytest
import logging
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from app.modules.scrapers.registry import ScraperRegistry
from app.core.schemas import ScrapedVesselRecord
from app.modules.scrapers.plugins.udp_scraper import msg_buffer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

@pytest.mark.live
class TestUDPScraperUnit:
    '''
    Unit testing for backend/app/modules/scrapers/plugins/udp_scraper.py
    '''
    # Generic test area (not used but still required to work with AbstractScraper)
    _predefined_coords = {
        "long_min": 103.82335160632802,
        "long_max": 103.85594676548685,
        "lat_min": 1.2535264424975803,
        "lat_max": 1.266477533544827
    }

    def setup_method(self):
        while not msg_buffer.empty():
            msg_buffer.get_nowait()

    @patch('app.modules.scrapers.plugins.udp_scraper.threading.Thread')
    @patch('app.modules.scrapers.plugins.udp_scraper.decode')
    def test_unit_scraper_returns_valid_records(self, mock_decode, mock_thread, scraper_name="UDP_Scraper"):
        '''
        Test scraper with mocked pyais decode
        '''
        # Mock pyais decode
        mock_decoded = MagicMock()
        mock_decoded.asdict.return_value = {
            "msg_type": 1, "mmsi": 123456789, "imo": 1234567,
            "lat": 1.25, "lon": 103.8, "speed": 10.5, "course": 90.0,
            "heading": 85, "timestamp": 1600000000, "status": 0, "shipname": "TEST"
        }
        mock_decode.return_value = mock_decoded
        
        # Instantiate via registry
        try:
            scraper = ScraperRegistry.instantiate(scraper_name)
        except ValueError as e:
            pytest.skip(f"Scraper '{scraper_name}' not registered. Error: {e}")

        msg_buffer.put("DUMMY_NMEA_MSG")
        records = scraper.run(TestUDPScraperUnit._predefined_coords)

        # Basic shape assertions
        assert isinstance(records, list), "Scraper must return a list"
        if len(records) == 0:
            pytest.skip("Scraper returned empty dataset.")

        assert len(records) >= 1, "Expected at least 1 record"

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
                assert len(rec.imo) == 7, f"Invalid IMO length: {rec.imo}, raw: {rec.raw}"
                assert rec.imo.isdigit(), f"Non-numeric IMO: {rec.imo}, raw: {rec.raw}"

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
                assert 0 <= rec.heading_deg <= 360, f"Invalid heading: {rec.heading_deg}, raw: {rec.raw}"

            # nav status
            assert isinstance(rec.nav_status, (int, type(None))), f"Expected int, got {type(rec.nav_status)}, raw: {rec.raw}"
            if isinstance(rec.nav_status, int):
                assert 0 <= rec.nav_status <= 15, f"Invalid nav status: {rec.nav_status}, raw: {rec.raw}"

            # timestamp
            assert rec.timestamp is not None, f"Timestamp must not be none, raw: {rec.raw}"

        logger.info("%s Unit Tests successful", type(self).__name__)

    @patch('app.modules.scrapers.plugins.udp_scraper.threading.Thread')
    @patch('app.modules.scrapers.plugins.udp_scraper.decode')
    def test_unit_scraper_inserts_vessel_data_to_db(self, mock_decode, mock_thread, scraper_name="UDP_Scraper"):
        '''
        Test scraper with mocked pyais decode, insert vessel data into db
        '''
        from app.ingest.ingest import ScraperToIngest

        # Mock pyais decode
        mock_decoded = MagicMock()
        mock_decoded.asdict.return_value = {
            "msg_type": 1, "mmsi": 123456789, "imo": 1234567,
            "lat": 1.25, "lon": 103.8, "speed": 10.5, "course": 90.0,
            "heading": 85, "timestamp": 1600000000, "status": 0, "shipname": "TEST"
        }
        mock_decode.return_value = mock_decoded

        try:
            scraper = ScraperRegistry.instantiate(scraper_name)
        except ValueError as e:
            pytest.skip(f"Scraper '{scraper_name}' not registered. Error: {e}")

        msg_buffer.put("DUMMY_NMEA_MSG")
        records = scraper.run(TestUDPScraperUnit._predefined_coords)

        assert isinstance(records, list), "Scraper must return a list"

        for rec in records:
            ScraperToIngest.processVesselRecord(rec)

if __name__ == "__main__":
    a = TestUDPScraperUnit()
    # a.test_unit_scraper_returns_valid_records()
    a.test_unit_scraper_inserts_vessel_data_to_db()
