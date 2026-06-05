# backend/app/modules/alerts/evaluators.py
'''
Functions to evaluate rules
'''

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func, text
from geoalchemy2.functions import ST_Within, ST_DWithin, ST_Distance

from app.core.database import DBConn

from app.models.alert import AlertRule
from app.models.vessel import VesselData, VesselLocation
from app.models.geofence import Geofence

from app.modules.alerts.context_builder import build_geofence_context
from app.modules.alerts.deduplication import check_and_record_alert

import logging

logger = logging.getLogger(__name__)

def evaluate_geofence_enter_rule(rule: Dict[str, Any], vessel_data_id: int, vessel_location_id: int):
    '''
    Checks whether vessel location is entering any geofenced area.
    '''
    session = DBConn.get_session()

    vdata = session.get(VesselData, vessel_data_id)
    vloc = session.get(VesselLocation, vessel_location_id)

    geofence_id = rule["alert_rule_params"].get("geofence_id")
    vessel_mmsi = vdata.vessel_data_mmsi
    coords_geom = vloc.vessel_location_coords

    if geofence_id is None or coords_geom is None:
        return

    # Get geofence polygon
    geofence = session.get(Geofence, geofence_id)
    if not geofence or geofence.geofence_polygon is None:
        return

    # Check if vessel within geofence
    stmt = select(ST_Within(coords_geom, geofence.geofence_polygon))
    is_inside = session.execute(stmt).scalar()

    if is_inside:
        prev_loc = session.query(VesselLocation).filter(
            VesselLocation.vessel_location_vessel_data_id == vdata.vessel_data_id,
            VesselLocation.vessel_location_id < vloc.vessel_location_id
        ).order_by(VesselLocation.vessel_location_id.desc()).first()

        if prev_loc:
            # Check if that previous location is also inside geofence
            prev_stmt = select(ST_Within(prev_loc.vessel_location_coords, geofence.geofence_polygon))
            prev_is_inside = session.execute(prev_stmt).scalar()

            if prev_is_inside:
                return

        context = build_geofence_context(vessel_mmsi, geofence_id, 'enter')

        alert_id = check_and_record_alert(session, rule['alert_rule_id'], context)
        if alert_id:
            logger.info(f"Alert {alert_id}: Vessel {vessel_mmsi} entered geofence {geofence.geofence_name}")

def evaluate_geofence_exit_rule(rule: Dict[str, Any], vessel_data_id: int, vessel_location_id: int):
    '''
    Checks whether vessel location is exiting any geofenced area.
    '''
    session = DBConn.get_session()
    try:
        vdata = session.get(VesselData, vessel_data_id)
        vloc = session.get(VesselLocation, vessel_location_id)

        geofence_id = rule["alert_rule_params"].get("geofence_id")
        vessel_mmsi = vdata.vessel_data_mmsi
        coords_geom = vloc.vessel_location_coords

        if geofence_id is None or coords_geom is None:
            return

        # Get geofence polygon
        geofence = session.get(Geofence, geofence_id)
        if not geofence or geofence.geofence_polygon is None:
            return

        # Check if vessel is currently inside the geofence
        stmt = select(ST_Within(coords_geom, geofence.geofence_polygon))
        is_inside = session.execute(stmt).scalar()

        if not is_inside:
            prev_loc = session.query(VesselLocation).filter(
                VesselLocation.vessel_location_vessel_data_id == vdata.vessel_data_id,
                VesselLocation.vessel_location_id < vloc.vessel_location_id
            ).order_by(VesselLocation.vessel_location_id.desc()).first()

            if prev_loc:
                # Check if previous location is inside the geofence
                prev_stmt = select(ST_Within(prev_loc.vessel_location_coords, geofence.geofence_polygon))
                prev_is_inside = session.execute(prev_stmt).scalar()

                # If the previous location was already outside, don't care
                if not prev_is_inside:
                    return
            else:
                return

            # Vessel previous was inside and is currently outside.
            logger.info(vdata.vessel_data_ship_name, "is exiting geofence!")
            context = build_geofence_context(vessel_mmsi, geofence_id, 'exit')

            details = {
                "vessel_mmsi": vessel_mmsi,
                "geofence_name": geofence.geofence_name,
                "event": "exit"
            }

            alert_id = check_and_record_alert(session, rule['alert_rule_id'], context, details)
            if alert_id:
                logger.info(f"Alert {alert_id}: Vessel {vessel_mmsi} exited geofence {geofence.geofence_name}")
    finally:
        session.close()

def evaluate_rule(vessel_data_id: int, vessel_location_id: int) -> None:
    '''
    Get all active rules and routes to corresponding evaluator
    '''
    session = DBConn.get_session()
    active_rules = session.query(AlertRule).filter(AlertRule.alert_rule_enabled == True).all()

    for rule in active_rules:
        rule_dict = {
            'alert_rule_id': rule.alert_rule_id,
            'alert_rule_params': rule.alert_rule_params,
            'alert_rule_name': rule.alert_rule_name
        }

        rule_type = rule_dict['alert_rule_params'].get('type')

        try:
            if rule_type == 'geofence_enter':
                evaluate_geofence_enter_rule(rule_dict, vessel_data_id, vessel_location_id)
            elif rule_type == 'geofence_exit':
                evaluate_geofence_exit_rule(rule_dict, vessel_data_id, vessel_location_id)
            else:
                logger.warning(f"Unknown rule type: {rule_type}")

        except Exception as e:
            logger.error(f"Error evaluating rule {rule_dict['alert_rule_name']}: {e}")
            session.rollback()
            continue

        finally:
            session.close()
