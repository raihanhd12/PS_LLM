import json
import logging
from typing import Any, Dict, List, Optional

from fastapi.responses import StreamingResponse

from src.app.schemas.llm_schema import QueryRequest, QueryResponse, SourceResponse
from src.app.services.database_services import DatabaseService
from src.app.services.llm_services import LLMService

logger = logging.getLogger(__name__)


class LLMController:
    """Controller for chat-related operations"""

    @staticmethod
    def get_chat_history() -> List[Dict[str, Any]]:
        """Get all chat history"""
        chat_history = DatabaseService.load_chat_history_from_db()

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
    def get_chat_by_id(chat_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific chat by ID"""
        chat = DatabaseService.get_chat_by_id(chat_id)

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

    @classmethod
    async def process_query(cls, query_request: QueryRequest, stream_callback=None):
        """Process a user query"""
        logger.info(f"Processing query: {query_request.query}")

        # Proses query dan kembalikan hasilnya
        response_data = LLMService.process_query(
            query=query_request.query,
            context_limit=query_request.context_limit,
            selected_doc_id=query_request.document_id,
            llm_provider=query_request.provider,
            stream_callback=stream_callback,
            debug_mode=query_request.debug_mode,
        )

        # Konversi hasil
        sources = [SourceResponse(**source) for source in response_data["sources"]]
        return QueryResponse(
            id=response_data["id"],
            query=response_data["query"],
            response=response_data["response"],
            sources=sources,
            title=response_data["title"],
            timestamp=response_data["timestamp"],
        )

    @classmethod
    async def process_streaming_query(cls, query_request: QueryRequest):
        """Process a query with streaming response"""

        async def event_generator():
            buffer = ""

            # Define callback to handle streaming chunks
            def stream_callback(content):
                nonlocal buffer
                new_content = content[len(buffer) :]
                buffer = content
                return new_content

            # Start event
            yield 'data: {"status": "started"}\n\n'

            # Process with streaming
            response_data = LLMService.process_query(
                query=query_request.query,
                context_limit=query_request.context_limit,
                selected_doc_id=query_request.document_id,
                llm_provider=query_request.provider,
                stream_callback=stream_callback,
                debug_mode=query_request.debug_mode,
            )

            # Send complete data
            yield f"data: {json.dumps({'status': 'complete', 'data': response_data})}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")
