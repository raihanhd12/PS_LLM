from typing import Any, Callable, Dict, List, Optional

from app.db.session import get_chat_by_id, load_chat_history_from_db, save_chat_to_db
from app.models.chat import ChatHistory, Source
from app.services.ai_service import AIService, LLMProvider
from app.services.embedding_service import EmbeddingService


class ChatService:
    """Service for chat operations"""

    @classmethod
    def process_query(
        cls,
        query: str,
        context_limit: int = 3,
        selected_doc_id: str = "all",
        llm_provider: str = "Digital Ocean",
        stream_callback: Optional[Callable[[str], None]] = None,
        debug_mode: bool = False,
    ) -> Dict[str, Any]:
        """Process a query and generate a response"""
        # Set provider enum from string
        provider = (
            LLMProvider.DIGITAL_OCEAN
            if llm_provider == "Digital Ocean"
            else LLMProvider.OLLAMA
        )

        # Retrieve relevant documents
        sources, context = EmbeddingService.retrieve_context(
            query, context_limit, selected_doc_id
        )

        # Generate response
        response = AIService.generate_response(
            context, query, provider, stream_callback, debug_mode
        )

        # Generate title
        chat_title = AIService.generate_chat_title(query, response, provider)

        # Create chat history object
        chat = ChatHistory(
            query=query,
            response=response,
            sources=[Source(**source) for source in sources],
            title=chat_title,
        )

        # Save to database
        chat_id = save_chat_to_db(chat)

        # Return the complete response data
        return {
            "id": chat_id,
            "query": query,
            "response": response,
            "sources": sources,
            "title": chat_title,
            "timestamp": chat.timestamp,
        }

    @staticmethod
    def get_chat_history() -> List[ChatHistory]:
        """Get all chat history"""
        return load_chat_history_from_db()

    @staticmethod
    def get_chat(chat_id: int) -> Optional[ChatHistory]:
        """Get a specific chat by ID"""
        return get_chat_by_id(chat_id)
