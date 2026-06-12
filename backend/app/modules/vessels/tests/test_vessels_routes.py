import pytest
from unittest.mock import patch, MagicMock
from app.utils.vessel_helpers import get_all_vessels_in_bbox
from app.models.vessel import VesselData, VesselLocation

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
