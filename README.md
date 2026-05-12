# RAG System

Retrieval-Augmented Generation API

## Requirements

- Python 3.14+
- Docker & Docker Compose

## Installation

```bash
# Clone and navigate to project
cd RAG

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
```

## Configuration

Edit `.env` file and add your API keys:

```env
# MongoDB
MONGODB_URI_DOCKER_IMAGE="mongodb://mongo:27017"
MONGODB_DB_NAME="mini_rag_db"

# Qdrant (optional - uses local storage by default)
QDRANT_API_URL=""
QDRANT_API_KEY=""

# LLM Providers
GENERATION_BACKEND="Cohere"
EMBEDDINGS_BACKEND="Cohere"
GENERATION_MODEL="command-r"
EMBEDDING_MODEL="embed-multilingual-v3.0"
EMBEDDING_MODEL_SIZE=1024
COHERE_API_KEY="your_cohere_api_key"
```

## Running

### Using Docker (Recommended)

```bash
docker-compose -f docker/docker-compose.yaml up --build
```

### Local Development

```bash
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Services

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| Docs | http://localhost:8000/docs |
| Qdrant | http://localhost:6333 |

## API Endpoints

- **Project**: `/api/v1/project`
- **File Upload**: `/api/v1/data/upload/{proj_id}`
- **Process**: `/api/v1/data/process/{project_id}`
- **Vectorize**: `/api/v1/nlp/vectorize/{project_id}`
- **Search**: `/api/v1/nlp/search/{project_id}`
- **Answer**: `/api/v1/nlp/answer/{project_id}`