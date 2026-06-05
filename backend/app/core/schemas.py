from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class ScrapedVesselRecord:
    '''
    Standardized schema for all scraped vessel data.
    Combines vessel_data and vessel_location. Splitting them will occur in the data ingest phase.
    '''

    lat: float
    lon: float
    timestamp: datetime # Convert to Python's datetime before storing here!!!
    source: str
    raw: str

    mmsi: Optional[str] = None
    imo: Optional[str] = None
    ship_name: Optional[str] = None
    ship_type: Optional[str] = None
    flag: Optional[str] = None
    length_meters: Optional[int] = None
    beam_meters: Optional[int] = None

    speed_knots: Optional[float] = None
    course_deg: Optional[float] = None
    heading_deg: Optional[float] = None
    rate_of_turn_deg_per_sec: Optional[float] = None
    nav_status: Optional[int] = None

@dataclass
class IngestVesselData:
    '''
    Standardized schema for all vessel data.
    '''
    mmsi: Optional[str] = None
    imo: Optional[str] = None
    ship_name: Optional[str] = None
    ship_type: Optional[str] = None
    flag: Optional[str] = None
    length_meters: Optional[int] = None
    beam_meters: Optional[int] = None

    def __str__(self):
        return (f"<IngestVesselData "
                f"mmsi={self.mmsi}, "
                f"imo={self.imo}, "
                f"ship_name={self.ship_name}, "
                f"ship_type={self.ship_type}, "
                f"flag={self.flag}, "
                f"length_meters={self.length_meters}, "
                f"beam_meters={self.beam_meters}>")


@dataclass
class IngestVesselLocation:
    '''
    Standardized schema for all vessel location.
    '''
    lat: float
    lon: float
    timestamp: datetime # Convert to Python's datetime before storing here!!!
    source: str
    raw: str

    speed_knots: Optional[float] = None
    course_deg: Optional[float] = None
    heading_deg: Optional[float] = None
    rate_of_turn_deg_per_sec: Optional[float] = None
    nav_status: Optional[int] = None

    def __str__(self):
        return (f"<IngestVesselLocation "
                    f"lat={self.lat}, "
                    f"lon={self.lon}, "
                    f"timestamp={self.timestamp}, "
                    f"source={self.source}, "
                    f"speed_knots={self.speed_knots}, "
                    f"course_deg={self.course_deg}, "
                    f"heading_deg={self.heading_deg}, "
                    f"rate_of_turn_deg_per_sec={self.rate_of_turn_deg_per_sec}, "
                    f"nav_status={self.nav_status}, "
                    f"raw='{self.raw}'>")
