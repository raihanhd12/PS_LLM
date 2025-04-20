import logging
from typing import Dict, List, Optional, Tuple

import requests

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Proxy service for embedding API operations"""

    @staticmethod
    def setup_headers() -> Dict[str, str]:
        """Set up headers for API requests"""
        headers = {"Content-Type": "application/json"}
        if settings.EMBEDDING_API_KEY:
            headers["X-API-Key"] = settings.EMBEDDING_API_KEY
        return headers

    @classmethod
    def proxy_get_request(cls, endpoint: str) -> Dict:
        """Forward GET request to embedding API"""
        headers = cls.setup_headers()
        try:
            response = requests.get(
                f"{settings.EMBEDDING_API_URL}{endpoint}", headers=headers
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error in proxy GET request to {endpoint}: {e}")
            return {"error": str(e)}

    @classmethod
    def proxy_post_request(cls, endpoint: str, json_data: Dict) -> Dict:
        """Forward POST request with JSON to embedding API"""
        headers = cls.setup_headers()
        try:
            response = requests.post(
                f"{settings.EMBEDDING_API_URL}{endpoint}",
                headers=headers,
                json=json_data,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error in proxy POST request to {endpoint}: {e}")
            return {"error": str(e)}

    @classmethod
    def proxy_file_upload(
        cls, endpoint: str, files: Dict, extra_data: Optional[Dict] = None
    ) -> Dict:
        """Forward file upload to embedding API"""
        headers = {}
        if settings.EMBEDDING_API_KEY:
            headers["X-API-Key"] = settings.EMBEDDING_API_KEY

        try:
            response = requests.post(
                f"{settings.EMBEDDING_API_URL}{endpoint}",
                headers=headers,
                files=files,
                data=extra_data,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error in proxy file upload to {endpoint}: {e}")
            return {"error": str(e)}

    @classmethod
    def search_embeddings(
        cls, query: str, limit: int = 3, file_id: Optional[str] = None
    ) -> List[Dict]:
        """Search for relevant documents using the embedding API"""
        filter_metadata = {"active": True}
        if file_id and file_id != "all":
            filter_metadata["file_id"] = file_id

        search_payload = {
            "query": query,
            "limit": limit,
            "filter_metadata": filter_metadata,
        }

        try:
            result = cls.proxy_post_request("/api/v1/search", search_payload)
            return result.get("results", [])
        except Exception as e:
            logger.error(f"Error searching embeddings: {e}")
            return []

    @classmethod
    def retrieve_context(
        cls, query: str, context_limit: int, selected_doc_id: str
    ) -> Tuple[List[Dict], str]:
        """Retrieve relevant documents and create context string"""
        # Get search results
        search_results = cls.search_embeddings(query, context_limit, selected_doc_id)

        if not search_results:
            return [], ""

        # Process search results
        context_texts = []
        sources = []

        for result in search_results:
            text = result.get("text", "")
            if text:
                context_texts.append(text)

            source_info = {
                "id": result.get("id"),
                "score": result.get("score"),
                "metadata": result.get("metadata", {}),
                "text": text,
            }
            sources.append(source_info)

        # Create context string
        context = "\n\n".join(context_texts)
        return sources, context
