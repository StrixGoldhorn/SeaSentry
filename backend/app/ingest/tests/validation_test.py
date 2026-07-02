import pytest
from datetime import datetime

from app.core.schemas import IngestVesselData, IngestVesselLocation
from app.core.exceptions import DataValidationError
from app.ingest.validation import IngestValidation

@pytest.mark.ingestchain
class TestValidateVesselData:
    """Tests for IngestValidation.ValidateVesselData"""

    def test_path_all_valid(self):
        vdata = IngestVesselData(
            mmsi="123456789",
            imo="1234567",
            ship_name="Test Ship",
            ship_type="Cargo",
            flag="SG",
            length_meters=200,
            beam_meters=30
        )
        result = IngestValidation.ValidateVesselData(vdata)

        assert result.mmsi == "123456789"
        assert result.imo == "1234567"
        assert result.length_meters == 200
        assert result.beam_meters == 30

    def test_path_all_none(self):
        vdata = IngestVesselData()
        result = IngestValidation.ValidateVesselData(vdata)
        assert result.mmsi is None
        assert result.imo is None

    def test_path_zero_dimensions(self):
        vdata = IngestVesselData(length_meters=0, beam_meters=0)
        result = IngestValidation.ValidateVesselData(vdata)
        assert result.length_meters == 0
        assert result.beam_meters == 0

    @pytest.mark.parametrize("invalid_mmsi", ["12345678", "1234567890", "12345678a", "12345 789"])
    def test_invalid_mmsi_raises_error(self, invalid_mmsi):
        vdata = IngestVesselData(mmsi=invalid_mmsi)
        with pytest.raises(DataValidationError, match="MMSI expected"):
            IngestValidation.ValidateVesselData(vdata)

    @pytest.mark.parametrize("invalid_imo", ["123456", "12345678", "123456a"])
    def test_invalid_imo_raises_error(self, invalid_imo):
        vdata = IngestVesselData(imo=invalid_imo)
        with pytest.raises(DataValidationError, match="IMO expected"):
            IngestValidation.ValidateVesselData(vdata)

    def test_length_meters_too_large(self):
        vdata = IngestVesselData(length_meters=512)
        with pytest.raises(DataValidationError, match="Length expected to be less than 511m"):
            IngestValidation.ValidateVesselData(vdata)

    def test_beam_meters_too_large(self):
        vdata = IngestVesselData(beam_meters=600)
        with pytest.raises(DataValidationError, match="Beam expected to be less than 511m"):
            IngestValidation.ValidateVesselData(vdata)

class TestValidateVesselLocation:
    """Tests for IngestValidation.ValidateVesselLocation"""

    @pytest.fixture
    def base_vloc(self):
        return IngestVesselLocation(
            lat=1.3521,
            lon=103.8198,
            timestamp=datetime.now(),
            source="TestSource",
            raw="raw_payload",
            speed_knots=12.5,
            course_deg=90.0,
            heading_deg=90.0,
            rate_of_turn_deg_per_sec=0.0,
            nav_status=0
        )

    def test_path_all_valid(self, base_vloc):
        result = IngestValidation.ValidateVesselLocation(base_vloc)
        assert result.lat == 1.3521
        assert result.speed_knots == 12.5

    def test_path_ais_na_coordinates(self):
        vloc = IngestVesselLocation(lat=91.0, lon=181.0, timestamp=datetime.now(), source="S", raw="R")
        result = IngestValidation.ValidateVesselLocation(vloc)
        assert result.lat == 91.0
        assert result.lon == 181.0

    def test_invalid_latitude_too_high(self, base_vloc):
        base_vloc.lat = 91.1
        with pytest.raises(DataValidationError, match="Latitude expected"):
            IngestValidation.ValidateVesselLocation(base_vloc)

    def test_invalid_latitude_too_low(self, base_vloc):
        base_vloc.lat = -90.1
        with pytest.raises(DataValidationError, match="Latitude expected"):
            IngestValidation.ValidateVesselLocation(base_vloc)

    def test_invalid_longitude_too_high(self, base_vloc):
        base_vloc.lon = 181.1
        with pytest.raises(DataValidationError, match="Longitude expected"):
            IngestValidation.ValidateVesselLocation(base_vloc)

    def test_invalid_longitude_too_low(self, base_vloc):
        base_vloc.lon = -180.1
        with pytest.raises(DataValidationError, match="Longitude expected"):
            IngestValidation.ValidateVesselLocation(base_vloc)

    @pytest.mark.parametrize("valid_speed", [-1.0, 0.0, 50.5, 102.4])
    def test_valid_speed_knots_boundaries(self, base_vloc, valid_speed):
        base_vloc.speed_knots = valid_speed
        result = IngestValidation.ValidateVesselLocation(base_vloc)
        assert result.speed_knots == valid_speed

    @pytest.mark.parametrize("invalid_speed", [-1.1, 102.5, 150.0])
    def test_invalid_speed_knots(self, base_vloc, invalid_speed):
        base_vloc.speed_knots = invalid_speed
        with pytest.raises(DataValidationError, match="Speed expected"):
            IngestValidation.ValidateVesselLocation(base_vloc)

    @pytest.mark.parametrize("valid_course", [0.0, 180.0, 359.9, 360.0]) # 360 is AIS NA
    def test_valid_course_deg_boundaries(self, base_vloc, valid_course):
        base_vloc.course_deg = valid_course
        result = IngestValidation.ValidateVesselLocation(base_vloc)
        assert result.course_deg == valid_course

    def test_invalid_course_deg(self, base_vloc):
        base_vloc.course_deg = 360.1
        with pytest.raises(DataValidationError, match="Course expected"):
            IngestValidation.ValidateVesselLocation(base_vloc)

    @pytest.mark.parametrize("valid_heading", [0.0, 180.0, 359.0, 511.0]) # 511 is AIS NA
    def test_valid_heading_deg_boundaries(self, base_vloc, valid_heading):
        base_vloc.heading_deg = valid_heading
        result = IngestValidation.ValidateVesselLocation(base_vloc)
        assert result.heading_deg == valid_heading

    @pytest.mark.parametrize("invalid_heading", [-0.1, 360.0, 510.0, 512.0])
    def test_invalid_heading_deg(self, base_vloc, invalid_heading):
        base_vloc.heading_deg = invalid_heading
        with pytest.raises(DataValidationError, match="Heading expected"):
            IngestValidation.ValidateVesselLocation(base_vloc)

    @pytest.mark.parametrize("valid_nav", [0, 5, 15])
    def test_valid_nav_status_boundaries(self, base_vloc, valid_nav):
        base_vloc.nav_status = valid_nav
        result = IngestValidation.ValidateVesselLocation(base_vloc)
        assert result.nav_status == valid_nav

    @pytest.mark.parametrize("invalid_nav", [-1, 16, 20])
    def test_invalid_nav_status(self, base_vloc, invalid_nav):
        base_vloc.nav_status = invalid_nav
        with pytest.raises(DataValidationError, match="Nav status expected"):
            IngestValidation.ValidateVesselLocation(base_vloc)

    def test_none_optional_fields_pass(self):
        vloc = IngestVesselLocation(
            lat=1.0, lon=1.0, timestamp=datetime.now(), source="S", raw="R",
            speed_knots=None, course_deg=None, heading_deg=None, 
            rate_of_turn_deg_per_sec=None, nav_status=None
        )
        result = IngestValidation.ValidateVesselLocation(vloc)
        assert result.speed_knots is None
        assert result.nav_status is None
