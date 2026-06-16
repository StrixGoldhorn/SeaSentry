# backend/app/utils/vessel_of_interest_helpers.py

import logging
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.core.config import Settings
from app.core.database import DBConn
from app.models.vessel import VesselOfInterest

logger = logging.getLogger(__name__)

def add_vessel_of_interest(desc_name: str, description: str = None, mmsi: str = None, imo: str = None) -> int:
    '''
    Adds vessel of interest with given params
    
    Args:
        desc_name: str, user-defined name for vessel of interest
        description: str, description for vessel of interest
        mmsi: str, 9 digits representing MMSI of vessel
        imo: str, 7 digits representing IMO of vessel

    Returns:
        vessel_of_interest_id of newly added vessel of interest
    '''
    voi = VesselOfInterest(
        vessel_of_interest_desc_name = desc_name,
        vessel_of_interest_description = description,
        vessel_of_interest_mmsi = mmsi,
        vessel_of_interest_imo = imo
    )

    session = DBConn.get_session()

    try:
        session.add(voi)
        session.commit()
        logger.info("Added vessel of interest '%s' (id: %d)", desc_name, voi.vessel_of_interest_id)
        return voi.vessel_of_interest_id

    except IntegrityError as e:
        session.rollback()
        logger.warning("Vessel of interest with name '%s' already exists or violates unique constraint.", desc_name)
        raise ValueError(f"Vessel of interest name '{desc_name}' must be unique.") from e

    except Exception as e:
        session.rollback()
        logger.error("Failed to create vessel of interest '%s': %s", desc_name, str(e), exc_info=Settings.EXEC_INFO_API)
        raise

    finally:
        DBConn.close_session()

def check_if_vessel_of_interest_name_exists(name: str):
    '''
    Checks if vessel of interest with given name exists
    
    Args:
        name: vessel of interest name to query

    Returns:
        True if vessel of interest with name already exists, False otherwise
    '''

    session = DBConn.get_session()
    try:
        query = session.query(VesselOfInterest).filter(VesselOfInterest.vessel_of_interest_desc_name == name)
        res = query.first()
        if res is not None: return True
        return False
    except Exception as e:
        session.rollback()
        logger.error("DB Error in check_if_vessel_of_interest_name_exists: %s", e)
        raise
    finally:
        DBConn.close_session()

