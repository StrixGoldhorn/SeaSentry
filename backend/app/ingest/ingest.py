# backend/app/ingest/ingest.py
'''
Input -> Validation -> Normalization -> Insert to DB
'''

from app.core.schemas import IngestVesselData, IngestVesselLocation, ScrapedVesselRecord
from app.ingest.validation import IngestValidation
from app.ingest.normalisation import IngestNormalisation
from app.models.vessel import VesselData, VesselLocation
from app.models.source import DataSource, RawData
from app.core.database import DBConn
from app.utils.audit_log_helpers import write_audit_log, write_data_ingestion_audit_log
from app.core.exceptions import DataValidationError

from datetime import datetime
from typing import Tuple, Any, Optional

import logging

logger = logging.getLogger(__name__)

class ScraperToIngest():
    '''
    Class for scrapers to use to hand over data for ingestion.
    '''

    @classmethod
    def processVesselRecord(cls, scraped:ScrapedVesselRecord) -> Optional[Tuple[int, int, int, int]]:
        '''
        Class to do processing of ScrapedVesselRecord

        Args:
            scraped: ScrapedVesselRecord to be processed

        Returns:
            Tuple containing (vessel_data_id, data_source_id, raw_data_id, vessel_location_id)
            Returns None if not inserted.
        '''
        vdata, vloc = cls.splitData(scraped)
        raw = scraped.raw
        source = scraped.source

        # validation
        try:
            vdata = IngestValidation.ValidateVesselData(vdata)
            vloc = IngestValidation.ValidateVesselLocation(vloc)
        except DataValidationError as e:
            # Skip this log if either fails validation
            # Add to log
            write_audit_log("DataValidationError", __name__, {"error": str(e), "raw": scraped.raw, "source": scraped.source}, "ERROR")
            return None

        # normalisation
        vdata = IngestNormalisation.NormaliseVesselData(vdata)
        vloc = IngestNormalisation.NormaliseVesselLocation(vloc)

        # insert
        # Insert vessel data first -> get vessel_data_id
        # Insert data source -> get data_source_id
        # Insert raw data -> get raw_data_id
        # Insert vessel location
        vessel_data_id = IngestToDB.InsertVesselData(vdata)
        if vessel_data_id is None:
            return None
        data_source_id = IngestToDB.InsertDataSource(source)
        if vessel_data_id is None:
            return None
        raw_data_id = IngestToDB.InsertRawData(raw, data_source_id)
        if vessel_data_id is not None:
            vessel_location_id = IngestToDB.InsertVesselLocation(vloc, vessel_data_id, raw_data_id)
            return (vessel_data_id, data_source_id, raw_data_id, vessel_location_id)
        return None

    @classmethod
    def splitData(cls, scraped:ScrapedVesselRecord) -> Tuple[IngestVesselData, IngestVesselLocation]:
        '''
        Splits ScrapedVesselRecord into IngestVesselData and IngestVesselLocation
        
        Args:
            scraped: ScrapedVesselRecord to be split
        
        Returns:
            Tuple containing IngestVesselData and IngestVesselLocation
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
    def InsertVesselData(cls, vdata: VesselData) -> Optional[int]:
        '''
        Inserts vessel data into DB.
        Returns the vessel_data_id.
        
        Args:
            vdata: VesselData to be inserted into DB
        
        Returns:
            vessel_data_id of the new row
        '''

        try:
            vessel_data_id = cls.upsert_vessel_data(vdata)
            # logger.debug("Vessel with vessel_data_id %d inserted/updated!", vessel_data_id)
            return vessel_data_id

        except Exception as e:
            logger.warning("Error while attempting to insert vessel data, %s, with error %s", str(vdata), str(e))
            write_audit_log("Unknown Exception while attempting to insert vessel data", __name__, {"error": str(e), "vdata": str(vdata)}, "ERROR")
            return None

    @classmethod
    def upsert_vessel_data(cls, vdata: VesselData) -> int:
        '''
        Checks if MMSI or IMO exists. Updates if found, inserts if not.
        
        Args:
            vdata: VesselData to be upserted
        
        Returns:
            vessel_data_id of the new row
        '''

        session = DBConn.get_session()

        mmsi = vdata.vessel_data_mmsi
        imo = vdata.vessel_data_imo

        # This should NEVER happen due to data validation beforehand
        if not mmsi and not imo:
            logger.warning("Skipping vessel upsert: missing both MMSI and IMO")
            raise Exception("Skipping vessel upsert: missing both MMSI and IMO")

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

            # For now, we will take it as IMO is more important
            if mmsi and imo and existing.vessel_data_imo != imo and existing.vessel_data_mmsi != mmsi:
                logger.warning("MMSI and IMO conflict. Using IMO match.")
                write_audit_log("MMSI and IMO conflict", __name__, {"error": "MMSI and IMO conflict. Using IMO match.",
                                                                    "Scraped MMSI": str(mmsi), "Scraped IMO": str(imo),
                                                                    "DB MMSI": str(existing.vessel_data_mmsi), "DB IMO": str(existing.vessel_data_imo)
                                                                    }, "WARNING")

            session.commit() # Commit and get PK
            DBConn.close_session()
            return existing.vessel_data_id

        else:
            session.add(vdata)
            session.commit() # Commit and get PK
            DBConn.close_session()
            return vdata.vessel_data_id

    @classmethod
    def InsertDataSource(cls, data_source_name: str) -> Optional[int]:
        '''
        Inserts data source into DB.
        Returns data_source_id.
        
        Args:
            data_source_name: name of new data source to be inserted into DB
        
        Returns:
            data_source_id of the new row
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
            write_audit_log("Unknown Exception while attempting to insert data source",
                            __name__, {"error": str(e), "data source name": str(data_source_name)}, "ERROR")
            return None

        finally:
            DBConn.close_session()

    @classmethod
    def InsertRawData(cls, raw_data: Any, data_source_id: int) -> Optional[int]:
        '''
        Inserts raw data into DB.
        Returns raw_data_id.
        
        Args:
            raw_data: raw data to be inserted into DB
            data_source_id: data_source_id of the data source

        Returns:
            raw_data_id of the new row
        '''

        session = DBConn.get_session()

        try:
            temp = {"data": str(raw_data)}
            rawdata = RawData(
                raw_data_payload = temp,
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
                # Raw data already exists
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
    def InsertVesselLocation(cls, vloc: VesselLocation, vessel_data_id: int, raw_data_id: int) -> Optional[int]:
        '''
        Inserts vessel location into DB.
        Returns vessel_location_id.
        
        Args:
            vloc: VesselLocation to be inserted into DB
            vessel_data_id: vessel_data_id of the vessel involved
            raw_data_id: raw_data_id of the raw data involved
        
        Returns:
            vessel_location_id of the new row
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
            logger.warning("Error while attempting to insert vessel location, %s, with error %s", str(vloc), str(e))
            write_audit_log("Unknown Exception while attempting to insert vessel location",
                            __name__, {"error": str(e), "vloc": str(vloc)}, "ERROR")

        finally:
            DBConn.close_session()
