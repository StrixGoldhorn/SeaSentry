import asyncio
import xml.etree.ElementTree as ET
import pytak
import threading
from datetime import datetime, timedelta
from configparser import ConfigParser
from shapely import wkb
from geoalchemy2.shape import to_shape

from app.core.config import Settings

from app.utils.vessel_helpers import get_vessels_in_polygon
from app.models.vessel import VesselData, VesselLocation

import logging
logger = logging.getLogger(__name__)

def gen_cot_mmsi_imo(lat: float, lon: float, name: str = None,
                     mmsi: str = "000000000", imo: str = "0000000") -> bytes:
    """Generate CoT Event."""
    root = ET.Element("event")
    root.set("version", "2.0")
    root.set("type", "a-u-S") # atomic, unknown relation, surface target

    root.set("uid", f"{mmsi}-{imo}")

    root.set("how", "m-g") # machine generated
    root.set("time", pytak.cot_time())
    root.set("start", pytak.cot_time())
    root.set("stale", pytak.cot_time(15 * 60)) # 15 minutes

    pt_attr = {
        "lat": f"{lat}",
        "lon": f"{lon}",
        "hae": "0",
        "ce": "0",
        "le": "0",
    }

    ET.SubElement(root, "point", attrib=pt_attr)

    detail = ET.Element("detail")

    contact = ET.Element("contact")
    contact.set("callsign", str(name) if name else f"Vessel {mmsi}")
    detail.append(contact)

    remarks = ET.Element("remarks")
    remarks.text = f"MMSI: {mmsi}, IMO: {imo}"
    detail.append(remarks)

    root.append(detail)

    return ET.tostring(root)

class PolygonReceiver(pytak.QueueWorker):
    """Listens to the rx_queue for incoming CoT events and parses polygons."""
    def __init__(self, rx_queue, tx_queue, config):
        super().__init__(rx_queue, config)
        self.tx_queue = tx_queue

    async def handle_data(self, data: bytes):
        """Parse CoT XML and extract polygon vertices."""
        try:
            root = ET.fromstring(data)
            event_type = root.get("type")

            # Ignore events that are not of type "u-d-f" (polygon) or "u-d-r" (rectangle)
            if event_type not in ["u-d-f", "u-d-r"] :
                return

            uid = root.get("uid")
            detail = root.find("detail")
            coords = []

            poly_name = detail.find("contact").get("callsign")

            if "AOI" not in poly_name:
                return

            if detail is not None:
                links = detail.findall("link")
                for link in links:
                    point_str = link.get("point")
                    if point_str:
                        parts = point_str.split(",")
                        if len(parts) >= 2:
                            lat = float(parts[0])
                            lon = float(parts[1])
                            coords.append((lon, lat))

            if len(coords) >= 3:
                if coords[0] != coords[-1]:
                    coords.append(coords[0])

                print(f"Received Polygon - UID: {uid}, Type: {event_type}")
                print(f"Name: {poly_name}")
                print(f"Points: {coords}")
                logger.info(f"Received Polygon - UID: {uid}, Type: {event_type}, Vertices: {len(coords)}")

                await self.query_and_send_vessels(coords, poly_name)

        except ET.ParseError:
            pass
        except Exception as e:
            logger.error(f"Error parsing ATAK polygon: {e}")

    async def query_and_send_vessels(self, coords: list, poly_name: str):
        """Queries the database using the helper function and sends vessels to the TAK server."""
        time_lower_bound = 15

        results = get_vessels_in_polygon(coords, time_lower_bound)

        logger.info(f"ATAK-Integration: Found {len(results)} vessels inside polygon '{poly_name}'")

        for location, vessel in results:
            name = vessel.vessel_data_ship_name
            mmsi = str(vessel.vessel_data_mmsi)
            imo = str(vessel.vessel_data_imo)

            try:
                geom_shape = to_shape(location.vessel_location_coords)
                lon, lat = geom_shape.x, geom_shape.y

            except Exception as e:
                logger.warning(f"Could not extract coordinates for MMSI {mmsi}: {e}")
                continue

            if lon is not None and lat is not None:
                cot_event = gen_cot_mmsi_imo(lat=lat, lon=lon, name=name, mmsi=mmsi, imo=imo)
                await self.tx_queue.put(cot_event)
                logger.info(f"ATAK-Integration: Sent CoT for vessel '{name}' (MMSI: {mmsi}) inside '{poly_name}'")

    async def run(self):
        """Read from the receive queue, put data onto handler."""
        while True:
            data = await self.queue.get()
            await self.handle_data(data)

async def main():
    """
    Sets config params and adds serializer to task list
    """
    config = ConfigParser()
    config["mycottool"] = {
            "COT_URL": "tcp://192.168.1.17:8087",
            "MAX_OUT_QUEUE": "1000",
            "MAX_IN_QUEUE": "1000"
        }
    config = config["mycottool"]

    while True:
        try:
            logger.info("ATAK: Attempting to connect to TAK server...")
            clitool = pytak.CLITool(config)
            await clitool.setup()

            clitool.add_tasks(
                [
                    PolygonReceiver(clitool.rx_queue, clitool.tx_queue, config)
                ]
            )
            await clitool.run()

        except (ConnectionResetError, BrokenPipeError, OSError) as e:
            logger.warning(f"ATAK: Connection lost ({e}). Reconnecting in 5 seconds...")
            await asyncio.sleep(5)

        except asyncio.CancelledError:
            logger.info("ATAK: Shutdown signal received. Stopping thread.")
            break

        except Exception as e:
            logger.error(f"ATAK: Unexpected error ({e}). Reconnecting in 10 seconds...")
            await asyncio.sleep(10)

def start_atak_background():
    """Starts the ATAK asyncio event loop in a background daemon thread."""
    logger.info("Starting ATAK Integration background thread...")

    thread = threading.Thread(
        target=lambda: asyncio.run(main()),
        daemon=True,
        name="ATAK-Thread"
    )
    thread.start()
    return thread
