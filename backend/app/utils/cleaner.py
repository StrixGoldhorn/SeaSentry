# backend/app/utils/cleaner.py

import logging
from sqlalchemy import text
from app.core.database import DBConn
logger = logging.getLogger(__name__)

def clear_data_ingestion_audit_log_thirty_days():
    '''
    Deletes rows from data_ingestion_audit_log that are more than 30 days old.
    '''

    session = DBConn.get_session()
    try:
        cmd = text("DELETE FROM data_ingestion_audit_log WHERE data_ingestion_audit_log_timestamp < NOW() - INTERVAL '30 days';")
        session.execute(cmd, {"status_param": "active"})
        session.commit()
        logger.info("Cleared data older than 30 days.")

    except Exception as e:
        logger.error("Error in clear_data_ingestion_audit_log_thirty_days: %s", e, exc_info=True)
        return []

    finally:
        if session:
            DBConn.close_session()
