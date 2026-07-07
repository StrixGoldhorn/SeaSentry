import pytest
import json
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import IntegrityError
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
@patch('app.modules.geofences.routes.check_if_geofence_name_exists')
def test_add_geofence_box_success(mock_check_name, mock_add_rect, mock_audit, client):
    '''
    Test /api/v1/geofences/add/box with valid params
    '''
    mock_check_name.return_value = False
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
    assert json.loads(response.data)['error'] == 'Bounding box expected.'

def test_add_geofence_box_invalid_float(client):
    '''
    Test /api/v1/geofences/add/box with invalid float data
    '''
    response = client.post('/api/v1/geofences/add/box', data={
        'lat_min': 'not_a_number', 'lat_max': '20.5', 
        'long_min': '30.5', 'long_max': '40.5', 'name': 'TestBox'
    })
    assert response.status_code == 400
    assert json.loads(response.data)['error'] == 'Bounding box expected.'

@patch('app.modules.geofences.routes.check_if_geofence_name_exists')
def test_add_geofence_box_name_exists(mock_check_name, client):
    '''
    Test /api/v1/geofences/add/box with existing name
    '''
    mock_check_name.return_value = True

    response = client.post('/api/v1/geofences/add/box', data={
        'lat_min': '10', 'lat_max': '20', 'long_min': '30', 'long_max': '40',
        'name': 'ExistingBox', 'desc': 'Desc'
    })
    assert response.status_code == 403
    assert 'already exists' in json.loads(response.data)['error']


# ==========================================
# Tests for POST /api/v1/geofences/add/polygon
# ==========================================

@patch('app.modules.geofences.routes.write_audit_log')
@patch('app.modules.geofences.routes.add_polygon_geofence_to_db')
@patch('app.modules.geofences.routes.check_if_geofence_name_exists')
def test_add_geofence_polygon_success(mock_check_name, mock_add_poly, mock_audit, client):
    '''
    Test /api/v1/geofences/add/polygon with valid polygon
    '''
    mock_check_name.return_value = False
    mock_add_poly.return_value = 202

    coords = json.dumps([[30.0, 10.0], [40.0, 40.0], [20.0, 40.0], [10.0, 20.0], [30.0, 10.0]]) 

    response = client.post('/api/v1/geofences/add/polygon', data={
        'name': 'TestPoly', 'desc': 'Poly Desc', 'coords': coords
    })

    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['geofence_id'] == 202
    mock_add_poly.assert_called_once()

def test_add_geofence_polygon_missing_coords(client):
    '''
    Test /api/v1/geofences/add/polygon without coords
    '''
    response = client.post('/api/v1/geofences/add/polygon', data={'name': 'TestBox'})
    assert response.status_code == 400
    assert json.loads(response.data)['error'] == 'Array of [long, lat] expected.'

def test_add_geofence_polygon_invalid_json(client):
    '''
    Test /api/v1/geofences/add/polygon with invalid JSON coords
    '''
    response = client.post('/api/v1/geofences/add/polygon', data={
        'name': 'TestPoly', 'coords': 'this is not json'
    })
    assert response.status_code == 400
    assert 'Invalid coordinates format' in json.loads(response.data)['error']

@patch('app.modules.geofences.routes.Polygon')
@patch('app.modules.geofences.routes.check_if_geofence_name_exists')
def test_add_geofence_polygon_invalid_geometry(mock_check_name, mock_poly_class, client):
    '''
    Test /api/v1/geofences/add/polygon with invalid polygon geometry
    '''
    mock_check_name.return_value = False

    mock_poly_instance = MagicMock()
    mock_poly_instance.is_valid = False 
    mock_poly_class.return_value = mock_poly_instance

    coords = json.dumps([[0, 0], [1, 1], [2, 2], [0, 0]]) 
    response = client.post('/api/v1/geofences/add/polygon', data={
        'name': 'TestPoly', 'coords': coords
    })
    assert response.status_code == 400
    assert 'Invalid polygon geometry' in json.loads(response.data)['error']

@patch('app.modules.geofences.routes.check_if_geofence_name_exists')
def test_add_geofence_polygon_name_exists(mock_check_name, client):
    '''
    Test /api/v1/geofences/add/polygon with existing name
    '''
    mock_check_name.return_value = True

    coords = json.dumps([[0, 0], [1, 1], [2, 2], [0, 0]]) 
    response = client.post('/api/v1/geofences/add/polygon', data={
        'coords': coords,
        'name': 'ExistingBox', 'desc': 'Desc'
    })
    assert response.status_code == 403
    assert 'already exists' in json.loads(response.data)['error']


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
    assert data['data'][0]['geofence_polygon'] == [[-180, -90], [180, 90]]


# ==========================================
# Tests for GET /api/v1/geofences/<int:geofence_id>
# ==========================================

@patch('app.modules.geofences.routes.get_geofence_polygon_vertices')
@patch('app.modules.geofences.routes.get_geofence_by_id')
def test_get_geofence_by_id_success(mock_get_geofence, mock_get_verts, client):
    '''
    Test GET /api/v1/geofences/<int:geofence_id> with valid ID
    '''
    mock_geofence = MagicMock()
    mock_geofence.geofence_id = 1
    mock_geofence.geofence_timestamp = "2023-10-25T10:00:00"
    mock_geofence.geofence_name = "Test Geofence"
    mock_geofence.geofence_description = "Test Description"

    mock_get_geofence.return_value = mock_geofence
    mock_get_verts.return_value = [[0.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 0.0]]

    response = client.get('/api/v1/geofences/1')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['data']['geofence_id'] == 1
    assert data['data']['geofence_name'] == "Test Geofence"
    assert data['data']['geofence_polygon'] == [[0.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 0.0]]

@patch('app.modules.geofences.routes.get_geofence_by_id')
def test_get_geofence_by_id_not_found(mock_get_geofence, client):
    '''
    Test GET /api/v1/geofences/<int:geofence_id> with non-existent ID
    '''
    mock_get_geofence.return_value = None

    response = client.get('/api/v1/geofences/999')

    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['error'] == "Geofence with ID 999 not found."

@patch('app.modules.geofences.routes.write_audit_log')
@patch('app.modules.geofences.routes.get_geofence_by_id')
def test_get_geofence_by_id_internal_error(mock_get_geofence, mock_audit, client):
    '''
    Test GET /api/v1/geofences/<int:geofence_id> when an exception occurs
    '''
    mock_get_geofence.side_effect = Exception("Database connection failed")

    response = client.get('/api/v1/geofences/1')

    assert response.status_code == 500
    data = json.loads(response.data)
    assert data['error'] == "Internal server error"
    assert "Database connection failed" in data['details']

# ==========================================
# Tests for POST/PATCH /api/v1/geofences/<geofence_id>/update
# ==========================================

@patch('app.modules.geofences.routes.write_audit_log')
@patch('app.modules.geofences.routes.update_geofence_in_db')
def test_update_geofence_by_id_success_name_desc(mock_update, mock_audit, client):
    '''
    Test updating Geofence with name and description
    '''
    mock_update.return_value = True

    response = client.post('/api/v1/geofences/1/update', data={
        'name': 'NewName', 'desc': 'NewDesc'
    })

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['geofence_id'] == 1
    mock_update.assert_called_once_with(geofence_id=1, name='NewName', desc='NewDesc', geometry_wkb=None)

@patch('app.modules.geofences.routes.write_audit_log')
@patch('app.modules.geofences.routes.update_geofence_in_db')
def test_update_geofence_by_id_success_coords(mock_update, mock_audit, client):
    '''
    Test updating Geofence with new coordinates
    '''
    mock_update.return_value = True
    coords = json.dumps([[0.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, 0.0], [0.0, 0.0]])

    response = client.patch('/api/v1/geofences/2/update', data={
        'coords': coords
    })

    assert response.status_code == 200
    assert mock_update.called
    call_kwargs = mock_update.call_args.kwargs
    assert call_kwargs['geofence_id'] == 2
    assert call_kwargs['name'] is None
    assert call_kwargs['desc'] is None
    assert call_kwargs['geometry_wkb'] is not None

@patch('app.modules.geofences.routes.write_audit_log')
@patch('app.modules.geofences.routes.update_geofence_in_db')
def test_update_geofence_by_id_success_bbox(mock_update, mock_audit, client):
    '''
    Test updating Geofence with new bounding box
    '''
    mock_update.return_value = True

    response = client.post('/api/v1/geofences/3/update', data={
        'lat_min': '10.0', 'lat_max': '20.0', 'long_min': '30.0', 'long_max': '40.0'
    })

    assert response.status_code == 200
    assert mock_update.called
    call_kwargs = mock_update.call_args.kwargs
    assert call_kwargs['geofence_id'] == 3
    assert call_kwargs['geometry_wkb'] is not None

def test_update_geofence_by_id_missing_fields(client):
    '''
    Test updating Geofence without providing any fields
    '''
    response = client.post('/api/v1/geofences/1/update', data={})
    assert response.status_code == 400
    assert json.loads(response.data)['error'] == 'Requires at least 1 field to update.'

def test_update_geofence_by_id_both_coords_and_bbox(client):
    '''
    Test updating Geofence with both coords and bbox (should fail)
    '''
    coords = json.dumps([[0.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, 0.0], [0.0, 0.0]])
    response = client.post('/api/v1/geofences/1/update', data={
        'coords': coords,
        'lat_min': '10.0', 'lat_max': '20.0', 'long_min': '30.0', 'long_max': '40.0'
    })
    assert response.status_code == 400
    assert 'not both' in json.loads(response.data)['error']

def test_update_geofence_by_id_invalid_coords_json(client):
    '''
    Test updating Geofence with invalid coords JSON
    '''
    response = client.post('/api/v1/geofences/1/update', data={
        'coords': 'invalid json'
    })
    assert response.status_code == 400
    assert 'Invalid coordinates format' in json.loads(response.data)['error']

@patch('app.modules.geofences.routes.Polygon')
@patch('app.modules.geofences.routes.update_geofence_in_db')
def test_update_geofence_by_id_invalid_polygon_geometry(mock_update, mock_poly_class, client):
    '''
    Test updating Geofence with invalid polygon geometry
    '''
    mock_poly_instance = MagicMock()
    mock_poly_instance.is_valid = False 
    mock_poly_class.return_value = mock_poly_instance

    coords = json.dumps([[0, 0], [1, 1], [2, 2], [0, 0]]) 
    response = client.post('/api/v1/geofences/1/update', data={
        'coords': coords
    })
    assert response.status_code == 400
    assert 'Invalid polygon geometry' in json.loads(response.data)['error']

@patch('app.modules.geofences.routes.update_geofence_in_db')
def test_update_geofence_by_id_not_found(mock_update, client):
    '''
    Test updating Geofence that does not exist
    '''
    mock_update.return_value = False

    response = client.post('/api/v1/geofences/999/update', data={
        'name': 'NewName'
    })

    assert response.status_code == 404
    assert 'not found' in json.loads(response.data)['error']

@patch('app.modules.geofences.routes.write_audit_log')
@patch('app.modules.geofences.routes.check_if_geofence_name_exists')
@patch('app.modules.geofences.routes.update_geofence_in_db')
def test_update_geofence_by_id_duplicate_name(mock_update, mock_check_name, mock_audit, client):
    '''
    Test updating AOI with a name that already exists in the database
    '''
    mock_check_name.return_value = True

    # Adjust the endpoint URL if your geofence update route is different
    response = client.post('/api/v1/geofences/1/update', data={
        'name': 'ExistingName'
    })

    assert response.status_code == 403
    data = json.loads(response.data)
    # Adjust the expected error message if your geofence route formats it differently
    assert data['error'] == "Geofence with name 'ExistingName' already exists."

# ==========================================
# Tests for DELETE /api/v1/geofences/<int:geofence_id>/delete
# ==========================================

@patch('app.modules.geofences.routes.delete_geofence_in_db')
@patch('app.modules.geofences.routes.get_geofence_by_id')
def test_delete_geofence_success(mock_get_geofence, mock_delete, client):
    '''
    Test successful deletion of an Geofence
    '''
    mock_geofence = MagicMock()
    mock_geofence.geofence_name = "TestGeofence"

    mock_get_geofence.side_effect = [mock_geofence, None]
    mock_delete.return_value = True

    response = client.delete('/api/v1/geofences/1/delete?geofence_name=TestGeofence')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'deleted successfully' in data['message']
    mock_delete.assert_called_once_with(1)

def test_delete_geofence_missing_name(client):
    '''
    Test deletion without providing the required geofence_name query parameter
    '''
    response = client.delete('/api/v1/geofences/1/delete')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == "Missing required query parameter: 'geofence_name'."

@patch('app.modules.geofences.routes.get_geofence_by_id')
def test_delete_geofence_not_found(mock_get_geofence, client):
    '''
    Test deletion of a non-existent Geofence
    '''
    mock_get_geofence.return_value = None

    response = client.delete('/api/v1/geofences/999/delete?geofence_name=GhostGeofence')

    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['error'] == "Geofence with ID 999 not found."

@patch('app.modules.geofences.routes.get_geofence_by_id')
def test_delete_geofence_name_mismatch(mock_get_geofence, client):
    '''
    Test deletion with an incorrect geofence_name
    '''
    mock_geofence = MagicMock()
    mock_geofence.geofence_name = "RealGeofenceName"
    mock_get_geofence.return_value = mock_geofence

    response = client.delete('/api/v1/geofences/1/delete?geofence_name=WrongGeofenceName')

    assert response.status_code == 403
    data = json.loads(response.data)
    assert data['error'] == "'geofence_name' does not match the Geofence with the given ID."

@patch('app.modules.geofences.routes.delete_geofence_in_db')
@patch('app.modules.geofences.routes.get_geofence_by_id')
def test_delete_geofence_db_failure(mock_get_geofence, mock_delete, client):
    '''
    Test when the Geofence is not actually deleted from the database 
    '''
    mock_geofence = MagicMock()
    mock_geofence.geofence_name = "TestGeofence"

    mock_get_geofence.return_value = mock_geofence
    mock_delete.return_value = True

    response = client.delete('/api/v1/geofences/1/delete?geofence_name=TestGeofence')

    assert response.status_code == 500
    data = json.loads(response.data)
    assert data['error'] == "Internal server error: Failed to delete Geofence."

@patch('app.modules.geofences.routes.write_audit_log')
@patch('app.modules.geofences.routes.get_geofence_by_id')
def test_delete_geofence_internal_error(mock_get_geofence, mock_audit, client):
    '''
    Test internal server error during the deletion process
    '''
    mock_get_geofence.side_effect = Exception("Database connection failed")

    response = client.delete('/api/v1/geofences/1/delete?geofence_name=TestGeofence')

    assert response.status_code == 500
    data = json.loads(response.data)
    assert data['error'] == "Internal server error"

    mock_audit.assert_called_once()
