# backend/app/core/tests/test_db_conn.py

"""
Unit tests for database.py
"""

from ..database import DBConn
from sqlalchemy import text
from sqlalchemy.orm import scoped_session

import pytest
import logging

logger = logging.getLogger(__name__)

@pytest.mark.live
class TestDBConn:
    '''
    Class to do unit testing
    for backend/app/core/tests/test_db_conn.py
    '''
    
    def test_get_session(self):
        '''
        Test if can get session
        '''
        DBConn.init_db()
        session = DBConn.get_session()
        assert isinstance(DBConn.DB_SESSION, scoped_session), f"Expected scoped_session, got {type(DBConn.DB_SESSION)}"
        assert isinstance(session, scoped_session), f"Expected scoped_session, got {type(DBConn.DB_SESSION)}"
        logger.info("%s Tests successful", type(self).__name__)

    def test_get_session_same_session(self):
        '''
        Test if they return the same session
        '''
        DBConn.init_db()
        session1 = DBConn.get_session()
        session2 = DBConn.get_session()
        assert session1 is session2, "Same session expected"
        logger.info("%s Tests successful", type(self).__name__)

    def test_check_connection(self):
        '''
        Test if check_connection works
        '''
        DBConn.init_db()
        assert DBConn.check_connection() is True, "Expected to be connected!"
        logger.info("%s Tests successful", type(self).__name__)

    def test_get_postgis_version(self):
        '''
        Test if get_postgis_version works
        '''
        DBConn.init_db()
        assert DBConn.get_postgis_version() is not None, "Expected a response!"
        logger.info("%s Tests successful", type(self).__name__)


if __name__ == "__main__":
    a = TestDBConn()
    a.test_get_session()
    a.test_get_session_same_session()
    a.test_check_connection()
    a.test_get_postgis_version()
