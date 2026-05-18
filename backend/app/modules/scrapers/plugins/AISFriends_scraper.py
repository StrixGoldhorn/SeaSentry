# backend/app/modules/scrapers/plugins/AISFriends_scraper.py

from ..registry import ScraperRegistry
from ..base import AbstractScraper
import requests

@ScraperRegistry.register
class AISFriendsScraper(AbstractScraper):
    '''
    Scraper for the site www.aisfriends.com
    '''
    name = "AISFriends_Scraper"
    default_interval_seconds = 1 * 60 # 1 min

    base_url = "https://www.aisfriends.com/vessels/bounding-box"

    def fetch_data(self, coords: dict):
        '''
        Fetches data from the site, querying for locations of vessels within the specified coords.

        Args:
            coords (Dict[str, float]): A dict containing the queried coords.
        '''
        req_url = f"{self.base_url}?lon_min={coords['long_min']}&lat_min={coords['lat_min']}&lon_max={coords['long_max']}&lat_max={coords['lat_max']}&zoom=10"
        r = requests.get(req_url, timeout=30)
        r.raise_for_status()
        return r.json()

    def parse_data(self, raw):
        '''
        Parse data to fit fields in ScrapedVesselRecord
        '''
        data = raw
        output = []

        for vessel in data:

            # keys = ['id', 'vessel_id', 'class', 'imo', 'mmsi', 'name', 'name_ais',
            # 'ship_type_id', 'detailed_type_id', 'timestamp_of_position', 'length',
            # 'beam', 'to_bow', 'to_stern', 'to_port', 'to_starboard', 'true_heading',
            # 'course_over_ground', 'speed_over_ground', 'draught', 'navigational_status_id',
            # 'flag', 'latitude', 'longitude', 'lat_grid', 'lon_grid']
            output.append({
                "mmsi": vessel["mmsi"],
                "imo": vessel["imo"],
                "ship_name": vessel["name"],
                # ship_type = item.get("ship_type"),
                "flag": vessel["flag"],
                "length_meters": vessel["length"],
                "beam_meters": vessel["beam"],

                "lat": vessel["latitude"],
                "lon": vessel["longitude"],
                "timestamp": vessel["timestamp_of_position"],
                "speed_knots": vessel["speed_over_ground"],
                "course_deg": vessel["course_over_ground"] % 360,
                "heading_deg": vessel["true_heading"] % 360,
                # "rate_of_turn_deg_per_sec": item.get("rate_of_turn_deg_per_sec"),
                "nav_status": vessel["navigational_status_id"],

                "rawout": str(vessel)
            })

        return output
