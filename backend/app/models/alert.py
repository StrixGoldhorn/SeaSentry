# backend/app/models/alert.py

from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.core.database import DBConn

Base = DBConn.Base

class AlertRule(Base):
    __tablename__ = 'alert_rule'
    alert_rule_id = Column(Integer, primary_key=True)
    alert_rule_timestamp = Column(DateTime(timezone=True))
    alert_rule_name = Column(Text, unique=True, nullable=False)
    alert_rule_description = Column(Text, nullable=True)
    alert_rule_params = Column(JSONB, nullable=False)
    alert_rule_enabled = Column(Boolean, nullable=False)

    history = relationship("AlertHistory", back_populates="rule", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AlertRule(id: {self.alert_rule_id}, name: {self.alert_rule_name}, enabled: {self.alert_rule_enabled})>"


class AlertHistory(Base):
    __tablename__ = 'alert_history'
    alert_history_id = Column(Integer, primary_key=True)
    alert_history_timestamp = Column(DateTime(timezone=True))
    alert_history_read = Column(Boolean, nullable=False)
    alert_history_read_at = Column(DateTime(timezone=True), nullable=True)
    alert_history_alert_rule_id = Column(Integer, ForeignKey('alert_rule.alert_rule_id'), nullable=False)

    rule = relationship("AlertRule", back_populates="history")

    def __repr__(self):
        return f"<AlertHistory(id: {self.alert_history_id}, rule_id: {self.alert_history_alert_rule_id}, read: {self.alert_history_read})>"