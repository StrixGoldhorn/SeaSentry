# backend/app/modules/scrapers/plugins/AISFriends_scraper.py
'''
Scrape AISFriends
'''

from app.modules.scrapers.registry import ScraperRegistry
from app.modules.scrapers import AbstractScraper
from app.utils.audit_log_helpers import write_audit_log

from datetime import datetime, timezone
import requests

@ScraperRegistry.register
class AISFriendsScraper(AbstractScraper):
    '''
    Scraper for the site www.aisfriends.com
    '''
    name = "AISFriends_Scraper"
    default_interval_seconds = 1 * 60 # 1 min

    SHIP_TYPE_MAP = {
        "Fishing": [30],
        "Tug": [31, 32, 50, 52, 53, 54],
        "Military": [35],
        "SAR": [51],
        "Law Enforcement": [55],
        "Medical Transport": [58],
        "Sailing": [36],
        "Pleasure Craft": [37],
        "High Speed Craft": list(range(40, 50)),
        "Passenger": list(range(60, 70)),
        "Cargo": list(range(70, 80)),
        "Tanker": list(range(80, 90))
    }

    def get_ship_type(ship_type_id):
        for ship_type, ids in AISFriendsScraper.SHIP_TYPE_MAP.items():
            if ship_type_id in ids:
                return ship_type
        return None

    base_url = "https://www.aisfriends.com/vessels/bounding-box"

    def fetch_data(self, coords: dict):
        '''
        Fetches data from the site, querying for locations of vessels within the specified coords.

        Args:
            coords (Dict[str, float]): A dict containing the queried coords.
        '''
        req_url = f"{self.base_url}?lon_min={coords['long_min']}&lat_min={coords['lat_min']}&lon_max={coords['long_max']}&lat_max={coords['lat_max']}&zoom=15"
        headers = {
            "Referer": "https://www.aisfriends.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/119.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36"
        }
        r = requests.get(req_url, headers = headers, timeout = 30)
        try:
            r.raise_for_status()
        except requests.RequestException as e:
            write_audit_log("Error when scraping bounding box", __name__, {"scraper": self.name, "bbox": coords, "timestamp": str(datetime.now()), "error": str(e)})
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
                "ship_name": vessel["name_ais"],
                "ship_type": AISFriendsScraper.get_ship_type(vessel["ship_type_id"]),
                "flag": vessel["flag"],
                "length_meters": vessel["length"],
                "beam_meters": vessel["beam"],

                "lat": vessel["latitude"],
                "lon": vessel["longitude"],
                "timestamp": datetime.fromtimestamp(vessel["timestamp_of_position"], tz=timezone.utc),
                "speed_knots": vessel["speed_over_ground"],
                "course_deg": vessel["course_over_ground"] % 360,
                "heading_deg": vessel["true_heading"] % 360,
                # "rate_of_turn_deg_per_sec": item.get("rate_of_turn_deg_per_sec"),
                "nav_status": vessel["navigational_status_id"],

                "rawout": str(vessel)
            })

        return output
