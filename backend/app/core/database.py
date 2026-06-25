# backend/app/core/database.py

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from sqlalchemy.exc import OperationalError
from typing import Optional
import os
import time
import logging

from app.core.config import Settings

logger = logging.getLogger(__name__)

class DBConn():
    '''
    Class to handle connections to DB
    '''

    # Engine for database connections
    ENGINE: Optional[create_engine] = None

    # Session factory
    SESSION_FACTORY: Optional[sessionmaker] = None

    # One session, can technically make more if really needed
    DB_SESSION: Optional[scoped_session] = None

    Base = declarative_base()

    @classmethod
    def init_db(cls) -> None:
        '''
        Initialize database connection and session factory.
        Should be called once during application startup.
        '''
        _TRIES = 10
        _TIMEWAIT = 5
        for attempt in range(_TRIES):
            try:
                engine = create_engine(Settings.DATABASE_URL)
                with engine.connect() as connection:
                    print("Successfully connected to the database!")
                    cls.ENGINE = engine 
                    break
            except OperationalError:
                print(f"Database not ready yet... trying again in 5 seconds (Attempt {attempt + 1}/{_TRIES})")
                time.sleep(_TIMEWAIT)
        else:
            raise RuntimeError("Could not connect to the database.")

        # cls.ENGINE = create_engine(Settings.DATABASE_URL)

        cls.SESSION_FACTORY = sessionmaker(
            bind=cls.ENGINE,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )

        cls.DB_SESSION = scoped_session(cls.SESSION_FACTORY)

        cls.Base.query = cls.DB_SESSION.query_property()

        logger.debug("Database connection initialized successfully")

    @classmethod
    def get_session(cls) -> scoped_session:
        '''
        Get a database session for use.

        Returns:
            scoped_session to be used
        '''
        if cls.DB_SESSION is None:
            cls.init_db()
        return cls.DB_SESSION

    @classmethod
    def close_session(cls) -> None:
        '''
        Remove the current session. 
        Should be called at the end of each request (in Flask teardown).
        '''
        if cls.DB_SESSION is not None:
            cls.DB_SESSION.remove()

    @classmethod
    def run_init_sql(cls) -> None:
        '''
        Execute init.sql to set up PostGIS and create tables.
        Should be called once during initial setup if not in Docker container.
        '''
        if cls.ENGINE is None:
            cls.init_db()

        init_sql_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'db',
            'init.sql'
        )

        if not os.path.exists(init_sql_path):
            logger.warning("init.sql not found at %s", init_sql_path)
            return

        logger.debug("Executing %s", init_sql_path)

        try:
            with open(init_sql_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()

            # Execute the entire script
            with cls.ENGINE.connect() as conn:
                conn.execute(text(sql_script))
                conn.commit()

            logger.info("init.sql executed successfully")

        except Exception as e:
            logger.warning("Error executing init.sql: %s", e)
            raise

    @classmethod
    def drop_tables(cls, password1 = "qwertyuiop", password2 = "asdfgjkl") -> None:
        '''
        You have almost **no** reason to call this.
        
        DO **NOT** EVER EVER EVER TRY TO RUN THIS IF YOU DON'T KNOW WHAT YOU ARE DOING

        You must read the code to get the password. This is to ensure you know what the code does.
        
        Args:
            password1 (str): First part of password
            password2 (str): Second part of password
        '''
        if cls.ENGINE is None:
            raise RuntimeError("Database not initialized. Call init_db() first.")

        # Just to make sure the dev knows what they are doing
        # Not meant to be a "secure" check
        if password1 == "I_KN0W_WHAT_I_AM_D0ING" and password2 == "all_tables_will_be_gone":
            cls.Base.metadata.drop_all(bind=cls.ENGINE)
            logger.critical("All database tables dropped")
        else:
            logger.critical("Incorrect password to drop all tables")

    @classmethod
    def check_connection(cls) -> bool:
        '''
        Test database connection.

        Returns:
            True if connection is successful, False otherwise.
        '''
        if cls.ENGINE is None:
            return False

        try:
            with cls.ENGINE.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    @classmethod
    def get_postgis_version(cls) -> Optional[str]:
        '''
        Gets PostGIS version of DB

        Returns:
            String indicating PostGIS version 
        '''
        if cls.ENGINE is None:
            cls.init_db()

        try:
            with cls.ENGINE.connect() as conn:
                result = conn.execute(text("SELECT PostGIS_Version()"))
                out = result.scalar()
                return out

        except Exception as e:
            print(e)
            return None
