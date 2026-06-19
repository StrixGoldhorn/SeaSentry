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
@patch('app.modules.alerts.routes.build_sqlalchemy_expression')
@patch('app.modules.alerts.routes.add_alert_rule_to_db')
@patch('app.modules.alerts.routes.RuleTreeAdapter.validate_python')
def test_add_alert_rule_single_success(mock_validate, mock_add_db, mock_build_expr, client):
    '''
    Test adding a single valid alert rule
    '''
    mock_validated_params = MagicMock()
    mock_validated_params.model_dump.return_value = {"field": "speed", "operator": ">", "value": 10.0}
    mock_validate.return_value = mock_validated_params

    mock_build_expr.return_value = True
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

@patch('app.modules.alerts.routes.build_sqlalchemy_expression')
@patch('app.modules.alerts.routes.add_alert_rule_to_db')
@patch('app.modules.alerts.routes.RuleTreeAdapter.validate_python')
def test_add_alert_rule_combined_success(mock_validate, mock_add_db, mock_build_expr, client):
    '''
    Test adding a combined (OR/AND) alert rule
    '''
    mock_validated_params = MagicMock()
    mock_validated_params.model_dump.return_value = {"rules": [], "combinator": "or"}
    mock_validate.return_value = mock_validated_params
    mock_build_expr.return_value = True
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

@patch('app.modules.alerts.routes.build_sqlalchemy_expression')
@patch('app.modules.alerts.routes.write_audit_log')
@patch('app.modules.alerts.routes.add_alert_rule_to_db')
@patch('app.modules.alerts.routes.RuleTreeAdapter.validate_python')
def test_add_alert_rule_internal_error(mock_validate, mock_add_db, mock_audit, mock_build_expr, client):
    '''
    Test that internal server errors are caught, logged, and return 500
    '''
    mock_validated_params = MagicMock()
    mock_validated_params.model_dump.return_value = {}
    mock_validate.return_value = mock_validated_params
    mock_build_expr.return_value = True

    mock_add_db.side_effect = Exception("Database connection failed")

    payload = {"name": "Test", "params": {}}
    response = client.post('/api/v1/alerts/rule/add/', json=payload)

    assert response.status_code == 500
    data = json.loads(response.data)
    assert "Internal server error" in data['error']

    mock_audit.assert_called_once()

# ==========================================
# Tests for POST /api/v1/alerts/rule/<id>/mark/disable
# ==========================================

@patch('app.modules.alerts.routes.mark_rule_as_disable')
def test_mark_alert_rule_disable_success(mock_disable, client):
    '''
    Test disabling an alert rule successfully
    '''
    mock_disable.return_value = True

    response = client.post('/api/v1/alerts/rule/5/mark/disable')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    mock_disable.assert_called_once_with(5)

@patch('app.modules.alerts.routes.mark_rule_as_disable')
def test_mark_alert_rule_disable_not_found(mock_disable, client):
    '''
    Test disabling a non-existent alert rule
    '''
    mock_disable.return_value = False

    response = client.post('/api/v1/alerts/rule/999/mark/disable')

    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'not found' in data['message']

@patch('app.modules.alerts.routes.mark_rule_as_disable')
def test_mark_alert_rule_disable_internal_error(mock_disable, client):
    '''
    Test internal server error when disabling an alert rule
    '''
    mock_disable.side_effect = Exception("Database connection failed")

    response = client.post('/api/v1/alerts/rule/5/mark/disable')

    assert response.status_code == 500
    data = json.loads(response.data)
    assert data['error'] == 'Internal server error'
    assert 'Database connection failed' in data['details']

# ==========================================
# Tests for POST /api/v1/alerts/rule/<id>/mark/enable
# ==========================================

@patch('app.modules.alerts.routes.mark_rule_as_enable')
def test_mark_alert_rule_enable_success(mock_enable, client):
    '''
    Test enabling an alert rule successfully
    '''
    mock_enable.return_value = True

    response = client.post('/api/v1/alerts/rule/5/mark/enable')

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    mock_enable.assert_called_once_with(5)

@patch('app.modules.alerts.routes.mark_rule_as_enable')
def test_mark_alert_rule_enable_not_found(mock_enable, client):
    '''
    Test enabling a non-existent alert rule
    '''
    mock_enable.return_value = False

    response = client.post('/api/v1/alerts/rule/999/mark/enable')

    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'not found' in data['message']

@patch('app.modules.alerts.routes.mark_rule_as_enable')
def test_mark_alert_rule_enable_internal_error(mock_enable, client):
    '''
    Test internal server error when enabling an alert rule
    '''
    mock_enable.side_effect = Exception("Database connection failed")

    response = client.post('/api/v1/alerts/rule/5/mark/enable')

    assert response.status_code == 500
    data = json.loads(response.data)
    assert data['error'] == 'Internal server error'
    assert 'Database connection failed' in data['details']

# ==========================================
# Tests for POST/PATCH/PUT /api/v1/alerts/rule/<id>/update
# ==========================================

@patch('app.modules.alerts.routes.update_alert_rule_in_db')
def test_update_alert_rule_success_name_only(mock_update, client):
    '''
    Test updating just the name of an alert rule
    '''
    mock_update.return_value = True

    payload = {"name": "Updated Rule Name"}
    response = client.post('/api/v1/alerts/rule/5/update', json=payload)

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['alert_rule_id'] == 5

    mock_update.assert_called_once_with(
        alert_rule_id=5,
        name="Updated Rule Name",
        desc=None,
        params=None
    )

@patch('app.modules.alerts.routes.build_sqlalchemy_expression')
@patch('app.modules.alerts.routes.update_alert_rule_in_db')
@patch('app.modules.alerts.routes.RuleTreeAdapter.validate_python')
def test_update_alert_rule_success_with_params(mock_validate, mock_update, mock_build_expr, client):
    '''
    Test updating the params of an alert rule (requires validation and dry-run)
    '''
    mock_validated_params = MagicMock()
    mock_validated_params.model_dump.return_value = {"field": "speed", "operator": ">", "value": 20.0}
    mock_validate.return_value = mock_validated_params
    mock_build_expr.return_value = True
    mock_update.return_value = True

    payload = {
        "params": {"field": "speed", "operator": ">", "value": 20.0}
    }
    response = client.patch('/api/v1/alerts/rule/5/update', json=payload)

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'

    mock_validate.assert_called_once_with(payload['params'])
    mock_update.assert_called_once_with(
        alert_rule_id=5,
        name=None,
        desc=None,
        params=mock_validated_params.model_dump.return_value
    )

def test_update_alert_rule_missing_all_fields(client):
    '''
    Test updating without providing any fields to update
    '''
    payload = {}
    response = client.post('/api/v1/alerts/rule/5/update', json=payload)

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "At least one field" in data['error']

@patch('app.modules.alerts.routes.RuleTreeAdapter.validate_python')
def test_update_alert_rule_invalid_params_structure(mock_validate, client):
    '''
    Test updating params where Pydantic validation fails
    '''
    mock_validate.side_effect = ValueError("Invalid structure")

    payload = {"params": {"invalid": "structure"}}
    response = client.post('/api/v1/alerts/rule/5/update', json=payload)

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "Invalid rule parameters" in data['error']

@patch('app.modules.alerts.routes.build_sqlalchemy_expression')
@patch('app.modules.alerts.routes.RuleTreeAdapter.validate_python')
def test_update_alert_rule_invalid_params_logic(mock_validate, mock_build_expr, client):
    '''
    Test updating params where SQLAlchemy dry-run fails (ValueError)
    '''
    mock_validated_params = MagicMock()
    mock_validate.return_value = mock_validated_params
    mock_build_expr.side_effect = ValueError("Invalid operator for mmsi")

    payload = {"params": {"field": "mmsi", "operator": "LIKE", "value": "123"}}
    response = client.post('/api/v1/alerts/rule/5/update', json=payload)

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "Invalid rule logic" in data['error']

@patch('app.modules.alerts.routes.build_sqlalchemy_expression')
@patch('app.modules.alerts.routes.update_alert_rule_in_db')
@patch('app.modules.alerts.routes.RuleTreeAdapter.validate_python')
def test_update_alert_rule_not_found(mock_validate, mock_update, mock_build_expr, client):
    '''
    Test updating a non-existent alert rule
    '''
    mock_validated_params = MagicMock()
    mock_validated_params.model_dump.return_value = {}
    mock_validate.return_value = mock_validated_params
    mock_build_expr.return_value = True
    mock_update.return_value = False

    payload = {"name": "New Name", "params": {}}
    response = client.post('/api/v1/alerts/rule/999/update', json=payload)

    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['status'] == 'error'
    assert 'not found' in data['message']

@patch('app.modules.alerts.routes.build_sqlalchemy_expression')
@patch('app.modules.alerts.routes.update_alert_rule_in_db')
@patch('app.modules.alerts.routes.RuleTreeAdapter.validate_python')
def test_update_alert_rule_integrity_error(mock_validate, mock_update, mock_build_expr, client):
    '''
    Test updating a rule name to one that already exists (raises ValueError from DB helper)
    '''
    mock_validated_params = MagicMock()
    mock_validated_params.model_dump.return_value = {}
    mock_validate.return_value = mock_validated_params
    mock_build_expr.return_value = True
    mock_update.side_effect = ValueError("Rule name 'New Name' must be unique.")

    payload = {"name": "New Name", "params": {}}
    response = client.post('/api/v1/alerts/rule/5/update', json=payload)

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "must be unique" in data['error']

@patch('app.modules.alerts.routes.write_audit_log')
@patch('app.modules.alerts.routes.update_alert_rule_in_db')
def test_update_alert_rule_internal_error(mock_update, mock_audit, client):
    '''
    Test internal server error when updating an alert rule
    '''
    mock_update.side_effect = Exception("Database connection failed")

    payload = {"name": "New Name"}
    response = client.post('/api/v1/alerts/rule/5/update', json=payload)

    assert response.status_code == 500
    data = json.loads(response.data)
    assert data['error'] == 'Internal server error'

    mock_audit.assert_called_once()
