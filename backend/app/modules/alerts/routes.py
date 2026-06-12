# backend/app/modules/alerts/routes.py
# for api routes relating to alert queries

from flask import Blueprint, request, jsonify
import json
from datetime import datetime
from app.core.database import DBConn
from app.models.alert import AlertHistory, AlertRule
from app.core.config import Settings

from app.utils.audit_log_helpers import write_audit_log
from app.utils.alert_helpers import (
    get_all_alert_history, get_all_alert_rule,
    add_alert_rule_to_db
    )

from app.modules.alerts.custom_rules import RuleTreeAdapter

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

@alerts_bp.route('/rule/add/', methods=['POST'])
def add_alert_rule_web():
    '''
    POST /api/v1/alerts/rule/all
    Adds a new custom alert rule.
    
    Expected JSON payload for single rule:
    {
        "name": "name of alert",
        "description": "description of alert",
        "params": {
            "field": "speed",
            "operator": ">",
            "value": 10.0
        }
    }

    Expected JSON payload for multiple/combined rules:
    {
        "name": "name of alert",
        "description": "description of alert",
        "params": {
            "rules": [
                {
                    "field": "inside_geofence",
                    "value": true,
                    "operator": "=",
                    "valueGeofenceid": 3
                },
                {
                    "field": "enter_geofence",
                    "value": true,
                    "operator": "=",
                    "valueGeofenceid": 3
                },
                {
                    "field": "exit_geofence",
                    "value": true,
                    "operator": "=",
                    "valueGeofenceid": 3
                }
            ],
            "combinator": "or"
        }
    }
    '''
    data = None
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        rule_name = data.get('name')
        rule_description = data.get('description', '')
        rule_params = data.get('params')

        if not rule_name:
            return jsonify({"error": "Missing required fields: 'name'"}), 400

        if rule_params is None:
            return jsonify({"error": "Missing required fields: 'params'"}), 400

        try:
            validated_params = RuleTreeAdapter.validate_python(rule_params)
            params_for_db = validated_params.model_dump()
        except Exception as e:
            logger.error("Validation failed for new rule params: %s", str(e))
            return jsonify({"error": "Invalid rule parameters", "details": str(e)}), 400

        new_rule_id = add_alert_rule_to_db(rule_name, rule_description, params_for_db)

        return jsonify({
            "status": "success",
            "message": "Alert rule created successfully",
            "alert_rule_id": new_rule_id
        }), 201

    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format"}), 400
    except Exception as e:
        logger.error("Error in add_alert_rule_web: %s", str(e), exc_info=Settings.EXEC_INFO_API)
        write_audit_log("Error adding alert rule", __name__, {"info": str(e), "payload": str(data)}, "ERROR")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
