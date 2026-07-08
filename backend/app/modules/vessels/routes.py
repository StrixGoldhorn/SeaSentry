# backend/app/modules/vessels/routes.py
# for api routes relating to vessel queries, eg /api/v1/vessels, /api/v1/history

import csv
import io
import json
from flask import Blueprint, request, jsonify, Response, redirect
from datetime import datetime, timedelta, timezone
from sqlalchemy import func
from geoalchemy2.shape import to_shape

from app.core.config import Settings
from app.models.vessel import VesselData, VesselLocation
from app.utils.vessel_helpers import (get_all_vessels_in_bbox, get_vessel_by_vessel_data_id, get_all_vessels,
                                      update_vessel_data_in_db, get_vessel_history_stream,
                                      get_vessel_history_by_vessel_data_id)
from app.utils.audit_log_helpers import write_audit_log

import logging

logger = logging.getLogger(__name__)
vessels_bp = Blueprint('vessels', __name__, url_prefix='/api/v1/vessels')

@vessels_bp.route('/bbox', methods=['GET'])
def get_vessels_in_bbox():
    '''
    GET /api/v1/vessels/bbox
    Query vessel positions within a bounding box
    
    Query Params:
    - time_within: int (time in seconds, default 24hrs ie 60 * 60 * 24)
    - lat_min, lat_max, long_min, long_max: float (bounding box)
    - limit: int (default 500, max 5000)
    '''

    try:

        bbox_params = ["lat_min", "lat_max", "long_min", "long_max"]
        bbox_values = [request.args.get(p, type=float) for p in bbox_params]
        has_bbox = all(v is not None for v in bbox_values)
        bbox = dict(zip(bbox_params, bbox_values)) if has_bbox else None

        if has_bbox is False:
            return jsonify({"error": "Bounding box expected."}), 400

        try:
            limit = min(int(request.args.get("limit", default = 500)), 5000)
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid limit format. Must be an integer."}), 400

        try:
            time_within = int(request.args.get('time_within', default = 60 * 60 * 24))
            time_lower_bound = datetime.now(timezone.utc) - timedelta(seconds = time_within)
        except ValueError:
            return jsonify({"error": "Invalid time_within format. Ensure it is in seconds."}), 400

        envelope = func.ST_MakeEnvelope(
            bbox["long_min"], bbox["lat_min"],
            bbox["long_max"], bbox["lat_max"],
            4326
        )

        results = get_all_vessels_in_bbox(envelope, time_lower_bound, limit)

        data = []
        for location, vessel in results:
            geom_shape = to_shape(location.vessel_location_coords)
            lon, lat = geom_shape.x, geom_shape.y

            data.append({
                "vessel_location_id": location.vessel_location_id,
                "vessel_data_id": vessel.vessel_data_id,
                "mmsi": vessel.vessel_data_mmsi,
                "imo": vessel.vessel_data_imo,
                "ship_name": vessel.vessel_data_ship_name,
                "ship_type": vessel.vessel_data_ship_type,
                "flag": vessel.vessel_data_flag,
                "length_meters": vessel.vessel_data_length_meters,
                "beam_meters": vessel.vessel_data_beam_meters,
                "user_tags": vessel.vessel_data_user_tags,
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
        logger.error("Error in get_vessels_in_bbox: %s", e, exc_info=Settings.EXEC_INFO_API)
        write_audit_log("Error in get_vessels_in_bbox", __name__, {"info": str(e)}, "ERROR")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

# Easter egg or something idk
BAD_BAD_NO_NO = ["'", "\"", "\\", "/", "-", ";", "#", "%", "?", "`", "*", "|", "&", "+"]
def count_bad_chars(text):
    if not text:
        return 0
    return sum(1 for char in text if char in BAD_BAD_NO_NO)

@vessels_bp.route('/all', methods=['GET'])
def get_all_vessels_web():
    '''
    GET /api/v1/vessels/all
    Query for all vessels in database
    
    Query Params:
    - querystr: string, will be matched with name, mmsi, or imo LIKE given string
    - name: string, will be matched with name LIKE given string
    - mmsi: string, will be matched with mmsi LIKE given string
    - imo: string, will be matched with imo LIKE given string
    - shiptype: string, will be matched with shiptype LIKE given string
    - flag: string, will be matched with flag LIKE given string
    - limit: integer, max number of records to return (e.g., 50)
    - offset: integer, number of records to skip for pagination (e.g., 0)
    '''

    try:
        querystr_str = request.args.get('querystr')
        name_str = request.args.get('name')
        mmsi_str = request.args.get('mmsi')
        imo_str = request.args.get('imo')
        shiptype_str = request.args.get('shiptype')
        flag_str = request.args.get('flag')
        limit_str = request.args.get('limit')
        offset_str = request.args.get('offset')


        if Settings.ENABLE_EASTER_EGG:
            if count_bad_chars(querystr_str)+count_bad_chars(name_str)+count_bad_chars(mmsi_str)+count_bad_chars(imo_str)\
            +count_bad_chars(shiptype_str)+count_bad_chars(flag_str) > Settings.EASTER_EGG_TOLERANCE:
                return redirect('https://xkcd.com/327')

        querystr = None
        name = None
        mmsi = None
        imo = None
        shiptype = None
        flag = None
        limit = None
        offset = None

        querystr = querystr_str.strip() if querystr_str else None
        name = name_str.strip() if name_str else None

        if mmsi_str:
            mmsi_clean = str(mmsi_str).strip()
            if not mmsi_clean.isdigit():
                return jsonify({"status": "error", "error": "Invalid mmsi format."}), 400
            mmsi = mmsi_clean

        if imo_str:
            imo_clean = str(imo_str).strip()
            if not imo_clean.isdigit():
                return jsonify({"status": "error", "error": "Invalid imo format."}), 400
            imo = imo_clean

        shiptype = shiptype_str.strip() if shiptype_str else None
        flag = flag_str.strip() if flag_str else None

        if limit_str:
            try:
                limit = int(limit_str)
            except ValueError:
                return jsonify({"status": "error", "error": "Invalid limit format. Must be an integer"}), 400

        if offset_str:
            try:
                offset = int(offset_str)
            except ValueError:
                return jsonify({"status": "error", "error": "Invalid offset format. Must be an integer"}), 400


        results = get_all_vessels(querystr=querystr, name=name, mmsi=mmsi, imo=imo, shiptype=shiptype, flag=flag, limit=limit, offset=offset)

        data = []
        for vessel in results:
            data.append({
                "vessel_data_id": vessel.vessel_data_id,
                "mmsi": vessel.vessel_data_mmsi,
                "imo": vessel.vessel_data_imo,
                "ship_name": vessel.vessel_data_ship_name,
                "ship_type": vessel.vessel_data_ship_type,
                "flag": vessel.vessel_data_flag,
                "length_meters": vessel.vessel_data_length_meters,
                "beam_meters": vessel.vessel_data_beam_meters,
                "user_tags": vessel.vessel_data_user_tags
            })

        return jsonify({
            "status": "success",
            "filters": {
                "querystr": querystr,
                "name": name,
                "mmsi": mmsi,
                "imo": imo,
                "shiptype": shiptype,
                "flag": flag,
                "limit": limit,
                "offset": offset
            },
            "count": len(data),
            "data": data
        }), 200

    except Exception as e:
        logger.error("Error in get_all_vessels_web: %s", e, exc_info=Settings.EXEC_INFO_API)
        write_audit_log("Error in get_all_vessels_web", __name__, {"info": str(e)}, "ERROR")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@vessels_bp.route('/exportArea', methods=['GET'])
def get_vessel_export_area():
    '''
    GET /api/v1/vessels/exportArea
    Query vessel historical positions within a bounding box and time range.
    
    Query Params:
    - lat_min, lat_max, long_min, long_max: float (optional, bounding box, default whole Earth)
    - start_time: str (optional, datetime, eg '2026-06-07T12:00:00Z', default datetime.min)
    - end_time: str (optional, datetime, default datetime.now)
    - format: str (optional, 'json', 'geojson', or 'csv', default 'json')
    '''

    try:
        bbox_params = ["lat_min", "lat_max", "long_min", "long_max"]
        bbox_values = [request.args.get(p, type=float) for p in bbox_params]
        has_bbox = all(v is not None for v in bbox_values)
        bbox = dict(zip(bbox_params, bbox_values)) if has_bbox else None

        if not has_bbox:
            bbox = {
                "lat_min": -90.0,
                "lat_max": 90.0,
                "long_min": -180.0,
                "long_max": 180.0
            }
        else:
            bbox = dict(zip(bbox_params, bbox_values))

        start_time_str = request.args.get('start_time')
        end_time_str = request.args.get('end_time')

        try:
            if not start_time_str:
                start_time = datetime.min
            else:
                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))

            if not end_time_str:
                end_time = datetime.now(timezone.utc)
            else:
                end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))

            if start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=timezone.utc)
            if end_time.tzinfo is None:
                end_time = end_time.replace(tzinfo=timezone.utc)

        except ValueError:
            return jsonify({"error": "Invalid time format."}), 400

        if start_time >= end_time:
            return jsonify({"error": "start_time must be before end_time."}), 400

        export_format = request.args.get('format', 'json').lower()
        if export_format not in ['json', 'geojson', 'csv']:
            return jsonify({"error": "Invalid format. Choose 'json', 'geojson', or 'csv'."}), 400

        envelope = func.ST_MakeEnvelope(
            bbox["long_min"], bbox["lat_min"],
            bbox["long_max"], bbox["lat_max"],
            4326
        )

        vessel_stream = get_vessel_history_stream(envelope, start_time, end_time)

        def generate_csv(stream):
            fieldnames = [
                "location_id", "vessel_data_id", "mmsi", "imo", "ship_name", 
                "ship_type", "length_meters", "beam_meters", "user_tags",
                "flag", "latitude", "longitude", "speed_knots", 
                "course_deg", "heading_deg", "rate_of_turn", "nav_status", "timestamp"
            ]

            class CSVStream:
                def __init__(self):
                    self.buffer = io.StringIO()
                    self.writer = csv.writer(self.buffer)
                def write(self, row):
                    self.writer.writerow(row)
                    val = self.buffer.getvalue()
                    self.buffer.seek(0)
                    self.buffer.truncate(0)
                    return val

            stream_writer = CSVStream()
            yield stream_writer.write(fieldnames) 

            for location, vessel in stream:
                geom_shape = to_shape(location.vessel_location_coords)
                row = [
                    location.vessel_location_id, vessel.vessel_data_id,
                    vessel.vessel_data_mmsi, vessel.vessel_data_imo,
                    vessel.vessel_data_ship_name, vessel.vessel_data_ship_type,
                    vessel.vessel_data_length_meters, vessel.vessel_data_beam_meters,
                    vessel.vessel_data_user_tags, vessel.vessel_data_flag,
                    geom_shape.y, geom_shape.x,
                    location.vessel_location_speed_knots, location.vessel_location_course_deg,
                    location.vessel_location_heading_deg, location.vessel_location_rate_of_turn_deg_per_sec,
                    location.vessel_location_nav_status,
                    location.vessel_location_timestamp.isoformat() if location.vessel_location_timestamp else None
                ]
                yield stream_writer.write(row)

        def generate_geojson(stream):
            yield '{"type": "FeatureCollection", "features": ['
            first = True

            for location, vessel in stream:
                geom_shape = to_shape(location.vessel_location_coords)
                feature = {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [geom_shape.x, geom_shape.y]},
                    "properties": {
                        "vessel_location_id": location.vessel_location_id,
                        "vessel_data_id": vessel.vessel_data_id,
                        "mmsi": vessel.vessel_data_mmsi,
                        "imo": vessel.vessel_data_imo,
                        "ship_name": vessel.vessel_data_ship_name,
                        "ship_type": vessel.vessel_data_ship_type,
                        "flag": vessel.vessel_data_flag,
                        "length_meters": vessel.vessel_data_length_meters,
                        "beam_meters": vessel.vessel_data_beam_meters,
                        "user_tags": vessel.vessel_data_user_tags,
                        "speed_knots": location.vessel_location_speed_knots,
                        "course_deg": location.vessel_location_course_deg,
                        "heading_deg": location.vessel_location_heading_deg,
                        "rate_of_turn": location.vessel_location_rate_of_turn_deg_per_sec,
                        "nav_status": location.vessel_location_nav_status,
                        "timestamp": location.vessel_location_timestamp.isoformat() if location.vessel_location_timestamp else None
                    }
                }
                if not first:
                    yield ','
                else:
                    first = False
                yield json.dumps(feature)

            yield ']}'

        def generate_json(stream):
            yield '{"status": "success", "data": ['
            first = True

            for location, vessel in stream:
                geom_shape = to_shape(location.vessel_location_coords)
                item = {
                    "vessel_location_id": location.vessel_location_id,
                    "vessel_data_id": vessel.vessel_data_id,
                    "mmsi": vessel.vessel_data_mmsi,
                    "imo": vessel.vessel_data_imo,
                    "ship_name": vessel.vessel_data_ship_name,
                    "ship_type": vessel.vessel_data_ship_type,
                    "flag": vessel.vessel_data_flag,
                    "length_meters": vessel.vessel_data_length_meters,
                    "beam_meters": vessel.vessel_data_beam_meters,
                    "user_tags": vessel.vessel_data_user_tags,
                    "latitude": geom_shape.y, 
                    "longitude": geom_shape.x,
                    "speed_knots": location.vessel_location_speed_knots,
                    "course_deg": location.vessel_location_course_deg,
                    "heading_deg": location.vessel_location_heading_deg,
                    "rate_of_turn": location.vessel_location_rate_of_turn_deg_per_sec,
                    "nav_status": location.vessel_location_nav_status,
                    "timestamp": location.vessel_location_timestamp.isoformat() if location.vessel_location_timestamp else None
                }
                if not first:
                    yield ','
                else:
                    first = False
                yield json.dumps(item)
            yield ']}'

        if export_format == 'csv':
            return Response(
                generate_csv(vessel_stream),
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment;filename=vessel_history.csv'}
            )

        elif export_format == 'geojson':
            return Response(
                generate_geojson(vessel_stream),
                mimetype='application/geo+json',
                headers={'Content-Disposition': 'attachment;filename=vessel_history.geojson'}
            )

        else:
            return Response(
                generate_json(vessel_stream),
                mimetype='application/json'
            )

    except Exception as e:
        logger.error("Error in get_vessel_export_area: %s", e, exc_info=Settings.EXEC_INFO_API)
        write_audit_log("Error in get_vessel_export_area", __name__, {"info": str(e)}, "ERROR")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@vessels_bp.route('/<int:vessel_data_id>', methods=['GET'])
def get_vessel_by_vessel_data_id_web(vessel_data_id):
    '''
    GET /api/v1/vessels/<int:vessel_data_id>
    Returns details of vessel with given vessel_data_id
    '''

    try:
        vessel = get_vessel_by_vessel_data_id(vessel_data_id)
        if not vessel:
            return jsonify({"error": f"Vessel with ID {vessel_data_id} not found."}), 404
        return jsonify({
            "status": "success",
            "data": {
                "vessel_data_id": vessel.vessel_data_id,
                "mmsi": vessel.vessel_data_mmsi,
                "imo": vessel.vessel_data_imo,
                "ship_name": vessel.vessel_data_ship_name,
                "ship_type": vessel.vessel_data_ship_type,
                "flag": vessel.vessel_data_flag,
                "length_meters": vessel.vessel_data_length_meters,
                "beam_meters": vessel.vessel_data_beam_meters,
                "user_tags": vessel.vessel_data_user_tags
            }
        }), 200

    except Exception as e:
        logger.error("Error in get_vessel_by_vessel_data_id_web: %s", e, exc_info=Settings.EXEC_INFO_API)
        write_audit_log("Error in get_vessel_by_vessel_data_id_web", __name__, {"info": str(e)}, "ERROR")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@vessels_bp.route('/<int:vessel_data_id>/update', methods=['POST', 'PATCH'])
def update_vessel_by_id(vessel_data_id):
    '''
    POST/PATCH /api/v1/vessels/<vessel_data_id>/update
    Updates an existing Vessel. Supports partial updates.
    
    Query Params (all optional, but at least one required):
    ship_name: str, new ship name of vessel
    ship_type: str, new ship type of vessel
    flag: str, new flag of vessel
    length_meters: int, new length meters of vessel
    beam_meters: int, new beam meters of vessel
    user_tags: array, new user tags of vessel
    '''

    try:
        ship_name = request.form.get("ship_name")
        ship_type = request.form.get("ship_type")
        flag = request.form.get("flag")
        length_meters = request.form.get("length_meters")
        beam_meters = request.form.get("beam_meters")
        user_tags = request.form.get("user_tags")

        if not any([ship_name, ship_type, flag, length_meters, beam_meters, user_tags]):
            return jsonify({"error": "Requires at least 1 field to update."}), 400

        try:
            parsed_length = int(length_meters) if length_meters else None
            parsed_beam = int(beam_meters) if beam_meters else None
        except ValueError:
            return jsonify({"error": "Invalid data format: length_meters and beam_meters must be valid integers."}), 400

        parsed_tags = None
        if user_tags is not None:
            if isinstance(user_tags, str):
                try:
                    parsed_tags = json.loads(user_tags)
                except json.JSONDecodeError:
                    return jsonify({"error": "Invalid data format: user_tags should be an array of strings."}), 400
            elif isinstance(user_tags, list):
                parsed_tags = user_tags


        success = update_vessel_data_in_db(
            vessel_data_id = vessel_data_id,
            ship_name = str(ship_name).strip() if ship_name else None,
            ship_type = str(ship_type).strip() if ship_type else None,
            flag = str(flag).strip() if flag else None,
            length_meters = parsed_length,
            beam_meters = parsed_beam,
            user_tags = parsed_tags
        )

        if not success:
            return jsonify({"error": f"Vessel with ID {vessel_data_id} not found."}), 404

        write_audit_log("Updated Vessel", __name__, {"vessel_data_id": vessel_data_id, "client-form": str(request.form)}, "INFO")
        return jsonify({"status": "success", "vessel_data_id": vessel_data_id, "message": "Vessel updated successfully."}), 200

    except Exception as e:
        logger.error("Error in update_vessel_by_id: %s", e, exc_info=Settings.EXEC_INFO_API)
        write_audit_log("Error in update_vessel_by_id", __name__, {"vessel_data_id": vessel_data_id, "info": str(e)}, "ERROR")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@vessels_bp.route('/<int:vessel_data_id>/history', methods=['GET'])
def get_vessel_history_by_vessel_data_id_web(vessel_data_id):
    '''
    GET /api/v1/vessels/<int:vessel_data_id>/history
    Returns list of vessel locations tagged to the vessel

    Query Params (all optional):
    start_time_str: (optional, datetime, eg '2026-06-07T12:00:00Z', default datetime.min)
    end_time_str: (optional, datetime, eg '2026-06-07T12:00:00Z', default datetime.now)
    '''

    start_time_str = request.args.get('start_time')
    end_time_str = request.args.get('end_time')

    try:
        if not start_time_str:
            start_time = datetime.min
        else:
            start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))

        if not end_time_str:
            end_time = datetime.now(timezone.utc)
        else:
            end_time = datetime.fromisoformat(end_time_str.replace('Z', '+00:00'))

        if start_time.tzinfo is None:
            start_time = start_time.replace(tzinfo=timezone.utc)
        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=timezone.utc)

    except ValueError:
        return jsonify({"error": "Invalid time format."}), 400

    if start_time >= end_time:
        return jsonify({"error": "start_time must be before end_time."}), 400

    try:
        locations = get_vessel_history_by_vessel_data_id(vessel_data_id, start_time, end_time)
        if not locations:
            return jsonify({"error": f"No history exists."}), 404

        loc_result = []
        for loc in locations:
            geom_shape = to_shape(loc.vessel_location_coords)
            lon, lat = geom_shape.x, geom_shape.y
            loc_result.append({
                "location_id": loc.vessel_location_id,
                "latitude": lat,
                "longitude": lon,
                "timestamp":  loc.vessel_location_timestamp.isoformat() if loc.vessel_location_timestamp else None,
                "speed_knots": loc.vessel_location_speed_knots,
                "course_deg": loc.vessel_location_course_deg,
                "heading_deg": loc.vessel_location_heading_deg,
                "rate_of_turn": loc.vessel_location_rate_of_turn_deg_per_sec,
                "nav_status": loc.vessel_location_nav_status
            })

        return jsonify({
            "status": "success",
            "data": loc_result,
            "count": len(loc_result),
        }), 200

    except Exception as e:
        logger.error("Error in get_vessel_history_by_vessel_data_id_web: %s", str(e), exc_info=Settings.EXEC_INFO_API)
        write_audit_log("Error in get_vessel_history_by_vessel_data_id_web", __name__, {"info": str(e)}, "ERROR")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500
