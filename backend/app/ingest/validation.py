# backend/app/ingest/validation.py
'''
Perform validation checks
'''

from app.core.schemas import IngestVesselData, IngestVesselLocation
from app.utils.audit_log_helpers import write_audit_log
from app.core.exceptions import DataValidationError
from typing import Tuple

import logging

logger = logging.getLogger(__name__)

class IngestValidation:
    '''
    Class to handle validation checks on ingested data.
    '''

    @classmethod
    def ValidateVesselData(cls, vdata: IngestVesselData) -> IngestVesselData:
        '''
        Validate data in IngestVesselData

        Args:
            vloc: IngestVesselData to be validated

        Returns:
            IngestVesselData
        '''
        def basic_validate_MMSI(mmsi: str) -> str:
            if not mmsi: return mmsi
            if len(mmsi) != 9:
                raise DataValidationError(f"MMSI expected to be of length 9, length of {len(mmsi)} was given instead.")
            if not mmsi.isdigit():
                raise DataValidationError(f"MMSI expected to only have digits, {mmsi} was given instead.")
            return mmsi

        def basic_validate_IMO(imo: str) -> str:
            if not imo: return imo
            if len(imo) != 7:
                raise DataValidationError(f"IMO expected to be of length 7, length of {len(imo)} was given instead.")
            if not imo.isdigit():
                raise DataValidationError(f"IMO expected to only have digits, {imo} was given instead.")
            return imo

        def basic_validate_length_meters(length_meters: int) -> int:
            if not length_meters: return length_meters
            if length_meters > 511:
                raise DataValidationError(f"Length expected to be less than 511m, length of {length_meters}m was given instead.")
            return length_meters

        def basic_validate_beam_meters(beam_meters: int) -> int:
            if not beam_meters: return beam_meters
            if beam_meters > 511:
                raise DataValidationError(f"Beam expected to be less than 511m, beam of {beam_meters}m was given instead.")
            return beam_meters
        try:
            validated_mmsi = basic_validate_MMSI(vdata.mmsi)
            validated_imo = basic_validate_IMO(vdata.imo)
            validated_ship_name = vdata.ship_name
            validated_ship_type = vdata.ship_type
            validated_flag = vdata.flag
            validated_length_meters = basic_validate_length_meters(vdata.length_meters)
            validated_beam_meters = basic_validate_beam_meters(vdata.beam_meters)
        except DataValidationError as e:
            write_audit_log("DataValidationError", __name__, {"data": str(vdata), "error": str(e)}, "ERROR")
            logger.warning("DataValidationError, %s, vdata: %s, error: %s", __name__, str(vdata), str(e))

        vdata = IngestVesselData(
            mmsi = validated_mmsi,
            imo = validated_imo,
            ship_name = validated_ship_name,
            ship_type = validated_ship_type,
            flag = validated_flag,
            length_meters = validated_length_meters,
            beam_meters = validated_beam_meters
        )
        return vdata

    @classmethod
    def ValidateVesselLocation(cls, vloc: IngestVesselLocation) -> IngestVesselLocation:
        '''
        Validate data in IngestVesselLocation

        Args:
            vloc: IngestVesselLocation to be validated

        Returns:
            IngestVesselLocation
        '''
        def basic_validate_coords(lat: float, lon: float) -> Tuple[int, int]:
            if not -90 <= lat <= 91:
                raise DataValidationError(f"Latitude expected to be between -90 and 91 degrees, {lat} was given instead")
            if not -180 <= lon <= 181:
                raise DataValidationError(f"Longitude expected to be between -180 and 181 degrees, {lon} was given instead")
            return lat, lon

        def basic_validate_speed_knots(speed_knots: float) -> float:
            if not speed_knots: return speed_knots
            if not -1 <= speed_knots <= 102.4:
                raise DataValidationError(f"Speed expected to be between 0 and 102.4 knots, {speed_knots} was given instead")
            return speed_knots

        def basic_validate_course_deg(course_deg: float) -> float:
            if not course_deg: return course_deg
            if not 0 <= course_deg <= 359:
                raise DataValidationError(f"Course expected to be between 0 and 359 deg, {course_deg} was given instead")
            return course_deg

        def basic_validate_heading_deg(heading_deg: float) -> float:
            if not heading_deg: return heading_deg
            if not 0 <= heading_deg <= 359 and heading_deg != 511:
                raise DataValidationError(f"Heading expected to be between 0 and 359 deg, {heading_deg} was given instead")
            return heading_deg

        def basic_validate_nav_status(nav_status: int) -> int:
            if not nav_status: return nav_status
            if not 0 <= nav_status <= 15:
                raise DataValidationError(f"Nav status expected to be between 0 and 15, {nav_status} was given instead")
            return nav_status

        try:
            validated_lat, validated_lon = basic_validate_coords(vloc.lat, vloc.lon)
            validated_timestamp = vloc.timestamp
            validated_source = vloc.source
            validated_raw = vloc.raw

            validated_speed_knots = basic_validate_speed_knots(vloc.speed_knots)
            validated_course_deg = basic_validate_course_deg(vloc.course_deg)
            validated_heading_deg = basic_validate_heading_deg(vloc.heading_deg)
            validated_rate_of_turn_deg_per_sec = vloc.rate_of_turn_deg_per_sec
            validated_nav_status = basic_validate_nav_status(vloc.nav_status)
        except DataValidationError as e:
            write_audit_log("DataValidationError", __name__, {"data": str(vloc), "error": str(e)}, "ERROR")
            logger.warning("DataValidationError, %s, vloc: %s, error: %s", __name__, str(vloc), str(e))

        vloc = IngestVesselLocation(
            lat = validated_lat,
            lon = validated_lon,
            timestamp = validated_timestamp,
            source = validated_source,
            raw = validated_raw,

            speed_knots = validated_speed_knots,
            course_deg = validated_course_deg,
            heading_deg = validated_heading_deg,
            rate_of_turn_deg_per_sec = validated_rate_of_turn_deg_per_sec,
            nav_status = validated_nav_status
        )
        return vloc
