# backend/app/main.py

import sys
import signal
import threading
import logging
import time

from flask import Flask
from flask_cors import CORS
from app.modules.vessels.routes import vessels_bp
from app.modules.aois.routes import aois_bp
from app.core.database import DBConn
from app.modules.scrapers.scrape import run_all_scrapers
from app.core.config import Settings

from app.utils.geo_helpers import DBG_INSERT_DEFAULT

logging.basicConfig(level=logging.DEBUG) # NOTE: PLEASE ONLY CONTROL LOGGER LEVEL FROM HERE
logger = logging.getLogger(__name__)

_scraper_started = False

def create_app():
    app = Flask(__name__)

    app.register_blueprint(vessels_bp)
    app.register_blueprint(aois_bp)

    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "http://127.0.0.1:3000"]}})

    @app.teardown_appcontext
    def teardown_session(exception = None):
        DBConn.close_session()

    return app

def main():
    global _scraper_started
    DBConn.init_db()

    app = create_app()

    scraper_threads = []
    if not _scraper_started:
        _scraper_started = True
        SCRAPER_CONFIGS = Settings.SCRAPER_CONFIGS

        stop_event = threading.Event()
        scraper_threads = run_all_scrapers(stop_event, SCRAPER_CONFIGS)

        logger.info("Scraper thread launched.")

    def shutdown_handler(signum, frame):
        '''
        Handle scraper shutdown
        '''
        global _scraper_started
        logger.info("Received shutdown signal. Stopping scrapers...")
        stop_event.set()

        for t in scraper_threads:
            t.join(timeout=5.0)

        _scraper_started = False

        logger.info("All scrapers stopped. Shutting down Flask...")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    logger.info("Starting SeaSentry Backend + Scraper...")

    app.run(host="0.0.0.0", port = 5000, debug = False, threaded = True, use_reloader=False)

if __name__ == "__main__":
    time.sleep(10)#TODO: Fix hardcoded wait
    _scraper_started = False
    try:
        DBG_INSERT_DEFAULT()
    except:
        pass
    # time.sleep(5)
    main()
