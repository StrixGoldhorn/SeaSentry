# backend/app/utils/alert_helpers.py

import logging
from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.core.database import DBConn
from app.models.alert import AlertRule, AlertHistory

logger = logging.getLogger(__name__)

def get_all_alert_history(start_time: Optional[datetime] = None, end_time: Optional[datetime] = None,
                          limit: Optional[int] = None, offset: Optional[int] = None, is_read: Optional[bool] = None,
                          by_alert_rule_id: Optional[int] = None) -> List[AlertHistory]:
    '''
    Fetches all alert history from DB.
    Returns list of AlertHistory objects.
    '''

    session = DBConn.get_session()
    try:
        query = session.query(AlertHistory)

        query = query.order_by(AlertHistory.alert_history_timestamp.desc())

        if start_time is not None:
            query = query.filter(AlertHistory.alert_history_timestamp >= start_time)
        if end_time is not None:
            query = query.filter(AlertHistory.alert_history_timestamp <= end_time)
        if is_read is not None:
            query = query.filter(AlertHistory.alert_history_read == is_read)

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)
        if by_alert_rule_id is not None:
            query = query.where(AlertHistory.alert_history_alert_rule_id == by_alert_rule_id)

        return query.all()

    except Exception as e:
        logger.error("Error in get_all_alert_history: %s", e, exc_info=True)
        return []

    finally:
        if session:
            DBConn.close_session()

def get_all_alert_rule() -> List[AlertRule]:
    '''
    Fetches all alert rules from DB.
    Returns list of AlertRule objects.
    '''

    session = DBConn.get_session()
    try:
        query = session.query(AlertRule)
        return query.all()

    except Exception as e:
        logger.error("Error in get_all_alert_rule: %s", e, exc_info=True)
        return []

    finally:
        if session:
            DBConn.close_session()

def get_alert_rule_by_id(alert_rule_id: int) -> AlertRule:
    '''
    Fetches alert rule with given alert_rule_id from DB.
    Returns an AlertRule object.
    '''

    session = DBConn.get_session()
    try:
        query = session.query(AlertRule).filter(AlertRule.alert_rule_id == alert_rule_id)
        res = query.first()
        return res

    except Exception as e:
        session.rollback()
        logger.error("DB Error in get_alert_rule_by_id: %s", str(e), exc_info=True)
        raise

    finally:
        if session:
            DBConn.close_session()

def add_alert_rule_to_db(name: str, desc: str, params: Dict) -> int:

    rule = AlertRule(
        alert_rule_timestamp = datetime.now(),
        alert_rule_name = name,
        alert_rule_description = desc,
        alert_rule_params = params,
        alert_rule_enabled = True
    )

    session = DBConn.get_session()

    try:
        session.add(rule)
        session.commit()
        logger.info("Added rule '%s' (id: %d)", name, rule.alert_rule_id)
        return rule.alert_rule_id

    except IntegrityError as e:
        session.rollback()
        logger.warning("Rule name '%s' already exists or violates unique constraint.", name)
        raise ValueError(f"Rule name '{name}' must be unique.") from e

    except Exception as e:
        session.rollback()
        logger.error("Failed to create rule '%s': %s", name, e, exc_info=True)
        raise

    finally:
        DBConn.close_session()

def mark_alert_as_read(alert_id: int):
    '''
    Marks alert as read
    
    Args:
        alert_id: id of alert to be marked as read
    
    Returns:
        True if successful
    '''

    session = DBConn.get_session()
    try:
        alert = session.query(AlertHistory).filter(AlertHistory.alert_history_id == alert_id).first()
        if not alert:
            return False
        alert.alert_history_read = True
        session.commit()
        logger.info("Marked alert history id %d as read", alert.alert_history_id)
        return True

    except Exception as e:
        session.rollback()
        logger.error("Failed to mark alert history id %d as read: %s", alert_id, str(e), exc_info=True)
        raise

    finally:
        DBConn.close_session()

def mark_alert_as_unread(alert_id: int):
    '''
    Marks alert as unread
    
    Args:
        alert_id: id of alert to be marked as unread
    
    Returns:
        True if successful
    '''

    session = DBConn.get_session()
    try:
        alert = session.query(AlertHistory).filter(AlertHistory.alert_history_id == alert_id).first()
        if not alert:
            return False
        alert.alert_history_read = False
        session.commit()
        logger.info("Marked alert history id %d as unread", alert.alert_history_id)
        return True

    except Exception as e:
        session.rollback()
        logger.error("Failed to mark alert history id %d as unread: %s", alert_id, str(e), exc_info=True)
        raise

    finally:
        DBConn.close_session()

def mark_rule_as_disable(alert_rule_id: int):
    '''
    Disables rule
    
    Args:
        alert_rule_id: id of alert to be disabled
    
    Returns:
        True if successful
    '''

    session = DBConn.get_session()
    try:
        alert = session.query(AlertRule).filter(AlertRule.alert_rule_id == alert_rule_id).first()
        if not alert:
            return False
        alert.alert_rule_enabled = False
        session.commit()
        logger.info("Marked alert rule id %d as disabled", alert.alert_rule_id)
        return True

    except Exception as e:
        session.rollback()
        logger.error("Failed to mark rule id %d as disabled: %s", alert_rule_id, str(e), exc_info=True)
        raise

    finally:
        DBConn.close_session()

def mark_rule_as_enable(alert_rule_id: int):
    '''
    Enables rule
    
    Args:
        alert_rule_id: id of alert to be enabled
    
    Returns:
        True if successful
    '''

    session = DBConn.get_session()
    try:
        alert = session.query(AlertRule).filter(AlertRule.alert_rule_id == alert_rule_id).first()
        if not alert:
            return False
        alert.alert_rule_enabled = True
        session.commit()
        logger.info("Marked alert rule id %d as enabled", alert.alert_rule_id)
        return True

    except Exception as e:
        session.rollback()
        logger.error("Failed to mark rule id %d as enabled: %s", alert_rule_id, str(e), exc_info=True)
        raise

    finally:
        DBConn.close_session()

def update_alert_rule_in_db(alert_rule_id: int,
                            name: str = None, desc: str = None,
                            params: Dict = None) -> bool:
    '''
    Updates an existing vessel in the database. Supports partial updates.

    Args:
        alert_rule_id: int representing vessel_of_interest_id to be updated
        alert_rule_name: str = None, new name of alert rule
        alert_rule_description: str = None, new description of alert rule
        alert_rule_params: Dict = None, new of params alert rule

    Returns:
        True if successful
    '''

    session = DBConn.get_session()
    try:
        # RESERVED RULES!!!
        if alert_rule_id == 1 or alert_rule_id == 2:
            return False
        rule = session.query(AlertRule).filter(AlertRule.alert_rule_id == alert_rule_id).first()

        if not rule:
            return False

        if name is not None:
            rule.alert_rule_name = name

        if desc is not None:
            rule.alert_rule_description = desc

        if params is not None:
            rule.alert_rule_params = params

        session.commit()
        logger.info("Updated alert rule id %d", alert_rule_id)
        return True

    except IntegrityError as e:
        session.rollback()
        logger.warning("Rule name '%s' already exists or violates unique constraint.", name)
        raise ValueError(f"Rule name '{name}' must be unique.") from e

    except Exception as e:
        session.rollback()
        logger.error("Failed to update rule id %d: %s", alert_rule_id, e, exc_info=True)
        raise

    finally:
        DBConn.close_session()

def delete_alert_rule_in_db(alert_rule_id: int):
    '''
    Deletes an existing alert rule in the database.
    
    Args:
        alert_rule_id: int representing alert_rule_id to be deleted

    Returns:
        True if successful
    '''

    session = DBConn.get_session()
    try:
        # RESERVED RULES!!!
        if alert_rule_id == 1 or alert_rule_id == 2:
            return False
        rule = session.query(AlertRule).filter(AlertRule.alert_rule_id == alert_rule_id).first()
        if not rule:
            return False

        session.delete(rule)
        session.commit()
        return True

    except Exception as e:
        session.rollback()
        logger.error("DB Error in delete_alert_rule_in_db: %s", str(e))
        raise
    finally:
        DBConn.close_session()
