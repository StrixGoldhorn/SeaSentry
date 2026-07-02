import pytest
import json
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from flask import Flask
from shapely.geometry import box

from app.utils.vessel_helpers import get_all_vessels_in_bbox
from app.models.vessel import VesselData, VesselLocation
from app.modules.vessels.routes import vessels_bp  # Make sure this import matches your actual blueprint name

@pytest.fixture
def app():
    '''
    Create and configure a new app instance for each test.
    '''
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(vessels_bp)
    return app

@pytest.fixture
def client(app):
    '''
    Create a test client for the app.
    '''
    return app.test_client()

# ==========================================
# Tests for GET /api/v1/vessels/bbox
# ==========================================

@patch('app.utils.vessel_helpers.DBConn')
def test_get_all_vessels_in_bbox_success(mock_db_conn):
    '''
    Test fetching vessels within a bounding box
    '''
    mock_session = MagicMock()
    mock_db_conn.get_session.return_value = mock_session

    mock_query = MagicMock()
    mock_session.query.return_value = mock_query

    mock_join_result = MagicMock()
    mock_query.join.return_value = mock_join_result

    mock_filter_result = MagicMock()
    mock_join_result.filter.return_value = mock_filter_result

    mock_order_result = MagicMock()
    mock_filter_result.order_by.return_value = mock_order_result

    mock_distinct_result = MagicMock()
    mock_order_result.distinct.return_value = mock_distinct_result

    mock_limit_result = MagicMock()
    mock_distinct_result.limit.return_value = mock_limit_result

    fake_vessel_loc = MagicMock(spec=VesselLocation)
    fake_vessel_loc.vessel_location_id = 1
    fake_vessel_loc.vessel_location_coords = "POINT(1 1)"

    fake_vessel_data = MagicMock(spec=VesselData)
    fake_vessel_data.vessel_data_id = 101
    fake_vessel_data.vessel_data_mmsi = 123456789

    mock_limit_result.all.return_value = [(fake_vessel_loc, fake_vessel_data)]

    envelope = box(10, 10, 20, 20)
    result = get_all_vessels_in_bbox(envelope, "2023-01-01", limit=10)

    assert len(result) == 1
    loc, data = result[0]
    assert loc.vessel_location_id == 1
    assert data.vessel_data_mmsi == 123456789

    mock_db_conn.close_session.assert_called_once()

@patch('app.utils.vessel_helpers.DBConn')
def test_get_all_vessels_in_bbox_empty_result(mock_db_conn):
    '''
    Test fetching vessels when none are found
    '''
    mock_session = MagicMock()
    mock_db_conn.get_session.return_value = mock_session

    mock_query = MagicMock()
    mock_session.query.return_value = mock_query

    mock_join = MagicMock()
    mock_query.join.return_value = mock_join

    mock_filter = MagicMock()
    mock_join.filter.return_value = mock_filter

    mock_order = MagicMock()
    mock_filter.order_by.return_value = mock_order

    mock_distinct = MagicMock()
    mock_order.distinct.return_value = mock_distinct

    mock_limit = MagicMock()
    mock_distinct.limit.return_value = mock_limit

    mock_limit.all.return_value = []

    envelope = box(10, 10, 20, 20)
    result = get_all_vessels_in_bbox(envelope, "2023-01-01", limit=10)

    assert result == []
    mock_db_conn.close_session.assert_called_once()

@patch('app.utils.vessel_helpers.DBConn')
def test_get_all_vessels_in_bbox_exception(mock_db_conn):
    '''
    Test handling of database exceptions
    '''
    mock_session = MagicMock()
    mock_db_conn.get_session.return_value = mock_session

    mock_query = MagicMock()
    mock_session.query.return_value = mock_query

    mock_join = MagicMock()
    mock_query.join.return_value = mock_join

    mock_filter = MagicMock()
    mock_join.filter.return_value = mock_filter

    mock_order = MagicMock()
    mock_filter.order_by.return_value = mock_order

    mock_distinct = MagicMock()
    mock_order.distinct.return_value = mock_distinct

    mock_limit = MagicMock()
    mock_distinct.limit.return_value = mock_limit

    mock_limit.all.side_effect = Exception("Database connection failed")

    fake_envelope = MagicMock()
    result = get_all_vessels_in_bbox(fake_envelope, "2023-01-01", limit=10)

    assert result == []
    mock_db_conn.close_session.assert_called_once()

# ==========================================
# Tests for GET /api/v1/vessels/<int:vessel_data_id>
# ==========================================

@patch('app.modules.vessels.routes.get_vessel_by_vessel_data_id')
def test_get_vessel_by_vessel_data_id_success(mock_get_vessel, client):
    '''
    Test GET /api/v1/vessels/<int:vessel_data_id> with valid ID
    '''
    mock_vessel = MagicMock()
    mock_vessel.vessel_data_id = 101
    mock_vessel.vessel_data_mmsi = 123456789
    mock_vessel.vessel_data_imo = 9876543
    mock_vessel.vessel_data_ship_name = "Test Ship"
    mock_vessel.vessel_data_ship_type = "Cargo"
    mock_vessel.vessel_data_flag = "Panama"
    mock_vessel.vessel_data_length_meters = 150.5
    mock_vessel.vessel_data_beam_meters = 25.0
    mock_vessel.vessel_data_user_tags = ["tag1", "tag2"]

    mock_get_vessel.return_value = mock_vessel

    response = client.get('/api/v1/vessels/101')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['data']['vessel_data_id'] == 101
    assert data['data']['mmsi'] == 123456789
    assert data['data']['ship_name'] == "Test Ship"
    assert data['data']['user_tags'] == ["tag1", "tag2"]

@patch('app.modules.vessels.routes.get_vessel_by_vessel_data_id')
def test_get_vessel_by_vessel_data_id_not_found(mock_get_vessel, client):
    '''
    Test GET /api/v1/vessels/<int:vessel_data_id> with non-existent ID
    '''
    mock_get_vessel.return_value = None

    response = client.get('/api/v1/vessels/999')

    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['error'] == "Vessel with ID 999 not found."

@patch('app.modules.vessels.routes.write_audit_log')
@patch('app.modules.vessels.routes.logger')
@patch('app.modules.vessels.routes.get_vessel_by_vessel_data_id')
def test_get_vessel_by_vessel_data_id_exception(mock_get_vessel, mock_logger, mock_audit, client):
    '''
    Test GET /api/v1/vessels/<int:vessel_data_id> when an exception occurs
    '''
    mock_get_vessel.side_effect = Exception("Database connection failed")

    response = client.get('/api/v1/vessels/101')

    assert response.status_code == 500
    data = json.loads(response.data)
    assert data['error'] == "Internal server error"
    assert "Database connection failed" in data['details']

    mock_logger.error.assert_called_once()

# ==========================================
# Tests for GET /api/v1/vessels/exportArea
# ==========================================

def create_mock_stream():
    '''Helper to create a mock generator stream for route tests'''
    fake_loc = MagicMock()
    fake_loc.vessel_location_id = 1
    fake_loc.vessel_location_speed_knots = 10.5
    fake_loc.vessel_location_course_deg = 90.0
    fake_loc.vessel_location_heading_deg = 90.0
    fake_loc.vessel_location_rate_of_turn_deg_per_sec = 0.0
    fake_loc.vessel_location_nav_status = "Under way"
    fake_loc.vessel_location_timestamp = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    fake_loc.vessel_location_coords = MagicMock()

    fake_data = MagicMock()
    fake_data.vessel_data_id = 101
    fake_data.vessel_data_mmsi = 123456789
    fake_data.vessel_data_imo = 9876543
    fake_data.vessel_data_ship_name = "Test Ship"
    fake_data.vessel_data_ship_type = "Cargo"
    fake_data.vessel_data_flag = "SG"
    fake_data.vessel_data_length_meters = 150.5
    fake_data.vessel_data_beam_meters = 25.0
    fake_data.vessel_data_user_tags = ["tag1", "tag2"]

    return iter([(fake_loc, fake_data)])

@patch('app.modules.vessels.routes.get_vessel_history_stream')
def test_history_default_bbox(mock_stream, client):
    '''Test default bounding box (whole Earth) when parameters are missing'''
    mock_stream.return_value = create_mock_stream()

    response = client.get('/api/v1/vessels/exportArea?start_time=2026-01-01T00:00:00Z&end_time=2026-01-02T00:00:00Z')

    assert response.status_code == 200

@patch('app.modules.vessels.routes.get_vessel_history_stream')
def test_history_default_times(mock_stream, client):
    '''Test default times when start_time or end_time are missing'''
    mock_stream.return_value = create_mock_stream()

    response = client.get('/api/v1/vessels/exportArea?lat_min=10&lat_max=20&long_min=10&long_max=20')

    assert response.status_code == 200

@patch('app.modules.vessels.routes.get_vessel_history_stream')
def test_history_invalid_time_format(mock_stream, client):
    '''Test invalid time format'''
    response = client.get('/api/v1/vessels/exportArea?lat_min=10&lat_max=20&long_min=10&long_max=20&start_time=invalid&end_time=2023-01-02T00:00:00Z')

    assert response.status_code == 400
    assert "Invalid time format" in json.loads(response.data)['error']

@patch('app.modules.vessels.routes.get_vessel_history_stream')
def test_history_start_after_end(mock_stream, client):
    '''Test start_time is after end_time'''
    response = client.get('/api/v1/vessels/exportArea?lat_min=10&lat_max=20&long_min=10&long_max=20&start_time=2023-01-02T00:00:00Z&end_time=2023-01-01T00:00:00Z')

    assert response.status_code == 400
    assert "start_time must be before end_time" in json.loads(response.data)['error']

@patch('app.modules.vessels.routes.get_vessel_history_stream')
def test_history_invalid_format(mock_stream, client):
    '''Test invalid export format parameter'''
    response = client.get('/api/v1/vessels/exportArea?lat_min=10&lat_max=20&long_min=10&long_max=20&start_time=2023-01-01T00:00:00Z&end_time=2023-01-02T00:00:00Z&format=xml')

    assert response.status_code == 400
    assert "Invalid format" in json.loads(response.data)['error']

@patch('app.modules.vessels.routes.to_shape')
@patch('app.modules.vessels.routes.get_vessel_history_stream')
def test_history_success_json(mock_stream, mock_to_shape, client):
    '''Test successful JSON export'''
    mock_to_shape.return_value.x = 15.0
    mock_to_shape.return_value.y = 15.0
    mock_stream.return_value = create_mock_stream()

    response = client.get('/api/v1/vessels/exportArea?lat_min=10&lat_max=20&long_min=10&long_max=20&start_time=2023-01-01T00:00:00Z&end_time=2023-01-02T00:00:00Z&format=json')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert len(data['data']) == 1
    assert data['data'][0]['mmsi'] == 123456789
    assert data['data'][0]['latitude'] == 15.0

@patch('app.modules.vessels.routes.to_shape')
@patch('app.modules.vessels.routes.get_vessel_history_stream')
def test_history_success_geojson(mock_stream, mock_to_shape, client):
    '''Test successful GeoJSON export'''
    mock_to_shape.return_value.x = 15.0
    mock_to_shape.return_value.y = 15.0
    mock_stream.return_value = create_mock_stream()

    response = client.get('/api/v1/vessels/exportArea?lat_min=10&lat_max=20&long_min=10&long_max=20&start_time=2023-01-01T00:00:00Z&end_time=2023-01-02T00:00:00Z&format=geojson')

    assert response.status_code == 200
    assert response.mimetype == 'application/geo+json'
    data = json.loads(response.data)
    assert data['type'] == 'FeatureCollection'
    assert len(data['features']) == 1
    assert data['features'][0]['geometry']['coordinates'] == [15.0, 15.0]

@patch('app.modules.vessels.routes.to_shape')
@patch('app.modules.vessels.routes.get_vessel_history_stream')
def test_history_success_csv(mock_stream, mock_to_shape, client):
    '''Test successful CSV export'''
    mock_to_shape.return_value.x = 15.0
    mock_to_shape.return_value.y = 15.0
    mock_stream.return_value = create_mock_stream()

    response = client.get('/api/v1/vessels/exportArea?lat_min=10&lat_max=20&long_min=10&long_max=20&start_time=2023-01-01T00:00:00Z&end_time=2023-01-02T00:00:00Z&format=csv')

    assert response.status_code == 200
    assert response.mimetype == 'text/csv'
    csv_data = response.data.decode('utf-8')

    assert 'location_id,vessel_data_id,mmsi' in csv_data
    assert '123456789' in csv_data
    assert 'Test Ship' in csv_data

@patch('app.modules.vessels.routes.write_audit_log')
@patch('app.modules.vessels.routes.logger')
@patch('app.modules.vessels.routes.func')
def test_history_exception(mock_func, mock_logger, mock_audit, client):
    '''Test route exception handling'''
    mock_func.ST_MakeEnvelope.side_effect = Exception("PostGIS error")

    response = client.get('/api/v1/vessels/exportArea?lat_min=10&lat_max=20&long_min=10&long_max=20&start_time=2023-01-01T00:00:00Z&end_time=2023-01-02T00:00:00Z')

    assert response.status_code == 500
    data = json.loads(response.data)
    assert data['error'] == "Internal server error"
    assert "PostGIS error" in data['details']
    mock_logger.error.assert_called_once()

# ==========================================
# Tests for POST/PATCH /api/v1/vessels/<int:vessel_data_id>/update
# ==========================================

@patch('app.modules.vessels.routes.update_vessel_data_in_db')
def test_update_vessel_success_all_fields(mock_update, client):
    '''Test successful update with all fields provided'''
    mock_update.return_value = True

    form_data = {
        "ship_name": "New Ship Name",
        "ship_type": "Tanker",
        "flag": "Liberia",
        "length_meters": "200",
        "beam_meters": "30",
        "user_tags": '["tag1", "tag2"]'
    }

    response = client.post('/api/v1/vessels/101/update', data=form_data)

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['vessel_data_id'] == 101
    assert data['message'] == "Vessel updated successfully."

    mock_update.assert_called_once_with(
        vessel_data_id=101,
        ship_name="New Ship Name",
        ship_type="Tanker",
        flag="Liberia",
        length_meters=200,
        beam_meters=30,
        user_tags=["tag1", "tag2"]
    )

@patch('app.modules.vessels.routes.update_vessel_data_in_db')
def test_update_vessel_success_partial_fields(mock_update, client):
    '''Test successful update with only some fields provided'''
    mock_update.return_value = True
    form_data = {
        "ship_name": "Updated Name Only"
    }
    response = client.patch('/api/v1/vessels/101/update', data=form_data)

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'

    mock_update.assert_called_once_with(
        vessel_data_id=101,
        ship_name="Updated Name Only",
        ship_type=None,
        flag=None,
        length_meters=None,
        beam_meters=None,
        user_tags=None
    )

def test_update_vessel_no_fields_provided(client):
    '''Test update fails when no fields are provided'''
    response = client.post('/api/v1/vessels/101/update', data={})

    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == "Requires at least 1 field to update."

@patch('app.modules.vessels.routes.update_vessel_data_in_db')
def test_update_vessel_invalid_length_meters(mock_update, client):
    '''Test update fails when length_meters is not a valid integer'''
    form_data = {
        "length_meters": "not_a_number"
    }
    response = client.post('/api/v1/vessels/101/update', data=form_data)

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "Invalid data format: length_meters and beam_meters must be valid integers." in data['error']
    mock_update.assert_not_called()

@patch('app.modules.vessels.routes.update_vessel_data_in_db')
def test_update_vessel_invalid_user_tags_json(mock_update, client):
    '''Test update fails when user_tags is an invalid JSON string'''
    form_data = {
        "user_tags": "this is not valid json"
    }
    response = client.post('/api/v1/vessels/101/update', data=form_data)

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "Invalid data format: user_tags should be an array of strings." in data['error']
    mock_update.assert_not_called()

@patch('app.modules.vessels.routes.update_vessel_data_in_db')
def test_update_vessel_not_found(mock_update, client):
    '''Test update returns 404 when the vessel does not exist in the DB'''
    mock_update.return_value = False
    form_data = {
        "ship_name": "Boaty McBoatface"
    }
    response = client.post('/api/v1/vessels/999/update', data=form_data)

    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['error'] == "Vessel with ID 999 not found."

@patch('app.modules.vessels.routes.write_audit_log')
@patch('app.modules.vessels.routes.logger')
@patch('app.modules.vessels.routes.update_vessel_data_in_db')
def test_update_vessel_exception(mock_update, mock_logger, mock_audit, client):
    '''Test internal server error handling during update'''
    mock_update.side_effect = Exception("Database write failed")
    form_data = {
        "ship_name": "Shippy McShipface"
    }
    response = client.post('/api/v1/vessels/101/update', data=form_data)

    assert response.status_code == 500
    data = json.loads(response.data)
    assert data['error'] == "Internal server error"
    assert "Database write failed" in data['details']

    mock_logger.error.assert_called_once()
    mock_audit.assert_called_once()

# ==========================================
# Tests for GET /api/v1/vessels/<int:vessel_data_id>/history
# ==========================================

def create_mock_locations():
    '''Helper to create a mock list of VesselLocation objects'''
    fake_loc = MagicMock()
    fake_loc.vessel_location_id = 1
    fake_loc.vessel_location_speed_knots = 10.5
    fake_loc.vessel_location_course_deg = 90.0
    fake_loc.vessel_location_heading_deg = 90.0
    fake_loc.vessel_location_rate_of_turn_deg_per_sec = 0.0
    fake_loc.vessel_location_nav_status = "Under way"
    fake_loc.vessel_location_timestamp = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    fake_loc.vessel_location_coords = MagicMock()
    return [fake_loc]

@patch('app.modules.vessels.routes.to_shape')
@patch('app.modules.vessels.routes.get_vessel_history_by_vessel_data_id')
def test_vessel_history_success(mock_get_history, mock_to_shape, client):
    '''Test successful retrieval of vessel history'''
    mock_to_shape.return_value.x = 15.0
    mock_to_shape.return_value.y = 15.0
    mock_get_history.return_value = create_mock_locations()

    response = client.get('/api/v1/vessels/101/history?start_time=2067-01-01T00:00:00Z&end_time=2067-01-02T00:00:00Z')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['count'] == 1
    assert data['data'][0]['location_id'] == 1
    assert data['data'][0]['latitude'] == 15.0
    assert data['data'][0]['longitude'] == 15.0
    assert data['data'][0]['speed_knots'] == 10.5
    assert data['data'][0]['nav_status'] == "Under way"

@patch('app.modules.vessels.routes.to_shape')
@patch('app.modules.vessels.routes.get_vessel_history_by_vessel_data_id')
def test_vessel_history_default_times(mock_get_history, mock_to_shape, client):
    '''Test default times when start_time and end_time are missing'''
    mock_to_shape.return_value.x = 15.0
    mock_to_shape.return_value.y = 15.0
    mock_get_history.return_value = create_mock_locations()

    response = client.get('/api/v1/vessels/101/history')

    assert response.status_code == 200
    args, _ = mock_get_history.call_args
    assert args[0] == 101
    assert args[1] == datetime.min.replace(tzinfo=timezone.utc)
    assert isinstance(args[2], datetime)

def test_vessel_history_invalid_time_format(client):
    '''Test invalid time format returns 400'''
    response = client.get('/api/v1/vessels/101/history?start_time=invalid-date&end_time=2067-01-02T00:00:00Z')

    assert response.status_code == 400
    assert "Invalid time format" in json.loads(response.data)['error']

def test_vessel_history_start_after_end(client):
    '''Test start_time after end_time returns 400'''
    response = client.get('/api/v1/vessels/101/history?start_time=2069-01-01T00:00:00Z&end_time=2067-01-01T00:00:00Z')

    assert response.status_code == 400
    assert "start_time must be before end_time" in json.loads(response.data)['error']

@patch('app.modules.vessels.routes.get_vessel_history_by_vessel_data_id')
def test_vessel_history_not_found(mock_get_history, client):
    '''Test empty history returns 404'''
    mock_get_history.return_value = []

    response = client.get('/api/v1/vessels/101/history?start_time=2069-01-01T00:00:00Z&end_time=2069-01-02T00:00:00Z')

    assert response.status_code == 404
    assert "No history exists" in json.loads(response.data)['error']

@patch('app.modules.vessels.routes.write_audit_log')
@patch('app.modules.vessels.routes.logger')
@patch('app.modules.vessels.routes.get_vessel_history_by_vessel_data_id')
def test_vessel_history_exception(mock_get_history, mock_logger, mock_audit, client):
    '''Test internal server error handling'''
    mock_get_history.side_effect = Exception("Database connection failed")

    response = client.get('/api/v1/vessels/101/history?start_time=2069-01-01T00:00:00Z&end_time=2069-01-02T00:00:00Z')

    assert response.status_code == 500
    data = json.loads(response.data)
    assert data['error'] == "Internal server error"
    assert "Database connection failed" in data['details']
    mock_logger.error.assert_called_once()
