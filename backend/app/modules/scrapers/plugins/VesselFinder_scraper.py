# backend/app/modules/scrapers/plugins/vesselfinder_scraper.py
'''
Scrape vesselfinder.com
'''

from app.modules.scrapers.registry import ScraperRegistry
from app.modules.scrapers import AbstractScraper
from app.utils.audit_log_helpers import write_audit_log

import time
import logging
import tempfile
import shutil
import concurrent.futures
import random
import math
from playwright.sync_api import sync_playwright
from datetime import datetime, timezone, timedelta
from playwright_stealth import Stealth

logger = logging.getLogger(__name__)

def apply_stealth(page): Stealth().apply_stealth_sync(page)

class Playwright_VesselFinder():
    '''
    Class to use Playwright browser to scrape
    '''
    def __init__(self):
        self.temp_profile = tempfile.mkdtemp(prefix="seasentry_vf_")
        self.pw = None
        self.context = None
        self.page = None
        self._is_running = False

    def start(self):
        '''
        Start browser, pass cloudflare
        '''
        if self._is_running:
            return

        self.pw = sync_playwright().start()
        self.context = self.pw.chromium.launch_persistent_context(
            user_data_dir=self.temp_profile,
            headless=True,
            channel="chrome",
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox", # Required for Docker
                "--disable-setuid-sandbox"
            ]
        )
        self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
        apply_stealth(self.page)

        self.page.goto("https://www.vesselfinder.com/", wait_until="networkidle")

        try:
            self.page.wait_for_selector("div#map-container", timeout=1500)
            time.sleep(10)
        except Exception as e:
            logger.error(f"WAF challenge failed: {e}")
            write_audit_log("Failed to get authentication", __name__,
                            {"headless_browser": __name__, "site": "vesselfinder.com", "timestamp": str(datetime.now()), "error": str(e)})

        self._is_running = True

    def fetch_mp2(self, coords: dict, zoom: int = 15) -> bytes:
        """
        Fetches data directly from the /api/pub/mp2 endpoint.
        """
        if not self._is_running:
            self.start()

        long_min = round(coords['long_min'] * 600000)
        lat_min = round(coords['lat_min'] * 600000)
        long_max = round(coords['long_max'] * 600000)
        lat_max = round(coords['lat_max'] * 600000)

        bbox = f"{long_min}%2C{lat_min}%2C{long_max}%2C{lat_max}"
        req_url = f"https://www.vesselfinder.com/api/pub/mp2?bbox={bbox}&zoom={zoom}&mmsi=0"

        headers = {
            "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{random.randint(300,600)}.{random.randint(10,99)} (KHTML, like Gecko) Chrome/{random.randint(100,200)}.0.0.0 Safari/{random.randint(300,600)}.{random.randint(10,99)}",
            "Host": "www.vesselfinder.com",
            "Accept": "*/*",
            "Connection": "keep-alive",
            "Priority": "u=0, i",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Dnt": "1"
        }

        try:
            response = self.page.request.get(req_url, headers=headers)

            if not response.ok:
                logger.warning(f"Failed to fetch {req_url}. Status: {response.status}")
                return b""

            body = response.body()

            return body

        except Exception as e:
            logger.error(f"Exception during fetch: {e}")
            return b""

    def cleanup(self):
        '''
        Clean up and close stuff
        '''
        try:
            if self.context:
                self.context.close()
            if self.pw:
                self.pw.stop()
        except Exception:
            pass

        shutil.rmtree(self.temp_profile, ignore_errors=True)
        self._is_running = False

@ScraperRegistry.register
class vesselfinderScraper(AbstractScraper):
    '''
    Scraper for the site vesselfinder.com
    '''
    name = "VesselFinder_Scraper"
    default_interval_seconds = 10 * 60 # 10 min

    SHIP_TYPE_MAP = {
        0: None, # others, but we just mark as unknown
        1: None, # unknown
        2: "Tug",
        3: "Passenger",
        4: "Cargo",
        5: "Fishing",
        6: "Tanker",
        7: "Military",
        8: "Sailing"
    }

    base_url = "https://www.vesselfinder.com/api/pub/mp2"

    def fetch_data(self, coords: dict):
        '''
        Fetches data from the site. Runs in a separate thread.
        '''
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self._run_playwright_sync, coords)
            return future.result()

    def _run_playwright_sync(self, coords: dict) -> list:
        '''Helper to run Playwright synchronously in an isolated thread.'''
        scraper = Playwright_VesselFinder()
        try:
            lat_min, lat_max = coords['lat_min'], coords['lat_max']
            lon_min, lon_max = coords['long_min'], coords['long_max']

            lat_step = 10 / 60.0
            avg_lat = (lat_min + lat_max) / 2
            cos_lat = math.cos(math.radians(avg_lat))
            lon_step = 10 / (60.0 * cos_lat) if cos_lat > 0 else lat_step

            all_data_chunks = []
            scraper.start()

            curr_lat = lat_min
            while curr_lat < lat_max:
                next_lat = min(curr_lat + lat_step, lat_max)
                curr_lon = lon_min
                while curr_lon < lon_max:
                    next_lon = min(curr_lon + lon_step, lon_max)

                    chunk_coords = {
                        'lat_min': curr_lat, 'lat_max': next_lat,
                        'long_min': curr_lon, 'long_max': next_lon
                    }

                    data = scraper.fetch_mp2(chunk_coords)
                    if data:
                        all_data_chunks.append(data)
                    curr_lon += lon_step
                curr_lat += lat_step
                time.sleep(random.randint(1, 10))

            return all_data_chunks
        except Exception as e:
            write_audit_log("Error when scraping bounding box", __name__, {"scraper": self.name, "bbox": coords, "timestamp": str(datetime.now()), "error": str(e)})
            return []
        finally:
            scraper.cleanup()

    def parse_data(self, data, page=None):
        '''
        Parse data from VesselFinder to fit fields in ScrapedVesselRecord
        '''
        output = []

        if not data:
            logger.warning("No data to parse.")
            return output

        data_list = data if isinstance(data, list) else [data]
        mmsi_seen = set()
        zoomLevel = 15

        for blob in data_list:
            if not blob:
                continue

            try:
                text_data = blob.decode('utf-8')
                if text_data.startswith('{') or text_data.startswith('['):
                    logger.warning(f"Received JSON instead of binary data.")
                    continue
            except UnicodeDecodeError:
                pass

            idx = 12
            while idx < len(blob):
                try:
                    if idx + 2 > len(blob): break
                    flags = int.from_bytes(blob[idx:idx+2], byteorder='big', signed=False)
                    idx += 2

                    ship_type_code = (flags & 0x00F0) >> 4
                    ship_type = vesselfinderScraper.SHIP_TYPE_MAP.get(ship_type_code, None)

                    if idx + 4 > len(blob): break
                    mmsi = int.from_bytes(blob[idx:idx+4], "big")
                    idx += 4

                    if idx + 4 > len(blob): break
                    lat = int.from_bytes(blob[idx:idx+4], "big", signed=True) / 600000.0
                    idx += 4

                    if idx + 4 > len(blob): break
                    lon = int.from_bytes(blob[idx:idx+4], "big", signed=True) / 600000.0
                    idx += 4

                    if idx + 1 > len(blob): break
                    time__delta_byte = int.from_bytes(blob[idx:idx+1], "big", signed=False)
                    idx += 1

                    is_negative = (time__delta_byte & 0x80) != 0
                    magnitude = time__delta_byte & 0x7F

                    if is_negative:
                        if magnitude >= 24:
                            days = round(magnitude / 24)
                            minutes_ago = days * 24 * 60
                        else:
                            minutes_ago = magnitude * 60
                    else:
                        minutes_ago = time__delta_byte
                    vessel_timestamp = datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)

                    if minutes_ago >= 60 and page is not None:
                        try:
                            api_url = f"https://www.vesselfinder.com/api/pub/click/{mmsi}"
                            response = page.request.get(api_url)

                            if response.ok:
                                click_data = response.json() 
                                exact_ts = click_data.get('ts')
                                if exact_ts and exact_ts > 0:
                                    vessel_timestamp = datetime.fromtimestamp(exact_ts, tz=timezone.utc)

                            time.sleep(random.randint(1, 100) * 0.01)
                        except Exception as e:
                            logger.debug(f"Failed to fetch exact timestamp for {mmsi}: {e}")

                    if idx + 1 > len(blob): break
                    ship_name_length = blob[idx]
                    idx += 1

                    if idx + ship_name_length > len(blob): break
                    ship_name = blob[idx:idx+ship_name_length].decode("utf-8", errors="ignore")
                    ship_name = ship_name.replace('\x00', '').strip()
                    idx += ship_name_length

                    if zoomLevel >= 14:
                        if idx + 10 > len(blob): break
                        idx += 10

                    if mmsi not in mmsi_seen:
                        mmsi_seen.add(mmsi)
                        vessel_dict = {
                            "MMSI": mmsi,
                            "Ship Name": ship_name,
                            "Latitude": lat,
                            "Longitude": lon,
                            "Ship Type": ship_type
                        }

                        output.append({
                            "mmsi": vessel_dict["MMSI"],
                            "imo": None,
                            "ship_name": vessel_dict["Ship Name"],
                            "ship_type": vessel_dict["Ship Type"],
                            "length_meters": None,
                            "beam_meters": None,
                            "lat": vessel_dict["Latitude"],
                            "lon": vessel_dict["Longitude"],
                            "timestamp": vessel_timestamp,
                            "nav_status": None,
                            "rawout": str(vessel_dict)
                        })

                except Exception as e:
                    logger.debug(f"Error parsing vessel data blob at index {idx}: {e}")
                    break

        return output

if __name__ == "__main__":
    s = vesselfinderScraper()
    raw = s.fetch_data({
        "long_min": 103.82335160632802,
        "long_max": 103.85594676548685,
        "lat_min": 1.2535264424975803,
        "lat_max": 1.266477533544827
    })
    s.parse_data(raw)
