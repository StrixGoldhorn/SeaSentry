import pytest
import json
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock
from flask import Flask

from app.modules.alerts.routes import alerts_bp

@pytest.fixture
def app():
    '''
    Create and configure a new app instance for each test.
    '''
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(alerts_bp)
    return app

@pytest.fixture
def client(app):
    '''
    Create a test client for the app.
    '''
    return app.test_client()

# ==========================================
# Helper Mocks
# ==========================================

def create_mock_alert_history(alert_id=1, is_read=False):
    '''Helper to create a mock AlertHistory object'''
    mock_alert = MagicMock()
    mock_alert.alert_history_id = alert_id
    mock_alert.alert_history_timestamp = datetime.now(timezone.utc)
    mock_alert.alert_history_read = is_read
    mock_alert.alert_history_read_at = None
    mock_alert.alert_history_alert_rule_id = 10
    mock_alert.alert_history_context = {"vessel": "TestVessel"}
    return mock_alert

def create_mock_alert_rule(rule_id=1):
    '''Helper to create a mock AlertRule object'''
    mock_rule = MagicMock()
    mock_rule.alert_rule_id = rule_id
    mock_rule.alert_rule_timestamp = datetime.now(timezone.utc)
    mock_rule.alert_rule_name = "Test Rule"
    mock_rule.alert_rule_description = "Test Description"
    mock_rule.alert_rule_params = {"field": "speed", "operator": ">", "value": 10}
    mock_rule.alert_rule_enabled = True
    return mock_rule

# ==========================================
# Tests for GET /api/v1/alerts/history/all
# ==========================================

@patch('app.modules.alerts.routes.get_all_alert_history')
def test_get_all_alert_history_success(mock_get_history, client):
    '''
    Test /api/v1/alerts/history/all with valid params
    '''
    mock_get_history.return_value = [create_mock_alert_history(1, False), create_mock_alert_history(2, True)]

    response = client.get('/api/v1/alerts/history/all?limit=10&offset=0&start_time=2023-10-27T10:00:00&end_time=2023-10-28T10:00:00')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['count'] == 2
    assert data['filters_applied']['limit'] == 10

    mock_get_history.assert_called_once_with(
        datetime.fromisoformat('2023-10-27T10:00:00'),
        datetime.fromisoformat('2023-10-28T10:00:00'),
        10, 0
    )

@patch('app.modules.alerts.routes.get_all_alert_history')
def test_get_all_alert_history_invalid_start_time(mock_get_history, client):
    '''
    Test /api/v1/alerts/history/all with invalid start_time format
    '''
    response = client.get('/api/v1/alerts/history/all?start_time=not-a-date')

    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'Invalid start_time format' in data['error']
    mock_get_history.assert_not_called()

@patch('app.modules.alerts.routes.get_all_alert_history')
def test_get_all_alert_history_invalid_limit(mock_get_history, client):
    '''
    Test /api/v1/alerts/history/all with negative limit
    '''
    response = client.get('/api/v1/alerts/history/all?limit=-5')

    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'Limit must be a positive integer' in data['error']

# ==========================================
# Tests for GET /api/v1/alerts/history/unread
# ==========================================

@patch('app.modules.alerts.routes.get_all_alert_history')
def test_get_unread_alert_history_success(mock_get_history, client):
    '''
    Test /api/v1/alerts/history/unread calls helper with unread=False flag
    '''
    mock_get_history.return_value = [create_mock_alert_history(1, False)]

    response = client.get('/api/v1/alerts/history/unread')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['count'] == 1

    # Verify the 5th argument is False (indicating unread only)
    mock_get_history.assert_called_once_with(None, None, None, None, False)

# ==========================================
# Tests for POST /api/v1/alerts/history/<id>/mark/read
# ==========================================

@patch('app.modules.alerts.routes.mark_alert_as_read')
def test_mark_alert_history_read_success(mock_mark_read, client):
    '''
    Test marking an alert as read successfully
    '''
    mock_mark_read.return_value = True

    response = client.post('/api/v1/alerts/history/5/mark/read')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    mock_mark_read.assert_called_once_with(5)

@patch('app.modules.alerts.routes.mark_alert_as_read')
def test_mark_alert_history_read_not_found(mock_mark_read, client):
    '''
    Test marking a non-existent alert as read
    '''
    mock_mark_read.return_value = False

    response = client.post('/api/v1/alerts/history/999/mark/read')

    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'not found' in data['message']

# ==========================================
# Tests for POST /api/v1/alerts/history/<id>/mark/unread
# ==========================================

@patch('app.modules.alerts.routes.mark_alert_as_unread')
def test_mark_alert_history_unread_success(mock_mark_unread, client):
    '''
    Test marking an alert as unread successfully
    '''
    mock_mark_unread.return_value = True

    response = client.post('/api/v1/alerts/history/5/mark/unread')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    mock_mark_unread.assert_called_once_with(5)

# ==========================================
# Tests for GET /api/v1/alerts/rule/all
# ==========================================

@patch('app.modules.alerts.routes.get_all_alert_rule')
def test_get_all_alert_rule_success(mock_get_rules, client):
    '''
    Test fetching all alert rules
    '''
    mock_get_rules.return_value = [create_mock_alert_rule(1), create_mock_alert_rule(2)]

    response = client.get('/api/v1/alerts/rule/all')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['count'] == 2
    assert data['data'][0]['alert_rule_name'] == 'Test Rule'

# ==========================================
# Tests for POST /api/v1/alerts/rule/add/
# ==========================================

@patch('app.modules.alerts.routes.add_alert_rule_to_db')
@patch('app.modules.alerts.routes.RuleTreeAdapter.validate_python')
def test_add_alert_rule_single_success(mock_validate, mock_add_db, client):
    '''
    Test adding a single valid alert rule
    '''
    # Mock the validated params object
    mock_validated_params = MagicMock()
    mock_validated_params.model_dump.return_value = {"field": "speed", "operator": ">", "value": 10.0}
    mock_validate.return_value = mock_validated_params

    mock_add_db.return_value = 42

    payload = {
        "name": "High Speed Alert",
        "description": "Triggers when speed > 10",
        "params": {"field": "speed", "operator": ">", "value": 10.0}
    }

    response = client.post('/api/v1/alerts/rule/add/', json=payload)

    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['alert_rule_id'] == 42

    mock_validate.assert_called_once_with(payload['params'])
    mock_add_db.assert_called_once_with("High Speed Alert", "Triggers when speed > 10", mock_validated_params.model_dump.return_value)

@patch('app.modules.alerts.routes.add_alert_rule_to_db')
@patch('app.modules.alerts.routes.RuleTreeAdapter.validate_python')
def test_add_alert_rule_combined_success(mock_validate, mock_add_db, client):
    '''
    Test adding a combined (OR/AND) alert rule
    '''
    mock_validated_params = MagicMock()
    mock_validated_params.model_dump.return_value = {"rules": [], "combinator": "or"}
    mock_validate.return_value = mock_validated_params
    mock_add_db.return_value = 43

    payload = {
        "name": "Geofence Alert",
        "description": "Enter or exit zone",
        "params": {
            "rules": [{"field": "enter_geofence", "value": True}],
            "combinator": "or"
        }
    }

    response = client.post('/api/v1/alerts/rule/add/', json=payload)

    assert response.status_code == 201
    mock_add_db.assert_called_once()

def test_add_alert_rule_missing_name(client):
    '''
    Test adding a rule without the required 'name' field
    '''
    payload = {"description": "No name", "params": {"field": "speed"}}
    response = client.post('/api/v1/alerts/rule/add/', json=payload)

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "Missing required fields: 'name'" in data['error']

def test_add_alert_rule_missing_params(client):
    '''
    Test adding a rule without the required 'params' field
    '''
    payload = {"name": "Test Rule", "description": "No params"}
    response = client.post('/api/v1/alerts/rule/add/', json=payload)

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "Missing required fields: 'params'" in data['error']

@patch('app.modules.alerts.routes.RuleTreeAdapter.validate_python')
def test_add_alert_rule_invalid_params(mock_validate, client):
    '''
    Test adding a rule where RuleTreeAdapter validation fails
    '''
    mock_validate.side_effect = ValueError("Invalid operator")

    payload = {
        "name": "Bad Rule",
        "params": {"field": "speed", "operator": "INVALID"}
    }
    response = client.post('/api/v1/alerts/rule/add/', json=payload)

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "Invalid rule parameters" in data['error']

@patch('app.modules.alerts.routes.write_audit_log')
@patch('app.modules.alerts.routes.add_alert_rule_to_db')
@patch('app.modules.alerts.routes.RuleTreeAdapter.validate_python')
def test_add_alert_rule_internal_error(mock_validate, mock_add_db, mock_audit, client):
    '''
    Test that internal server errors are caught, logged, and return 500
    '''
    mock_validated_params = MagicMock()
    mock_validated_params.model_dump.return_value = {}
    mock_validate.return_value = mock_validated_params

    mock_add_db.side_effect = Exception("Database connection failed")

    payload = {"name": "Test", "params": {}}
    response = client.post('/api/v1/alerts/rule/add/', json=payload)

    assert response.status_code == 500
    data = json.loads(response.data)
    assert "Internal server error" in data['error']

    mock_audit.assert_called_once()
