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
DO_CHATBOT_ID=your_chatbot_id
OLLAMA_API_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=deepseek-r1

# PostgreSQL Database
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=doc_assistant
```

5. Set up the database:

```bash
# Create PostgreSQL database
createdb doc_assistant

# Run database migrations
alembic upgrade head
```

### Running the Service

Start the service with:

```bash
python main.py
```

The API will be available at `http://localhost:8000`.
API documentation is available at `http://localhost:8000/docs`.

## API Endpoints

### Document Management

- `GET /api/v1/documents/` - Get all documents
- `POST /api/v1/documents/upload` - Upload a document
- `POST /api/v1/documents/search` - Search for relevant document chunks

### Chat

- `POST /api/v1/chat/query` - Process a query and generate a response
- `GET /api/v1/chat/history` - Get all chat history
- `GET /api/v1/chat/history/{chat_id}` - Get a specific chat by ID

## Development

### Project Structure

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

### Testing

To run tests:

```bash
pytest
```

## License

[MIT License](LICENSE)

## Credits

This project was developed with FastAPI and leverages various AI models for document processing and question answering.
