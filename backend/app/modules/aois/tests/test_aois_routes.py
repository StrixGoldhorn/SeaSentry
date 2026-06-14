import pytest
import json
from unittest.mock import patch, MagicMock
from flask import Flask

from app.modules.aois.routes import aois_bp

@pytest.fixture
def app():
    '''
    Create and configure a new app instance for each test.
    '''
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(aois_bp)
    return app

@pytest.fixture
def client(app):
    '''
    Create a test client for the app.
    '''
    return app.test_client()

# ==========================================
# Tests for POST /api/v1/aois/add/box
# ==========================================

@patch('app.modules.aois.routes.write_audit_log')
@patch('app.modules.aois.routes.add_rectangle_aoi_to_db')
@patch('app.modules.aois.routes.check_if_aoi_name_exists')
def test_add_aoi_box_success(mock_check_name, mock_add_rect, mock_audit, client):
    '''
    Test /api/v1/aois/add/box with valid params
    '''
    mock_check_name.return_value = False
    mock_add_rect.return_value = 101

    response = client.post('/api/v1/aois/add/box', data={
        'lat_min': '10.5', 'lat_max': '20.5', 
        'long_min': '30.5', 'long_max': '40.5',
        'name': 'TestBox', 'desc': 'Test Description'
    })

    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['aoi_id'] == 101
    
    mock_add_rect.assert_called_once_with('TestBox', 30.5, 40.5, 10.5, 20.5, 'Test Description')

def test_add_aoi_box_missing_bbox(client):
    '''
    Test /api/v1/aois/add/box without bbox
    '''
    response = client.post('/api/v1/aois/add/box', data={'name': 'TestBox'})
    assert response.status_code == 400
    assert json.loads(response.data)['error'] == 'Bounding box expected.'

def test_add_aoi_box_invalid_float(client):
    '''
    Test /api/v1/aois/add/box with invalid float data
    '''
    response = client.post('/api/v1/aois/add/box', data={
        'lat_min': 'not_a_number', 'lat_max': '20.5', 
        'long_min': '30.5', 'long_max': '40.5', 'name': 'TestBox'
    })
    assert response.status_code == 400
    assert json.loads(response.data)['error'] == 'Bounding box expected.'

@patch('app.modules.aois.routes.check_if_aoi_name_exists')
def test_add_aoi_box_name_exists(mock_check_name, client):
    '''
    Test /api/v1/aois/add/box with existing name
    '''
    mock_check_name.return_value = True

    response = client.post('/api/v1/aois/add/box', data={
        'lat_min': '10', 'lat_max': '20', 'long_min': '30', 'long_max': '40',
        'name': 'ExistingBox', 'desc': 'Desc'
    })
    assert response.status_code == 403
    assert 'already exists' in json.loads(response.data)['error']


# ==========================================
# Tests for POST /api/v1/aois/add/polygon
# ==========================================

@patch('app.modules.aois.routes.write_audit_log')
@patch('app.modules.aois.routes.add_polygon_aoi_to_db')
@patch('app.modules.aois.routes.check_if_aoi_name_exists')
def test_add_aoi_polygon_success(mock_check_name, mock_add_poly, mock_audit, client):
    '''
    Test /api/v1/aois/add/polygon with valid polygon
    '''
    mock_check_name.return_value = False
    mock_add_poly.return_value = 202

    coords = json.dumps([[30.0, 10.0], [40.0, 40.0], [20.0, 40.0], [10.0, 20.0], [30.0, 10.0]]) 

    response = client.post('/api/v1/aois/add/polygon', data={
        'name': 'TestPoly', 'desc': 'Poly Desc', 'coords': coords
    })

    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['area_of_interest_id'] == 202
    mock_add_poly.assert_called_once()

def test_add_aoi_polygon_missing_coords(client):
    '''
    Test /api/v1/aois/add/polygon without coords
    '''
    response = client.post('/api/v1/aois/add/polygon', data={'name': 'TestBox'})
    assert response.status_code == 400
    assert json.loads(response.data)['error'] == 'Array of [long, lat] expected.'

def test_add_aoi_polygon_invalid_json(client):
    '''
    Test /api/v1/aois/add/polygon with invalid JSON coords
    '''
    response = client.post('/api/v1/aois/add/polygon', data={
        'name': 'TestPoly', 'coords': 'this is not json'
    })
    assert response.status_code == 400
    assert 'Invalid coordinates format' in json.loads(response.data)['error']

@patch('app.modules.aois.routes.Polygon')
@patch('app.modules.aois.routes.check_if_aoi_name_exists')
def test_add_aoi_polygon_invalid_geometry(mock_check_name, mock_poly_class, client):
    '''
    Test /api/v1/aois/add/polygon with invalid polygon geometry
    '''
    mock_check_name.return_value = False
    
    mock_poly_instance = MagicMock()
    mock_poly_instance.is_valid = False 
    mock_poly_class.return_value = mock_poly_instance

    coords = json.dumps([[0, 0], [1, 1], [2, 2], [0, 0]]) 
    response = client.post('/api/v1/aois/add/polygon', data={
        'name': 'TestPoly', 'coords': coords
    })
    assert response.status_code == 400
    assert 'Invalid polygon geometry' in json.loads(response.data)['error']

@patch('app.modules.aois.routes.check_if_aoi_name_exists')
def test_add_aoi_polygon_name_exists(mock_check_name, client):
    '''
    Test /api/v1/aois/add/polygon with existing name
    '''
    mock_check_name.return_value = True

    coords = json.dumps([[0, 0], [1, 1], [2, 2], [0, 0]]) 
    response = client.post('/api/v1/aois/add/polygon', data={
        'coords': coords,
        'name': 'ExistingBox', 'desc': 'Desc'
    })
    assert response.status_code == 403
    assert 'already exists' in json.loads(response.data)['error']


# ==========================================
# Tests for GET /api/v1/aois/get/all
# ==========================================

@patch('app.modules.aois.routes.get_aoi_polygon_vertices')
@patch('app.modules.aois.routes.get_all_aois')
def test_get_all_aois_success(mock_get_all, mock_get_verts, client):
    '''
    Test /api/v1/aois/get/all
    '''
    mock_aoi = MagicMock()
    mock_aoi.area_of_interest_id = 1
    mock_aoi.area_of_interest_timestamp = "2023-10-25T10:00:00"
    mock_aoi.area_of_interest_name = "Global"
    mock_aoi.area_of_interest_description = "World map"

    mock_get_all.return_value = [mock_aoi]
    mock_get_verts.return_value = [[-180, -90], [180, 90]]

    response = client.get('/api/v1/aois/get/all')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['count'] == 1
    assert data['data'][0]['area_of_interest_name'] == "Global"
    assert data['data'][0]['area_of_interest_polygon'] == [[-180, -90], [180, 90]]


# ==========================================
# Tests for POST/PATCH /api/v1/aois/<aoi_id>/update/
# ==========================================

@patch('app.modules.aois.routes.write_audit_log')
@patch('app.modules.aois.routes.update_aoi_in_db')
def test_update_aoi_by_id_success_name_desc(mock_update, mock_audit, client):
    '''
    Test updating AOI with name and description
    '''
    mock_update.return_value = True

    response = client.post('/api/v1/aois/1/update', data={
        'name': 'NewName', 'desc': 'NewDesc'
    })

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['aoi_id'] == 1
    mock_update.assert_called_once_with(aoi_id=1, name='NewName', desc='NewDesc', geometry_wkb=None)

@patch('app.modules.aois.routes.update_aoi_in_db')
def test_update_aoi_by_id_success_coords(mock_update, client):
    '''
    Test updating AOI with new coordinates
    '''
    mock_update.return_value = True
    # Use a valid polygon (a square) to avoid Shapely invalid geometry errors
    coords = json.dumps([[0.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, 0.0], [0.0, 0.0]])

    response = client.patch('/api/v1/aois/2/update', data={
        'coords': coords
    })

    assert response.status_code == 200
    assert mock_update.called
    call_kwargs = mock_update.call_args.kwargs
    assert call_kwargs['aoi_id'] == 2
    assert call_kwargs['name'] is None
    assert call_kwargs['desc'] is None
    assert call_kwargs['geometry_wkb'] is not None

@patch('app.modules.aois.routes.update_aoi_in_db')
def test_update_aoi_by_id_success_bbox(mock_update, client):
    '''
    Test updating AOI with new bounding box
    '''
    mock_update.return_value = True

    response = client.post('/api/v1/aois/3/update', data={
        'lat_min': '10.0', 'lat_max': '20.0', 'long_min': '30.0', 'long_max': '40.0'
    })

    assert response.status_code == 200
    assert mock_update.called
    call_kwargs = mock_update.call_args.kwargs
    assert call_kwargs['aoi_id'] == 3
    assert call_kwargs['geometry_wkb'] is not None

def test_update_aoi_by_id_missing_fields(client):
    '''
    Test updating AOI without providing any fields
    '''
    response = client.post('/api/v1/aois/1/update', data={})
    assert response.status_code == 400
    assert json.loads(response.data)['error'] == 'Requires at least 1 field to update.'

def test_update_aoi_by_id_both_coords_and_bbox(client):
    '''
    Test updating AOI with both coords and bbox (should fail)
    '''
    coords = json.dumps([[0.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, 0.0], [0.0, 0.0]])
    response = client.post('/api/v1/aois/1/update', data={
        'coords': coords,
        'lat_min': '10.0', 'lat_max': '20.0', 'long_min': '30.0', 'long_max': '40.0'
    })
    assert response.status_code == 400
    assert 'not both' in json.loads(response.data)['error']

def test_update_aoi_by_id_invalid_coords_json(client):
    '''
    Test updating AOI with invalid coords JSON
    '''
    response = client.post('/api/v1/aois/1/update', data={
        'coords': 'invalid json'
    })
    assert response.status_code == 400
    assert 'Invalid coordinates format' in json.loads(response.data)['error']

@patch('app.modules.aois.routes.Polygon')
@patch('app.modules.aois.routes.update_aoi_in_db')
def test_update_aoi_by_id_invalid_polygon_geometry(mock_update, mock_poly_class, client):
    '''
    Test updating AOI with invalid polygon geometry
    '''
    mock_poly_instance = MagicMock()
    mock_poly_instance.is_valid = False 
    mock_poly_class.return_value = mock_poly_instance

    coords = json.dumps([[0, 0], [1, 1], [2, 2], [0, 0]]) 
    response = client.post('/api/v1/aois/1/update', data={
        'coords': coords
    })
    assert response.status_code == 400
    assert 'Invalid polygon geometry' in json.loads(response.data)['error']

@patch('app.modules.aois.routes.update_aoi_in_db')
def test_update_aoi_by_id_not_found(mock_update, client):
    '''
    Test updating AOI that does not exist
    '''
    mock_update.return_value = False

    response = client.post('/api/v1/aois/999/update', data={
        'name': 'NewName'
    })

    assert response.status_code == 404
    assert 'not found' in json.loads(response.data)['error']
