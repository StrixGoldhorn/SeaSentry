# backend/app/modules/vessels/tests/test_vessels_routes.py

import pytest
import json
from unittest.mock import patch, MagicMock
from flask import Flask
from datetime import datetime, timezone

from app.modules.vessels.routes import vessels_bp

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

def test_get_vessels_in_bbox_missing_bbox(client):
    '''
    Test /api/v1/vessels/bbox with missing bbox
    '''
    response = client.get('/api/v1/vessels/bbox')
    assert response.status_code == 400
    assert b"Bounding box expected." in response.data

@patch('app.modules.vessels.routes.to_shape')
@patch('app.modules.vessels.routes.func')
@patch('app.modules.vessels.routes.DBConn')
def test_get_vessels_in_bbox_success(mock_db, mock_func, mock_to_shape, client):
    '''
    Test /api/v1/vessels/bbox with correct params
    '''
    mock_session = MagicMock()
    mock_db.get_session.return_value = mock_session

    mock_query = MagicMock()
    mock_session.query.return_value.join.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.distinct.return_value = mock_query
    mock_query.limit.return_value = mock_query

    # Fake vessel_location results
    mock_location = MagicMock()
    mock_location.vessel_location_id = 1
    mock_location.vessel_location_vessel_data_id = 10
    mock_location.vessel_location_speed_knots = 12.5
    mock_location.vessel_location_course_deg = 90.0
    mock_location.vessel_location_heading_deg = 90.0
    mock_location.vessel_location_rate_of_turn_deg_per_sec = 0.0
    mock_location.vessel_location_nav_status = 0
    mock_location.vessel_location_timestamp = datetime(2023, 10, 25, 10, 0, 0, tzinfo=timezone.utc)

    # Fake vessel_data results
    mock_vessel = MagicMock()
    mock_vessel.vessel_data_id = 10
    mock_vessel.vessel_data_mmsi = 123456789
    mock_vessel.vessel_data_imo = 9876543
    mock_vessel.vessel_data_ship_name = "Test Ship"
    mock_vessel.vessel_data_ship_type = "Cargo"
    mock_vessel.vessel_data_flag = "US"

    mock_query.all.return_value = [(mock_location, mock_vessel)]

    mock_geom = MagicMock()
    mock_geom.x = -122.4194
    mock_geom.y = 37.7749
    mock_to_shape.return_value = mock_geom

    response = client.get('/api/v1/vessels/bbox?lat_min=37&lat_max=38&long_min=-123&long_max=-122&limit=10')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['count'] == 1
    assert data['data'][0]['ship_name'] == "Test Ship"
    assert data['data'][0]['latitude'] == 37.7749
    assert data['data'][0]['longitude'] == -122.4194

    mock_query.limit.assert_called_once_with(10)

def test_get_vessels_in_bbox_invalid_limit(client):
    '''
    Test /api/v1/vessels/bbox with invalid limit
    '''
    response = client.get('/api/v1/vessels/bbox?lat_min=37&lat_max=38&long_min=-123&long_max=-122&limit=abc')
    assert response.status_code == 400
    assert b"Invalid limit format. Must be an integer." in response.data

def test_get_vessels_in_bbox_invalid_time_within(client):
    '''
    Test /api/v1/vessels/bbox with invalid time within
    '''
    response = client.get('/api/v1/vessels/bbox?lat_min=37&lat_max=38&long_min=-123&long_max=-122&time_within=abc')
    assert response.status_code == 400
    assert b"Invalid time_within format. Ensure it is in seconds." in response.data

def test_get_vessels_in_bbox_limit_capped_at_1000(client):
    '''
    Test /api/v1/vessels/bbox exceeding limit
    '''
    response = client.get('/api/v1/vessels/bbox?lat_min=37&lat_max=38&long_min=-123&long_max=-122&limit=5000')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['filters']['limit'] == 1000
