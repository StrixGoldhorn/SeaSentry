import asyncio
import xml.etree.ElementTree as ET
import pytak
import threading
from datetime import datetime, timedelta
from configparser import ConfigParser
from sqlalchemy import desc
from geoalchemy2.functions import ST_X, ST_Y

from app.core.database import DBConn
from app.models.vessel import VesselData, VesselLocation
from app.utils.audit_log_helpers import write_audit_log

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

class MySender(pytak.QueueWorker):
    """
    Process or generate your Cursor-On-Target Events,
    then adds the COT Events to a queue for TX to a COT_URL.
    """

    async def handle_data(self, data):
        """Handle pre-CoT data, serialize to CoT Event, puts on queue."""
        event = data
        await self.put_queue(event)

    async def run(self):
        """Run loop for processing or generating pre-CoT data."""
        while True:
            data = gen_cot_mmsi_imo()
            self._logger.info("Sending:\n%s\n", data.decode())
            await self.handle_data(data)
            await asyncio.sleep(5)

class MyReceiver(pytak.QueueWorker):
    """Handle events from RX Queue."""

    async def handle_data(self, data):
        """Handle data from the receive queue."""
        self._logger.info("Received:\n%s\n", data.decode())

    async def run(self):
        """Read from the receive queue, put data onto handler."""
        while True:
            data = (
                await self.queue.get()
            )
            await self.handle_data(data)

class VesselScheduler(pytak.QueueWorker):
    """Periodically checks for vessel updates and sends to ATAK."""
    async def run(self):
        while True:
            try:
                await check_all_vessels(15, self.queue)
            except Exception as e:
                self._logger.error(f"Error in VesselScheduler: {e}")

            await asyncio.sleep(60)

async def check_all_vessels(n: int, tx_queue: asyncio.Queue):
    '''
    Function that scheduler should call, checks alert rules for all vessel locations within the past n minutes.
    
    Args:
        n: int, checks for all vessels within the past n minutes
        tx_queue: asyncio.Queue, queue to send CoT events to ATAK server
    '''
    session = DBConn.get_session()
    try:
        threshold_time = datetime.now() - timedelta(minutes=n)

        results = session.query(
            VesselData.vessel_data_ship_name,
            VesselData.vessel_data_mmsi,
            VesselData.vessel_data_imo,
            ST_X(VesselLocation.vessel_location_coords).label('lon'),
            ST_Y(VesselLocation.vessel_location_coords).label('lat')
        )\
        .join(VesselLocation, VesselData.vessel_data_id == VesselLocation.vessel_location_vessel_data_id)\
        .filter(VesselLocation.vessel_location_timestamp >= threshold_time)\
        .distinct(VesselData.vessel_data_mmsi) \
        .order_by(
            VesselData.vessel_data_mmsi,
            desc(VesselLocation.vessel_location_timestamp)
        )\
        .all()

        logger.debug("ATAK-Integration: Processing %d unique vessels", len(results))

        for name, mmsi, imo, lon, lat in results:
            logger.debug(f"ATAK-Integration: Processing Name: {str(name)} MMSI: {mmsi}, IMO: {imo}")
            if lon is not None and lat is not None:
                cot_event = gen_cot_mmsi_imo(float(lat), float(lon), name, str(mmsi), str(imo))
                await tx_queue.put(cot_event)
                logger.info(f"ATAK-Integration: Sent CoT event for Name: {str(name)} MMSI: {mmsi}, IMO: {imo}")
            else:
                logger.warning(f"ATAK-Integration: Skipping MMSI {mmsi} due to missing coordinates.")

    except Exception as e:
        logger.error("ATAK-Integration: Error in check_all_vessels: %s", str(e))
        write_audit_log("ATAK-Integration: Error in check_all_vessels", __name__, {"info": str(e)}, "ERROR")

    finally:
        session.close()

async def main():
    """
    Sets config params and adds serializer to task list
    """
    config = ConfigParser()
    # +wo will discard all incoming cos we don't need incoming data (yet)
    config["mycottool"] = {"COT_URL": "tcp+wo://192.168.1.17:8087"} 
    config = config["mycottool"]

    while True:
        try:
            logger.info("ATAK: Attempting to connect to TAK server...")
            clitool = pytak.CLITool(config)
            await clitool.setup()

            clitool.add_tasks(
                [
                    VesselScheduler(clitool.tx_queue, config)
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
