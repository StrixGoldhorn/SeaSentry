# backend/app/utils/audit_log_helpers.py

import logging
from datetime import datetime

from app.core.database import DBConn
from app.models.logging import AuditLog, DataIngestionAuditLog

logger = logging.getLogger(__name__)

def write_audit_log(event_type: str, triggered_by: str, event_desc: dict, severity: str = "CRITICAL", timestamp: datetime = datetime.now()):
    '''
    Writes a log into the audit_log table.
    Returns audit_log_id.

    Severity: ENUM('INFO', 'WARN', 'ERROR', 'CRITICAL')
    '''

    session = DBConn.get_session()

    try:
        log = AuditLog(
            audit_log_timestamp = timestamp,
            audit_log_event_type = event_type,
            audit_log_severity = severity,
            audit_log_triggered_by = triggered_by,
            audit_log_event_desc = event_desc
        )
        session.add(log)
        session.commit()
        logger.info("Added log id: %d", log.audit_log_id)
        return log.audit_log_id
    
    except Exception as e:
        session.rollback()
        logger.error("Failed to add log: %s", e, exc_info=True)
        raise

def write_data_ingestion_audit_log(raw_data_id: int, triggered_by: str, event_desc: dict, timestamp: datetime = datetime.now()):
    '''
    Writes a log into the data_ingestion_audit_log table.
    Returns data_ingestion_audit_log_id.
    '''

    session = DBConn.get_session()

    try:
        log = DataIngestionAuditLog(
            data_ingestion_audit_log_timestamp = timestamp,
            data_ingestion_audit_log_triggered_by = triggered_by,
            data_ingestion_audit_log_event_desc = event_desc,
            data_ingestion_audit_log_raw_data_id = raw_data_id
        )
        session.add(log)
        session.commit()
        logger.debug("Added data_ingest_audit_log id: %d", log.data_ingestion_audit_log_id)
        return log.data_ingestion_audit_log_id

    except Exception as e:
        session.rollback()
        logger.error("Failed to add data_ingest_audit_log: %s", e, exc_info=True)
        raise
