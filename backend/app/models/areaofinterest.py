# backend/app/models/areaofinterest.py

from sqlalchemy import Column, Integer, Text, DateTime
from geoalchemy2 import Geometry
from app.core.database import DBConn

Base = DBConn.Base

class AreaOfInterest(Base):
    __tablename__ = 'area_of_interest'
    area_of_interest_id = Column(Integer, primary_key=True)
    area_of_interest_timestamp = Column(DateTime(timezone=True))
    area_of_interest_name = Column(Text, unique=True, nullable=False)
    area_of_interest_description = Column(Text, nullable=True)
    area_of_interest_polygon = Column(Geometry('POLYGON', srid=4326), nullable=False)

    def __repr__(self):
        return f"<AOI(id: {self.area_of_interest_id}, name: {self.area_of_interest_name})>"
