# backend/app/core/config.py

'''
Global settings
'''

import os
from dotenv import load_dotenv

class Settings():
    '''
    Global settings
    '''

    CORS_ALLOWED: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]

    SCRAPER_CONFIGS: dict = {
        "AISFriends_Scraper": {
            "enabled": True,
            # "enabled": False,
            "interval_seconds": (300, 600)
        },
        "aprs_Scraper": {
            # "enabled": True,
            "enabled": False,
            "interval_seconds": (600, 1800)
        },
        "VesselFinder_Scraper": {
            # "enabled": True,
            "enabled": False,
            "interval_seconds": (600, 1800)
        }
    }

    # ATAK
    # ENABLE_ATAK_INTEGRATION: bool =  True
    ENABLE_ATAK_INTEGRATION: bool =  False

    # Alerts
    ALERT_RECHECK_MINUTES: int = 10
    ALERT_CHECK_PREVIOUS_MINUTES: int = 180

    # env
    ENV = os.getenv("ENV", "local")
    if ENV == "docker":
        load_dotenv("../.env.docker")
    else:
        load_dotenv("../.env.local")

    # Scraper
    SCRAPE_RESET_TIMER_SECONDS: int = os.getenv("SCRAPE_RESET_TIMER_SECONDS")

    # Database
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT")

    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

    EXEC_INFO_API: bool = os.getenv("EXEC_INFO_API")

    ENABLE_EASTER_EGG: bool = True
    EASTER_EGG_TOLERANCE: int = 8