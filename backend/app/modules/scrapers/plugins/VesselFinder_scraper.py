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
import json
from playwright.sync_api import sync_playwright
from datetime import datetime, timezone
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
            self.page.wait_for_selector("div#map-container", timeout=15000)
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

    base_url = "https://www.vesselfinder.com/api/pub/mp2"

    def fetch_data(self, coords: dict):
        '''
        Fetches data from the site. Runs in a separate thread.
        '''
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self._run_playwright_sync, coords)
            return future.result()

    def _run_playwright_sync(self, coords: dict) -> bytes:
        '''Helper to run Playwright synchronously in an isolated thread.'''
        scraper = Playwright_VesselFinder()
        try:
            data = scraper.fetch_mp2(coords)
            return data if data else b""
        except Exception as e:
            write_audit_log("Error when scraping bounding box", __name__, {"scraper": self.name, "bbox": coords, "timestamp": str(datetime.now()), "error": str(e)})
            return b""
        finally:
            scraper.cleanup()

    def parse_data(self, data: bytes):
        '''
        Parse data from VesselFinder to fit fields in ScrapedVesselRecord
        '''
        output = []

        if not data:
            logger.warning("No data to parse.")
            return output

        # Check if data is JSON (NOT SUPPOSED TO BE!!!)
        try:
            text_data = data.decode('utf-8')
            if text_data.startswith('{') or text_data.startswith('['):
                logger.warning(f"Received JSON instead of binary data: {text_data[:100]}")
                return output
        except UnicodeDecodeError:
            pass # Expected for binary data

        idx = 12
        part_header_length = 2
        mmsi_length = 4
        lat_length = 4
        long_length = 4
        is_selected_length = 1
        extra_zoom_info_length = 10
        zoomLevel = 15

        while idx < len(data):
            try:
                if idx + part_header_length > len(data): break
                part_header_data = data[idx:idx+part_header_length]
                idx += part_header_length

                if idx + mmsi_length > len(data): break
                mmsi_data = data[idx:idx+mmsi_length]
                mmsi = int.from_bytes(mmsi_data, "big")
                idx += mmsi_length

                if idx + lat_length > len(data): break
                lat_data = data[idx:idx+lat_length]
                lat = int.from_bytes(lat_data, "big") / 600000
                idx += lat_length

                if idx + long_length > len(data): break
                long_data = data[idx:idx+long_length]
                long = int.from_bytes(long_data, "big") / 600000
                idx += long_length

                if idx + is_selected_length > len(data): break
                is_selected = data[idx:idx+is_selected_length]
                idx += is_selected_length

                if idx + 1 > len(data): break
                ship_name_length = data[idx]
                idx += 1

                if idx + ship_name_length > len(data): break
                ship_name = data[idx:idx+ship_name_length]
                idx += ship_name_length

                if zoomLevel >= 14:
                    if idx + extra_zoom_info_length > len(data): break
                    idx += extra_zoom_info_length

                vessel_dict = {
                    "MMSI": mmsi,
                    "Ship Name": ship_name.decode("utf-8", errors="ignore"),
                    "Latitude": lat,
                    "Longitude": long
                }

                output.append({
                    "mmsi": vessel_dict.get("MMSI"),
                    "imo": None,
                    "ship_name": vessel_dict.get("Ship Name"),
                    "length_meters": None,
                    "beam_meters": None,
                    "lat": vessel_dict.get("Latitude"),
                    "lon": vessel_dict.get("Longitude"),
                    "timestamp": datetime.now(timezone.utc),
                    "nav_status": None,
                    "rawout": str(vessel_dict)
                })

            except Exception as e:
                logger.debug(f"Error parsing vessel data at index {idx}: {e}")
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
