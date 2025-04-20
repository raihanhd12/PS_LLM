from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request schema for querying documents"""

    query: str
    context_limit: int = Field(3, ge=1, le=10)
    document_id: str = "all"
    provider: str = "Digital Ocean"
    debug_mode: bool = False


class SourceResponse(BaseModel):
    """Response schema for document sources"""

    id: str
    score: float
    metadata: Dict[str, Any] = {}
    text: str


class QueryResponse(BaseModel):
    """Response schema for query results"""

    id: Optional[int] = None
    query: str
    response: str
    sources: List[SourceResponse]
    title: str
    timestamp: str
