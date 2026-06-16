from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
import datetime
from database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, index=True)
    chat_id = Column(String, index=True)
    chat_title = Column(String)
    user_hash = Column(String, index=True)
    text = Column(Text)
    timestamp = Column(DateTime)
    lang = Column(String)
    risk_score = Column(Float, default=0.0)
    metadata_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="open", index=True)
    user_hash = Column(String, index=True)
    risk_score = Column(Float)
    initial_message_id = Column(Integer, ForeignKey("messages.id"))
    summary = Column(Text)
    agent_analysis = Column(JSON)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, index=True)
    user_id = Column(String)
    details = Column(JSON)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
