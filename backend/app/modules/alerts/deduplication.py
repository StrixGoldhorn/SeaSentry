# backend/app/modules/alerts/deduplication.py

from datetime import timedelta, datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.alert import AlertHistory

import logging

logger = logging.getLogger(__name__)

ALERT_COOLDOWN = timedelta(hours = 1)

def is_duplicate_alert(session: Session, rule_id: int, context: Dict[str, Any]) -> bool:
    '''
    Check if an identical alert was triggered within cooldown period.
    
    Args:
        session: SQLAlchemy session
        rule_id: The alert rule ID
        context: The alert context dictionary
    
    Returns:
        True if duplicate found, False otherwise
    '''
    cutoff_time = datetime.now() - ALERT_COOLDOWN

    query = session.query(AlertHistory).filter(
        AlertHistory.alert_history_alert_rule_id == rule_id,
        AlertHistory.alert_history_context.contains(context),
        AlertHistory.alert_history_timestamp > cutoff_time
    )

    return session.query(query.exists()).scalar()

def record_alert(session: Session, rule_id: int, context: Dict[str, Any]) -> int:
    '''
    Record a new unique alert in the database.
    
    Args:
        session: SQLAlchemy session
        rule_id: The alert rule ID
        context: The alert context dictionary
        details: Additional details about the alert
    
    Returns:
        alert_history_id
    '''
    new_alert = AlertHistory(
        alert_history_alert_rule_id = rule_id,
        alert_history_context = context,
        alert_history_read = False,
        alert_history_timestamp = datetime.now()
    )

    session.add(new_alert)
    session.commit()

    return new_alert.alert_history_id

def check_and_record_alert(session, rule_id: int, context: Dict[str, Any]) -> Optional[int]:
    '''
    Check for if alert is duplicate, and records alert if unique.
    
    Args:
        session: SQLAlchemy session
        rule_id: The alert rule ID
        context: The alert context dictionary
    
    Returns:
        Alert ID if recorded, None if duplicate
    '''

    if is_duplicate_alert(session, rule_id, context):
        logger.debug("Alert is duplicate! context: %s", str(context))
        return None

    logger.debug("Alert generated, rule id: %d", rule_id)
    return record_alert(session, rule_id, context)
