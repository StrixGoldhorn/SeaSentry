# backend/app/utils/geofence_helpers.py

import logging
from typing import List, Optional
from datetime import datetime
from geoalchemy2.shape import to_shape, from_shape
from shapely.geometry import box
from sqlalchemy.exc import IntegrityError

from app.core.database import DBConn
from app.models.geofence import Geofence

logger = logging.getLogger(__name__)

def get_all_geofences() -> List[Geofence]:
    '''
    Fetches all geofences from DB.
    Returns list of Geofence objects.
    '''

    session = DBConn.get_session()
    try:
        query = session.query(Geofence)
        return query.all()

    except Exception as e:
        logger.error("Error in get_all_geofences: %s", e, exc_info=True)
        return []

    finally:
        if session:
            DBConn.close_session()

def get_geofence_by_id(id: int):
    '''
    Returns Geofence with given ID
    
    Args:
        id: id of Geofence

    Returns:
        Geofence object if exists, None otherwise
    '''

    session = DBConn.get_session()
    try:
        query = session.query(Geofence).filter(Geofence.geofence_id == id)
        res = query.first()
        return res
    except Exception as e:
        session.rollback()
        logger.error("DB Error in get_geofence_by_id: %s", str(e))
        raise
    finally:
        DBConn.close_session()

def get_geofence_polygon_corners(geofence: Geofence) -> dict:
    '''
    Returns Axis-Aligned Bounding Box of the geofence
    '''
    if not geofence.geofence_polygon:
        raise ValueError("Geofence instance has no polygon data loaded.")

    geom = to_shape(geofence.geofence_polygon)
    long_min, lat_min, long_max, lat_max = geom.bounds

    return {
                "long_min": long_min,
                "long_max": long_max,
                "lat_min": lat_min,
                "lat_max": lat_max
            }

def get_geofence_polygon_vertices(geofence: Geofence) -> list:
    '''
    Returns all vertices of the geofence polygon
    '''
    if not geofence.geofence_polygon:
        raise ValueError("Geofence instance has no polygon data loaded.")

    geom = to_shape(geofence.geofence_polygon)

    coords = list(geom.exterior.coords)

    # Remove last index (same as first)
    if coords and coords[0] == coords[-1]:
        coords = coords[:-1]

    return [[long, lat] for long, lat in coords]

def add_rectangle_geofence_to_db(
        name: str,
        long_min: float, long_max: float, lat_min: float, lat_max: float,
        desc: Optional[str] = "No desc."
        ) -> int:
    '''
    Adds the 4 corners to DB.
    Returns the geofence_id.
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
        geofence = Geofence(
            geofence_name = name,
            geofence_description = desc,
            geofence_timestamp = datetime.now(),
            geofence_polygon = db_poly
        )
        session.add(geofence)
        session.commit()
        logger.info("Added geofence '%s' (id: %d)", name, geofence.geofence_id)
        return geofence.geofence_id

    except IntegrityError as e:
        session.rollback()
        logger.warning("geofence name '%s' already exists or violates unique constraint.", name)
        raise ValueError(f"geofence name '{name}' must be unique.") from e

    except Exception as e:
        session.rollback()
        logger.error("Failed to create geofence '%s': %s", name, e, exc_info=True)
        raise

    finally:
        DBConn.close_session()

def add_polygon_geofence_to_db(name: str, geometry_wkb, description: str = "") -> int:
    """
    Inserts a new geofence with a pre-built geometry object.
    """
    session = DBConn.get_session()
    try:
        geofence = Geofence(
            geofence_name=name,
            geofence_description=description,
            geofence_timestamp=datetime.now(),
            geofence_polygon=geometry_wkb
        )
        session.add(geofence)
        session.commit()
        return geofence.geofence_id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        DBConn.close_session()

def update_geofence_in_db(geofence_id: int, name: str = None, desc: str = None, geometry_wkb = None) -> bool:
    '''
    Updates an existing Geofence in the database. Supports partial updates.
    Returns True if successful.
    '''
    session = DBConn.get_session()
    try:
        geofence = session.query(Geofence).filter(Geofence.geofence_id == geofence_id).first()
        if not geofence:
            return False

        if name is not None:
            if check_if_geofence_name_exists(name) and geofence.geofence_name != name: return False
        if name is not None:
            geofence.geofence_name = name
        if desc is not None:
            geofence.geofence_description = desc
        if geometry_wkb is not None:
            geofence.geofence_polygon = geometry_wkb

        session.commit()
        return True

    except Exception as e:
        session.rollback()
        logger.error("DB Error in update_geofence_in_db: %s", e)
        raise
    finally:
        DBConn.close_session()

def check_if_geofence_name_exists(name: str, exclude_id: int = None):
    '''
    Checks if geofence with given name exists
    
    Args:
        name: geofence name to query
        exclude_id: excludes id from search

    Returns:
        True if geofence with name already exists, False otherwise
    '''

    session = DBConn.get_session()
    try:
        query = session.query(Geofence).filter(Geofence.geofence_name == name)

        if exclude_id is not None:
            query = query.filter(Geofence.geofence_id != exclude_id)

        res = query.first()
        if res is not None: return True
        return False
    except Exception as e:
        session.rollback()
        logger.error("DB Error in check_if_geofence_name_exists: %s", e)
        raise


def delete_geofence_in_db(geofence_id: int):
    '''
    Deletes an existing Geofence in the database.
    
    Args:
        geofence_id: int representing geofence_id to be deleted

    Returns:
        True if successful
    '''

    session = DBConn.get_session()
    try:
        geofence = session.query(Geofence).filter(Geofence.geofence_id == geofence_id).first()
        if not geofence:
            return False

        session.delete(geofence)
        session.commit()
        return True

    except Exception as e:
        session.rollback()
        logger.error("DB Error in delete_geofence_in_db: %s", str(e))
        raise
    finally:
        DBConn.close_session()

def DBG_INSERT_DEFAULT_GEOFENCE():
    logging.warning("ADDING DEFAULT geofence TO DB-------------------------------------")

    # "Brani FS"
    # [[103.83626890897152, 1.2550314620372511], [103.83653064092152, 1.2544436544288544],
    #  [103.84035799647933, 1.2562639613923625], [103.84010764418319, 1.2567455840643549]]

    add_rectangle_geofence_to_db(
            "Default Brani B4 B5",
            103.83038861637286,
            103.8362986882725,
            1.2633555273033408,
            1.2648144491763031
    )

if __name__ == "__main__":
    ADD_DEFAULT = False
    if ADD_DEFAULT:
        import time
        time.sleep(15)
        logging.warning("ADDING TO DB-------------------------------------")
        add_rectangle_geofence_to_db(
            "Default Brani B4 B5",
            103.83038861637286,
            103.8362986882725,
            1.2633555273033408,
            1.2648144491763031
        )
