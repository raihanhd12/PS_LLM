from typing import List, Dict, Any, Optional, Callable
import logging

from app.schemas.chat import QueryRequest, QueryResponse, SourceResponse
from app.services.chat_service import ChatService
from app.models.chat import ChatHistory

logger = logging.getLogger(__name__)


class ChatController:
    """Controller for chat-related operations"""

    @classmethod
    def process_query(
        cls,
        query_request: QueryRequest,
        stream_callback: Optional[Callable[[str], None]] = None,
    ) -> QueryResponse:
        """Process a user query"""
        logger.info(f"Processing query: {query_request.query}")

        response_data = ChatService.process_query(
            query=query_request.query,
            context_limit=query_request.context_limit,
            selected_doc_id=query_request.document_id,
            llm_provider=query_request.provider,
            stream_callback=stream_callback,
            debug_mode=query_request.debug_mode,
        )

        # Convert sources to source response objects
        sources = [SourceResponse(**source) for source in response_data["sources"]]

        # Create query response
        query_response = QueryResponse(
            id=response_data["id"],
            query=response_data["query"],
            response=response_data["response"],
            sources=sources,
            title=response_data["title"],
            timestamp=response_data["timestamp"],
        )

        return query_response

    @staticmethod
    def get_chat_history() -> List[Dict[str, Any]]:
        """Get all chat history"""
        chat_history = ChatService.get_chat_history()

        # Convert to dict representation
        history_data = []
        for chat in chat_history:
            history_data.append(
                {
                    "id": chat.id,
                    "timestamp": chat.timestamp,
                    "query": chat.query,
                    "response": chat.response,
                    "sources": [s.dict() for s in chat.sources],
                    "title": chat.title,
                }
            )

        return history_data

    @staticmethod
    def get_chat(chat_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific chat by ID"""
        chat = ChatService.get_chat(chat_id)

        if not chat:
            return None

        return {
            "id": chat.id,
            "timestamp": chat.timestamp,
            "query": chat.query,
            "response": chat.response,
            "sources": [s.dict() for s in chat.sources],
            "title": chat.title,
        }
