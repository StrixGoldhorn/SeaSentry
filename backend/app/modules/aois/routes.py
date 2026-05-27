# backend/app/modules/aois/routes.py
# for api routes relating to aoi queries

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta, timezone
from sqlalchemy import func
from geoalchemy2.shape import to_shape
from app.core.database import DBConn
from app.models.areaofinterest import AreaOfInterest
from app.core.config import Settings
from app.utils.geo_helpers import add_rectangle_aoi_to_db, get_all_aois, get_aoi_polygon_corners
from app.utils.audit_log_helpers import write_audit_log
import logging

logger = logging.getLogger(__name__)
aois_bp = Blueprint('aois', __name__, url_prefix='/api/v1/aois')

@aois_bp.route('/add/box', methods=['POST'])
def add_aoi_box():
    '''
    POST /api/v1/aois/add/box
    Query vessel positions within a bounding box
    
    Query Params:
    - lat_min, lat_max, long_min, long_max: float (bounding box)
    - name: str (name of AOI)
    - desc: str (description of AOI)
    '''

    session = DBConn.get_session()
    try:
        bbox_params = ["lat_min", "lat_max", "long_min", "long_max"]
        bbox_values = [request.form.get(p, type=float) for p in bbox_params]
        has_bbox = all(v is not None for v in bbox_values)
        bbox = dict(zip(bbox_params, bbox_values)) if has_bbox else None

        if has_bbox is False:
            return jsonify({"error": "Bounding box expected."}), 400

        name = str(request.form.get("name"))
        if name is None:
            return jsonify({"error": "Name of AOI expected."}), 400
        
        desc = str(request.form.get("desc"))

        def check_if_name_exists(name):
            query = session.query(AreaOfInterest).filter(AreaOfInterest.area_of_interest_name == name)
            res = query.all()
            if len(res) != 0: return True
            return False
        
        if check_if_name_exists(name):
            return jsonify({"error": f"AOI with name '{name}' already exists."}), 403

        try:
            aoi_id = add_rectangle_aoi_to_db(name, bbox["long_min"], bbox["long_max"], bbox["lat_min"], bbox["lat_max"], desc)
            return jsonify({
                "status": "success",
                "aoi_id": aoi_id
            }), 201
        
        except Exception as e:
            logger.error("Error while adding to DB in add_aoi_box: %s", e, exc_info=Settings.EXEC_INFO_API)
            write_audit_log("Error while adding to DB in add_aoi_box", __name__, {"client-form": str(request.form), "info": str(e)}, "ERROR")
            return jsonify({"error": "Internal server error", "details": str(e)}), 500
        
        finally:
            if session:
                DBConn.close_session()

    except Exception as e:
        logger.error("Error in add_aoi_box: %s", e, exc_info=Settings.EXEC_INFO_API)
        write_audit_log("Error in add_aoi_box", __name__, {"client-form": str(request.form), "info": str(e)}, "ERROR")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

    finally:
        if session:
            DBConn.close_session()

@aois_bp.route('/get/all', methods=['GET'])
def get_all_aois_web():
    '''
    POST /api/v1/aois/get/all
    Query for all AOIs
    '''

    try:
        data = []
        all_aois = get_all_aois()
        for aoi in all_aois:
            data.append({
                "area_of_interest_id": aoi.area_of_interest_id,
                "area_of_interest_timestamp": aoi.area_of_interest_timestamp,
                "area_of_interest_name": aoi.area_of_interest_name,
                "area_of_interest_description": aoi.area_of_interest_description,
                "area_of_interest_polygon": get_aoi_polygon_corners(aoi),
            })
        return jsonify({
            "status": "success",
            "count": len(data),
            "data": data
        }), 200

    except Exception as e:
        logger.error("Error in get_all_aois_web: %s", e, exc_info=Settings.EXEC_INFO_API)
        write_audit_log("Error in get_all_aois_web", __name__, {"info": str(e)}, "ERROR")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
