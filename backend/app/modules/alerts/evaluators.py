# backend/app/modules/alerts/evaluators.py
'''
Functions to evaluate rules
'''

import json
from sqlalchemy import select
from geoalchemy2.functions import ST_Within, ST_X, ST_Y

from app.core.database import DBConn
from app.models.alert import AlertRule
from app.models.vessel import VesselData, VesselLocation
from app.utils.audit_log_helpers import write_audit_log

from app.modules.alerts.deduplication import check_and_record_alert
from app.modules.alerts.custom_rules import RuleTreeAdapter, build_sqlalchemy_expression

import logging

logger = logging.getLogger(__name__)

def complex_evaluator(vessel_data_id: int, vessel_location_id: int):
    '''
    Evaluates complex custom user rules.

    Args:
        vessel_data_id: vessel data id to query
        vessel_location_id: vessel location id to query
    '''
    session = DBConn.get_session()

    # logger.debug(f"Evaluating vessel_data_id {vessel_data_id}, vessel_location_id {vessel_location_id}")
    try:
        vloc = session.get(VesselLocation, vessel_location_id)
        vdata = session.get(VesselData, vessel_data_id)

        if not vloc or not vdata:
            logger.warning("Vessel location %d or data %d not found.", vessel_location_id, vessel_data_id)
            return

        rules = session.execute(
            select(AlertRule).where(AlertRule.alert_rule_enabled == True)
        ).scalars().all()

        for rule in rules:
            try:
                params_to_validate = rule.alert_rule_params
                if isinstance(params_to_validate, str):
                    params_to_validate = json.loads(params_to_validate)

                parsed_params = RuleTreeAdapter.validate_python(params_to_validate)

                where_expression = build_sqlalchemy_expression(parsed_params)

            except Exception as e:
                logger.error("Validation failed for rule %d with exception %s", rule.alert_rule_id, str(e))
                write_audit_log(f"Validation failed for rule {rule.alert_rule_id}", __name__, {"rule": str(rule), "info": str(e)}, "ERROR")
                continue

            query = (
                select(VesselLocation)
                .join(VesselData, VesselLocation.vessel_location_vessel_data_id == VesselData.vessel_data_id)
                .where(
                    VesselLocation.vessel_location_id == vessel_location_id,
                    where_expression
                )
            )

            try:
                result = session.execute(query).scalar_one_or_none()
            except Exception as e:
                logger.error("Error executing query for rule %d: %s", rule.alert_rule_id, str(e))
                write_audit_log(f"Error in complex_evaluator for rule {rule.alert_rule_id}", __name__, {"rule": str(rule), "info": str(e)}, "ERROR")
                session.rollback()
                continue

            if result:
                lat, lon = None, None
                if vloc.vessel_location_coords is not None:
                    lat, lon = session.execute(
                        select(ST_Y(vloc.vessel_location_coords), ST_X(vloc.vessel_location_coords))
                    ).one()

                context = {
                    "rule_id": rule.alert_rule_id,
                    "rule_name": rule.alert_rule_name,
                    "rule_desc": rule.alert_rule_description,
                    "matched_vessels": [
                        {
                            "mmsi": vdata.vessel_data_mmsi,
                            "ship_data_id": vdata.vessel_data_id,
                            "ship_name": vdata.vessel_data_ship_name,
                            "ship_type": vdata.vessel_data_ship_type,
                            "speed_knots": vloc.vessel_location_speed_knots,
                            "lat": lat,
                            "lon": lon
                        }
                    ]
                }

                check_and_record_alert(session, rule.alert_rule_id, context)

    except Exception as e:
        logger.error("Fatal error in complex_evaluator: %s", str(e))
        write_audit_log("Error in complex_evaluator", __name__, {"info": str(e)}, "ERROR")
        session.rollback()

    finally:
        session.close()
