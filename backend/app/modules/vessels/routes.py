# backend/app/modules/vessels/routes.py
# for api routes relating to vessel queries, eg /api/v1/vessels, /api/v1/history

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta, timezone
from sqlalchemy import func
from geoalchemy2.shape import to_shape
from app.core.database import DBConn
from app.models.vessel import VesselData, VesselLocation
from app.core.config import Settings
import logging

logger = logging.getLogger(__name__)
vessels_bp = Blueprint('vessels', __name__, url_prefix='/api/v1/vessels')

@vessels_bp.route('/bbox', methods=['GET'])
def get_vessel_history():
    '''
    GET /api/v1/vessels/bbox
    Query vessel positions within a bounding box
    
    Query Params:
    - time_within: int (time in seconds, default 24hrs ie 60 * 60 * 24)
    - lat_min, lat_max, long_min, long_max: float (bounding box)
    - limit: int (default 50, max 1000)
    '''

    session = DBConn.get_session()
    try:
        time_within = int(request.args.get('time_within', default = 60 * 60 * 24))

        bbox_params = ["lat_min", "lat_max", "long_min", "long_max"]
        bbox_values = [request.args.get(p, type=float) for p in bbox_params]
        has_bbox = all(v is not None for v in bbox_values)
        bbox = dict(zip(bbox_params, bbox_values)) if has_bbox else None

        if has_bbox is False:
            return jsonify({"error": "Bounding box expected."}), 400

        limit = min(int(request.args.get("limit", default = 50)), 1000)

        query = session.query(VesselLocation, VesselData).join(
            VesselData,
            VesselLocation.vessel_location_vessel_data_id == VesselData.vessel_data_id,
        )

        if time_within:
            try:
                time_lower_bound = datetime.now(timezone.utc) - timedelta(seconds = time_within)
                query = query.filter(VesselLocation.vessel_location_timestamp >= time_lower_bound)
            except ValueError:
                return jsonify({"error": "Invalid time_within format. Ensure it is in seconds."}), 400

        envelope = func.ST_MakeEnvelope(
            bbox["long_min"], bbox["lat_min"],
            bbox["long_max"], bbox["lat_max"],
            4326
        )
        query = query.filter(
            VesselLocation.vessel_location_coords.ST_Within(envelope)
        )

        query = query.order_by(
            VesselLocation.vessel_location_vessel_data_id,
            VesselLocation.vessel_location_timestamp.desc()
        )

        query = query.distinct(VesselLocation.vessel_location_vessel_data_id)

        query = query.limit(limit)

        results = query.all()

        data = []
        for location, vessel in results:
            geom_shape = to_shape(location.vessel_location_coords)
            lon, lat = geom_shape.x, geom_shape.y

            data.append({
                "location_id": location.vessel_location_id,
                "vessel_data_id": vessel.vessel_data_id,
                "mmsi": vessel.vessel_data_mmsi,
                "imo": vessel.vessel_data_imo,
                "ship_name": vessel.vessel_data_ship_name,
                "ship_type": vessel.vessel_data_ship_type,
                "flag": vessel.vessel_data_flag,
                "latitude": lat,
                "longitude": lon,
                "speed_knots": location.vessel_location_speed_knots,
                "course_deg": location.vessel_location_course_deg,
                "heading_deg": location.vessel_location_heading_deg,
                "rate_of_turn": location.vessel_location_rate_of_turn_deg_per_sec,
                "nav_status": location.vessel_location_nav_status,
                "timestamp": location.vessel_location_timestamp.isoformat() if location.vessel_location_timestamp else None
            })

        return jsonify({
            "status": "success",
            "filters": {
                "time_within": time_within,
                "bbox": bbox,
                "limit": limit
            },
            "count": len(data),
            "data": data
        }), 200

    except Exception as e:
        logger.error("Error in get_vessel_history: %s", e, exc_info=Settings.EXEC_INFO_API)
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

    finally:
        if session:
            DBConn.close_session()
