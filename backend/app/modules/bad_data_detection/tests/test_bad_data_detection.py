import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

from app.core.config import Settings
from app.modules.bad_data_detection.engine import bad_data_check
from app.modules.bad_data_detection.detector import detector

def create_mock_engine_session(query_all_return=None, query_all_side_effect=None):
    '''Helper to create a mock session for engine.py (bad_data_check)'''
    mock_session = MagicMock()
    mock_query = MagicMock()
    mock_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query

    if query_all_side_effect:
        mock_query.all.side_effect = query_all_side_effect
    else:
        mock_query.all.return_value = query_all_return if query_all_return is not None else []

    return mock_session

def create_mock_detector_session(get_return, scalar_returns, first_returns):
    '''
    Helper to create a mock session for detector.py.
    Uses side_effect to handle sequential calls to .get(), .scalar(), and .first()
    '''
    mock_session = MagicMock()
    mock_query = MagicMock()
    mock_session.query.return_value = mock_query

    mock_query.join.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value = mock_query

    mock_query.get.side_effect = get_return if isinstance(get_return, list) else [get_return]
    mock_query.scalar.side_effect = scalar_returns
    mock_query.first.side_effect = first_returns

    return mock_session

def create_mock_location(loc_id, timestamp, speed, raw_data_id, vessel_data_id):
    '''Helper to create a mock VesselLocation object'''
    loc = MagicMock()
    loc.vessel_location_id = loc_id
    loc.vessel_location_timestamp = timestamp
    loc.vessel_location_speed_knots = speed
    loc.vessel_location_coords = "POINT(0 0)"
    loc.vessel_location_raw_data_id = raw_data_id
    loc.vessel_location_vessel_data_id = vessel_data_id
    return loc

@pytest.fixture
def mock_settings(monkeypatch):
    '''Fixture to override Settings for detector testing'''
    monkeypatch.setattr("app.modules.bad_data_detection.detector.Settings.TIME_TOLERANCE_SECONDS", Settings.TIME_TOLERANCE_SECONDS)
    monkeypatch.setattr("app.modules.bad_data_detection.detector.Settings.SPATIAL_TOLERANCE_METERS", Settings.SPATIAL_TOLERANCE_METERS)
    monkeypatch.setattr("app.modules.bad_data_detection.detector.Settings.SPEED_CHECK_WINDOW_MINUTES", Settings.SPEED_CHECK_WINDOW_MINUTES)
    monkeypatch.setattr("app.modules.bad_data_detection.detector.Settings.SPEED_BUFFER_KNOTS", Settings.SPEED_BUFFER_KNOTS)

# ==========================================
# Tests for engine.py bad_data_check
# ==========================================

@patch('app.modules.bad_data_detection.engine.write_audit_log')
@patch('app.modules.bad_data_detection.engine.detector')
@patch('app.modules.bad_data_detection.engine.DBConn.get_session')
def test_bad_data_check_success_multiple_records(mock_get_session, mock_detector, mock_audit_log):
    '''
    Test that bad_data_check correctly iterates over multiple records 
    and calls the detector for each, then closes the session.
    '''
    mock_session = create_mock_engine_session(query_all_return=[(1, 101), (2, 102)])
    mock_get_session.return_value = mock_session

    bad_data_check(n=5)

    assert mock_detector.call_count == 2
    mock_detector.assert_any_call(mock_session, 1, 101)
    mock_detector.assert_any_call(mock_session, 2, 102)
    mock_session.close.assert_called_once()
    mock_audit_log.assert_not_called()

@patch('app.modules.bad_data_detection.engine.write_audit_log')
@patch('app.modules.bad_data_detection.engine.detector')
@patch('app.modules.bad_data_detection.engine.DBConn.get_session')
def test_bad_data_check_success_no_records(mock_get_session, mock_detector, mock_audit_log):
    '''
    Test that bad_data_check handles an empty result set gracefully.
    '''
    mock_session = create_mock_engine_session(query_all_return=[])
    mock_get_session.return_value = mock_session

    bad_data_check(n=5)

    mock_detector.assert_not_called()
    mock_session.close.assert_called_once()
    mock_audit_log.assert_not_called()

@patch('app.modules.bad_data_detection.engine.write_audit_log')
@patch('app.modules.bad_data_detection.engine.detector')
@patch('app.modules.bad_data_detection.engine.DBConn.get_session')
def test_bad_data_check_handles_query_exception(mock_get_session, mock_detector, mock_audit_log):
    '''
    Test that if the database query fails, the exception is caught, 
    an audit log is written, and the session is still closed.
    '''
    mock_session = create_mock_engine_session(query_all_side_effect=Exception("DB Connection Lost"))
    mock_get_session.return_value = mock_session

    bad_data_check(n=5)

    mock_detector.assert_not_called()
    mock_audit_log.assert_called_once()
    args, _ = mock_audit_log.call_args
    assert "DB Connection Lost" in str(args[2]["info"])
    mock_session.close.assert_called_once()

@patch('app.modules.bad_data_detection.engine.write_audit_log')
@patch('app.modules.bad_data_detection.engine.detector')
@patch('app.modules.bad_data_detection.engine.DBConn.get_session')
def test_bad_data_check_handles_detector_exception(mock_get_session, mock_detector, mock_audit_log):
    '''
    Test that if the detector function fails, the exception is caught and logged.
    '''
    mock_session = create_mock_engine_session(query_all_return=[(1, 101)])
    mock_get_session.return_value = mock_session
    mock_detector.side_effect = Exception("PostGIS Error")

    bad_data_check(n=5)

    mock_detector.assert_called_once()
    mock_audit_log.assert_called_once()
    args, _ = mock_audit_log.call_args
    assert "PostGIS Error" in str(args[2]["info"])
    mock_session.close.assert_called_once()


# ==========================================
# Tests for detector.py discrepancy between sources
# ==========================================

@patch('app.modules.bad_data_detection.detector.check_and_record_alert')
def test_detector_location_not_found(mock_check_alert, mock_settings):
    '''
    Test that detector returns early if the location ID does not exist in DB.
    '''
    mock_session = create_mock_detector_session(
        get_return=[None],
        scalar_returns=[],
        first_returns=[]
    )

    detector(mock_session, vessel_data_id=1, vessel_location_id=999)

    mock_check_alert.assert_not_called()

@patch('app.modules.bad_data_detection.detector.check_and_record_alert')
def test_detector_spatial_mismatch(mock_check_alert, mock_settings):
    '''
    Test that an alert is triggered when different sources report locations > SPATIAL_TOLERANCE_METERS apart.
    (Note: speed is set to None to skip the teleport check and keep the mock sequence simple)
    '''
    t0 = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    current_loc = create_mock_location(1, t0, None, 100, 1)
    conflicting_loc = create_mock_location(2, t0 + timedelta(seconds=10), None, 200, 1)

    mock_session = create_mock_detector_session(
        get_return=[current_loc],
        scalar_returns=[1, 2],
        first_returns=[conflicting_loc]
    )

    detector(mock_session, vessel_data_id=1, vessel_location_id=1)

    mock_check_alert.assert_called_once()
    args, _ = mock_check_alert.call_args
    assert args[0] == mock_session
    assert args[1] == 2
    assert "spatial mismatch" in args[2]["reason"].lower()
    assert args[2]["source 1"] == 1
    assert args[2]["source 2"] == 2

# ==========================================
# Tests for detector.py teleport/speeding
# ==========================================

@patch('app.modules.bad_data_detection.detector.check_and_record_alert')
def test_detector_teleport_anomaly(mock_check_alert, mock_settings):
    '''
    Test that an alert is triggered when implied speed exceeds reported speed + buffer.
    '''
    t0 = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    current_loc = create_mock_location(1, t0, 10.0, 100, 1)
    prev_loc = create_mock_location(2, t0 - timedelta(minutes=1), 10.0, 100, 1)

    mock_session = create_mock_detector_session(
        get_return=[current_loc],
        scalar_returns=[1, 2000.0],
        first_returns=[None, prev_loc]
    )

    detector(mock_session, vessel_data_id=1, vessel_location_id=1)

    mock_check_alert.assert_called_once()
    args, _ = mock_check_alert.call_args
    assert "distance covered more than given speed" in args[2]["reason"].lower()
    assert args[2]["current speed"] == 10.0
    assert args[2]["prev speed"] == 10.0

@patch('app.modules.bad_data_detection.detector.check_and_record_alert')
def test_detector_teleport_within_buffer(mock_check_alert, mock_settings):
    '''
    Test that no alert is triggered when implied speed is within reported speed + buffer.
    '''
    t0 = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    current_loc = create_mock_location(1, t0, 10.0, 100, 1)
    prev_loc = create_mock_location(2, t0 - timedelta(minutes=1), 10.0, 100, 1)

    mock_session = create_mock_detector_session(
        get_return=[current_loc],
        scalar_returns=[1, 100.0],
        first_returns=[None, prev_loc]
    )

    detector(mock_session, vessel_data_id=1, vessel_location_id=1)

    mock_check_alert.assert_not_called()

@patch('app.modules.bad_data_detection.detector.check_and_record_alert')
def test_detector_missing_speed_data(mock_check_alert, mock_settings):
    '''
    Test that no alert is triggered and function returns early if speed data is missing.
    '''
    t0 = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    current_loc = create_mock_location(1, t0, None, 100, 1)
    prev_loc = create_mock_location(2, t0 - timedelta(minutes=1), 10.0, 100, 1)
    
    mock_session = create_mock_detector_session(
        get_return=[current_loc],
        scalar_returns=[1],
        first_returns=[None, prev_loc]
    )

    detector(mock_session, vessel_data_id=1, vessel_location_id=1)

    mock_check_alert.assert_not_called()
    assert mock_session.query.return_value.scalar.call_count == 1 

@patch('app.modules.bad_data_detection.detector.check_and_record_alert')
def test_detector_no_previous_location(mock_check_alert, mock_settings):
    '''
    Test that no teleport alert is triggered if there is no previous location in the time window.
    '''
    t0 = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    current_loc = create_mock_location(1, t0, 10.0, 100, 1)

    mock_session = create_mock_detector_session(
        get_return=[current_loc],
        scalar_returns=[1],
        first_returns=[None, None]
    )
    
    detector(mock_session, vessel_data_id=1, vessel_location_id=1)
    
    mock_check_alert.assert_not_called()

@patch('app.modules.bad_data_detection.detector.check_and_record_alert')
def test_detector_multiple_alerts_spatial_and_teleport(mock_check_alert, mock_settings):
    '''
    Test that both a spatial mismatch alert and a teleport anomaly alert are triggered
    when both conditions are violated for the same vessel location.
    '''
    t0 = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    current_loc = create_mock_location(1, t0, 10.0, 100, 1)
    conflicting_loc = create_mock_location(2, t0 + timedelta(seconds=10), 10.0, 200, 1)
    prev_loc = create_mock_location(3, t0 - timedelta(minutes=1), 10.0, 100, 1)

    mock_session = create_mock_detector_session(
        get_return=[current_loc],
        scalar_returns=[1, 2, 5000.0],
        first_returns=[conflicting_loc, prev_loc]
    )

    detector(mock_session, vessel_data_id=1, vessel_location_id=1)

    assert mock_check_alert.call_count == 2

    args1, _ = mock_check_alert.call_args_list[0]
    assert args1[0] == mock_session
    assert args1[1] == 2
    assert "spatial mismatch" in args1[2]["reason"].lower()
    assert args1[2]["source 1"] == 1
    assert args1[2]["source 2"] == 2

    args2, _ = mock_check_alert.call_args_list[1]
    assert args2[0] == mock_session
    assert args2[1] == 2
    assert "distance covered more than given speed" in args2[2]["reason"].lower()

@patch('app.modules.bad_data_detection.detector.check_and_record_alert')
def test_detector_teleport_missing_prev_speed(mock_check_alert, mock_settings):
    '''
    Test that no alert is triggered if prev_speed is None, even if current_speed is valid and implied speed is high.
    The logic requires both current and previous speeds to be present to calculate a valid max reported speed.
    '''
    t0 = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    current_loc = create_mock_location(1, t0, 10.0, 100, 1)
    prev_loc = create_mock_location(2, t0 - timedelta(minutes=1), None, 100, 1)

    mock_session = create_mock_detector_session(
        get_return=[current_loc],
        scalar_returns=[1, 5000.0],
        first_returns=[None, prev_loc]
    )

    detector(mock_session, vessel_data_id=1, vessel_location_id=1)

    mock_check_alert.assert_not_called()

@patch('app.modules.bad_data_detection.detector.check_and_record_alert')
def test_detector_teleport_zero_time_diff(mock_check_alert, mock_settings):
    '''
    Test that no alert is triggered and distance query is skipped if the time difference 
    between current and previous location is zero.
    '''
    t0 = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    current_loc = create_mock_location(1, t0, 10.0, 100, 1)
    prev_loc = create_mock_location(2, t0, 10.0, 100, 1)

    mock_session = create_mock_detector_session(
        get_return=[current_loc],
        scalar_returns=[1],
        first_returns=[None, prev_loc]
    )

    detector(mock_session, vessel_data_id=1, vessel_location_id=1)

    mock_check_alert.assert_not_called()

@patch('app.modules.bad_data_detection.detector.check_and_record_alert')
def test_detector_teleport_zero_distance(mock_check_alert, mock_settings):
    '''
    Test that no alert is triggered if the calculated distance between current and previous location is zero.
    '''
    t0 = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    current_loc = create_mock_location(1, t0, 10.0, 100, 1)
    prev_loc = create_mock_location(2, t0 - timedelta(minutes=1), 10.0, 100, 1)

    mock_session = create_mock_detector_session(
        get_return=[current_loc],
        scalar_returns=[1, 0.0],
        first_returns=[None, prev_loc]
    )

    detector(mock_session, vessel_data_id=1, vessel_location_id=1)

    mock_check_alert.assert_not_called()

@patch('app.modules.bad_data_detection.detector.check_and_record_alert')
def test_detector_teleport_null_distance(mock_check_alert, mock_settings):
    '''
    Test that no alert is triggered if the distance query returns None (e.g., PostGIS null geometry).
    '''
    t0 = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    current_loc = create_mock_location(1, t0, 10.0, 100, 1)
    prev_loc = create_mock_location(2, t0 - timedelta(minutes=1), 10.0, 100, 1)

    mock_session = create_mock_detector_session(
        get_return=[current_loc],
        scalar_returns=[1, None],
        first_returns=[None, prev_loc]
    )

    detector(mock_session, vessel_data_id=1, vessel_location_id=1)

    mock_check_alert.assert_not_called()

@patch('app.modules.bad_data_detection.engine.write_audit_log')
@patch('app.modules.bad_data_detection.engine.detector')
@patch('app.modules.bad_data_detection.engine.DBConn.get_session')
def test_bad_data_check_stops_processing_on_detector_error(mock_get_session, mock_detector, mock_audit_log):
    '''
    Test that if detector raises an exception on the first record,
    the loop aborts and subsequent records are not processed.
    '''
    mock_session = create_mock_engine_session(query_all_return=[(1, 101), (2, 102), (3, 103)])
    mock_get_session.return_value = mock_session

    mock_detector.side_effect = [Exception("Fatal DB Error"), None, None]

    bad_data_check(n=5)

    assert mock_detector.call_count == 1
    mock_detector.assert_called_once_with(mock_session, 1, 101)
    mock_audit_log.assert_called_once()
