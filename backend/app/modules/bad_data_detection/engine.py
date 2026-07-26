# backend/app/modules/bad_data_detection/engine.py

from sqlalchemy import desc
from datetime import datetime, timedelta
import logging
from app.modules.bad_data_detection.detector import detector

from app.core.database import DBConn
from app.models.vessel import VesselLocation
from app.utils.audit_log_helpers import write_audit_log

logger = logging.getLogger(__name__)

def bad_data_check(n: int):
    '''
    Function that scheduler should call. Checks all vessel locations within the past n minutes.
    '''
    session = DBConn.get_session()
    try:
        threshold_time = datetime.now() - timedelta(minutes=n)

        results = session.query(
            VesselLocation.vessel_location_vessel_data_id, 
            VesselLocation.vessel_location_id
        ).filter(
            VesselLocation.vessel_location_timestamp >= threshold_time
        ).all()

        logger.debug("Processing %d records for bad data detection", len(results))

        for vessel_data_id, vessel_location_id in results:
            detector(session, vessel_data_id, vessel_location_id)

    except Exception as e:
        logger.error("Error in bad_data_check: %s", str(e))
        write_audit_log("Error in bad_data_check", __name__, {"info": str(e)}, "ERROR")
    finally:
        session.close()
