# backend/app/utils/alert_helpers.py

import logging
from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from app.core.database import DBConn
from app.models.alert import AlertRule, AlertHistory

logger = logging.getLogger(__name__)

def get_all_alert_history(start_time: Optional[datetime] = None, end_time: Optional[datetime] = None,
                          limit: Optional[int] = None, offset: Optional[int] = None, is_read: Optional[bool] = None) -> List[AlertHistory]:
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

# def DBG_INSERT_DEFAULT_AOI():
#     logging.warning("ADDING DEFAULT AOI TO DB-------------------------------------")
#     add_rectangle_aoi_to_db(
#         "Default Brani",
#         103.82335160632802,
#         103.85594676548685,
#         1.2535264424975803,
#         1.266477533544827
#     )

# if __name__ == "__main__":
#     # {
#     #     "long_min": 103.82335160632802,
#     #     "long_max": 103.85594676548685,
#     #     "lat_min": 1.2535264424975803,
#     #     "lat_max": 1.266477533544827
#     # }
#     ADD_DEFAULT = False
#     if ADD_DEFAULT:
#         import time
#         time.sleep(15)
#         logging.warning("ADDING TO DB-------------------------------------")
#         add_rectangle_aoi_to_db(
#             "Default Brani",
#             103.82335160632802,
#             103.85594676548685,
#             1.2535264424975803,
#             1.266477533544827
#         )