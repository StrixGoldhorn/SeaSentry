import pytest
import json
from unittest.mock import patch, MagicMock
from flask import Flask

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

    from shapely.geometry import box
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

    from shapely.geometry import box
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
    assert data['data']['vessel_data_mmsi'] == 123456789
    assert data['data']['vessel_data_ship_name'] == "Test Ship"
    assert data['data']['vessel_data_user_tags'] == ["tag1", "tag2"]

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
