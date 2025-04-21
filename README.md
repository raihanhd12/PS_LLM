# Document AI Assistant API

A service-oriented backend for the Document AI Assistant application. This service provides APIs for document management, embedding search, and AI-powered question answering based on document content.

## Features

- Document upload and management
- Semantic search using embeddings
- AI-powered question answering using multiple LLM providers:
  - Digital Ocean AI API
  - Ollama (local model deployment)
- Chat history management
- Streaming responses for real-time feedback

## Architecture

This project follows a service-oriented architecture with clear separation of concerns:

- **API Layer**: FastAPI endpoints for client interaction
- **Controller Layer**: Request handling and response formatting
- **Service Layer**: Core business logic implementation
- **Data Layer**: PostgreSQL database for persistent storage

The system is designed with the following key components:

### 1. Embedding Service Proxy

Instead of reimplementing document management functionality, this service acts as a proxy to the existing embedding service. This eliminates duplication and ensures all document operations are handled by the specialized embedding service.

### 2. LLM Service

The AI service component provides a clean interface to multiple LLM providers:

- Digital Ocean AI API integration
- Ollama local model integration
- Streaming response support
- Context handling and prompt formatting

### 3. Chat History Management

All interactions are stored in PostgreSQL for:

- Persistent chat history across sessions
- Fast retrieval of previous conversations
- Analytics possibilities

### 4. Database Migration

Alembic is integrated for seamless database schema management and migration.

## Setup and Installation

### Prerequisites

- Python 3.8+
- PostgreSQL database
- Embedding API service running (configured via env variables)
- Digital Ocean API key (optional)
- Ollama installation (optional)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/document-ai-assistant.git
cd document-ai-assistant
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file with your configuration:

```
# Embedding API
API_URL=http://localhost:8001
API_KEY=your_embedding_api_key

# LLM Providers
DO_API_URL=https://agent-url.ondigitalocean.app
DO_API_KEY=your_digital_ocean_api_key
OLLAMA_API_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=deepseek-r1

# PostgreSQL Database
POSTGRES_URL=postgresql://username:password@localhost:5432/doc_assistant
API_PORT=8002
API_HOST=0.0.0.0
```

5. Set up alembic for database migrations:

```bash
# Install alembic if not already installed
pip install alembic

# Initialize alembic
alembic init migrations

# Edit migrations/env.py to import your models
# Add these lines to migrations/env.py:
from app.db.session import Base
from app.core.config import DB_URL
target_metadata = Base.metadata
config.set_main_option("sqlalchemy.url", DB_URL)

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

6. Start the service:

```bash
python main.py
```

The API will be available at `http://localhost:8002` with documentation at `http://localhost:8002/docs`.

## API Usage Guide

### 1. Chat Query Endpoint

Use this endpoint to ask questions about your documents:

```
POST /api/v1/chat/query
```

**Request body**:

```json
{
  "query": "What are the main features of this application?",
  "context_limit": 3,
  "document_id": "all",
  "provider": "Digital Ocean",
  "debug_mode": false
}
```

Parameters:

- `query`: Your question text
- `context_limit`: Number of relevant document chunks to use (1-10)
- `document_id`: Filter by document ID or use "all"
- `provider`: LLM provider ("Digital Ocean" or "Ollama")
- `debug_mode`: Enable detailed logging

**Response**:

```json
{
  "id": 1,
  "query": "What are the main features of this application?",
  "response": "The main features of this application include...",
  "sources": [
    {
      "id": "doc1",
      "score": 0.89,
      "metadata": {
        "filename": "README.md"
      },
      "text": "Feature text snippet..."
    }
  ],
  "title": "Application Features",
  "timestamp": "2025-04-21 06:55:00"
}
```

### 2. Streaming Responses

For real-time streaming responses, add the `stream=true` query parameter:

```
POST /api/v1/chat/query?stream=true
```

This returns a Server-Sent Event stream with partial response chunks.

### 3. Chat History

Retrieve all chat history:

```
GET /api/v1/chat/history
```

Get a specific chat by ID:

```
GET /api/v1/chat/history/{chat_id}
```

### 4. Health Check

Check API status:

```
GET /api/v1/health
```

## Example Usage with curl

```bash
# Simple query
curl -X POST http://localhost:8002/api/v1/chat/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What features does this API provide?", "provider": "Digital Ocean"}'

# Streaming response
curl -X POST http://localhost:8002/api/v1/chat/query?stream=true \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain the architecture", "provider": "Ollama"}'
```

## Project Structure

```
app/
├── api/v1/ - FastAPI endpoint definitions
├── controllers/ - Request handling and response formatting
├── services/ - Core business logic
├── models/ - Data models
├── schemas/ - Request/response schemas
├── db/ - Database interactions
├── core/ - Configuration and constants
└── utils/ - Helper functions
```

## License

[MIT License](LICENSE)

## Credits

This project was developed with FastAPI and leverages various AI models for document processing and question answering.
