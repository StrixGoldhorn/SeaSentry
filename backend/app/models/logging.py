# backend/app/models/logging.py

from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.core.database import DBConn

Base = DBConn.Base
log_severity = Enum('INFO', 'WARN', 'ERROR', 'CRITICAL')

class AuditLog(Base):
    __tablename__ = 'audit_log'
    audit_log_id = Column(Integer, primary_key=True)
    audit_log_timestamp = Column(DateTime(timezone=True))
    audit_log_event_type = Column(Text, nullable=True)
    audit_log_severity = Column(log_severity, nullable=True)
    audit_log_triggered_by = Column(Text, nullable=True)
    audit_log_event_desc = Column(JSONB, nullable=True)

    def __repr__(self):
        return f"<AuditLog(id: {self.audit_log_id})>"
    
class DataIngestionAuditLog(Base):
    __tablename__ = 'data_ingestion_audit_log'
    data_ingestion_audit_log_id = Column(Integer, primary_key=True)
    data_ingestion_audit_log_timestamp = Column(DateTime(timezone=True))
    data_ingestion_audit_log_triggered_by = Column(Text, nullable=True)
    data_ingestion_audit_log_event_desc = Column(JSONB, nullable=True)
    data_ingestion_audit_log_raw_data_id = Column(Integer, ForeignKey('raw_data.raw_data_id'), nullable=False)

    raw_data = relationship("RawData", back_populates="ingestion_audit")

    def __repr__(self):
        return f"<DataIngestionAuditLog(id: {self.data_ingestion_audit_log_id}, raw_id: {self.data_ingestion_audit_log_raw_data_id})>"
