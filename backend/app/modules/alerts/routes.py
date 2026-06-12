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
    
    Query Parameters (all optional):
    - start_time: ISO format datetime string (e.g., 2023-10-27T10:00:00)
    - end_time: ISO format datetime string (e.g., 2023-10-28T10:00:00)
    - limit: integer, max number of records to return (e.g., 50)
    - offset: integer, number of records to skip for pagination (e.g., 0)
    '''
    try:
        start_time_str = request.args.get('start_time')
        end_time_str = request.args.get('end_time')
        limit_str = request.args.get('limit')
        offset_str = request.args.get('offset')

        start_time = None
        end_time = None
        limit = None
        offset = None

        if start_time_str:
            try:
                start_time = datetime.fromisoformat(start_time_str)
            except ValueError:
                return jsonify({"error": "Invalid start_time format. Use ISO format (e.g., 2023-10-27T10:00:00)"}), 400

        if end_time_str:
            try:
                end_time = datetime.fromisoformat(end_time_str)
            except ValueError:
                return jsonify({"error": "Invalid end_time format. Use ISO format (e.g., 2023-10-27T10:00:00)"}), 400

        if limit_str:
            try:
                limit = int(limit_str)
                if limit < 1:
                    return jsonify({"error": "Limit must be a positive integer"}), 400
            except ValueError:
                return jsonify({"error": "Invalid limit format. Must be an integer"}), 400

        if offset_str:
            try:
                offset = int(offset_str)
                if offset < 0:
                    return jsonify({"error": "Offset must be a non-negative integer"}), 400
            except ValueError:
                return jsonify({"error": "Invalid offset format. Must be an integer"}), 400

        results = get_all_alert_history(start_time, end_time, limit, offset)

        data = []
        for alert in results:
            data.append({
                "alert_history_id": alert.alert_history_id,
                "alert_history_timestamp": alert.alert_history_timestamp.isoformat() if alert.alert_history_timestamp else None,
                "alert_history_read": alert.alert_history_read,
                "alert_history_read_at": alert.alert_history_read_at.isoformat() if alert.alert_history_read_at else None,
                "alert_history_alert_rule_id": alert.alert_history_alert_rule_id,
                "alert_history_context": alert.alert_history_context
            })

        return jsonify({
            "status": "success",
            "count": len(data),
            "data": data,
            "filters_applied": {
                "start_time": start_time_str,
                "end_time": end_time_str,
                "limit": limit,
                "offset": offset
            }
        }), 200

    except Exception as e:
        logger.error("Error in get_all_alert_history_web: %s", e, exc_info=Settings.EXEC_INFO_API)
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@alerts_bp.route('/history/unread', methods=['GET'])
def get_unread_alert_history():
    '''
    GET /api/v1/alerts/history/unread
    Returns history of all unread alerts.
    
    Query Parameters (all optional):
    - start_time: ISO format datetime string (e.g., 2023-10-27T10:00:00)
    - end_time: ISO format datetime string (e.g., 2023-10-28T10:00:00)
    - limit: integer, max number of records to return (e.g., 50)
    - offset: integer, number of records to skip for pagination (e.g., 0)
    '''
    try:
        start_time_str = request.args.get('start_time')
        end_time_str = request.args.get('end_time')
        limit_str = request.args.get('limit')
        offset_str = request.args.get('offset')

        start_time = None
        end_time = None
        limit = None
        offset = None

        if start_time_str:
            try:
                start_time = datetime.fromisoformat(start_time_str)
            except ValueError:
                return jsonify({"error": "Invalid start_time format. Use ISO format (e.g., 2023-10-27T10:00:00)"}), 400

        if end_time_str:
            try:
                end_time = datetime.fromisoformat(end_time_str)
            except ValueError:
                return jsonify({"error": "Invalid end_time format. Use ISO format (e.g., 2023-10-27T10:00:00)"}), 400

        if limit_str:
            try:
                limit = int(limit_str)
                if limit < 1:
                    return jsonify({"error": "Limit must be a positive integer"}), 400
            except ValueError:
                return jsonify({"error": "Invalid limit format. Must be an integer"}), 400

        if offset_str:
            try:
                offset = int(offset_str)
                if offset < 0:
                    return jsonify({"error": "Offset must be a non-negative integer"}), 400
            except ValueError:
                return jsonify({"error": "Invalid offset format. Must be an integer"}), 400

        results = get_all_alert_history(start_time, end_time, limit, offset, False)

        data = []
        for alert in results:
            data.append({
                "alert_history_id": alert.alert_history_id,
                "alert_history_timestamp": alert.alert_history_timestamp.isoformat() if alert.alert_history_timestamp else None,
                "alert_history_read": alert.alert_history_read,
                "alert_history_read_at": alert.alert_history_read_at.isoformat() if alert.alert_history_read_at else None,
                "alert_history_alert_rule_id": alert.alert_history_alert_rule_id,
                "alert_history_context": alert.alert_history_context
            })

        return jsonify({
            "status": "success",
            "count": len(data),
            "data": data,
            "filters_applied": {
                "start_time": start_time_str,
                "end_time": end_time_str,
                "limit": limit,
                "offset": offset
            }
        }), 200

    except Exception as e:
        logger.error("Error in get_unread_alert_history: %s", e, exc_info=Settings.EXEC_INFO_API)
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

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
