# backend/app/core/config.py

import os
from dotenv import load_dotenv

class Settings():
    load_dotenv()
    # Scraper
    SCRAPE_RESET_TIMER_SECONDS: int = os.getenv("SCRAPE_RESET_TIMER_SECONDS")

    # Database
    POSTGRES_USER: str = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT")

    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

    SCRAPER_CONFIGS: dict = {
        "AISFriends_Scraper": {
            "enabled": True,
            "interval_seconds": 300
        }
    }