import pytest
import json
from unittest.mock import patch, MagicMock
from flask import Flask

from app.modules.vessel_of_interest.routes import vessel_of_interest_bp

@pytest.fixture
def app():
    '''
    Create and configure a new app instance for each test.
    '''
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(vessel_of_interest_bp)
    return app

@pytest.fixture
def client(app):
    '''
    Create a test client for the app.
    '''
    return app.test_client()

# ==========================================
# Tests for POST /api/v1/vessel_of_interest/add
# ==========================================

@patch('app.modules.vessel_of_interest.routes.write_audit_log')
@patch('app.modules.vessel_of_interest.routes.add_vessel_of_interest')
@patch('app.modules.vessel_of_interest.routes.check_if_vessel_of_interest_name_exists')
def test_add_voi_success(mock_check_name, mock_add, mock_audit, client):
    '''
    Test /api/v1/vessel_of_interest/add with valid params
    '''
    mock_check_name.return_value = False
    mock_add.return_value = 101

    response = client.post('/api/v1/vessel_of_interest/add', data={
        'name': 'TestVOI', 
        'desc': 'Test Description', 
        'mmsi': '123456789', 
        'imo': '1234567'
    })

    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['voi_id'] == 101

    mock_add.assert_called_once_with('TestVOI', 'Test Description', '123456789', '1234567')

def test_add_voi_missing_name(client):
    '''
    Test /api/v1/vessel_of_interest/add without name
    '''
    response = client.post('/api/v1/vessel_of_interest/add', data={'desc': 'Test'})
    assert response.status_code == 400
    assert json.loads(response.data)['error'] == 'User-defined name for Vessel of Interest expected.'

def test_add_voi_invalid_mmsi(client):
    '''
    Test /api/v1/vessel_of_interest/add with invalid MMSI (not 9 digits)
    '''
    response = client.post('/api/v1/vessel_of_interest/add', data={
        'name': 'TestVOI', 'mmsi': '12345' 
    })
    assert response.status_code == 400
    assert json.loads(response.data)['error'] == 'MMSI should be 9 digits.'

def test_add_voi_invalid_imo(client):
    '''
    Test /api/v1/vessel_of_interest/add with invalid IMO (not 7 digits)
    '''
    response = client.post('/api/v1/vessel_of_interest/add', data={
        'name': 'TestVOI', 'imo': '123' 
    })
    assert response.status_code == 400
    assert json.loads(response.data)['error'] == 'IMO should be 7 digits.'

def test_add_voi_missing_mmsi_and_imo(client):
    '''
    Test /api/v1/vessel_of_interest/add without mmsi or imo
    '''
    response = client.post('/api/v1/vessel_of_interest/add', data={
        'name': 'TestVOI'
    })
    assert response.status_code == 400
    assert json.loads(response.data)['error'] == 'Either MMSI or IMO must be provided.'

@patch('app.modules.vessel_of_interest.routes.check_if_vessel_of_interest_name_exists')
def test_add_voi_name_exists(mock_check_name, client):
    '''
    Test /api/v1/vessel_of_interest/add with existing name
    '''
    mock_check_name.return_value = True

    response = client.post('/api/v1/vessel_of_interest/add', data={
        'name': 'ExistingVOI', 'mmsi': '123456789'
    })
    assert response.status_code == 403
    assert 'already exists' in json.loads(response.data)['error']

@patch('app.modules.vessel_of_interest.routes.write_audit_log')
@patch('app.modules.vessel_of_interest.routes.add_vessel_of_interest')
@patch('app.modules.vessel_of_interest.routes.check_if_vessel_of_interest_name_exists')
def test_add_voi_db_exception(mock_check_name, mock_add, mock_audit, client):
    '''
    Test /api/v1/vessel_of_interest/add when DB add raises exception
    '''
    mock_check_name.return_value = False
    mock_add.side_effect = Exception("Database connection failed")

    response = client.post('/api/v1/vessel_of_interest/add', data={
        'name': 'TestVOI', 'mmsi': '123456789'
    })
    assert response.status_code == 500
    data = json.loads(response.data)
    assert data['error'] == 'Internal server error'
    assert 'Database connection failed' in data['details']

# ==========================================
# Tests for GET /api/v1/vessel_of_interest/get/all
# ==========================================

@patch('app.modules.vessel_of_interest.routes.get_all_vessel_of_interest')
def test_get_all_voi_success(mock_get_all, client):
    '''
    Test /api/v1/vessel_of_interest/get/all with valid data
    '''
    mock_voi = MagicMock()
    mock_voi.vessel_of_interest_id = 1
    mock_voi.vessel_of_interest_desc_name = "Test VOI"
    mock_voi.vessel_of_interest_description = "Test Desc"
    mock_voi.vessel_of_interest_mmsi = "123456789"
    mock_voi.vessel_of_interest_imo = "1234567"

    mock_get_all.return_value = [mock_voi]

    response = client.get('/api/v1/vessel_of_interest/get/all')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['count'] == 1
    assert data['data'][0]['vessel_of_interest_desc_name'] == "Test VOI"
    assert data['data'][0]['vessel_of_interest_mmsi'] == "123456789"

@patch('app.modules.vessel_of_interest.routes.get_all_vessel_of_interest')
def test_get_all_voi_internal_error(mock_get_all, client):
    '''
    Test /api/v1/vessel_of_interest/get/all when an exception occurs
    '''
    mock_get_all.side_effect = Exception("Database connection failed")

    response = client.get('/api/v1/vessel_of_interest/get/all')

    assert response.status_code == 500
    data = json.loads(response.data)
    assert data['error'] == "Internal get_all_vessel_of_interest_web error"
    assert "Database connection failed" in data['details']

# ==========================================
# Tests for GET /api/v1/vessel_of_interest/<int:vessel_of_interest_id>
# ==========================================

@patch('app.modules.vessel_of_interest.routes.get_vessel_of_interest_by_vessel_of_interest_id')
def test_get_voi_by_id_success(mock_get_voi, client):
    '''
    Test GET /api/v1/vessel_of_interest/<int:vessel_of_interest_id> with valid ID
    '''
    mock_voi = MagicMock()
    mock_voi.vessel_of_interest_id = 1
    mock_voi.vessel_of_interest_desc_name = "Test VOI"
    mock_voi.vessel_of_interest_description = "Test Desc"
    mock_voi.vessel_of_interest_mmsi = "123456789"
    mock_voi.vessel_of_interest_imo = "1234567"

    mock_get_voi.return_value = mock_voi

    response = client.get('/api/v1/vessel_of_interest/1')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['data']['vessel_of_interest_id'] == 1
    assert data['data']['vessel_of_interest_desc_name'] == "Test VOI"

@patch('app.modules.vessel_of_interest.routes.get_vessel_of_interest_by_vessel_of_interest_id')
def test_get_voi_by_id_not_found(mock_get_voi, client):
    '''
    Test GET /api/v1/vessel_of_interest/<int:vessel_of_interest_id> with non-existent ID
    '''
    mock_get_voi.return_value = None

    response = client.get('/api/v1/vessel_of_interest/999')

    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['error'] == "Vessel of interest with ID 999 not found."

@patch('app.modules.vessel_of_interest.routes.get_vessel_of_interest_by_vessel_of_interest_id')
def test_get_voi_by_id_internal_error(mock_get_voi, client):
    '''
    Test GET /api/v1/vessel_of_interest/<int:vessel_of_interest_id> when an exception occurs
    '''
    mock_get_voi.side_effect = Exception("Database connection failed")

    response = client.get('/api/v1/vessel_of_interest/1')

    assert response.status_code == 500
    data = json.loads(response.data)
    assert data['error'] == "Internal server error"
    assert "Database connection failed" in data['details']
