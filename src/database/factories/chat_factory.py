from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

# Base class for SQLAlchemy models
Base = declarative_base()

# Define SQLAlchemy model for chat history
class ChatHistoryModel(Base):
    """SQLAlchemy model for chat history table"""

    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(String, nullable=False)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    sources = Column(Text, nullable=False)  # JSON string of sources
    title = Column(String, nullable=False)
