# backend/app/modules/alerts/engine.py

from sqlalchemy import desc
from datetime import datetime, timedelta
import logging

from app.modules.alerts.evaluators import complex_evaluator
from app.core.database import DBConn
from app.models.vessel import VesselLocation
from app.utils.audit_log_helpers import write_audit_log

logger = logging.getLogger(__name__)

def process_alerts_for_vessel(vessel_data_id: int, vessel_location_id: int):
    '''
    Main entry point, processes alerts for a new vessel location
    
    Args:
        vessel_data_id: int, vessel data id in DB
        vessel_location_id: int, vessel location id in DB
    '''

    try:
        complex_evaluator(vessel_data_id, vessel_location_id)

    except Exception as e:
        logger.error("Error processing alerts for vessel_data_id %d, location_id %d: %s", vessel_data_id, vessel_location_id, str(e))
        write_audit_log("Error processing alerts for vessel_data_id", __name__, {"vessel_data_id": vessel_data_id, "vessel_location_id": vessel_location_id, "info": str(e)}, "ERROR")

def check_all_vessels(n: int):
    '''
    Function that scheduler should call, checks alert rules for all vessel locations within the past n minutes.
    
    Args:
        n: int, checks for all vessels within the past n minutes
    '''

    session = DBConn.get_session()
    try:
        threshold_time = datetime.now() - timedelta(minutes=n)

        results = session.query(VesselLocation.vessel_location_vessel_data_id, VesselLocation.vessel_location_id)\
                        .filter(VesselLocation.vessel_location_timestamp >= threshold_time)\
                        .distinct(VesselLocation.vessel_location_vessel_data_id)\
                        .order_by(
                            VesselLocation.vessel_location_vessel_data_id, 
                            desc(VesselLocation.vessel_location_timestamp)
                        )\
                        .all()

        logger.debug("Processing %d records", len(results))

        for vessel_data_id, vessel_location_id in results:
            process_alerts_for_vessel(vessel_data_id, vessel_location_id)

    except Exception as e:
        logger.error("Error in check_all_vessels: %s", str(e))
        write_audit_log("Error in check_all_vessels", __name__, {"info": str(e)}, "ERROR")

    finally:
        session.close()
