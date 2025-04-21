import json
from typing import List, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import src.config.env as env
from src.app.models.llm_models import ChatHistory, Source
from src.database.factories.chat_factory import Base, ChatHistoryModel

# Create SQLAlchemy engine and session factory
engine = create_engine(env.DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class DatabaseService:
    """Database service for chat history operations"""

    @staticmethod
    def init_db():
        """Initialize the database and create tables"""
        Base.metadata.create_all(bind=engine)

    @staticmethod
    def get_db():
        """Get a database session"""
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    @classmethod
    def save_chat_to_db(cls, chat: ChatHistory) -> int:
        """Save a chat entry to the database"""
        with DatabaseService.get_db() as db:
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

    @classmethod
    def load_chat_history_from_db(cls) -> List[ChatHistory]:
        """Load all chat history from the database"""
        with DatabaseService.get_db() as db:
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

    @classmethod
    def get_chat_by_id(cls, chat_id: int) -> Optional[ChatHistory]:
        """Get a specific chat by ID"""
        with DatabaseService.get_db() as db:
            chat_model = (
                db.query(ChatHistoryModel)
                .filter(ChatHistoryModel.id == chat_id)
                .first()
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
