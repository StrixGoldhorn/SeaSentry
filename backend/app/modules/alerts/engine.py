# backend/app/modules/alerts/engine.py

from app.modules.alerts.evaluators import evaluate_rule
from app.core.database import DBConn
from app.models.vessel import VesselData, VesselLocation

from typing import Dict, Any
from app.modules.alerts.evaluators import evaluate_rule

import logging

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
        logger.error(f"Error processing alerts: {e}")
