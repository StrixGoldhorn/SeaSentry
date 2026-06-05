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
        }
    }

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
