# RAG System Documentation

## Overview

This is a **Retrieval-Augmented Generation (RAG)** system built with FastAPI. It allows users to create projects, upload documents (PDF/TXT), process them into chunks, vectorize them for semantic search, and answer questions using LLM-powered AI.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           RAG System Architecture                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   Client    │───▶│  FastAPI   │───▶│ Controllers │───▶│  Services   │  │
│  │  (Frontend) │    │   Server   │    │             │    │             │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│       │                   │                   │                   │         │
│       │                   │                   │                   ▼         │
│       │                   │                   │    ┌─────────────────────────┤
│       │                   │                   │    │     Data Layer          │
│       │                   │                   │    │  ┌─────────┐ ┌────────┐ │
│       │                   │                   │    │  │ MongoDB │ │ Qdrant │ │
│       │                   │                   │    │  │   (DB)  │ │  (Vec) │ │
│       │                   │                   │    │  └─────────┘ └────────┘ │
│       │                   │                   │    └─────────────────────────┤
│       │                   │                   │                              │
│       ▼                   ▼                   ▼                              │
│  ┌──────────────────────────────────────────────────────────────────────┐    │
│  │                        External Services                             │    │
│  │  ┌─────────────────┐                    ┌────────────────────────┐   │    │
│  │  │   OpenAI API   │                    │    Cohere API          │   │    │
│  │  │ (LLM + Embed)   │                    │ (LLM + Embeddings)    │   │    │
│  │  └─────────────────┘                    └────────────────────────┘   │    │
│  └──────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
RAG/
├── src/
│   ├── main.py                 # FastAPI application entry point
│   ├── helpers/
│   │   └── config.py           # Configuration management (Pydantic)
│   ├── models/
│   │   ├── db_schemes/         # Pydantic models for MongoDB documents
│   │   │   ├── project.py      # Project schema
│   │   │   └── data_chunk.py   # Data chunk schema
│   │   ├── repos/              # Repository pattern implementations
│   │   │   ├── base_data_repo.py    # Abstract base repository
│   │   │   ├── project_repo.py      # Project CRUD operations
│   │   │   └── data_chunk_repo.py   # Data chunk CRUD operations
│   │   └── enums/              # Enumerations
│   │       ├── db_enums.py         # Database collection names
│   │       ├── FileExtEnums.py     # Supported file extensions
│   │       └── ResponseEnum.py     # Response signals
│   ├── controllers/            # Business logic layer
│   │   ├── BaseController.py       # Base controller (file/dir management)
│   │   ├── ProjectController.py   # Project operations
│   │   ├── DataController.py      # File validation & upload
│   │   ├── ProccessController.py  # File processing & chunking
│   │   └── NLPController.py       # Vectorization, search, Q&A
│   ├── routes/                 # API endpoints
│   │   ├── project.py             # Project endpoints
│   │   ├── file.py                # File upload & processing endpoints
│   │   ├── NLP.py                 # NLP endpoints
│   │   └── schema/                # Request/Response schemas
│   │       └── file.py            # File processing request schema
│   └── stores/
│       ├── llm/                     # LLM providers
│       │   ├── LLMInterface.py      # Abstract LLM interface
│       │   ├── LLMEnums.py         # LLM enumerations
│       │   ├── LLMProvideFactory.py # LLM factory
│       │   └── provider/
│       │       ├── open_ai_provider.py # OpenAI implementation
│       │       └── cohere_provider.py  # Cohere implementation
│       └── vectordb/                # Vector database providers
│           ├── vectorDBInterface.py   # Abstract vector DB interface
│           ├── vectorDBEnum.py        # Vector DB enumerations
│           ├── vectorDBProviderFactory.py # Vector DB factory
│           └── provider/
│               └── QdrantDB_provider.py # Qdrant implementation
├── docker/
│   ├── docker-compose.yaml     # Docker Compose for services
│   └── Dockerfile              # FastAPI container definition
├── requirements.txt            # Python dependencies
└── .env.example               # Environment variables template
```

## Data Flow

### 1. Project Creation Flow

```
Client Request
      │
      ▼
 POST /api/v1/project/create
      │
      ▼
ProjectController.create_project()
      │
      ▼
ProjectRepository.create_one()
      │
      ▼
MongoDB (projects collection)
```

### 2. File Upload Flow

```
Client Request (Upload File)
      │
      ▼
 POST /api/v1/data/upload/{proj_id}
      │
      ▼
DataController.Validate_File() ──▶ File type/size validation
      │
      ▼
File saved to: src/assets/files/{proj_id}/{hash_filename}
      │
      ▼
Response: { "Signal": "File uploaded successfully", "File Name": "..." }
```

### 3. File Processing Flow

```
Client Request (Process File)
      │
      ▼
 POST /api/v1/data/process/{project_id}
      │
      ▼
ProcessController.get_file_content()
      │
      ├─▶ PyMuPDFLoader (for PDF)
      └─▶ TextLoader (for TXT)
      │
      ▼
ProcessController.process_file_content()
      │
      ▼
RecursiveCharacterTextSplitter (chunk_size, overlap)
      │
      ▼
ProcessController.prepare_chunks_for_db()
      │
      ▼
DataChunkRepository.create_many()
      │
      ▼
MongoDB (chunks collection)
```

### 4. Vectorization Flow

```
Client Request (Vectorize)
      │
      ▼
 POST /api/v1/nlp/vectorize/{project_id}
      │
      ▼
NLPController.vectorize_project()
      │
      ▼
DataChunkRepository.get_project_chunks() ──▶ Fetch chunks from MongoDB
      │
      ▼
QDrantProvider.create_collection() ──▶ Create "project_{project_id}" collection
      │
      ▼
For each chunk:
   LLMProvider.embed_text() ──▶ Generate embedding
   │
   ▼
QDrantProvider.insert_many() ──▶ Store vectors in Qdrant
      │
      ▼
Response: { "success": true, "chunks_count": N, ... }
```

### 5. Semantic Search Flow

```
Client Request (Search)
      │
      ▼
 POST /api/v1/nlp/search/{project_id}
      │
      ▼
NLPController.get_similar_vectors()
      │
      ▼
LLMProvider.embed_text(query) ──▶ Generate query embedding
      │
      ▼
QDrantProvider.search_by_vector() ──▶ Similarity search
      │
      ▼
Return: [{ "text": "...", "score": 0.95, "metadata": {...} }, ...]
```

### 6. Question Answering Flow (RAG)

```
Client Request (Ask Question)
      │
      ▼
 POST /api/v1/nlp/answer/{project_id}
      │
      ▼
NLPController.answer_user_question()
      │
      ├─▶ Step 1: Generate query embedding
      │        LLMProvider.embed_text(question)
      │
      ├─ Step 2: Retrieve relevant context
      │        QDrantProvider.search_by_vector()
      │
      ├─ Step 3: Build augmented prompt
      │        "Context: {retrieved_docs}\n\nQuestion: {question}"
      │
      ├─ Step 4: Generate answer
      │        LLMProvider.generate_text(augmented_prompt)
      │
      └─ Step 5: Return answer with sources
           │
           ▼
{
  "success": true,
  "question": "...",
  "answer": "...",
  "sources": [{ "text": "...", "score": 0.95 }, ...],
  "sources_count": N
}
```

## API Endpoints

### Project Endpoints (`/api/v1/project`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/create` | Create a new project |
| GET | `/all` | List all projects (paginated) |
| GET | `/{project_id}` | Get project by ID |
| PATCH | `/{project_id}` | Update project |
| DELETE | `/{project_id}` | Delete project |

### Data Endpoints (`/api/v1/data`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload/{proj_id}` | Upload file to project |
| POST | `/process/{project_id}` | Process uploaded file into chunks |
| GET | `/chunks/{project_id}` | Get all chunks for a project |

### NLP Endpoints (`/api/v1/nlp`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/vectorize/{project_id}` | Vectorize project chunks |
| GET | `/vectorization-info/{project_id}` | Check vectorization status |
| POST | `/search/{project_id}` | Semantic search in project |
| POST | `/{project_id}/answer` | Answer question using RAG |

## Technology Stack

| Component | Technology |
|-----------|------------|
| **API Framework** | FastAPI |
| **Database (Metadata)** | MongoDB (via Motor) |
| **Vector Database** | Qdrant |
| **LLM Providers** | OpenAI, Cohere |
| **Document Loaders** | PyMuPDF, LangChain TextLoader |
| **Text Splitting** | LangChain RecursiveCharacterTextSplitter |
| **Container** | Docker, Docker Compose |

## Configuration

The system is configured via environment variables (`.env` file):

### Application Settings
```env
APP_NAME="mini-rag"
APP_VERSION="0.1.0"
FILE_ALLOWED_TYPES=["plain/text", "application/pdf"]
FILE_MAX_SIZE_MB=10
FILE_CHUNK_SIZE=8192
```

### MongoDB Configuration
```env
MONGODB_URI_DOCKER_IMAGE="mongodb://mongo:27017"
MONGODB_DB_NAME="mini_rag_db"
```

### Qdrant Configuration
```env
VECTOR_DB_PATH="./src/assets/qdrant_data"
VECTOR_DISTANCE_METRIC="cosine"
```

### LLM Configuration
```env
GENERATION_BACKEND="Cohere"
EMBEDDINGS_BACKEND="Cohere"
GENERATION_MODEL="command-r"
EMBEDDING_MODEL="embed-multilingual-v3.0"
EMBEDDING_MODEL_SIZE=1024
COHERE_API_KEY="your_cohere_key"
```

## Running the Application

### Using Docker Compose (Recommended)

```bash
# From project root
docker-compose -f docker/docker-compose.yaml up -d

# Or build and run
docker-compose -f docker/docker-compose.yaml up --build
```

Services will be available at:
- **FastAPI**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MongoDB**: localhost:27017
- **Qdrant Dashboard**: http://localhost:6333

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Update .env with your API keys

# Run the server
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Usage Example

### 1. Create a Project

```bash
curl -X POST http://localhost:8000/api/v1/project/create \
  -H "Content-Type: application/json" \
  -d '{"project_id": "my-project", "project_name": "My First Project"}'
```

### 2. Upload a File

```bash
curl -X POST http://localhost:8000/api/v1/data/upload/my-project \
  -F "file=@document.pdf"
```

### 3. Process the File

```bash
curl -X POST http://localhost:8000/api/v1/data/process/my-project \
  -H "Content-Type: application/json" \
  -d '{"file_name": "abc123.pdf", "chunk_size": 512, "overlap_size": 200}'
```

### 4. Vectorize the Project

```bash
curl -X POST http://localhost:8000/api/v1/nlp/vectorize/my-project \
  -H "Content-Type: application/json" \
  -d '{"do_reset": false}'
```

### 5. Ask a Question

```bash
curl -X POST http://localhost:8000/api/v1/nlp/answer/my-project \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?", "limit": 5}'
```

## Extending the System

### Adding New LLM Providers

1. Create a new provider in `src/stores/llm/provider/`
2. Implement the `LLMFactoryInterface`
3. Register in `LLMProvideFactory`

### Adding New Vector Databases

1. Create a new provider in `src/stores/vectordb/provider/`
2. Implement the `VectorDBInterface`
3. Register in `VectorDBProviderFactory`

### Adding New Document Types

Update `ProcessController.loader()` in `src/controllers/ProccessController.py` to handle new file types using LangChain loaders.