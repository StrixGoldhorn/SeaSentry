# backend/app/modules/geofences/tests/test_geofences_routes.py

import pytest
import json
from unittest.mock import patch, MagicMock
from flask import Flask

from app.modules.geofences.routes import geofences_bp

@pytest.fixture
def app():
    '''
    Create and configure a new app instance for each test.
    '''
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(geofences_bp)
    return app

@pytest.fixture
def client(app):
    '''
    Create a test client for the app.
    '''
    return app.test_client()

# ==========================================
# Tests for POST /api/v1/geofences/add/box
# ==========================================

@patch('app.modules.geofences.routes.write_audit_log')
@patch('app.modules.geofences.routes.add_rectangle_geofence_to_db')
@patch('app.modules.geofences.routes.Geofence')
@patch('app.modules.geofences.routes.DBConn')
def test_add_geofence_box_success(mock_db, mock_geofence_model, mock_add_rect, mock_audit, client):
    '''
    Test /api/v1/geofences/add/box with valid params
    '''
    mock_session = MagicMock()
    mock_db.get_session.return_value = mock_session

    mock_session.query.return_value.filter.return_value.first.return_value = None 

    mock_add_rect.return_value = 101

    response = client.post('/api/v1/geofences/add/box', data={
        'lat_min': '10.5', 'lat_max': '20.5', 
        'long_min': '30.5', 'long_max': '40.5',
        'name': 'TestBox', 'desc': 'Test Description'
    })

    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['geofence_id'] == 101

    mock_add_rect.assert_called_once_with('TestBox', 30.5, 40.5, 10.5, 20.5, 'Test Description')

def test_add_geofence_box_missing_bbox(client):
    '''
    Test /api/v1/geofences/add/box without bbox
    '''
    response = client.post('/api/v1/geofences/add/box', data={'name': 'TestBox'})
    assert response.status_code == 400

def test_add_geofence_box_invalid_float(client):
    '''
    Test /api/v1/geofences/add/box with invalid data
    '''
    response = client.post('/api/v1/geofences/add/box', data={
        'lat_min': 'not_a_number', 'lat_max': '20.5', 
        'long_min': '30.5', 'long_max': '40.5', 'name': 'TestBox'
    })
    assert response.status_code == 400

@patch('app.modules.geofences.routes.Geofence')
@patch('app.modules.geofences.routes.DBConn')
def test_add_geofence_box_name_exists(mock_db, mock_geofence_model, client):
    '''
    Test /api/v1/geofences/add/box with existing name
    '''
    mock_session = MagicMock()
    mock_db.get_session.return_value = mock_session

    mock_session.query.return_value.filter.return_value.first.return_value = MagicMock()

    response = client.post('/api/v1/geofences/add/box', data={
        'lat_min': '10', 'lat_max': '20', 'long_min': '30', 'long_max': '40',
        'name': 'ExistingBox', 'desc': 'Desc'
    })
    assert response.status_code == 403


# ==========================================
# Tests for POST /api/v1/geofences/add/polygon
# ==========================================

@patch('geoalchemy2.shape.from_shape')
@patch('shapely.geometry.Polygon')
@patch('app.modules.geofences.routes.write_audit_log')
@patch('app.modules.geofences.routes.add_polygon_geofence_to_db')
@patch('app.modules.geofences.routes.Geofence')
@patch('app.modules.geofences.routes.DBConn')
def test_add_geofence_polygon_success(mock_db, mock_geofence_model, mock_add_poly, mock_audit, mock_poly_class, mock_from_shape, client):
    '''
    Test /api/v1/geofences/add/polygon with valid polygon
    '''
    mock_session = MagicMock()
    mock_db.get_session.return_value = mock_session
    mock_session.query.return_value.filter.return_value.first.return_value = None

    mock_poly_instance = MagicMock()
    mock_poly_instance.is_valid = True
    mock_poly_class.return_value = mock_poly_instance

    mock_add_poly.return_value = 202

    coords = '[[30.0, 10.0], [40.0, 40.0], [20.0, 40.0], [10.0, 20.0]]' 

    response = client.post('/api/v1/geofences/add/polygon', data={
        'name': 'TestPoly', 'desc': 'Poly Desc', 'coords': coords
    })

    assert response.status_code == 201
    assert json.loads(response.data)['geofence_id'] == 202
    mock_add_poly.assert_called_once()

def test_add_geofence_polygon_missing_polygon(client):
    '''
    Test /api/v1/geofences/add/polygon without polygon
    '''
    response = client.post('/api/v1/geofences/add/polygon', data={'name': 'TestBox'})
    assert response.status_code == 400

def test_add_geofence_polygon_invalid_json(client):
    '''
    Test /api/v1/geofences/add/polygon without valid polygon
    '''
    response = client.post('/api/v1/geofences/add/polygon', data={
        'name': 'TestPoly', 'coords': 'this is not json'
    })
    assert response.status_code == 400

@patch('shapely.geometry.Polygon')
@patch('app.modules.geofences.routes.Geofence')
@patch('app.modules.geofences.routes.DBConn')
def test_add_geofence_polygon_invalid_geometry(mock_db, mock_geofence_model, mock_poly_class, client):
    '''
    Test /api/v1/geofences/add/polygon with valid polygon
    '''
    mock_session = MagicMock()
    mock_db.get_session.return_value = mock_session
    mock_session.query.return_value.filter.return_value.first.return_value = None

    mock_poly_instance = MagicMock()
    mock_poly_instance.is_valid = False 
    mock_poly_class.return_value = mock_poly_instance

    coords = '[[0,0], [1,1], [2,2]]' 
    response = client.post('/api/v1/geofences/add/polygon', data={
        'name': 'TestPoly', 'coords': coords
    })
    assert response.status_code == 400

@patch('app.modules.geofences.routes.Geofence')
@patch('app.modules.geofences.routes.DBConn')
def test_add_geofence_polygon_name_exists(mock_db, mock_geofence_model, client):
    '''
    Test /api/v1/geofences/add/polygon with existing name
    '''
    mock_session = MagicMock()
    mock_db.get_session.return_value = mock_session

    mock_session.query.return_value.filter.return_value.first.return_value = MagicMock()

    coords = '[[0,0], [1,1], [2,2]]' 
    response = client.post('/api/v1/geofences/add/polygon', data={
        'coords': coords,
        'name': 'ExistingBox', 'desc': 'Desc'
    })
    assert response.status_code == 403

# ==========================================
# Tests for GET /api/v1/geofences/get/all
# ==========================================

@patch('app.modules.geofences.routes.get_geofence_polygon_vertices')
@patch('app.modules.geofences.routes.get_all_geofences')
def test_get_all_geofences_success(mock_get_all, mock_get_verts, client):
    '''
    Test /api/v1/geofences/get/all
    '''
    mock_geofence = MagicMock()
    mock_geofence.geofence_id = 1
    mock_geofence.geofence_timestamp = "2023-10-25T10:00:00"
    mock_geofence.geofence_name = "Global"
    mock_geofence.geofence_description = "World map"

    mock_get_all.return_value = [mock_geofence]
    mock_get_verts.return_value = [[-180, -90], [180, 90]]

    response = client.get('/api/v1/geofences/get/all')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['count'] == 1
    assert data['data'][0]['geofence_name'] == "Global"
