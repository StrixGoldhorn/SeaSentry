# backend/app/modules/vessel_of_interest/routes.py

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta, timezone
from sqlalchemy import func
from geoalchemy2.shape import to_shape

from app.core.config import Settings
from app.models.vessel import VesselData, VesselLocation
from app.utils.vessel_of_interest_helpers import (get_all_vessel_of_interest, get_vessel_of_interest_by_vessel_of_interest_id,
                                                  add_vessel_of_interest,
                                                  check_if_vessel_of_interest_name_exists)
from app.utils.audit_log_helpers import write_audit_log

import logging

logger = logging.getLogger(__name__)
vessel_of_interest_bp = Blueprint('vessel_of_interest', __name__, url_prefix='/api/v1/vessel_of_interest')

@vessel_of_interest_bp.route('/add', methods=['POST'])
def add_vessel_of_interest_web():
    '''
    POST /api/v1/vessel_of_interest/add
    Adds new vessel of interest
    
    Query Params:
    - name: str (User-defined name for Vessel of Interest)
    - desc: str (Description of Vessel of Interest)
    - mmsi: str (MMSI of Vessel of Interest)
    - imo: str (IMO of Vessel of Interest)
    '''

    try:
        name = request.form.get("name")
        if not name:
            return jsonify({"error": "User-defined name for Vessel of Interest expected."}), 400

        desc = request.form.get("desc", "")

        mmsi = request.form.get("mmsi")
        if mmsi is not None:
            if not mmsi.isdigit() or len(mmsi) != 9:
                return jsonify({"error": "MMSI should be 9 digits."}), 400

        imo = request.form.get("imo")
        if imo is not None:
            if not imo.isdigit() or len(imo) != 7:
                return jsonify({"error": "IMO should be 7 digits."}), 400 

        if not mmsi and not imo:
            return jsonify({"error": "Either MMSI or IMO must be provided."}), 400

        if check_if_vessel_of_interest_name_exists(name):
            return jsonify({"error": f"Vessel of Interest with name '{name}' already exists."}), 403

        try:
            voi_id = add_vessel_of_interest(name, desc, mmsi, imo)
            return jsonify({
                "status": "success",
                "voi_id": voi_id
            }), 201

        except Exception as e:
            logger.error("Error while adding to DB in add_vessel_of_interest_web: %s", str(e), exc_info=Settings.EXEC_INFO_API)
            write_audit_log("Error while adding to DB in add_vessel_of_interest_web", __name__, {"client-form": str(request.form), "info": str(e)}, "ERROR")
            return jsonify({"error": "Internal server error", "details": str(e)}), 500

    except Exception as e:
        logger.error("Error in add_vessel_of_interest_web: %s", str(e), exc_info=Settings.EXEC_INFO_API)
        write_audit_log("Error in add_vessel_of_interest_web", __name__, {"client-form": str(request.form), "info": str(e)}, "ERROR")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@vessel_of_interest_bp.route('/get/all', methods=['GET'])
def get_all_vessel_of_interest_web():
    '''
    GET /api/v1/vessel_of_interest/get/all
    Returns all vessels of interest
    '''

    try:
        results = get_all_vessel_of_interest()

        data = []
        for voi in results:
            data.append({
                "vessel_of_interest_id": voi.vessel_of_interest_id,
                "vessel_of_interest_desc_name": voi.vessel_of_interest_desc_name,
                "vessel_of_interest_description": voi.vessel_of_interest_description,
                "vessel_of_interest_mmsi": voi.vessel_of_interest_mmsi,
                "vessel_of_interest_imo": voi.vessel_of_interest_imo
            })

        return jsonify({
            "status": "success",
            "count": len(data),
            "data": data
        }), 200

    except Exception as e:
        logger.error("Error in get_all_vessel_of_interest_web: %s", str(e), exc_info=Settings.EXEC_INFO_API)
        write_audit_log("Error in get_all_vessel_of_interest_web", __name__, {"info": str(e)}, "ERROR")
        return jsonify({"error": "Internal get_all_vessel_of_interest_web error", "details": str(e)}), 500

@vessel_of_interest_bp.route('/<int:vessel_of_interest_id>', methods=['GET'])
def get_vessel_of_interest_by_vessel_of_interest_id_web(vessel_of_interest_id):
    '''
    GET /api/v1/vessel_of_interest/<int:vessel_of_interest>
    Returns details of vessel with given vessel_of_interest
    '''

    try:
        voi = get_vessel_of_interest_by_vessel_of_interest_id(vessel_of_interest_id)
        if not voi:
            return jsonify({"error": f"Vessel of interest with ID {vessel_of_interest_id} not found."}), 404
        return jsonify({
            "status": "success",
            "data": {
                "vessel_of_interest_id": voi.vessel_of_interest_id,
                "vessel_of_interest_desc_name": voi.vessel_of_interest_desc_name,
                "vessel_of_interest_description": voi.vessel_of_interest_description,
                "vessel_of_interest_mmsi": voi.vessel_of_interest_mmsi,
                "vessel_of_interest_imo": voi.vessel_of_interest_imo
            }
        }), 200

    except Exception as e:
        logger.error("Error in get_vessel_of_interest_by_vessel_of_interest_id: %s", str(e), exc_info=Settings.EXEC_INFO_API)
        write_audit_log("Error in get_vessel_of_interest_by_vessel_of_interest_id", __name__, {"info": str(e)}, "ERROR")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
