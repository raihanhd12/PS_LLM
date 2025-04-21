import json
from contextlib import contextmanager
from typing import List, Optional

from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import src.config.env as env
from src.app.models.llm import ChatHistory, Source

# Create SQLAlchemy engine and session factory
engine = create_engine(env.DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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


def init_db():
    """Initialize database and create tables"""
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db():
    """Get a database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_chat_to_db(chat: ChatHistory) -> int:
    """Save a chat entry to the database"""
    with get_db() as db:
        # Convert sources to JSON string
        sources_json = json.dumps([s.dict() for s in chat.sources])

        # Create DB model from chat object
        chat_model = ChatHistoryModel(
            timestamp=chat.timestamp,
            query=chat.query,
            response=chat.response,
            sources=sources_json,
            title=chat.title,
        )

        # Add to DB and commit
        db.add(chat_model)
        db.commit()
        db.refresh(chat_model)

        return chat_model.id


def load_chat_history_from_db() -> List[ChatHistory]:
    """Load all chat history from the database"""
    with get_db() as db:
        chat_models = db.query(ChatHistoryModel).all()

        # Convert DB models to ChatHistory objects
        chat_history = []
        for model in chat_models:
            # Parse sources from JSON string
            sources_json = json.loads(model.sources) if model.sources else []
            sources = [Source(**source) for source in sources_json]

            # Create ChatHistory object
            chat_history.append(
                ChatHistory(
                    id=model.id,
                    timestamp=model.timestamp,
                    query=model.query,
                    response=model.response,
                    sources=sources,
                    title=model.title,
                )
            )

        return chat_history


def get_chat_by_id(chat_id: int) -> Optional[ChatHistory]:
    """Get a specific chat by ID"""
    with get_db() as db:
        chat_model = (
            db.query(ChatHistoryModel).filter(ChatHistoryModel.id == chat_id).first()
        )

        if not chat_model:
            return None

        # Parse sources from JSON string
        sources_json = json.loads(chat_model.sources) if chat_model.sources else []
        sources = [Source(**source) for source in sources_json]

        # Create ChatHistory object
        return ChatHistory(
            id=chat_model.id,
            timestamp=chat_model.timestamp,
            query=chat_model.query,
            response=chat_model.response,
            sources=sources,
            title=chat_model.title,
        )
