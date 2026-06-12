# backend/app/utils/aoi_helpers.py

import logging
from typing import List
from datetime import datetime

from app.core.database import DBConn
from app.models.vessel import VesselData, VesselLocation

logger = logging.getLogger(__name__)

def get_all_vessels_in_bbox(envelope, time_lower_bound: datetime, limit: int) -> List[tuple]:
    '''
    Fetches all AOIs in database

    Args:
        envelope: The bounding box
        time_lower_bound: datetime object representing earliest time it will search for
        limit: int, limits to the n most recent locations

    Returns:
        List of AOI objects
    '''

    session = DBConn.get_session()
    try:
        query = session.query(VesselLocation, VesselData).join(
            VesselData,
            VesselLocation.vessel_location_vessel_data_id == VesselData.vessel_data_id,
        ).filter(
            VesselLocation.vessel_location_timestamp >= time_lower_bound,
            VesselLocation.vessel_location_coords.ST_Within(envelope)
        ).order_by(
            VesselLocation.vessel_location_vessel_data_id,
            VesselLocation.vessel_location_timestamp.desc()
        ).distinct(VesselLocation.vessel_location_vessel_data_id).limit(limit)

        return query.all()

    except Exception as e:
        logger.error("Error in get_all_aois: %s", e, exc_info=True)
        return []

    finally:
        if session:
            DBConn.close_session()
