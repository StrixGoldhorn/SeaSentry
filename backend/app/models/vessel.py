from sqlalchemy import Column, Integer, String, Text, Float, SmallInteger, ForeignKey, BigInteger, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from geoalchemy2 import Geometry
from sqlalchemy.orm import relationship
from app.core.database import DBConn

Base = DBConn.Base

class VesselData(Base):
    __tablename__ = 'vessel_data'
    
    vessel_data_id = Column(Integer, primary_key=True)
    vessel_data_mmsi = Column(String(9))
    vessel_data_imo = Column(String(7))
    vessel_data_ship_name = Column(Text)
    vessel_data_ship_type = Column(Text)
    vessel_data_flag = Column(Text)
    vessel_data_length_meters = Column(Integer)
    vessel_data_beam_meters = Column(Integer)
    vessel_data_user_tags = Column(ARRAY(Text))

    locations = relationship("VesselLocation", back_populates="vessel_data")

    def __repr__(self):
        return f"<Vessel(id: {self.vessel_data_id}, MMSI: {self.vessel_data_mmsi}, IMO: {self.vessel_data_imo}, Name: {self.vessel_data_ship_name})>"

class VesselLocation(Base):
    __tablename__ = 'vessel_location'

    vessel_location_id = Column(BigInteger, primary_key=True)
    vessel_location_coords = Column(Geometry('POINT', srid=4326), nullable=False)
    vessel_location_timestamp = Column(DateTime(timezone=True))
    vessel_location_speed_knots = Column(Float)
    vessel_location_course_deg = Column(Float)
    vessel_location_heading_deg = Column(Float)
    vessel_location_rate_of_turn_deg_per_sec = Column(Float)
    vessel_location_nav_status = Column(SmallInteger)
    vessel_location_vessel_data_id = Column(Integer, ForeignKey('vessel_data.vessel_data_id'))
    vessel_location_raw_data_id = Column(BigInteger, ForeignKey('raw_data.raw_data_id'))

    vessel_data = relationship("VesselData", back_populates="locations")
    raw_data = relationship("RawData", back_populates="vessel_locations")

    def __repr__(self):
        return f"<VesselLocation(id: {self.vessel_location_id}, vessel_data_id: {self.vessel_location_vessel_data_id}, Timestamp: {self.vessel_location_timestamp})>"

class VesselOfInterest(Base):
    __tablename__ = 'vessel_of_interest'

    vessel_of_interest_id = Column(Integer, primary_key=True)
    vessel_of_interest_desc_name = Column(Text, nullable=False)
    vessel_of_interest_description = Column(Text)
    vessel_of_interest_mmsi = Column(String(9))
    vessel_of_interest_imo = Column(String(7))

    def __repr__(self):
        return f"<VesselOfInterest(id: {self.vessel_of_interest_id}, name: {self.vessel_of_interest_desc_name})>"
