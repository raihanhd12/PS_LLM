from typing import Dict, List
import logging

from app.schemas.document import (
    DocumentBase,
    SearchRequest,
    SearchResponse,
    SearchResult,
)
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class DocumentController:
    """Controller for document-related operations through embedding API"""

    @staticmethod
    def get_documents() -> List[Dict]:
        """Get all documents by proxying to embedding API"""
        result = EmbeddingService.proxy_get_request("/api/v1/documents")
        return result.get("documents", [])

    @staticmethod
    def upload_document(file_content: bytes, filename: str, content_type: str) -> Dict:
        """Upload a document by proxying to embedding API"""
        # Configure files for upload
        files = {"files": (filename, file_content, content_type)}

        # Upload file
        result = EmbeddingService.proxy_file_upload("/api/v1/upload/batch", files)

        if not result.get("successful"):
            return {
                "success": False,
                "error": "Upload failed or no files were processed",
            }

        # Get file ID and trigger embedding
        file_id = result["successful"][0]["file_id"]

        embed_result = EmbeddingService.proxy_post_request(
            "/api/v1/embedding/batch", {"file_ids": [file_id]}
        )

        if "error" in embed_result:
            return {
                "success": True,
                "file_id": file_id,
                "warning": "File uploaded but embedding failed. File may not be searchable.",
            }

        return {"success": True, "file_id": file_id}

    @staticmethod
    def search_documents(search_request: SearchRequest) -> SearchResponse:
        """Search documents through embedding API"""
        results = EmbeddingService.search_embeddings(
            search_request.query, search_request.limit, search_request.document_id
        )

        search_results = [SearchResult(**result) for result in results]
        return SearchResponse(results=search_results)
