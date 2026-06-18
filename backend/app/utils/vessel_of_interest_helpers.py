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

def get_all_vessel_of_interest():
    '''
    Returns all vessels of interest

    Returns:
        List of VesselOfInterest objects
    '''
    session = DBConn.get_session()

    try:
        query = session.query(VesselOfInterest)
        res = query.all()
        return res

    except Exception as e:
        session.rollback()
        logger.error("Error in get_all_vessel_of_interest: %s", str(e), exc_info=Settings.EXEC_INFO_API)
        raise

    finally:
        DBConn.close_session()

def get_vessel_of_interest_by_vessel_of_interest_id(vessel_of_interest_id: int) -> VesselOfInterest:
    '''
    Returns vessel_of_interest with the vessel_of_interest_id

    Args:
        vessel_of_interest_id: The vessel_of_interest_id

    Returns:
        A VesselOfInterest object containing the vessel details
    '''

    session = DBConn.get_session()
    try:
        query = session.query(VesselOfInterest).filter(VesselOfInterest.vessel_of_interest_id == vessel_of_interest_id)
        res = query.first()
        return res
    except Exception as e:
        logger.error("DB Error in get_vessel_of_interest_by_vessel_data_id: %s", str(e))
        raise
    finally:
        DBConn.close_session()

def update_vessel_of_interest_data_in_db(vessel_of_interest_id: int,
                                         desc_name: str = None, description: str = None,
                                         mmsi: str = None, imo: str = None) -> bool:
    '''
    Updates an existing vessel in the database. Supports partial updates.

    Args:
        vessel_of_interest_id: int representing vessel_of_interest_id to be updated
        desc_name: str = None, new user-defined name of vessel of interest
        description: str = None, new description of vessel of interest
        mmsi: str = None, new mmsi of vessel of interest
        imo: str = None, new imo of vessel of interest

    Returns:
        True if successful
    '''

    session = DBConn.get_session()
    try:
        voi = session.query(VesselOfInterest).filter(VesselOfInterest.vessel_of_interest_id == vessel_of_interest_id).first()

        if not voi:
            return False

        final_mmsi = voi.vessel_of_interest_mmsi
        final_imo = voi.vessel_of_interest_imo

        if desc_name is not None and desc_name != "" and not check_if_vessel_of_interest_name_exists(desc_name):
            voi.vessel_of_interest_desc_name = desc_name

        if description is not None:
            voi.vessel_of_interest_description = description if description != "" else None

        if mmsi is not None:
            final_mmsi = mmsi if mmsi != "" else None
            voi.vessel_of_interest_mmsi = final_mmsi

        if imo is not None:
            final_imo = imo if imo != "" else None
            voi.vessel_of_interest_imo = final_imo

        if not final_mmsi and not final_imo:
            raise ValueError("Vessel of Interest must have at least an MMSI or an IMO.")

        if final_mmsi and not (len(final_mmsi) == 9 and final_mmsi.isdigit()):
            raise ValueError("MMSI must be 9 digits.")

        if final_imo and not (len(final_imo) == 7 and final_imo.isdigit()):
            raise ValueError("IMO must be 9 digits.")

        session.commit()
        return True

    except ValueError as e:
        session.rollback()
        raise e
    except Exception as e:
        session.rollback()
        logger.error("DB Error in update_vessel_of_interest_data_in_db: %s", str(e))
        raise
    finally:
        DBConn.close_session()
