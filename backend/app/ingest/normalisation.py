# backend/app/ingest/normalisation.py
'''
To normalize vessel data and vessel location
'''

from app.core.schemas import IngestVesselData, IngestVesselLocation
from app.models.vessel import VesselData, VesselLocation
from app.utils.audit_log_helpers import write_audit_log

from sqlalchemy import func

class IngestNormalisation:
    '''
    Class to handle normalisation of ingested data to prepare for insertion.
    ie convert from IngestVesselData to VesselData
    '''

    @classmethod
    def NormaliseVesselData(cls, vdata: IngestVesselData) -> VesselData:
        '''
        Class to normalise vessel data

        Args:
            vdata: IngestVesselData to be normalised

        Returns:
            VesselData with the data normalised
        '''
        try:
            vesselData = VesselData()
            if vdata.mmsi is not None and vdata.mmsi != "000000000":
                vesselData.vessel_data_mmsi = vdata.mmsi
            if vdata.imo is not None and vdata.imo != "0000000":
                vesselData.vessel_data_imo = vdata.imo
            if vdata.ship_name is not None:
                vesselData.vessel_data_ship_name = vdata.ship_name
            if vdata.ship_type is not None:
                vesselData.vessel_data_ship_type = vdata.ship_type
            if vdata.flag is not None:
                vesselData.vessel_data_flag = vdata.flag
            if vdata.length_meters is not None:
                vesselData.vessel_data_length_meters = vdata.length_meters
            if vdata.beam_meters is not None:
                vesselData.vessel_data_beam_meters = vdata.beam_meters

        except Exception as e:
            write_audit_log("Unknown Exception while normalising IngestVesselData",
                            __name__, {"error": str(e), "vdata": str(vdata)}, "ERROR")
            raise e

        return vesselData

    @classmethod
    def NormaliseVesselLocation(cls, vloc: IngestVesselLocation) -> VesselLocation:
        '''
        Class to normalise vessel location

        Args:
            vdata: IngestVesselLocation to be normalised

        Returns:
            VesselLocation with the data normalised
        '''
        try:
            vesselLoc = VesselLocation()

            if vloc.lat  is not None and vloc.lon is not None:
                # Default when unavailable
                if vloc.lat == 91 or vloc.lon == 181:
                    vesselLoc.vessel_location_coords = None

                # NOTE: I don't want to mess with raw text in "user" input, don't know what funny ways people can sqli this
                vesselLoc.vessel_location_coords = func.ST_SetSRID(
                    func.ST_MakePoint(vloc.lon, vloc.lat),
                    4326
                )

            if vloc.timestamp is not None:
                vesselLoc.vessel_location_timestamp = vloc.timestamp
            if vloc.speed_knots is not None:
                # Default when unavailable
                if vloc.speed_knots == 102.3:
                    vesselLoc.vessel_location_speed_knots = None
                vesselLoc.vessel_location_speed_knots = vloc.speed_knots
            if vloc.course_deg is not None:
                # Default when unavailable
                if vloc.course_deg == 360.0:
                    vesselLoc.vessel_location_course_deg = None
                vesselLoc.vessel_location_course_deg = vloc.course_deg
            if vloc.heading_deg is not None:
                # Default when unavailable
                if vloc.course_deg == 511:
                    vesselLoc.vessel_location_course_deg = None
                vesselLoc.vessel_location_heading_deg = vloc.heading_deg
            if vloc.rate_of_turn_deg_per_sec is not None:
                # Default when unavailable
                if vloc.rate_of_turn_deg_per_sec == 127 or vloc.rate_of_turn_deg_per_sec == -127:
                    vesselLoc.vessel_location_rate_of_turn_deg_per_sec = None
                vesselLoc.vessel_location_rate_of_turn_deg_per_sec = vloc.rate_of_turn_deg_per_sec
            if vloc.nav_status is not None:
                vesselLoc.vessel_location_nav_status = vloc.nav_status

        except Exception as e:
            write_audit_log("Unknown Exception while normalising IngestVesselLocation",
                            __name__, {"error": str(e), "vloc": str(vloc)}, "ERROR")
            raise e

        return vesselLoc
