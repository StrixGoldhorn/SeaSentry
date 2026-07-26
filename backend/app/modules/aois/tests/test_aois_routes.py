import pytest
import json
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import IntegrityError
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
# Tests for GET /api/v1/aois/<int:aoi_id>
# ==========================================

@patch('app.modules.aois.routes.get_aoi_polygon_vertices')
@patch('app.modules.aois.routes.get_aoi_by_id')
def test_get_aoi_by_id_success(mock_get_aoi, mock_get_verts, client):
    '''
    Test GET /api/v1/aois/<int:aoi_id> with valid ID
    '''
    mock_aoi = MagicMock()
    mock_aoi.area_of_interest_id = 1
    mock_aoi.area_of_interest_timestamp = "2023-10-25T10:00:00"
    mock_aoi.area_of_interest_name = "Test AOI"
    mock_aoi.area_of_interest_description = "Test Description"

    mock_get_aoi.return_value = mock_aoi
    mock_get_verts.return_value = [[0.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 0.0]]

    response = client.get('/api/v1/aois/1')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['data']['area_of_interest_id'] == 1
    assert data['data']['area_of_interest_name'] == "Test AOI"
    assert data['data']['area_of_interest_polygon'] == [[0.0, 0.0], [1.0, 1.0], [0.0, 1.0], [0.0, 0.0]]

@patch('app.modules.aois.routes.get_aoi_by_id')
def test_get_aoi_by_id_not_found(mock_get_aoi, client):
    '''
    Test GET /api/v1/aois/<int:aoi_id> with non-existent ID
    '''
    mock_get_aoi.return_value = None

    response = client.get('/api/v1/aois/999')

    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['error'] == "AOI with ID 999 not found."

@patch('app.modules.aois.routes.write_audit_log')
@patch('app.modules.aois.routes.get_aoi_by_id')
def test_get_aoi_by_id_internal_error(mock_get_aoi, mock_audit, client):
    '''
    Test GET /api/v1/aois/<int:aoi_id> when an exception occurs
    '''
    mock_get_aoi.side_effect = Exception("Database connection failed")

    response = client.get('/api/v1/aois/1')

    assert response.status_code == 500
    data = json.loads(response.data)
    assert data['error'] == "Internal server error"
    assert "Database connection failed" in data['details']

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
@patch('app.modules.aois.routes.check_if_aoi_name_exists')
@patch('app.modules.aois.routes.update_aoi_in_db')
def test_update_aoi_by_id_success_name_desc(mock_update, mock_check_name, mock_audit, client):
    '''
    Test updating AOI with name and description
    '''
    mock_check_name.return_value = False
    mock_update.return_value = True

    response = client.post('/api/v1/aois/1/update', data={
        'name': 'NewName', 'desc': 'NewDesc'
    })

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['aoi_id'] == 1
    mock_update.assert_called_once_with(aoi_id=1, name='NewName', desc='NewDesc', geometry_wkb=None)

@patch('app.modules.aois.routes.write_audit_log')
@patch('app.modules.aois.routes.update_aoi_in_db')
def test_update_aoi_by_id_success_coords(mock_update, mock_audit, client):
    '''
    Test updating AOI with new coordinates
    '''
    mock_update.return_value = True
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

@patch('app.modules.aois.routes.write_audit_log')
@patch('app.modules.aois.routes.update_aoi_in_db')
def test_update_aoi_by_id_success_bbox(mock_update, mock_audit, client):
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

@patch('app.modules.aois.routes.check_if_aoi_name_exists')
@patch('app.modules.aois.routes.update_aoi_in_db')
def test_update_aoi_by_id_not_found(mock_update, mock_check_name, client):
    '''
    Test updating AOI that does not exist
    '''
    mock_check_name.return_value = False
    mock_update.return_value = False

    response = client.post('/api/v1/aois/999/update', data={
        'name': 'NewName'
    })

    assert response.status_code == 404
    assert 'not found' in json.loads(response.data)['error']
@patch('app.modules.aois.routes.write_audit_log')
@patch('app.modules.aois.routes.check_if_aoi_name_exists')
@patch('app.modules.aois.routes.update_aoi_in_db')
def test_update_aoi_by_id_duplicate_name(mock_update, mock_check_name, mock_audit, client):
    '''
    Test updating AOI with a name that already exists in the database
    '''
    mock_check_name.return_value = True

    response = client.post('/api/v1/aois/1/update', data={
        'name': 'ExistingName'
    })

    assert response.status_code == 403
    data = json.loads(response.data)
    assert data['error'] == "AOI with name 'ExistingName' already exists."

# ==========================================
# Tests for DELETE /api/v1/aois/<int:aoi_id>/delete
# ==========================================

@patch('app.modules.aois.routes.delete_aoi_in_db')
@patch('app.modules.aois.routes.get_aoi_by_id')
def test_delete_aoi_success(mock_get_aoi, mock_delete, client):
    '''
    Test successful deletion of an AOI
    '''
    mock_aoi = MagicMock()
    mock_aoi.area_of_interest_name = "TestAOI"

    mock_get_aoi.side_effect = [mock_aoi, None]
    mock_delete.return_value = True

    response = client.delete('/api/v1/aois/1/delete?aoi_name=TestAOI')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'deleted successfully' in data['message']
    mock_delete.assert_called_once_with(1)

def test_delete_aoi_missing_name(client):
    '''
    Test deletion without providing the required aoi_name query parameter
    '''
    response = client.delete('/api/v1/aois/1/delete')

    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == "Missing required query parameter: 'aoi_name'."

@patch('app.modules.aois.routes.get_aoi_by_id')
def test_delete_aoi_not_found(mock_get_aoi, client):
    '''
    Test deletion of a non-existent AOI
    '''
    mock_get_aoi.return_value = None

    response = client.delete('/api/v1/aois/999/delete?aoi_name=GhostAOI')

    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['error'] == "AOI with ID 999 not found."

@patch('app.modules.aois.routes.get_aoi_by_id')
def test_delete_aoi_name_mismatch(mock_get_aoi, client):
    '''
    Test deletion with an incorrect aoi_name
    '''
    mock_aoi = MagicMock()
    mock_aoi.area_of_interest_name = "RealAOIName"
    mock_get_aoi.return_value = mock_aoi

    response = client.delete('/api/v1/aois/1/delete?aoi_name=WrongAOIName')

    assert response.status_code == 403
    data = json.loads(response.data)
    assert data['error'] == "'aoi_name' does not match the AOI with the given ID."

@patch('app.modules.aois.routes.delete_aoi_in_db')
@patch('app.modules.aois.routes.get_aoi_by_id')
def test_delete_aoi_db_failure(mock_get_aoi, mock_delete, client):
    '''
    Test when the AOI is not actually deleted from the database 
    '''
    mock_aoi = MagicMock()
    mock_aoi.area_of_interest_name = "TestAOI"

    mock_get_aoi.return_value = mock_aoi
    mock_delete.return_value = True

    response = client.delete('/api/v1/aois/1/delete?aoi_name=TestAOI')

    assert response.status_code == 500
    data = json.loads(response.data)
    assert data['error'] == "Internal server error: Failed to delete AOI."

@patch('app.modules.aois.routes.write_audit_log')
@patch('app.modules.aois.routes.get_aoi_by_id')
def test_delete_aoi_internal_error(mock_get_aoi, mock_audit, client):
    '''
    Test internal server error during the deletion process
    '''
    mock_get_aoi.side_effect = Exception("Database connection failed")

    response = client.delete('/api/v1/aois/1/delete?aoi_name=TestAOI')

    assert response.status_code == 500
    data = json.loads(response.data)
    assert data['error'] == "Internal server error"

    mock_audit.assert_called_once()

# ==========================================
# Tests for POST /api/v1/aois/<int:aoi_id>/scrape
# ==========================================

def create_mock_aoi():
    '''Helper to create a mock AOI object'''
    mock_aoi = MagicMock()
    mock_aoi.area_of_interest_id = 1
    return mock_aoi

@patch('app.modules.aois.routes.run_force_all_scrapers_for_aoi')
@patch('app.modules.aois.routes.get_aoi_by_id')
def test_force_scrape_success(mock_get_aoi, mock_run_scrapers, client):
    '''Test successful forced scrape of an AOI'''
    mock_get_aoi.return_value = create_mock_aoi()
    mock_run_scrapers.return_value = [MagicMock(), MagicMock()]

    response = client.post('/api/v1/aois/1/scrape')
    assert response.status_code == 200
    data = json.loads(response.data)

    assert data == {"status": "success"}

    mock_get_aoi.assert_called_once_with(1)
    mock_run_scrapers.assert_called_once()
    args, _ = mock_run_scrapers.call_args
    assert args[0] == 1

@patch('app.modules.aois.routes.get_aoi_by_id')
def test_force_scrape_not_found(mock_get_aoi, client):
    '''Test scraping an AOI that does not exist returns 404'''
    mock_get_aoi.return_value = None

    response = client.post('/api/v1/aois/67/scrape')

    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['error'] == "AOI with ID 67 not found."

    mock_get_aoi.assert_called_once_with(67)

@patch('app.modules.aois.routes.write_audit_log')
@patch('app.modules.aois.routes.logger')
@patch('app.modules.aois.routes.run_force_all_scrapers_for_aoi')
@patch('app.modules.aois.routes.get_aoi_by_id')
def test_force_scrape_exception(mock_get_aoi, mock_run_scrapers, mock_logger, mock_audit, client):
    '''Test internal server error handling during scrape'''
    mock_get_aoi.return_value = create_mock_aoi()
    mock_run_scrapers.side_effect = Exception("Scraper thread failed to start")

    response = client.post('/api/v1/aois/1/scrape')

    assert response.status_code == 500
    data = json.loads(response.data)
    assert data['error'] == "Internal server error"
    assert "Scraper thread failed to start" in data['details']
    mock_logger.error.assert_called_once()
    mock_audit.assert_called_once()
