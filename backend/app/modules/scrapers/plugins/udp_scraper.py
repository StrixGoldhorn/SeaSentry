# backend/app/modules/scrapers/plugins/udp_listener_scraper.py

import socket
import threading
import queue
from datetime import datetime, timezone
from pyais import decode

from app.core.config import Settings
from app.modules.scrapers.registry import ScraperRegistry
from app.modules.scrapers import AbstractScraper
from app.utils.audit_log_helpers import write_audit_log
from app.utils.vessel_helpers import update_vessel_data_in_db, get_vessel_by_mmsi

import logging
logger = logging.getLogger(__name__)

msg_buffer = queue.Queue()

def _background_udp_listener(host, port, stop_event):
    """
    Listens to UDP socket and adds messages to the queue.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    sock.settimeout(1.0)

    logger.info(f"Continuous AIS Listener started on {host}:{port}")
    try:
        while not stop_event.is_set():
            try:
                data, addr = sock.recvfrom(4096)

                lines = data.decode('utf-8', errors='ignore').splitlines()
                for line in lines:
                    msg = line.strip()
                    if msg:
                        msg_buffer.put(msg)
            except socket.timeout:
                continue
            except Exception as e:
                logger.error(f"Socket error in listener: {e}")
                break
    finally:
        sock.close()
        logger.info("AIS UDP Listener stopped.")


@ScraperRegistry.register
class UDPScraper(AbstractScraper):
    '''
    Listens to UDP stream of NMEA messages.
    '''
    name = "UDP_Scraper"

    _listener_thread = None
    _stop_event = threading.Event()

    default_interval_seconds = 60

    def __init__(self):
        super().__init__()

        # only need ONE instancee of listener
        if not UDPScraper._listener_thread or not UDPScraper._listener_thread.is_alive():
            self._start_listener()

    def _start_listener(self):
        self.__class__._stop_event.clear()
        self.__class__._listener_thread = threading.Thread(
            target=_background_udp_listener,
            args=(Settings.UDP_IP, Settings.UDP_PORT, self.__class__._stop_event),
            daemon=True
        )
        self.__class__._listener_thread.start()

    def fetch_data(self, coords: dict):
        '''
        Empty queue.
        '''
        raw_messages = []

        while not msg_buffer.empty():
            try:
                raw_messages.append(msg_buffer.get_nowait())
            except queue.Empty:
                break

        return raw_messages

    def parse_data(self, raw):
        '''
        Parse raw NMEA messages.
        '''
        messages = raw
        output = []

        for message in messages:
            try:
                decoded_msg = decode(message)
                dict_msg = decoded_msg.asdict()
                msg_type = dict_msg.get("msg_type")

                if msg_type not in [1,2,3,18,19]:
                    write_audit_log("Non-position NMEA msg", __name__, {"msg": str(decoded_msg), "msg_type": str(msg_type)}, "INFO")
                    if msg_type == 24:
                        mmsi = dict_msg.get("mmsi")
                        vessel = get_vessel_by_mmsi(str(mmsi))
                        if vessel is None:
                            continue

                        to_bow = dict_msg.get("to_bow", None)
                        to_stern = dict_msg.get("to_stern", None)
                        to_port = dict_msg.get("to_port", None)
                        to_starboard = dict_msg.get("to_starboard", None)

                        length = None
                        beam = None

                        if to_bow is not None and to_stern is not None:
                            length = int(to_bow) + int(to_stern)

                        if to_port is not None and to_starboard is not None:
                            beam = int(to_port) + int(to_starboard)

                        update_vessel_data_in_db(
                            vessel.vessel_data_id,
                            ship_name=dict_msg.get("shipname", None),
                            length_meters=length,
                            beam_meters=beam
                        )
                        write_audit_log("Updated vessel", __name__, {"mmsi": str(mmsi), "message": str(message)}, "INFO")
                        continue
                    continue

                lat = dict_msg.get("lat")
                lon = dict_msg.get("lon")

                if lat is None or lon is None:
                    continue

                speed = dict_msg.get("speed")
                if speed is not None and speed >= 102.3: speed = None

                course = dict_msg.get("course")
                if course is not None and course >= 360: course = None

                heading = dict_msg.get("heading")
                if heading is not None and heading >= 511: heading = None

                ts = dict_msg.get("timestamp")
                dt = datetime.fromtimestamp(ts, tz=timezone.utc) if ts else datetime.now(timezone.utc)

                mmsi = dict_msg.get("mmsi")
                imo = dict_msg.get("imo")

                if (mmsi is not None or imo is not None) and (lat is not None and lon is not None) and (dt is not None):
                    output.append({
                        "mmsi": mmsi,
                        "imo": imo,
                        "ship_name": dict_msg.get("shipname", None),
                        "flag": None,
                        "length_meters": None,
                        "beam_meters": None,
                        "lat": lat,
                        "lon": lon,
                        "timestamp": dt,
                        "speed_knots": speed,
                        "course_deg": course % 360 if course is not None else None,
                        "heading_deg": heading % 360 if heading is not None else None,
                        "nav_status": dict_msg.get("status"),
                        "rawout": str(decoded_msg)
                    })

            except Exception as e:
                logger.debug(f"Failed to parse NMEA message: {message}. Error: {e}")
                write_audit_log("Failed to parse NMEA message", __name__, {"error": str(e), "message": str(message)}, "ERROR")

        return output
