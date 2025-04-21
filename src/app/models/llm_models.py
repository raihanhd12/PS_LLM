from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

class Source(BaseModel):
    """Document source information"""

    id: str
    score: float
    metadata: Dict[str, Any] = {}
    text: str

class ChatHistory(BaseModel):
    """Chat history entry model"""

    id: Optional[int] = None
    timestamp: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    query: str
    response: str
    sources: List[Source] = []
    title: str = "Untitled Chat"
