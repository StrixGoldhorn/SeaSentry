# backend/app/modules/scrapers/plugins/aprs_scraper.py
'''
Scrape aprs.fi
'''

from app.modules.scrapers.registry import ScraperRegistry
from app.modules.scrapers import AbstractScraper
from app.utils.audit_log_helpers import write_audit_log

import logging
import tempfile
import shutil
import xml.etree.ElementTree as ET
import json
import concurrent.futures
import re
import random
from playwright.sync_api import sync_playwright
from datetime import datetime, timezone
from playwright_stealth import Stealth

logger = logging.getLogger(__name__)

def apply_stealth(page): Stealth().apply_stealth_sync(page)

class Playwright_aprs():
    '''
    Class to use Playwright browser to scrape
    '''
    def __init__(self):
        # Secure temporary directory for WAF cookies
        self.temp_profile = tempfile.mkdtemp(prefix="seasentry_")
        self.pw = None
        self.context = None
        self.page = None
        self._is_running = False

    def start(self):
        '''
        Start browser, get waf token
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
        self.page.goto("https://aprs.fi/", wait_until="domcontentloaded")

        try:
            # Wait for the map to ensure the WAF challenge is complete
            self.page.wait_for_selector("div#map")
            # logger.debug("WAF chall complete")
        except Exception as e:
            logger.debug("WAF chall failed")
            write_audit_log("Failed to get authentication", __name__, {"headless_browser": __name__, "site": "aprs.fi", "timestamp": str(datetime.now()), "error": str(e)})

        self._is_running = True

    def fetch_xml2(self, coords: dict, timerange: int = 24 * 60 * 60, tail: int = 0) -> str:
        """
        Fetches data directly from the /xml2 endpoint using custom GET parameters.
        """
        if not self._is_running:
            self.start()

        base_url = "https://aprs.fi/xml2"
        req_url = f"{base_url}?box={coords['lat_min']}%2C{coords['long_min']}%2C{coords['lat_max']}%2C{coords['long_max']}&timerange={timerange}&tail={tail}"

        # Use the browser's authenticated session to make the API request, include Cloudflare cookies
        response = self.page.request.get(
            req_url,
            headers={
                "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{random.randint(300,600)}.{random.randint(10,99)} (KHTML, like Gecko) Chrome/{random.randint(100,200)}.0.0.0 Safari/{random.randint(300,600)}.{random.randint(10,99)}",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://aprs.fi/",
                "Origin": "https://aprs.fi",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "X-Requested-With": "XMLHttpRequest",  # Required for internal API endpoints
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
            }
        )

        if not response.ok:
            logger.debug("Fetching url failed")
            return None

        # logger.debug(f"Response: {response.text()}")

        # Parse based on what the API returns
        content_type = response.headers.get("content-type", "")
        if "xml" in content_type or "text" in content_type:
            return response.text()
        else:
            return ""

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

        # Delete the temporary profile directory completely
        shutil.rmtree(self.temp_profile, ignore_errors=True)
        self._is_running = False

@ScraperRegistry.register
class aprsScraper(AbstractScraper):
    '''
    Scraper for the site aprs.fi
    '''
    name = "aprs_Scraper"
    default_interval_seconds = 10 * 60 # 10 min

    base_url = "https://aprs.fi/xml2"

    def fetch_data(self, coords: dict):
        '''
        Fetches data from the site. Runs in a separate thread to avoid 
        'Sync API inside asyncio loop' errors while remaining synchronous.
        '''
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self._run_playwright_sync, coords)
            return future.result()

    def _run_playwright_sync(self, coords: dict) -> str:
        '''Helper to run Playwright synchronously in an isolated thread.'''
        scraper = Playwright_aprs()
        try:
            data = scraper.fetch_xml2(coords)
            return data if data else ""
        except Exception as e:
            write_audit_log("Error when scraping bounding box", __name__, {"scraper": self.name, "bbox": coords, "timestamp": str(datetime.now()), "error": str(e)})
            return ""
        finally:
            scraper.cleanup()

    def parse_data(self, data):
        '''
        Parse data to fit fields in ScrapedVesselRecord
        '''

        def processVessel(vessel: dict) -> dict:
            '''
            Converts into appropriate dict
            '''
            return {
                    "mmsi": vessel.get("name", None),
                    "imo": vessel.get("imo", None),
                    "ship_name": vessel.get("showname", None),
                    "length_meters": vessel.get("length", None),
                    "beam_meters": vessel.get("width", None),
                    "lat": vessel.get("lat", None),
                    "lon": vessel.get("lng", None),
                    "timestamp": datetime.fromtimestamp(vessel["time"], tz=timezone.utc) if vessel.get("time") is not None else None,
                    "nav_status": vessel.get("navstat", None),
                    "rawout": str(vessel)
                }

        output = []

        if not data or data == "":
            return output

        try:
            root = ET.fromstring(data)
        except ET.ParseError:
            logger.warning("Failed to parse XML data from aprs.fi")
            return output

        for child in root:
            if child.text and child.text.startswith("it("):
                match = re.search(r'it\((\{.*\})\);?', child.text, re.DOTALL)
                if match:
                    try:
                        vessel = json.loads(match.group(1))
                        vessel = processVessel(vessel)
                        output.append(vessel)
                    except json.JSONDecodeError:
                        pass

        return output

if __name__ == "__main__":
    s = aprsScraper()
    raw = s.fetch_data({
        "long_min": 103.82335160632802,
        "long_max": 103.85594676548685,
        "lat_min": 1.2535264424975803,
        "lat_max": 1.266477533544827
    })
    s.parse_data(raw)
