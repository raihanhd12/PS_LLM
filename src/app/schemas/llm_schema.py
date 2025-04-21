from typing import List

from pydantic import BaseModel, Field

from src.app.services.llm_services import LLMProvider


class SourceResponse(BaseModel):
    """Source document information response schema"""

    id: str
    score: float
    metadata: dict = {}
    text: str


class QueryRequest(BaseModel):
    """Chat query request schema"""

    query: str
    context_limit: int = Field(default=3, ge=1, le=10)
    document_id: str = "all"  # "all" or specific document ID
    provider: LLMProvider = LLMProvider.DIGITAL_OCEAN
    debug_mode: bool = False


class QueryResponse(BaseModel):
    """Chat query response schema"""

    id: int
    query: str
    response: str
    sources: List[SourceResponse] = []
    title: str
    timestamp: str
