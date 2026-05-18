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
    timestamp: datetime # = field(default_factory=lambda: datetime.now(timezone.utc))
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