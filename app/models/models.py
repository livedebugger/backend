from datetime import datetime
from app.db.database import Base
from sqlalchemy import (JSON, Column, DateTime, ForeignKey, Integer, String,
                        Text)
from sqlalchemy.orm import relationship

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True, index=True)
    created_by = Column(String)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    logs = relationship("LogEntry", back_populates="session")



class LogEntry(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    text = Column(Text)
    session = relationship("Session", back_populates="logs")


class ChatMessage(Base):
    __tablename__ = "chat"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    sender = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    message = Column(Text)

class Suggestion(Base):
    __tablename__ = "suggestions"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    suggestion = Column(Text)

class FeedEvent(Base):
    __tablename__ = "feed"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    type = Column(String)  # log, suggestion, chat
    content = Column(JSON)
