from dotenv import dotenv_values

# Load environment variables from .env file
config = dotenv_values(".env")

# Database configuration
DB_URL = config.get("POSTGRES_URL", "")

# API settings
API_PORT = int(config.get("API_PORT", "8002"))
API_HOST = config.get("API_HOST", "0.0.0.0")
API_KEY = config.get("API_KEY", "")

# LLM Provider settings
DO_API_URL = config.get(
    "DO_API_URL", "https://agent-9d0a55ab65f61611182c-p7e2w.ondigitalocean.app"
)
DO_API_KEY = config.get("DO_API_KEY", "")

# Ollama settings
OLLAMA_API_URL = config.get("OLLAMA_API_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = config.get("OLLAMA_MODEL", "deepseek-r1")

# Embedding API settings
EMBEDDING_API_URL = config.get("API_URL", "http://localhost:8001")
EMBEDDING_API_KEY = config.get("EMBEDDING_KEY", "")
