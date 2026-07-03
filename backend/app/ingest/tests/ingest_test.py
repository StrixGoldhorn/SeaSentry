import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from app.core.schemas import ScrapedVesselRecord
from app.core.exceptions import DataValidationError
from app.ingest.ingest import ScraperToIngest, IngestToDB

@pytest.mark.ingestchain
class TestScraperToIngest:
    """Tests for the ScraperToIngest pipeline orchestration."""

    def test_split_data(self):
        """Ensures ScrapedVesselRecord is correctly split into data and location schemas."""
        scraped = ScrapedVesselRecord(
            lat=1.0, lon=2.0, timestamp=datetime.now(), source="S", raw="R",
            mmsi="123456789", imo="1234567", ship_name="Test Ship", speed_knots=10.0
        )
        vdata, vloc = ScraperToIngest.splitData(scraped)

        assert vdata.mmsi == "123456789"
        assert vdata.ship_name == "Test Ship"
        assert vloc.lat == 1.0
        assert vloc.speed_knots == 10.0
        assert vloc.source == "S"

    @patch('app.ingest.ingest.write_audit_log')
    @patch('app.ingest.ingest.IngestToDB')
    @patch('app.ingest.ingest.IngestNormalisation')
    @patch('app.ingest.ingest.IngestValidation')
    def test_process_vessel_record_validation_fails(self, mock_val, mock_norm, mock_db, mock_audit):
        """If validation fails, the process should abort and return None."""
        mock_val.ValidateVesselData.side_effect = DataValidationError("Invalid MMSI")

        scraped = ScrapedVesselRecord(
            lat=1.0, lon=1.0, timestamp=datetime.now(), source="Test", raw="raw",
            mmsi="invalid"
        )

        result = ScraperToIngest.processVesselRecord(scraped)
        assert result is None
        mock_audit.assert_called_once()

    @patch('app.ingest.ingest.IngestToDB')
    @patch('app.ingest.ingest.IngestNormalisation')
    @patch('app.ingest.ingest.IngestValidation')
    def test_process_vessel_record_path(self, mock_val, mock_norm, mock_db):
        """All steps succeed and return the tuple of IDs."""
        mock_val.ValidateVesselData.side_effect = lambda x: x
        mock_val.ValidateVesselLocation.side_effect = lambda x: x
        mock_norm.NormaliseVesselData.side_effect = lambda x: x
        mock_norm.NormaliseVesselLocation.side_effect = lambda x: x

        mock_db.InsertVesselData.return_value = 1
        mock_db.InsertDataSource.return_value = 2
        mock_db.InsertRawData.return_value = 3
        mock_db.InsertVesselLocation.return_value = 4

        scraped = ScrapedVesselRecord(
            lat=1.0, lon=1.0, timestamp=datetime.now(), source="Test", raw="raw",
            mmsi="123456789", imo="1234567"
        )

        result = ScraperToIngest.processVesselRecord(scraped)
        assert result == (1, 2, 3, 4)

    @patch('app.ingest.ingest.IngestToDB')
    @patch('app.ingest.ingest.IngestNormalisation')
    @patch('app.ingest.ingest.IngestValidation')
    def test_process_vessel_record_data_source_fails(self, mock_val, mock_norm, mock_db):
        """If InsertDataSource fails, it should abort and not proceed to RawData/Location."""
        mock_val.ValidateVesselData.side_effect = lambda x: x
        mock_val.ValidateVesselLocation.side_effect = lambda x: x
        mock_norm.NormaliseVesselData.side_effect = lambda x: x
        mock_norm.NormaliseVesselLocation.side_effect = lambda x: x

        mock_db.InsertVesselData.return_value = 1
        mock_db.InsertDataSource.return_value = None # Simulate failure
        mock_db.InsertRawData.return_value = 3
        mock_db.InsertVesselLocation.return_value = 4

        scraped = ScrapedVesselRecord(
            lat=1.0, lon=1.0, timestamp=datetime.now(), source="Test", raw="raw",
            mmsi="123456789", imo="1234567"
        )

        result = ScraperToIngest.processVesselRecord(scraped)
        assert result is None
        mock_db.InsertRawData.assert_not_called()
        mock_db.InsertVesselLocation.assert_not_called()


@pytest.mark.ingestchain
class TestIngestToDB:
    """Tests for the IngestToDB database operations."""

    @patch('app.ingest.ingest.write_audit_log')
    @patch('app.ingest.ingest.DBConn')
    def test_insert_vessel_data_exception(self, mock_db_conn, mock_audit):
        """If upsert_vessel_data throws an exception, InsertVesselData should catch it and return None."""
        mock_session = MagicMock()
        mock_db_conn.get_session.return_value = mock_session
        mock_session.query.side_effect = Exception("DB Connection Error")

        vdata = MagicMock()
        result = IngestToDB.InsertVesselData(vdata)

        assert result is None
        mock_audit.assert_called()

    @patch('app.ingest.ingest.DBConn')
    def test_upsert_vessel_data_insert_new(self, mock_db_conn):
        """If no existing vessel is found, it should add a new one and return the new ID."""
        mock_session = MagicMock()
        mock_db_conn.get_session.return_value = mock_session
        mock_session.query.return_value.filter.return_value.first.return_value = None

        vdata = MagicMock()
        vdata.vessel_data_mmsi = "123456789"
        vdata.vessel_data_imo = "1234567"
        vdata.vessel_data_id = 99

        result = IngestToDB.upsert_vessel_data(vdata)
        assert result == 99
        mock_session.add.assert_called_once_with(vdata)
        mock_session.commit.assert_called_once()

    @patch('app.ingest.ingest.DBConn')
    def test_upsert_vessel_data_update_existing(self, mock_db_conn):
        """If an existing vessel is found, it should update None fields and return the existing ID."""
        mock_session = MagicMock()
        mock_db_conn.get_session.return_value = mock_session

        existing = MagicMock()
        existing.vessel_data_id = 50
        existing.vessel_data_mmsi = None
        existing.vessel_data_imo = "1234567"
        existing.vessel_data_ship_name = None

        mock_session.query.return_value.filter.return_value.first.return_value = existing

        vdata = MagicMock()
        vdata.vessel_data_mmsi = "123456789"
        vdata.vessel_data_imo = "1234567"
        vdata.vessel_data_ship_name = "New Name"

        result = IngestToDB.upsert_vessel_data(vdata)
        assert result == 50
        assert existing.vessel_data_mmsi == "123456789"
        assert existing.vessel_data_ship_name == "New Name"
        mock_session.add.assert_not_called()

    @patch('app.ingest.ingest.write_audit_log')
    @patch('app.ingest.ingest.DBConn')
    def test_upsert_vessel_data_missing_both_ids(self, mock_db_conn, mock_audit):
        """If both MMSI and IMO are missing, it should raise an Exception."""
        mock_session = MagicMock()
        mock_db_conn.get_session.return_value = mock_session

        vdata = MagicMock()
        vdata.vessel_data_mmsi = None
        vdata.vessel_data_imo = None

        with pytest.raises(Exception, match="missing both MMSI and IMO"):
            IngestToDB.upsert_vessel_data(vdata)

    @patch('app.ingest.ingest.DBConn')
    def test_insert_data_source_new(self, mock_db_conn):
        """If data source doesn't exist, insert it and return the new ID."""
        mock_session = MagicMock()
        mock_db_conn.get_session.return_value = mock_session
        mock_session.query.return_value.filter.return_value.first.return_value = None

        with patch('app.ingest.ingest.DataSource') as mock_ds_model:
            mock_instance = MagicMock()
            mock_instance.data_source_id = 10
            mock_ds_model.return_value = mock_instance

            result = IngestToDB.InsertDataSource("TestSource")

        assert result == 10
        mock_session.add.assert_called_once()

    @patch('app.ingest.ingest.DBConn')
    def test_insert_data_source_existing(self, mock_db_conn):
        """If data source exists, return the existing ID without inserting."""
        mock_session = MagicMock()
        mock_db_conn.get_session.return_value = mock_session

        existing = MagicMock()
        existing.data_source_id = 20
        mock_session.query.return_value.filter.return_value.first.return_value = existing

        result = IngestToDB.InsertDataSource("ExistingSource")
        assert result == 20
        mock_session.add.assert_not_called()

    @patch('app.ingest.ingest.write_data_ingestion_audit_log')
    @patch('app.ingest.ingest.DBConn')
    def test_insert_raw_data_new(self, mock_db_conn, mock_audit_log):
        """If raw data doesn't exist, insert it and log the ingestion."""
        mock_session = MagicMock()
        mock_db_conn.get_session.return_value = mock_session
        mock_session.query.return_value.filter.return_value.first.return_value = None

        with patch('app.ingest.ingest.RawData') as mock_rd_model:
            mock_instance = MagicMock()
            mock_instance.raw_data_id = 30
            mock_rd_model.return_value = mock_instance

            result = IngestToDB.InsertRawData({"some": "data"}, 10)

        assert result == 30
        mock_session.add.assert_called_once()
        mock_audit_log.assert_called_once_with(30, 'app.ingest.ingest', {})

    @patch('app.ingest.ingest.write_data_ingestion_audit_log')
    @patch('app.ingest.ingest.DBConn')
    def test_insert_raw_data_existing(self, mock_db_conn, mock_audit_log):
        """If raw data exists, return the existing ID and log the ingestion."""
        mock_session = MagicMock()
        mock_db_conn.get_session.return_value = mock_session

        existing = MagicMock()
        existing.raw_data_id = 40
        mock_session.query.return_value.filter.return_value.first.return_value = existing

        result = IngestToDB.InsertRawData({"some": "data"}, 10)
        assert result == 40
        mock_session.add.assert_not_called()
        mock_audit_log.assert_called_once_with(40, 'app.ingest.ingest', {})

    @patch('app.ingest.ingest.DBConn')
    def test_insert_vessel_location_new(self, mock_db_conn):
        """If location doesn't exist, insert it and return the new ID."""
        mock_session = MagicMock()
        mock_db_conn.get_session.return_value = mock_session
        mock_session.query.return_value.filter.return_value.filter.return_value.filter.return_value.first.return_value = None

        vloc = MagicMock()
        vloc.vessel_location_id = 50

        result = IngestToDB.InsertVesselLocation(vloc, 1, 2)
        assert result == 50
        assert vloc.vessel_location_vessel_data_id == 1
        assert vloc.vessel_location_raw_data_id == 2
        mock_session.add.assert_called_once_with(vloc)

    @patch('app.ingest.ingest.DBConn')
    def test_insert_vessel_location_existing(self, mock_db_conn):
        """If location exists, return the existing ID without inserting."""
        mock_session = MagicMock()
        mock_db_conn.get_session.return_value = mock_session

        existing = MagicMock()
        existing.vessel_location_id = 60
        mock_session.query.return_value.filter.return_value.filter.return_value.filter.return_value.first.return_value = existing

        vloc = MagicMock()
        result = IngestToDB.InsertVesselLocation(vloc, 1, 2)
        assert result == 60
        mock_session.add.assert_not_called()
