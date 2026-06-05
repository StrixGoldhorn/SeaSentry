# backend/app/ingest/normalisation.py

from app.core.schemas import IngestVesselData, IngestVesselLocation
from app.models.vessel import VesselData, VesselLocation
from app.utils.audit_log_helpers import write_audit_log, write_data_ingestion_audit_log

from sqlalchemy import func

class IngestNormalisation:
    '''
    Class to handle normalisation of ingested data to prepare for insertion.
    ie convert from IngestVesselData to VesselData
    '''

    @classmethod
    def NormaliseVesselData(cls, vdata: IngestVesselData) -> VesselData:
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
            # TODO: Add exception handling
            pass

        return vesselData

    @classmethod
    def NormaliseVesselLocation(cls, vloc: IngestVesselLocation) -> VesselLocation:
        try:
            vesselLoc = VesselLocation()

            if vloc.lat  is not None and vloc.lon is not None:
                # NOTE: I don't want to mess with raw text in "user" input, don't know what funny ways people can sqli this
                vesselLoc.vessel_location_coords = func.ST_SetSRID(
                    func.ST_MakePoint(vloc.lon, vloc.lat),
                    4326
                )

            if vloc.timestamp is not None:
                vesselLoc.vessel_location_timestamp = vloc.timestamp
            if vloc.speed_knots is not None:
                vesselLoc.vessel_location_speed_knots = vloc.speed_knots
            if vloc.course_deg is not None:
                vesselLoc.vessel_location_course_deg = vloc.course_deg
            if vloc.heading_deg is not None:
                vesselLoc.vessel_location_heading_deg = vloc.heading_deg
            if vloc.rate_of_turn_deg_per_sec is not None:
                vesselLoc.vessel_location_rate_of_turn_deg_per_sec = vloc.rate_of_turn_deg_per_sec
            if vloc.nav_status is not None:
                vesselLoc.vessel_location_nav_status = vloc.nav_status

        except Exception as e:
            # TODO: Add exception handling
            pass

        return vesselLoc
