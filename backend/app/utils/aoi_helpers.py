# backend/app/utils/aoi_helpers.py

import logging
from typing import List, Optional
from datetime import datetime
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import box
from sqlalchemy.exc import IntegrityError

from app.core.database import DBConn
from app.models.areaofinterest import AreaOfInterest

logger = logging.getLogger(__name__)

def get_all_aois() -> List[AreaOfInterest]:
    '''
    Fetches all AOIs in database

    Returns:
        List of AOI objects
    '''

    session = DBConn.get_session()
    try:
        query = session.query(AreaOfInterest)
        return query.all()

    except Exception as e:
        logger.error("Error in get_all_aois: %s", e, exc_info=True)
        return []

    finally:
        if session:
            DBConn.close_session()

def get_aoi_polygon_corners(aoi: AreaOfInterest) -> dict:
    '''
    Returns the coordinates of the bounding box of the AOI
    
    Args:
        aoi: The AOI object of interest

    Returns:
        Dictionary with bounding box coordinates of the AOI
    '''
    if not aoi.area_of_interest_polygon:
        raise ValueError("AOI instance has no polygon data loaded.")

    geom = to_shape(aoi.area_of_interest_polygon)
    long_min, lat_min, long_max, lat_max = geom.bounds

    return {
                "long_min": long_min,
                "long_max": long_max,
                "lat_min": lat_min,
                "lat_max": lat_max
            }

def get_aoi_polygon_vertices(aoi: AreaOfInterest) -> list:
    '''
    Returns all vertices of the AOI polygon
    
    Args:
        aoi: The AOI object of interest

    Returns:
        List of [longitude, latitude] pairs for each vertice in the AOI polygon
    '''
    if not aoi.area_of_interest_polygon:
        raise ValueError("AOI instance has no polygon data loaded.")

    geom = to_shape(aoi.area_of_interest_polygon)

    coords = list(geom.exterior.coords)

    # Remove last index (same as first)
    if coords and coords[0] == coords[-1]:
        coords = coords[:-1]

    return [[long, lat] for long, lat in coords]

def add_rectangle_aoi_to_db(name: str, long_min: float, long_max: float, lat_min: float, lat_max: float,desc: str = "") -> int:
    '''
    Inserts new AOI with given name and bounding box
    
    Args:
        name: str, name of new AOI
        description: str, description of new AOI
        long_min: float, long_max: float, lat_min: float, lat_max: float, coordinates of the bounding box

    Returns:
        aoi_id of new AOI
    '''

    # In case user does not know min/max
    if long_min > long_max:
        long_max, long_min = long_min, long_max
    if lat_min > lat_max:
        lat_max, lat_min = lat_min, lat_max

    # Basic validation
    if long_min < -180 or long_max > 180:
        raise ValueError("Check your longitude. -180 deg <= longitude <= 180 deg")
    if lat_min < -90 or lat_max > 90:
        raise ValueError("Check your latitude. -90 deg <= latitude <= 90 deg")

    poly = box(long_min, lat_min, long_max, lat_max)
    db_poly = from_shape(poly, srid = 4326)

    session = DBConn.get_session()

    try:
        aoi = AreaOfInterest(
            area_of_interest_name = name,
            area_of_interest_description = desc,
            area_of_interest_timestamp = datetime.now(),
            area_of_interest_polygon = db_poly
        )
        session.add(aoi)
        session.commit()
        logger.info("Added AOI '%s' (id: %d)", name, aoi.area_of_interest_id)
        return aoi.area_of_interest_id

    except IntegrityError as e:
        session.rollback()
        logger.warning("AOI name '%s' already exists or violates unique constraint.", name)
        raise ValueError(f"AOI name '{name}' must be unique.") from e

    except Exception as e:
        session.rollback()
        logger.error("Failed to create AOI '%s': %s", name, e, exc_info=True)
        raise

    finally:
        DBConn.close_session()

def add_polygon_aoi_to_db(name: str, geometry_wkb, description: str = "") -> int:
    '''
    Inserts new AOI with given name and polygon
    
    Args:
        name: str, name of new AOI
        description: str, description of new AOI
        geometry_wkb: geometry of new AOI

    Returns:
        aoi_id of new AOI
    '''

    session = DBConn.get_session()
    try:
        aoi = AreaOfInterest(
            area_of_interest_name=name,
            area_of_interest_description=description,
            area_of_interest_timestamp=datetime.now(),
            area_of_interest_polygon=geometry_wkb
        )
        session.add(aoi)
        session.commit()
        return aoi.area_of_interest_id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        DBConn.close_session()

def update_aoi_in_db(aoi_id: int, name: str = None, desc: str = None, geometry_wkb = None) -> bool:
    '''
    Updates an existing AOI in the database. Supports partial updates.
    
    Args:
        aoi_id: int representing aoi_id to be updated
        name: str = None, new name of AOI
        desc: str = None, new description for AOI
        geometry_wkb = None, new polygon for AOI

    Returns:
        True if successful
    '''

    session = DBConn.get_session()
    try:
        aoi = session.query(AreaOfInterest).filter(AreaOfInterest.area_of_interest_id == aoi_id).first()
        if not aoi:
            return False

        if name is not None:
            aoi.area_of_interest_name = name
        if desc is not None:
            aoi.area_of_interest_description = desc
        if geometry_wkb is not None:
            aoi.area_of_interest_polygon = geometry_wkb

        session.commit()
        return True

    except Exception as e:
        session.rollback()
        logger.error("DB Error in update_aoi_in_db: %s", e)
        raise
    finally:
        DBConn.close_session()

def check_if_aoi_name_exists(name: str):
    '''
    Checks if AOI with given name exists
    
    Args:
        name: AOI name to query

    Returns:
        True if AOI with name already exists, False otherwise
    '''

    session = DBConn.get_session()
    try:
        query = session.query(AreaOfInterest).filter(AreaOfInterest.area_of_interest_name == name)
        res = query.first()
        if res is not None: return True
        return False
    except Exception as e:
        session.rollback()
        logger.error("DB Error in check_if_aoi_name_exists: %s", e)
        raise
    finally:
        DBConn.close_session()

def DBG_INSERT_DEFAULT_AOI():
    logging.warning("ADDING DEFAULT AOI TO DB-------------------------------------")
    add_rectangle_aoi_to_db(
        "Default Brani",
        103.82335160632802,
        103.85594676548685,
        1.2535264424975803,
        1.266477533544827
    )

if __name__ == "__main__":
    # {
    #     "long_min": 103.82335160632802,
    #     "long_max": 103.85594676548685,
    #     "lat_min": 1.2535264424975803,
    #     "lat_max": 1.266477533544827
    # }
    ADD_DEFAULT = False
    if ADD_DEFAULT:
        import time
        time.sleep(15)
        logging.warning("ADDING TO DB-------------------------------------")
        add_rectangle_aoi_to_db(
            "Default Brani",
            103.82335160632802,
            103.85594676548685,
            1.2535264424975803,
            1.266477533544827
        )