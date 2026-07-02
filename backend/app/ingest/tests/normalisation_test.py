import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

from app.core.schemas import IngestVesselData, IngestVesselLocation
from app.ingest.normalisation import IngestNormalisation

@patch('app.ingest.normalisation.func')
@pytest.mark.ingestchain
class TestNormaliseVesselData:
    """Tests for IngestNormalisation.NormaliseVesselData"""

    def test_path_all_valid(self, mock_func):
        vdata = IngestVesselData(
            mmsi="123456789", imo="1234567", ship_name="Test Ship",
            ship_type="Cargo", flag="SG", length_meters=200, beam_meters=30
        )
        result = IngestNormalisation.NormaliseVesselData(vdata)

        assert result.vessel_data_mmsi == "123456789"
        assert result.vessel_data_imo == "1234567"
        assert result.vessel_data_ship_name == "Test Ship"
        assert result.vessel_data_length_meters == 200

    def test_na_mmsi_and_imo_filtered_out(self, mock_func):
        """AIS 'Not Available' defaults for MMSI and IMO should be treated as None."""
        vdata = IngestVesselData(mmsi="000000000", imo="0000000")
        result = IngestNormalisation.NormaliseVesselData(vdata)

        assert getattr(result, 'vessel_data_mmsi', None) is None
        assert getattr(result, 'vessel_data_imo', None) is None

    def test_all_none_fields(self, mock_func):
        """If all fields are None, it should return an empty VesselData object without crashing."""
        vdata = IngestVesselData()
        result = IngestNormalisation.NormaliseVesselData(vdata)

        assert getattr(result, 'vessel_data_mmsi', None) is None


@patch('app.ingest.normalisation.func')
@pytest.mark.ingestchain
class TestNormaliseVesselLocation:
    """Tests for IngestNormalisation.NormaliseVesselLocation"""

    @pytest.fixture
    def base_vloc(self):
        """Provides a base valid IngestVesselLocation object."""
        return IngestVesselLocation(
            lat=1.3521, lon=103.8198, timestamp=datetime.now(), 
            source="TestSource", raw="raw_payload",
            speed_knots=12.5, course_deg=90.0, heading_deg=90.0,
            rate_of_turn_deg_per_sec=0.0, nav_status=0
        )

    def test_path_valid_coordinates(self, mock_func, base_vloc):
        result = IngestNormalisation.NormaliseVesselLocation(base_vloc)

        mock_func.ST_MakePoint.assert_called_once_with(103.8198, 1.3521)
        mock_func.ST_SetSRID.assert_called_once()

        assert result.vessel_location_speed_knots == 12.5
        assert result.vessel_location_course_deg == 90.0
        assert result.vessel_location_heading_deg == 90.0

    def test_na_coordinates_91_181(self, mock_func, base_vloc):
        """Lat 91 or Lon 181 are AIS NA. Coords should be None, and ST_SetSRID should NOT be called."""
        base_vloc.lat = 91.0
        base_vloc.lon = 181.0

        result = IngestNormalisation.NormaliseVesselLocation(base_vloc)

        assert result.vessel_location_coords is None
        mock_func.ST_SetSRID.assert_not_called()
        mock_func.ST_MakePoint.assert_not_called()

    def test_na_speed_knots(self, mock_func, base_vloc):
        """102.3 is AIS NA for speed. Should be converted to None."""
        base_vloc.speed_knots = 102.3
        result = IngestNormalisation.NormaliseVesselLocation(base_vloc)
        assert result.vessel_location_speed_knots is None

    def test_na_course_deg(self, mock_func, base_vloc):
        """360.0 is AIS NA for course. Should be converted to None."""
        base_vloc.course_deg = 360.0
        result = IngestNormalisation.NormaliseVesselLocation(base_vloc)
        assert result.vessel_location_course_deg is None

    def test_na_heading_deg(self, mock_func, base_vloc):
        """511 is AIS NA for heading. Should be converted to None."""
        base_vloc.heading_deg = 511.0
        result = IngestNormalisation.NormaliseVesselLocation(base_vloc)
        assert result.vessel_location_heading_deg is None

    @pytest.mark.parametrize("na_rot", [127.0, -127.0])
    def test_na_rate_of_turn(self, mock_func, base_vloc, na_rot):
        """127 and -127 are AIS NA for rate of turn. Should be converted to None."""
        base_vloc.rate_of_turn_deg_per_sec = na_rot
        result = IngestNormalisation.NormaliseVesselLocation(base_vloc)
        assert result.vessel_location_rate_of_turn_deg_per_sec is None

    def test_valid_non_na_values_preserved(self, mock_func, base_vloc):
        """Ensure normal values are not accidentally by NA checks."""
        base_vloc.speed_knots = 102.2
        base_vloc.course_deg = 359.9
        base_vloc.heading_deg = 359.0 
        base_vloc.rate_of_turn_deg_per_sec = 126.0

        result = IngestNormalisation.NormaliseVesselLocation(base_vloc)

        assert result.vessel_location_speed_knots == 102.2
        assert result.vessel_location_course_deg == 359.9
        assert result.vessel_location_heading_deg == 359.0
        assert result.vessel_location_rate_of_turn_deg_per_sec == 126.0

    def test_none_optional_fields_skipped(self, mock_func):
        vloc = IngestVesselLocation(
            lat=1.0, lon=1.0, timestamp=datetime.now(), source="S", raw="R",
            speed_knots=None, course_deg=None, heading_deg=None, 
            rate_of_turn_deg_per_sec=None, nav_status=None
        )
        result = IngestNormalisation.NormaliseVesselLocation(vloc)

        mock_func.ST_SetSRID.assert_called_once()

        assert getattr(result, 'vessel_location_speed_knots', None) is None
        assert getattr(result, 'vessel_location_nav_status', None) is None
