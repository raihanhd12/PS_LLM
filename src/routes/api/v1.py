import asyncio
import json
import logging
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from src.app.controllers.llm import ChatController
from src.app.schemas.chat import QueryRequest, QueryResponse

# Define router for all endpoints
router = APIRouter()
logger = logging.getLogger(__name__)

# -------------------- Chat Endpoints -------------------- #


@router.post("/chat/query", response_model=QueryResponse, tags=["chat"])
async def process_query(query_request: QueryRequest, request: Request):
    """Process a query and generate a response"""
    try:
        # Check if streaming is requested
        stream_param = request.query_params.get("stream", "false").lower() == "true"

        if stream_param:
            return StreamingResponse(
                stream_response(query_request), media_type="text/event-stream"
            )

        # Process normally if not streaming
        response = ChatController.process_query(query_request)
        return response
    except Exception as e:
        logger.error(f"Error in process_query: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}",
        )


async def stream_response(query_request: QueryRequest):
    """Stream the response back to the client"""

    # Create a queue for the streaming response
    queue = asyncio.Queue()

    # Callback to add new content to the queue
    def stream_callback(content: str):
        asyncio.create_task(queue.put(content))

    # Start processing in background task to not block
    asyncio.create_task(process_query_background(query_request, stream_callback, queue))

    # Stream response back to client
    last_response = ""
    try:
        while True:
            content = await queue.get()

            if content == "__DONE__":
                # Final message with complete response data
                yield f"data: {content}\n\n"
                break

            # Only yield the new part of the response
            new_content = content[len(last_response) :]
            last_response = content

            if new_content:
                # Format as server-sent event
                yield f"data: {json.dumps({'text': new_content})}\n\n"

            # Mark this task as done
            queue.task_done()

    except asyncio.CancelledError:
        logger.info("Streaming response cancelled")
        raise
    except Exception as e:
        logger.error(f"Error in stream_response: {str(e)}")
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


async def process_query_background(
    query_request: QueryRequest, callback, queue: asyncio.Queue
):
    """Process the query in a background task and stream results"""
    try:
        # Process the query with streaming
        response = ChatController.process_query(query_request, callback)

        # Signal that we're done by sending a special message
        await queue.put("__DONE__")

        return response
    except Exception as e:
        logger.error(f"Error in process_query_background: {str(e)}")
        await queue.put(f"Error: {str(e)}")
        await queue.put("__DONE__")


@router.get("/chat/history", response_model=List[Dict[str, Any]], tags=["chat"])
async def get_chat_history():
    """Get all chat history"""
    try:
        history = ChatController.get_chat_history()
        return history
    except Exception as e:
        logger.error(f"Error in get_chat_history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving chat history: {str(e)}",
        )


@router.get("/chat/history/{chat_id}", response_model=Dict[str, Any], tags=["chat"])
async def get_chat(chat_id: int):
    """Get a specific chat by ID"""
    try:
        chat = ChatController.get_chat(chat_id)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chat with ID {chat_id} not found",
            )
        return chat
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving chat: {str(e)}",
        )


# -------------------- Health Check Endpoint -------------------- #


@router.get("/health", tags=["system"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "services": {
            "api": "running",
            "db": "connected",
            "embedding": "available",
        },
    }
