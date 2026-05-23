# backend/app/models/source.py

from sqlalchemy import Column, Integer, Text, ForeignKey, Enum, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.core.database import DBConn

Base = DBConn.Base
data_source_input_types = Enum('web_scraper', 'web_api', 'receiver', 'others', name='data_source_input_types')

class DataSource(Base):
    __tablename__ = 'data_source'
    data_source_id = Column(Integer, primary_key=True)
    data_source_name = Column(Text, unique=True, nullable=False)
    data_source_type = Column(data_source_input_types, nullable=True)
    data_source_desc = Column(Text, nullable=True)

    raw_data_entries = relationship("RawData", back_populates="source", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DataSource(id: {self.data_source_id}, name: {self.data_source_name})>"


class RawData(Base):
    __tablename__ = 'raw_data'
    raw_data_id = Column(Integer, primary_key=True)
    raw_data_timestamp = Column('raw_data_timestamp', DateTime(timezone=True))
    raw_data_payload = Column('raw_data_payload', JSONB, nullable=False)
    raw_data_data_source_id = Column(Integer, ForeignKey('data_source.data_source_id'), nullable=False)

    source = relationship("DataSource", back_populates="raw_data_entries")
    vessel_locations = relationship("VesselLocation", back_populates="raw_data")
    ingestion_audit = relationship("DataIngestionAuditLog", back_populates="raw_data")

    def __repr__(self):
        return f"<RawData(id: {self.raw_data_id}, source_id: {self.raw_data_data_source_id})>"
