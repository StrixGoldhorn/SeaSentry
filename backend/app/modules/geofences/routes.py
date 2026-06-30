# backend/app/modules/geofences/routes.py
# for api routes relating to geofence queries

from flask import Blueprint, request, jsonify
from json import JSONDecodeError

from shapely.geometry import Polygon, box
from geoalchemy2.shape import from_shape

from app.models.geofence import Geofence
from app.core.config import Settings
from app.utils.geofence_helpers import (
    add_rectangle_geofence_to_db, add_polygon_geofence_to_db,
    get_all_geofences, get_geofence_polygon_vertices, get_geofence_by_id,
    update_geofence_in_db,
    delete_geofence_in_db,
    check_if_geofence_name_exists
    )
from app.utils.audit_log_helpers import write_audit_log

import json
import logging

logger = logging.getLogger(__name__)
geofences_bp = Blueprint('geofences', __name__, url_prefix='/api/v1/geofences')

@geofences_bp.route('/add/box', methods=['POST'])
def add_geofence_box():
    '''
    POST /api/v1/geofences/add/box
    Adds specified bounding box.
    
    Query Params:
    - lat_min, lat_max, long_min, long_max: float (bounding box)
    - name: str (name of geofence)
    - desc: str (description of geofence)
    '''

    try:
        bbox_params = ["lat_min", "lat_max", "long_min", "long_max"]
        bbox_values = [request.form.get(p, type=float) for p in bbox_params]
        has_bbox = all(v is not None for v in bbox_values)
        bbox = dict(zip(bbox_params, bbox_values)) if has_bbox else None

        if has_bbox is False:
            return jsonify({"error": "Bounding box expected."}), 400

        name = str(request.form.get("name"))
        if name is None or name.strip() == "":
            return jsonify({"error": "Name of geofence expected."}), 400

        desc = str(request.form.get("desc"))

        if check_if_geofence_name_exists(name):
            return jsonify({"error": f"Geofence with name '{name}' already exists."}), 403

        try:
            geofence_id = add_rectangle_geofence_to_db(name, bbox["long_min"], bbox["long_max"], bbox["lat_min"], bbox["lat_max"], desc)
            return jsonify({
                "status": "success",
                "geofence_id": geofence_id
            }), 201

        except Exception as e:
            logger.error("Error while adding to DB in add_geofence_box: %s", e, exc_info=Settings.EXEC_INFO_API)
            write_audit_log("Error while adding to DB in add_geofence_box", __name__, {"client-form": str(request.form), "info": str(e)}, "ERROR")
            return jsonify({"error": "Internal server error", "details": str(e)}), 500

    except Exception as e:
        logger.error("Error in add_geofence_box: %s", e, exc_info=Settings.EXEC_INFO_API)
        write_audit_log("Error in add_geofence_box", __name__, {"client-form": str(request.form), "info": str(e)}, "ERROR")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@geofences_bp.route('/add/polygon', methods=['POST'])
def add_geofence_polygon():
    '''
    POST /api/v1/geofences/add/polygon
    Adds specified bounding polygon.
    
    Query Params:
    - coords: [[long1, lat1], [long2, lat2], [long3, lat3], ..., [long1, lat1]] (polygon bounding geofence. last coords should be same as first coords. else it will automatically close the loop, which may lead to unexpected behaviours.)
    - name: str (name of geofence)
    - desc: str (description of geofence)
    '''

    try:
        name = str(request.form.get("name"))
        if name is None or name.strip() == "":
            return jsonify({"error": "Name of geofence expected."}), 400

        desc = str(request.form.get("desc"))

        coords_raw = request.form.get("coords")
        if coords_raw is None:
            return jsonify({"error": "Array of [long, lat] expected."}), 400

        try:
            coords_list = json.loads(coords_raw)

            if not isinstance(coords_list, list) or len(coords_list) < 3:
                raise ValueError("Polygon must have at least 3 points.")

            shapely_coords = [(float(c[0]), float(c[1])) for c in coords_list]

            # Check if polygon is closed (first point == last point)
            if shapely_coords[0] != shapely_coords[-1]:
                shapely_coords.append(shapely_coords[0]) # Close the loop
        except (JSONDecodeError, IndexError, TypeError, ValueError):
            return jsonify({"error": "Invalid coordinates format. Array of [long, lat] expected."}), 400

        if check_if_geofence_name_exists(name):
            return jsonify({"error": f"Geofence with name '{name}' already exists."}), 403

        try:

            poly = Polygon(shapely_coords)

            if not poly.is_valid:
                return jsonify({"error": "Invalid polygon geometry (self-intersecting or degenerate)."}), 400

            geom_wkb = from_shape(poly, srid=4326)

            geofence_id = add_polygon_geofence_to_db(name, geom_wkb, desc)

            return jsonify({
                "status": "success",
                "geofence_id": geofence_id
            }), 201

        except Exception as e:
            logger.error("Error while adding polygon to DB: %s", e, exc_info=True)
            write_audit_log("Error adding polygon geofence", __name__, {"name": name, "info": str(e)}, "ERROR")
            return jsonify({"error": "Internal server error", "details": str(e)}), 500

    except Exception as e:
        logger.error("Error in add_geofence_polygon: %s", e, exc_info=Settings.EXEC_INFO_API)
        write_audit_log("Error in add_geofence_polygon", __name__, {"client-form": str(request.form), "info": str(e)}, "ERROR")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@geofences_bp.route('/get/all', methods=['GET'])
def get_all_geofences_web():
    '''
    GET /api/v1/geofences/get/all
    Query for all geofences
    '''

    try:
        data = []
        all_geofences = get_all_geofences()
        for geofence in all_geofences:
            data.append({
                "geofence_id": geofence.geofence_id,
                "geofence_timestamp": geofence.geofence_timestamp,
                "geofence_name": geofence.geofence_name,
                "geofence_description": geofence.geofence_description,
                "geofence_polygon": get_geofence_polygon_vertices(geofence),
            })
        return jsonify({
            "status": "success",
            "count": len(data),
            "data": data
        }), 200

    except Exception as e:
        logger.error("Error in get_all_geofences_web: %s", e, exc_info=Settings.EXEC_INFO_API)
        write_audit_log("Error in get_all_geofences_web", __name__, {"info": str(e)}, "ERROR")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@geofences_bp.route('/<int:geofence_id>', methods=['GET'])
def get_geofence_by_id_web(geofence_id):
    '''
    GET /api/v1/geofences/<int:geofence_id>
    Returns details of Geofence with given ID
    '''

    try:
        geofence = get_geofence_by_id(geofence_id)
        if not geofence:
            return jsonify({"error": f"Geofence with ID {geofence_id} not found."}), 404
        return jsonify({
            "status": "success",
            "data": {
                "geofence_id": geofence.geofence_id,
                "geofence_timestamp": geofence.geofence_timestamp,
                "geofence_name": geofence.geofence_name,
                "geofence_description": geofence.geofence_description,
                "geofence_polygon": get_geofence_polygon_vertices(geofence),
            }
        }), 200

    except Exception as e:
        logger.error("Error in get_geofence_by_id_web: %s", e, exc_info=Settings.EXEC_INFO_API)
        write_audit_log("Error in get_geofence_by_id_web", __name__, {"info": str(e)}, "ERROR")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@geofences_bp.route('/<int:geofence_id>/update', methods=['POST', 'PATCH'])
def update_geofence_by_id(geofence_id):
    '''
    POST/PATCH /api/v1/geofences/<geofence_id>/update
    Updates an existing Geofence. Supports partial updates.
    
    Query Params (all optional, but at least one required):
    - name: str (new name of Geofence)
    - desc: str (new description of Geofence)
    - coords: str (JSON array of [[long, lat], ...] for polygon update)
    - lat_min, lat_max, long_min, long_max: float (for bounding box update)
    '''

    try:
        name_raw = request.form.get("name")
        desc_raw = request.form.get("desc")
        coords_raw = request.form.get("coords")

        bbox_params = ["lat_min", "lat_max", "long_min", "long_max"]
        bbox_values = [request.form.get(p, type=float) for p in bbox_params]
        has_bbox = all(v is not None for v in bbox_values)

        if not name_raw and not desc_raw and not coords_raw and not has_bbox:
            return jsonify({"error": "Requires at least 1 field to update."}), 400

        if coords_raw is not None and has_bbox:
            return jsonify({"error": "Provide either 'coords' for a polygon OR bounding box parameters, not both."}), 400

        geom_wkb = None
        if coords_raw is not None:
            try:
                coords_list = json.loads(coords_raw)
                if not isinstance(coords_list, list) or len(coords_list) < 3:
                    raise ValueError("Polygon must have at least 3 points.")

                shapely_coords = [(float(c[0]), float(c[1])) for c in coords_list]
                if shapely_coords[0] != shapely_coords[-1]:
                    shapely_coords.append(shapely_coords[0])

                poly = Polygon(shapely_coords)
                if not poly.is_valid:
                    return jsonify({"error": "Invalid polygon geometry."}), 400

                geom_wkb = from_shape(poly, srid=4326)
            except (json.JSONDecodeError, IndexError, TypeError, ValueError):
                return jsonify({"error": "Invalid coordinates format."}), 400

        elif has_bbox:
            geom_wkb = from_shape(box(bbox_values[2], bbox_values[0], bbox_values[3], bbox_values[1]), srid=4326)

        success = update_geofence_in_db(
            geofence_id=geofence_id,
            name=str(name_raw).strip() if name_raw is not None else None,
            desc=str(desc_raw).strip() if desc_raw is not None else None,
            geometry_wkb=geom_wkb
        )

        if not success:
            return jsonify({"error": f"Geofence with ID {geofence_id} not found."}), 404

        write_audit_log("Updated Geofence", __name__, {"geofence_id": geofence_id, "client-form": str(request.form)}, "INFO")
        return jsonify({"status": "success", "geofence_id": geofence_id, "message": "Geofence updated successfully."}), 200

    except Exception as e:
        logger.error("Error in update_geofence_by_id: %s", e, exc_info=Settings.EXEC_INFO_API)
        write_audit_log("Error in update_geofence_by_id", __name__, {"geofence_id": geofence_id, "info": str(e)}, "ERROR")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@geofences_bp.route('/<int:geofence_id>/delete', methods=['DELETE'])
def delete_geofence_by_id_web(geofence_id):
    '''
    DELETE /api/v1/geofences/<geofence_id>/delete
    Deletes an existing Geofence.

    Query Param:
    - geofence_name: str (Name of Geofence to be deleted, so that users can't spam through geofence_ids and accidentally delete)
    '''
    try:
        geofence_name = request.args.get("geofence_name")

        if not geofence_name:
            return jsonify({"error": "Missing required query parameter: 'geofence_name'."}), 400

        geofence = get_geofence_by_id(geofence_id)
        if not geofence:
            return jsonify({"error": f"Geofence with ID {geofence_id} not found."}), 404

        if geofence.geofence_name != geofence_name:
            return jsonify({"error": "'geofence_name' does not match the Geofence with the given ID."}), 403

        delete_geofence_in_db(geofence_id)

        checkgeofence = get_geofence_by_id(geofence_id)
        if not checkgeofence:
            return jsonify({
                "status": "success", 
                "message": f"Geofence '{geofence_name}' (ID: {geofence_id}) deleted successfully."
            }), 200
        else:
            logger.error("Failed to delete Geofence with ID %d. User provided %s", geofence_id, str(request.args.get("geofence_name")))
            return jsonify({"error": "Internal server error: Failed to delete Geofence."}), 500

    except Exception as e:
        logger.error("Error in delete_geofence_by_id_web: %s", str(e), exc_info=Settings.EXEC_INFO_API)
        write_audit_log("Error in delete_geofence_by_id_web", __name__, {"geofence_id": geofence_id, "info": str(e)}, "ERROR")

        return jsonify({"error": "Internal server error"}), 500
