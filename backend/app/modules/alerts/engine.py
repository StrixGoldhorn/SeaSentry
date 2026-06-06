from datetime import datetime, timedelta
import logging

from app.modules.alerts.evaluators import evaluate_rule
from app.core.database import DBConn
from app.models.vessel import VesselData, VesselLocation

logger = logging.getLogger(__name__)

def process_alerts_for_vessel(vessel_data_id: int, vessel_location_id: int) -> None:
    '''
    Main entry point - process alerts for a new vessel location
    
    Args:
        vessel_data_id: int, vessel data id in DB
        vessel_location_id: int, vessel location id in DB
    '''

    try:
        evaluate_rule(vessel_data_id, vessel_location_id)

    except Exception as e:
        logger.error(f"Error processing alerts for vessel_data_id {vessel_data_id}, location_id {vessel_location_id}: {e}")

def check_all_vessels(n: int):
    '''
    Function that scheduler should call, checks alert rules for all vessel locations 
    within the past n minutes.
    
    Args:
        n: int, checks for all vessels within the past n minutes
    '''

    session = DBConn.get_session()
    try:
        threshold_time = datetime.now() - timedelta(minutes=n)

        results = session.query(VesselLocation.vessel_location_vessel_data_id, VesselLocation.vessel_location_id)\
                        .filter(VesselLocation.vessel_location_timestamp >= threshold_time).all()

        for vessel_data_id, vessel_location_id in results:
            process_alerts_for_vessel(vessel_data_id, vessel_location_id)

    except Exception as e:
        logger.error(f"Error in check_all_vessels scheduler task: {e}")

    finally:
        session.close()
