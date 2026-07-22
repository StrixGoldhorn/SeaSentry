# backend/app/utils/vessel_helpers.py

import logging
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
from sqlalchemy import desc, func, or_, and_
from geoalchemy2.functions import ST_X, ST_Y

from app.core.database import DBConn
from app.models.vessel import VesselData, VesselLocation

logger = logging.getLogger(__name__)

def get_all_vessels_in_bbox(envelope, time_lower_bound: datetime, limit: int, shiptype: str = None) -> List:
    '''
    Fetches all Vessels in given bounding box

    Args:
        envelope: The bounding box
        time_lower_bound: datetime object representing earliest time it will search for
        limit: int, limits to the n most recent locations

    Returns:
        List of tuples containing VesselLocation and VesselData objects
    '''

    session = DBConn.get_session()
    try:
        latest_locations_subq = session.query(
            VesselLocation.vessel_location_vessel_data_id,
            VesselLocation.vessel_location_timestamp
        ).filter(
            VesselLocation.vessel_location_timestamp >= time_lower_bound
        ).order_by(
            VesselLocation.vessel_location_vessel_data_id,
            VesselLocation.vessel_location_timestamp.desc()
        ).distinct(
            VesselLocation.vessel_location_vessel_data_id
        ).subquery('latest_locations')

        if shiptype and shiptype != "":
            query = query.filter(VesselData.vessel_data_ship_type.ilike(f"%{shiptype}%"))

        query = session.query(VesselLocation, VesselData).join(
            VesselData,
            VesselLocation.vessel_location_vessel_data_id == VesselData.vessel_data_id,
        ).join(
            latest_locations_subq,
            and_(
                VesselLocation.vessel_location_vessel_data_id == latest_locations_subq.c.vessel_location_vessel_data_id,
                VesselLocation.vessel_location_timestamp == latest_locations_subq.c.vessel_location_timestamp
            )
        ).filter(
            VesselLocation.vessel_location_coords.ST_Within(envelope)
        ).limit(limit)

        return query.all()

    except Exception as e:
        logger.error("Error in get_all_vessels_in_bbox: %s", e, exc_info=True)
        return []

    finally:
        if session:
            DBConn.close_session()

def get_vessels_in_polygon(coords: List[Tuple[float, float]], time_threshold_minutes: int = 15) -> List:
    """
    Queries the database for vessels located within a given polygon and updated within a specific time threshold.

    Args:
        coords: List of (longitude, latitude) tuples defining the polygon vertices.
        time_threshold_minutes: How far back to look for vessel location updates.

    Returns:
        A list of dictionaries containing vessel information.
    """
    if not coords or len(coords) < 3:
        logger.warning("Invalid polygon coordinates provided.")
        return []

    session = DBConn.get_session()
    try:
        closed_coords = list(coords)
        if closed_coords[0] != closed_coords[-1]:
            closed_coords.append(closed_coords[0])

        wkt_coords = ", ".join([f"{lon} {lat}" for lon, lat in closed_coords])
        wkt_polygon = f"POLYGON(({wkt_coords}))"

        polygon_geom = func.ST_GeomFromText(wkt_polygon, 4326)

        threshold_time = datetime.now() - timedelta(minutes=time_threshold_minutes)

        query = session.query(VesselLocation, VesselData).join(
            VesselLocation, VesselData.vessel_data_id == VesselLocation.vessel_location_vessel_data_id
        ).filter(
            VesselLocation.vessel_location_timestamp >= threshold_time,
            func.ST_Within(VesselLocation.vessel_location_coords, polygon_geom)
        ).distinct(
            VesselData.vessel_data_mmsi
        ).order_by(
            VesselData.vessel_data_mmsi,
            desc(VesselLocation.vessel_location_timestamp)
        )

        return query.all()

    except Exception as e:
        logger.error(f"Error in get_vessels_in_polygon: {e}")
        return []

    finally:
        session.close()

def get_all_vessels(querystr: Optional[str] = None, name: Optional[str] = None,
                    mmsi: Optional[str] = None, imo: Optional[str] = None,
                    shiptype: Optional[str] = None, flag: Optional[str] = None,
                    limit: Optional[int] = None, offset: Optional[int] = None) -> Dict[str, Any]:
    '''
    Fetches all vessels from DB.
    Returns list of VesselData objects.
    '''

    session = DBConn.get_session()
    try:
        query = session.query(VesselData)

        query = query.order_by(VesselData.vessel_data_id.desc())

        if querystr is not None:
            query = query.filter(or_(
                VesselData.vessel_data_ship_name.ilike(f"%{querystr}%"),
                VesselData.vessel_data_mmsi.ilike(f"%{querystr}%"),
                VesselData.vessel_data_imo.ilike(f"%{querystr}%")
            ))
        if name is not None:
            query = query.filter(VesselData.vessel_data_ship_name.ilike(f"%{name}%"))
        if mmsi is not None:
            query = query.filter(VesselData.vessel_data_mmsi.ilike(f"%{mmsi}%"))
        if imo is not None:
            query = query.filter(VesselData.vessel_data_imo.ilike(f"%{imo}%"))
        if shiptype is not None:
            query = query.filter(VesselData.vessel_data_ship_type.ilike(f"%{shiptype}%"))
        if flag is not None:
            query = query.filter(VesselData.vessel_data_flag.ilike(f"%{flag}%"))

        total_count = session.query(func.count()).select_from(query.subquery()).scalar()

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        res = query.all()

        return {
            "results": res,
            "total": total_count
        }

    except Exception as e:
        logger.error("Error in get_all_vessels: %s", e, exc_info=True)
        return {"results": [], "total": 0}

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


def get_vessel_by_mmsi(mmsi: str) -> VesselData:
    '''
    Returns vessel with the MMSI

    Args:
        mmsi: The MMSI

    Returns:
        A VesselData object containing the vessel details
    '''

    session = DBConn.get_session()
    try:
        query = session.query(VesselData).filter(VesselData.vessel_data_mmsi == str(mmsi))
        res = query.first()
        return res
    except Exception as e:
        logger.error("DB Error in get_vessel_by_mmsi: %s", str(e))
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

def get_vessel_history_stream(envelope, start_time: datetime, end_time: datetime) -> List:
    '''
    Fetches vessel historical locations in database within a bounding box and time range

    Args:
        envelope: bounding box
        start_time: datetime object representing the start of the time range
        end_time: datetime object representing the end of the time range

    Returns:
        List of tuples containing VesselLocation and VesselData objects
    '''

    session = DBConn.get_session()
    try:
        query = session.query(VesselLocation, VesselData).join(
            VesselData,
            VesselLocation.vessel_location_vessel_data_id == VesselData.vessel_data_id,
        ).filter(
            VesselLocation.vessel_location_timestamp >= start_time,
            VesselLocation.vessel_location_timestamp <= end_time,
            VesselLocation.vessel_location_coords.ST_Within(envelope)
        ).order_by(
            VesselLocation.vessel_location_timestamp.desc()
        ).yield_per(1000)
        res = query.yield_per(1000)
        for location, vessel in res:
            yield location, vessel

    except Exception as e:
        logger.error("Error in get_vessel_history_stream: %s", e, exc_info=True)
        return []

    finally:
        if session:
            DBConn.close_session()

def get_vessel_history_by_vessel_data_id(vessel_data_id: int,
                                       start_time: datetime = datetime.min, end_time: datetime = datetime.now(timezone.utc)) -> List[VesselLocation]:
    '''
    Fetches vessel historical locations in database for vessel
    with given vessel_data_id and within start_time and end_time

    Args:
        vessel_data_id: bounding box
        start_time: datetime object = datetime.min, representing the start of the time range
        end_time: datetime object = datetime.now, representing the end of the time range

    Returns:
        List containing VesselLocation objects
    '''

    session = DBConn.get_session()
    try:
        query = session.query(VesselLocation).join(
            VesselData,
            VesselLocation.vessel_location_vessel_data_id == VesselData.vessel_data_id,
        ).filter(
            VesselLocation.vessel_location_timestamp <= end_time,
            VesselLocation.vessel_location_timestamp >= start_time,
            VesselData.vessel_data_id == vessel_data_id
        ).order_by(
            VesselLocation.vessel_location_vessel_data_id,
            VesselLocation.vessel_location_timestamp.desc()
        )

        return query.all()

    except Exception as e:
        logger.error("Error in get_vessel_track_by_vessel_data_id: %s", e, exc_info=True)
        return []

    finally:
        if session:
            DBConn.close_session()
