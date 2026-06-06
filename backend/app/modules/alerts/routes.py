# backend/app/modules/alerts/routes.py
# for api routes relating to alert queries

from flask import Blueprint, request, jsonify
from json import JSONDecodeError
from datetime import datetime
from app.core.database import DBConn
from app.models.alert import AlertHistory, AlertRule
from app.core.config import Settings

from app.utils.audit_log_helpers import write_audit_log
from app.utils.alert_helpers import (
    get_all_alert_history, get_all_alert_rule,
    add_alert_rule_to_db
    )

import logging

logger = logging.getLogger(__name__)
alerts_bp = Blueprint('alerts', __name__, url_prefix='/api/v1/alerts')

@alerts_bp.route('/history/all', methods=['GET'])
def get_all_alert_history_web():
    '''
    GET /api/v1/alerts/history/all
    Returns history of all alerts, both read and unread.
    '''

    try:
        results = get_all_alert_history()

        data = []
        for alert in results:
            data.append({
                "alert_history_id": alert.alert_history_id,
                "alert_history_timestamp": alert.alert_history_timestamp,
                "alert_history_read": alert.alert_history_read,
                "alert_history_read_at": alert.alert_history_read_at,
                "alert_history_alert_rule_id": alert.alert_history_alert_rule_id,
                "alert_history_context": alert.alert_history_context
            })

        return jsonify({
            "status": "success",
            "count": len(data),
            "data": data
        }), 200

    except Exception as e:
        logger.error("Error in get_all_alert_history_web: %s", e, exc_info=Settings.EXEC_INFO_API)
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@alerts_bp.route('/history/unread', methods=['GET'])
def get_unread_alert_history():
    '''
    GET /api/v1/alerts/history/unread
    Returns all unread alerts.
    '''

    session = DBConn.get_session()
    try:
        query = session.query(AlertHistory).filter(AlertHistory.alert_history_read == False)
        results = query.all()

        data = []
        for alert in results:
            data.append({
                "alert_history_id": alert.alert_history_id,
                "alert_history_timestamp": alert.alert_history_timestamp,
                "alert_history_read": alert.alert_history_read,
                "alert_history_read_at": alert.alert_history_read_at,
                "alert_history_alert_rule_id": alert.alert_history_alert_rule_id,
                "alert_history_context": alert.alert_history_context
            })

        return jsonify({
            "status": "success",
            "count": len(data),
            "data": data
        }), 200

    except Exception as e:
        logger.error("Error in get_unread_alert_history: %s", e, exc_info=Settings.EXEC_INFO_API)
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

    finally:
        if session:
            DBConn.close_session()

@alerts_bp.route('/rule/all', methods=['GET'])
def get_all_alert_rule_web():
    '''
    GET /api/v1/alerts/rule/all
    Returns all rules.
    '''

    try:
        results = get_all_alert_rule()

        data = []
        for rule in results:
            data.append({
                "alert_rule_id": rule.alert_rule_id,
                "alert_rule_timestamp": rule.alert_rule_timestamp,
                "alert_rule_name": rule.alert_rule_name,
                "alert_rule_description": rule.alert_rule_description,
                "alert_rule_params": rule.alert_rule_params,
                "alert_rule_enabled": rule.alert_rule_enabled
            })

        return jsonify({
            "status": "success",
            "count": len(data),
            "data": data
        }), 200

    except Exception as e:
        logger.error("Error in get_all_alert_rule_web: %s", e, exc_info=Settings.EXEC_INFO_API)
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@alerts_bp.route('/rule/add/geofence', methods=['POST'])
def add_rule_geofence():
    '''
    POST /api/v1/alerts/rule/add/geofence
    Adds rule regarding geofence.
    
    Query Params:
    - name: str (name of rule)
    - desc: str (description of rule)
    - geofence_id: int (id of geofence for this rule)
    - trigger_on_enter: boolean (true for trigger on entry)
    - trigger_on_exit: boolean (true for trigger on exit)
    '''

    session = DBConn.get_session()
    try:
        name = str(request.form.get("name"))
        if name is None:
            return jsonify({"error": "Name of AOI expected."}), 400

        desc = str(request.form.get("desc"))

        try:
            geofence_id = int(request.form.get("geofence_id"))
        except (JSONDecodeError, IndexError, TypeError, ValueError):
            return jsonify({"error": "geofence_id should be an integer."}), 400

        def parse_bool(val):
            if isinstance(val, bool):
                return val
            if isinstance(val, str):
                return val.lower() in ('true', '1')
            return False

        trigger_on_enter = parse_bool(request.form.get("trigger_on_enter"))
        trigger_on_exit = parse_bool(request.form.get("trigger_on_exit"))

        if not trigger_on_enter and not trigger_on_exit:
            return jsonify({"error": "Either trigger_on_enter or trigger_no_exit or both should be True."}), 403

        def check_if_name_exists(name):
            query = session.query(AlertRule).filter(AlertRule.alert_rule_name == name)
            res = query.first()
            if res is not None: return True
            return False

        if check_if_name_exists(name):
            return jsonify({"error": f"Rule with name '{name}' already exists."}), 403

        alert_rule_id_list = []
        errors = []

        if trigger_on_enter:
            params = {
                "type": "geofence_enter",
                "geofence_id": geofence_id
            }

            try:
                alert_rule_id = add_alert_rule_to_db(name + " (Enter)", desc, params)
                alert_rule_id_list.append(alert_rule_id)

            except Exception as e:
                logger.error("Failed to add trigger on enter: %s", str(e), exc_info=Settings.EXEC_INFO_API)
                errors.append("Failed to add trigger on enter")

        if trigger_on_exit:
            params = {
                "type": "geofence_exit",
                "geofence_id": geofence_id
            }

            try:
                alert_rule_id = add_alert_rule_to_db(name + " (Exit)", desc, params)
                alert_rule_id_list.append(alert_rule_id)

            except Exception as e:
                logger.error("Failed to add trigger on exit: %s", str(e), exc_info=Settings.EXEC_INFO_API)
                errors.append("Failed to add trigger on exit")

        if errors:
            status_code = 500 if not alert_rule_id_list else 400
            return jsonify({
                "status": "partial_success" if alert_rule_id_list else "failed",
                "alert_rule_id": alert_rule_id_list,
                "errors": errors
            }), status_code

        return jsonify({
            "status": "success",
            "alert_rule_id": alert_rule_id_list
        }), 201

    except Exception as e:
        logger.error("Error in add_rule_geofence: %s", str(e), exc_info=Settings.EXEC_INFO_API)
        write_audit_log("Error in add_rule_geofence", __name__, {"client-form": str(request.form), "info": str(e)}, "ERROR")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

    finally:
        if session:
            DBConn.close_session()
