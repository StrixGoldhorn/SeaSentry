# backend/app/utils/geo_helper.py

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
    Fetches all AOIs from DB.
    Returns list of AreaOfInterest objects.
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
    Returns Axis-Aligned Bounding Box of the AOI
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

def add_rectangle_aoi_to_db(
        name: str,
        long_min: float, long_max: float, lat_min: float, lat_max: float,
        desc: Optional[str] = "No desc."
        ) -> int:
    '''
    Adds the 4 corners to DB.
    Returns the area_of_interest_id.
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

def DBG_INSERT_DEFAULT():
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
    ADD_DEFAULT = True
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