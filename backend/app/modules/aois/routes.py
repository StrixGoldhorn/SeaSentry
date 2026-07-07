# backend/app/modules/aois/routes.py
# for api routes relating to aoi queries

import json
from flask import Blueprint, request, jsonify

from shapely.geometry import Polygon, box
from geoalchemy2.shape import from_shape

from app.models.areaofinterest import AreaOfInterest
from app.core.config import Settings
from app.utils.aoi_helpers import (add_rectangle_aoi_to_db, add_polygon_aoi_to_db,
                                   get_all_aois, get_aoi_polygon_vertices, get_aoi_by_id,
                                   update_aoi_in_db,
                                   delete_aoi_in_db,
                                   check_if_aoi_name_exists)
from app.utils.audit_log_helpers import write_audit_log
from app.modules.scrapers.scrape import run_force_all_scrapers_for_aoi
import logging

logger = logging.getLogger(__name__)
aois_bp = Blueprint('aois', __name__, url_prefix='/api/v1/aois')

@aois_bp.route('/add/box', methods=['POST'])
def add_aoi_box():
    '''
    POST /api/v1/aois/add/box
    Adds specified bounding box.
    
    Query Params:
    - lat_min, lat_max, long_min, long_max: float (bounding box)
    - name: str (name of AOI)
    - desc: str (description of AOI)
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
            return jsonify({"error": "Name of AOI expected."}), 400

        desc = str(request.form.get("desc"))

        if check_if_aoi_name_exists(name):
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

    except Exception as e:
        logger.error("Error in add_aoi_box: %s", e, exc_info=Settings.EXEC_INFO_API)
        write_audit_log("Error in add_aoi_box", __name__, {"client-form": str(request.form), "info": str(e)}, "ERROR")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@aois_bp.route('/add/polygon', methods=['POST'])
def add_aoi_polygon():
    '''
    POST /api/v1/aois/add/polygon
    Adds specified bounding polygon.
    
    Query Params:
    - coords: [[long1, lat1], [long2, lat2], [long3, lat3], ..., [long1, lat1]] (polygon bounding AOI. last coords should be same as first coords. else it will automatically close the loop, which may lead to unexpected behaviours.)
    - name: str (name of AOI)
    - desc: str (description of AOI)
    '''

    try:
        name = str(request.form.get("name"))
        if name is None or name.strip() == "":
            return jsonify({"error": "Name of AOI expected."}), 400

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
        except (json.JSONDecodeError, IndexError, TypeError, ValueError):
            return jsonify({"error": "Invalid coordinates format. Array of [long, lat] expected."}), 400

        if check_if_aoi_name_exists(name):
            return jsonify({"error": f"AOI with name '{name}' already exists."}), 403

        try:
            from shapely.geometry import Polygon
            from geoalchemy2.shape import from_shape

            poly = Polygon(shapely_coords)

            if not poly.is_valid:
                return jsonify({"error": "Invalid polygon geometry (self-intersecting or degenerate)."}), 400

            geom_wkb = from_shape(poly, srid=4326)

            area_of_interest_id = add_polygon_aoi_to_db(name, geom_wkb, desc)

            return jsonify({
                "status": "success",
                "area_of_interest_id": area_of_interest_id
            }), 201

        except Exception as e:
            logger.error("Error while adding polygon to DB: %s", e, exc_info=True)
            write_audit_log("Error adding polygon AOI", __name__, {"name": name, "info": str(e)}, "ERROR")
            return jsonify({"error": "Internal server error", "details": str(e)}), 500

    except Exception as e:
        logger.error("Error in add_aoi_polygon: %s", e, exc_info=Settings.EXEC_INFO_API)
        write_audit_log("Error in add_aoi_polygon", __name__, {"client-form": str(request.form), "info": str(e)}, "ERROR")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@aois_bp.route('/get/all', methods=['GET'])
def get_all_aois_web():
    '''
    GET /api/v1/aois/get/all
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
                "area_of_interest_polygon": get_aoi_polygon_vertices(aoi),
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

@aois_bp.route('/<int:aoi_id>', methods=['GET'])
def get_aoi_by_id_web(aoi_id):
    '''
    GET /api/v1/aois/<int:aoi_id>
    Returns details of AOI with given ID
    '''

    try:
        aoi = get_aoi_by_id(aoi_id)
        if not aoi:
            return jsonify({"error": f"AOI with ID {aoi_id} not found."}), 404
        return jsonify({
            "status": "success",
            "data": {
                "area_of_interest_id": aoi.area_of_interest_id,
                "area_of_interest_timestamp": aoi.area_of_interest_timestamp,
                "area_of_interest_name": aoi.area_of_interest_name,
                "area_of_interest_description": aoi.area_of_interest_description,
                "area_of_interest_polygon": get_aoi_polygon_vertices(aoi),
            }
        }), 200

    except Exception as e:
        logger.error("Error in get_aoi_by_id_web: %s", e, exc_info=Settings.EXEC_INFO_API)
        write_audit_log("Error in get_aoi_by_id_web", __name__, {"info": str(e)}, "ERROR")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@aois_bp.route('/<int:aoi_id>/update', methods=['POST', 'PATCH'])
def update_aoi_by_id(aoi_id):
    '''
    POST/PATCH /api/v1/aois/<aoi_id>/update
    Updates an existing Area of Interest. Supports partial updates.
    
    Query Params (all optional, but at least one required):
    - name: str (new name of AOI)
    - desc: str (new description of AOI)
    - coords: str (JSON array of [[long, lat], ...] for polygon update)
    - lat_min, lat_max, long_min, long_max: float (for bounding box update)
    '''

    try:
        name_raw = request.form.get("name")
        desc_raw = request.form.get("desc")
        coords_raw = request.form.get("coords")

        name = str(name_raw).strip() if name_raw is not None else None
        desc = str(desc_raw).strip() if desc_raw is not None else None

        bbox_params = ["lat_min", "lat_max", "long_min", "long_max"]
        bbox_values = [request.form.get(p, type=float) for p in bbox_params]
        has_bbox = all(v is not None for v in bbox_values)

        if not name and not desc and not coords_raw and not has_bbox:
            return jsonify({"error": "Requires at least 1 field to update."}), 400

        if name is not None and check_if_aoi_name_exists(name):
            return jsonify({"error": f"AOI with name '{name}' already exists."}), 403

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

        success = update_aoi_in_db(
            aoi_id=aoi_id,
            name=name,
            desc=desc,
            geometry_wkb=geom_wkb
        )

        if not success:
            return jsonify({"error": f"AOI with ID {aoi_id} not found."}), 404

        write_audit_log("Updated AOI", __name__, {"aoi_id": aoi_id, "client-form": str(request.form)}, "INFO")
        return jsonify({"status": "success", "aoi_id": aoi_id, "message": "AOI updated successfully."}), 200

    except Exception as e:
        logger.error("Error in update_aoi: %s", e, exc_info=Settings.EXEC_INFO_API)
        write_audit_log("Error in update_aoi", __name__, {"aoi_id": aoi_id, "info": str(e)}, "ERROR")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@aois_bp.route('/<int:aoi_id>/delete', methods=['DELETE'])
def delete_aoi_by_id_web(aoi_id):
    '''
    DELETE /api/v1/aois/<aoi_id>/delete
    Deletes an existing Area of Interest.

    Query Param:
    - aoi_name: str (Name of AOI to be deleted, so that users can't spam through aoi_ids and accidentally delete)
    '''
    try:
        aoi_name = request.args.get("aoi_name")

        if not aoi_name:
            return jsonify({"error": "Missing required query parameter: 'aoi_name'."}), 400

        aoi = get_aoi_by_id(aoi_id)
        if not aoi:
            return jsonify({"error": f"AOI with ID {aoi_id} not found."}), 404

        if aoi.area_of_interest_name != aoi_name:
            return jsonify({"error": "'aoi_name' does not match the AOI with the given ID."}), 403

        delete_aoi_in_db(aoi_id)

        checkaoi = get_aoi_by_id(aoi_id)
        if not checkaoi:
            return jsonify({
                "status": "success", 
                "message": f"AOI '{aoi_name}' (ID: {aoi_id}) deleted successfully."
            }), 200
        else:
            logger.error("Failed to delete AOI with ID %d. User provided %s", aoi_id, str(request.args.get("aoi_name")))
            return jsonify({"error": "Internal server error: Failed to delete AOI."}), 500

    except Exception as e:
        logger.error("Error in delete_aoi_by_id_web: %s", str(e), exc_info=Settings.EXEC_INFO_API)
        write_audit_log("Error in delete_aoi_by_id_web", __name__, {"aoi_id": aoi_id, "info": str(e)}, "ERROR")

        return jsonify({"error": "Internal server error"}), 500

@aois_bp.route('/<int:aoi_id>/scrape', methods=['POST'])
def force_scrape_aoi_by_id_web(aoi_id):
    '''
    POST /api/v1/aois/<int:aoi_id>/scrape
    Forces enabled scrapers to start scanning the selected AOI instantly. Does not affect scheduled scrapes.
    '''

    try:
        aoi = get_aoi_by_id(aoi_id)
        if not aoi:
            return jsonify({"error": f"AOI with ID {aoi_id} not found."}), 404

        SCRAPER_CONFIGS = Settings.SCRAPER_CONFIGS
        threads = run_force_all_scrapers_for_aoi(aoi_id, SCRAPER_CONFIGS)

        return jsonify({
            "status": "success",
        }), 200

    except Exception as e:
        logger.error("Error in force_scrape_aoi_by_id_web: %s", e, exc_info=Settings.EXEC_INFO_API)
        write_audit_log("Error in force_scrape_aoi_by_id_web", __name__, {"info": str(e)}, "ERROR")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
