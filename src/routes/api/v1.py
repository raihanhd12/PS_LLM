from typing import Any, Dict, List

from fastapi import APIRouter

from src.app.controllers.llm_controllers import LLMController
from src.app.schemas.llm_schema import QueryRequest, QueryResponse

# Define router for all endpoints
router = APIRouter()


@router.post("/chat/query", response_model=QueryResponse, tags=["chat"])
async def process_query(query_request: QueryRequest):
    """Process a query and generate a response"""
    # Directly call the service, no try-except needed here
    return await LLMController.process_query(query_request)


@router.get("/chat/history", response_model=List[Dict[str, Any]], tags=["chat"])
async def get_chat_history():
    """Get all chat history"""
    return await LLMController.get_chat_history()


@router.get("/chat/history/{chat_id}", response_model=Dict[str, Any], tags=["chat"])
async def get_chat_by_id(chat_id: int):
    """Get a specific chat by ID"""
    return await LLMController.get_chat_by_id(chat_id)
