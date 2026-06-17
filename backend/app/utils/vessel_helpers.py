# backend/app/utils/vessel_helpers.py

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

def get_vessel_by_vessel_data_id(vessel_data_id: int) -> VesselData:
    '''
    Returns vessel with the vessel_data_id

    Args:
        vessel_data_id: The vessel_data_id

    Returns:
        A VesselData object containing the vessel details
    '''

    session = DBConn.get_session()
    try:
        query = session.query(VesselData).filter(VesselData.vessel_data_id == vessel_data_id)
        res = query.first()
        return res
    except Exception as e:
        logger.error("DB Error in get_vessel_by_vessel_data_id: %s", str(e))
        raise
    finally:
        DBConn.close_session()

def update_vessel_data_in_db(vessel_data_id: int, ship_name: str = None, ship_type: str = None,
                            flag: str = None, length_meters: int = None, beam_meters: int = None,
                            user_tags: List[str] = None) -> bool:
    '''
    Updates an existing vessel in the database. Supports partial updates.
    
    Args:
        vessel_data_id: int representing vessel_data_id to be updated
        ship_name: str = None, new ship name of vessel
        ship_type: str = None, new ship type of vessel
        flag: str = None, new flag of vessel
        length_meters: int = None, new length meters of vessel
        beam_meters: int = None, new beam meters of vessel
        user_tags: list = None, new user tags of vessel

    Returns:
        True if successful
    '''

    session = DBConn.get_session()
    try:
        vessel = session.query(VesselData).filter(VesselData.vessel_data_id == vessel_data_id).first()
        if not vessel:
            return False

        if ship_name is not None:
            vessel.vessel_data_ship_name = ship_name

        if ship_type is not None:
            vessel.vessel_data_ship_type = ship_type

        if flag is not None:
            vessel.vessel_data_flag = flag

        if length_meters is not None:
            vessel.vessel_data_length_meters = length_meters

        if beam_meters is not None:
            vessel.vessel_data_beam_meters = beam_meters

        if user_tags is not None:
            vessel.vessel_data_user_tags = user_tags

        session.commit()
        return True

    except Exception as e:
        session.rollback()
        logger.error("DB Error in update_vessel_data_in_db: %s", str(e))
        raise
    finally:
        DBConn.close_session()
