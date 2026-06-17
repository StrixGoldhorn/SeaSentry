# backend/app/ingest/ingest.py
# placeholder for input -> validation -> normalization -> insert to DB

from app.core.schemas import IngestVesselData, IngestVesselLocation, ScrapedVesselRecord
from app.ingest.validation import IngestValidation
from app.ingest.normalisation import IngestNormalisation
from app.models.vessel import VesselData, VesselLocation
from app.models.source import DataSource, RawData
from app.core.database import DBConn
from app.utils.audit_log_helpers import write_audit_log, write_data_ingestion_audit_log
from app.core.exceptions import DataValidationError

from app.modules.alerts.engine import process_alerts_for_vessel

from datetime import datetime
from typing import Tuple, Any

import threading
import logging

logger = logging.getLogger(__name__)

class ScraperToIngest():
    '''
    Class for scrapers to use to hand over data for ingestion.
    '''

    @classmethod
    def processVesselRecord(cls, scraped:ScrapedVesselRecord):
        vdata, vloc = cls.splitData(scraped)
        raw = scraped.raw
        source = scraped.source

        # validation
        vdata = IngestValidation.ValidateVesselData(vdata)
        vloc = IngestValidation.ValidateVesselLocation(vloc)
        try:
            vdata = IngestValidation.ValidateVesselData(vdata)
            vloc = IngestValidation.ValidateVesselLocation(vloc)
        except DataValidationError as e:
            # Skip this log if either fails validation
            # Add to log
            write_audit_log("DataValidationError", __name__, {"error": e, "raw": scraped.raw, "source": scraped.source}, "ERROR")
            #TODO: Alert user
            return e

        # normalisation
        vdata = IngestNormalisation.NormaliseVesselData(vdata)
        vloc = IngestNormalisation.NormaliseVesselLocation(vloc)

        # insert
        # Insert vessel data first -> get vessel_data_id
        # Insert data source -> get data_source_id
        # Insert raw data -> get raw_data_id
        # Insert vessel location
        vessel_data_id = IngestToDB.InsertVesselData(vdata)
        data_source_id = IngestToDB.InsertDataSource(source)
        raw_data_id = IngestToDB.InsertRawData(raw, data_source_id)
        if vessel_data_id is not None:
            vessel_location_id = IngestToDB.InsertVesselLocation(vloc, vessel_data_id, raw_data_id)

    @classmethod
    def splitData(cls, scraped:ScrapedVesselRecord) -> Tuple[IngestVesselData, IngestVesselLocation]:
        '''
        Splits ScrapedVesselRecord into IngestVesselData and IngestVesselLocation
        '''
        vdata = IngestVesselData(
            mmsi = scraped.mmsi,
            imo = scraped.imo,
            ship_name = scraped.ship_name,
            ship_type = scraped.ship_type,
            flag = scraped.flag,
            length_meters = scraped.length_meters,
            beam_meters = scraped.beam_meters
        )

        vloc = IngestVesselLocation(
            lat = scraped.lat,
            lon = scraped.lon,
            timestamp = scraped.timestamp,
            source = scraped.source,
            raw = scraped.raw,

            speed_knots = scraped.speed_knots,
            course_deg = scraped.course_deg,
            heading_deg = scraped.heading_deg,
            rate_of_turn_deg_per_sec = scraped.rate_of_turn_deg_per_sec,
            nav_status = scraped.nav_status
        )

        return (vdata, vloc)



class IngestToDB:
    '''
    Class to handle inserting ingested data to DB.
    '''

    @classmethod
    def InsertVesselData(cls, vdata: VesselData) -> int:
        '''
        Inserts vessel data into DB.
        Returns the vessel_data_id.
        '''

        try:
            vessel_data_id = cls.upsert_vessel_data(vdata)
            logger.debug("Vessel with vessel_data_id %d inserted/updated!", vessel_data_id)
            return vessel_data_id

        except Exception as e:
            logger.warning("Error while attempting to insert vessel data, %s, with error %s", str(vdata), str(e))
            # TODO: Add exception handling
            return None

    @classmethod
    def upsert_vessel_data(cls, vdata: VesselData) -> int:
        '''
        Checks if MMSI or IMO exists. Updates if found, inserts if not.
        Returns the vessel_data_id.
        '''

        session = DBConn.get_session()

        mmsi = vdata.vessel_data_mmsi
        imo = vdata.vessel_data_imo

        # This should NEVER happen due to data validation beforehand
        if not mmsi and not imo:
            logger.warning("Skipping vessel upsert: missing both MMSI and IMO")
            raise Exception("Something went wrong") # TODO: Be more specific

        # Prioritise IMO first since it is tagged to each ship.
        # But recall that not all ships have an IMO, so we also do MMSI just in case.
        query = session.query(VesselData)
        if imo and imo != "0000000":
            existing = query.filter(VesselData.vessel_data_imo == imo).first()
        else:
            existing = query.filter(VesselData.vessel_data_mmsi == mmsi).first()

        if existing is not None:
            if existing.vessel_data_mmsi is None:
                existing.vessel_data_mmsi = vdata.vessel_data_mmsi
            if existing.vessel_data_imo is None:
                existing.vessel_data_imo = vdata.vessel_data_imo
            if existing.vessel_data_ship_name is None:
                existing.vessel_data_ship_name = vdata.vessel_data_ship_name
            if existing.vessel_data_ship_type is None:
                existing.vessel_data_ship_type = vdata.vessel_data_ship_type
            if existing.vessel_data_flag is None:
                existing.vessel_data_flag = vdata.vessel_data_flag
            if existing.vessel_data_length_meters is None:
                existing.vessel_data_length_meters = vdata.vessel_data_length_meters
            if existing.vessel_data_beam_meters is None:
                existing.vessel_data_beam_meters = vdata.vessel_data_beam_meters

            # TODO: This can be a conflict we handle later.
            # For now, we will take it as IMO is more important
            if mmsi and imo and existing.vessel_data_imo != imo and existing.vessel_data_mmsi != mmsi:
                logger.warning("MMSI and IMO conflict. Using IMO match.")

            session.commit() # Commit and get PK
            DBConn.close_session()
            return existing.vessel_data_id

        else:
            session.add(vdata)
            session.commit() # Commit and get PK
            DBConn.close_session()
            return vdata.vessel_data_id

    @classmethod
    def InsertDataSource(cls, data_source_name: str) -> int:
        '''
        Inserts data source into DB.
        Returns data_source_id.
        '''

        session = DBConn.get_session()

        try:

            datasource = DataSource(
                data_source_name = data_source_name
            )

            existing = session.query(DataSource).filter(DataSource.data_source_name == data_source_name).first()

            if existing is None:
                session.add(datasource)
                session.commit() # Commit and get PK
                DBConn.close_session()
                return datasource.data_source_id

            else:
                # Data source already exists
                session.flush() # Flush and get PK
                return existing.data_source_id

        except Exception as e:
            logger.warning("Error while attempting to insert data source, %s, with error %s", data_source_name, str(e))
            # TODO: Add exception handling
            return None

        finally:
            DBConn.close_session()

    @classmethod
    def InsertRawData(cls, raw_data: Any, data_source_id: int) -> int:
        '''
        Inserts raw data into DB.
        Returns raw_data_id.
        '''

        session = DBConn.get_session()

        try:
            temp = {"data": str(raw_data)}
            rawdata = RawData(
                raw_data_payload = temp, # Placeholder. TODO: Actually convert to JSON-style before writing to DB
                raw_data_timestamp = datetime.now(),
                raw_data_data_source_id = data_source_id
            )

            existing = session.query(RawData).filter(RawData.raw_data_payload == temp).first()

            if existing is None:
                session.add(rawdata)
                session.commit() # Commit and get PK
                DBConn.close_session()
                write_data_ingestion_audit_log(rawdata.raw_data_id, __name__, {})
                return rawdata.raw_data_id

            else:
                # Raw data already exists)
                session.flush() # Flush and get PK
                write_data_ingestion_audit_log(existing.raw_data_id, __name__, {})
                return existing.raw_data_id

        except Exception as e:
            logger.warning("Error while attempting to insert raw data, %s, with error %s", str(raw_data), str(e))
            # TODO: Add exception handling
            return None

        finally:
            DBConn.close_session()


    @classmethod
    def InsertVesselLocation(cls, vloc: VesselLocation, vessel_data_id: int, raw_data_id: int) -> int:
        '''
        Inserts vessel location into DB.
        Returns vessel_location_id.
        '''

        session = DBConn.get_session()

        try:
            vloc.vessel_location_vessel_data_id = vessel_data_id
            vloc.vessel_location_raw_data_id = raw_data_id

            existing = session.query(VesselLocation)\
                .filter(VesselLocation.vessel_location_vessel_data_id == vloc.vessel_location_vessel_data_id)\
                .filter(VesselLocation.vessel_location_timestamp == vloc.vessel_location_timestamp)\
                .filter(VesselLocation.vessel_location_raw_data_id == vloc.vessel_location_raw_data_id)\
                .first()

            if existing is None:
                session.add(vloc)
                session.commit() # Commit and get PK
                return vloc.vessel_location_id

            else:
                # Raw data already exists
                session.flush() # Flush and get PK
                return existing.vessel_location_id

        except Exception as e:
            # TODO: Add exception handling
            logger.warning("Error while attempting to insert vessel location, %s, with error %s", str(vloc), str(e))
            pass

        finally:
            DBConn.close_session()
