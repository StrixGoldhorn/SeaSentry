# backend/app/models/areaofinterest.py

from sqlalchemy import Column, Integer, Text, DateTime
from geoalchemy2 import Geometry
from app.core.database import DBConn

Base = DBConn.Base

class Geofence(Base):
    __tablename__ = 'geofence'
    geofence_id = Column(Integer, primary_key=True)
    geofence_timestamp = Column(DateTime(timezone=True))
    geofence_name = Column(Text, unique=True, nullable=False)
    geofence_description = Column(Text, nullable=True)
    geofence_polygon = Column(Geometry('POLYGON', srid=4326), nullable=False)

    def __repr__(self):
        return f"<Geofence(id: {self.geofence_id}, name: {self.geofence_name})>"
