from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, status
import logging

from app.schemas.document import DocumentBase, SearchRequest, SearchResponse
from app.schemas.chat import DocumentUploadResponse, DocumentListResponse
from app.controllers.document_controller import DocumentController

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=DocumentListResponse)
async def get_documents():
    """Get all documents"""
    documents = DocumentController.get_documents()
    return DocumentListResponse(documents=documents)


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload a document for processing"""
    try:
        file_content = await file.read()
        result = DocumentController.upload_document(
            file_content=file_content,
            filename=file.filename,
            content_type=file.content_type,
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Unknown error during document upload"),
            )

        response = DocumentUploadResponse(success=True, file_id=result.get("file_id"))

        if "warning" in result:
            response.warning = result["warning"]

        return response

    except Exception as e:
        logger.error(f"Error in upload_document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}",
        )


@router.post("/search", response_model=SearchResponse)
async def search_documents(search_request: SearchRequest):
    """Search for relevant documents"""
    try:
        results = DocumentController.search_documents(search_request)
        return results
    except Exception as e:
        logger.error(f"Error in search_documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching documents: {str(e)}",
        )
