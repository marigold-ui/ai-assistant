# Marigold RAG ETL Pipeline

Python ETL pipeline for processing Marigold UI documentation into vector embeddings and storing in PostgreSQL.

## Architecture

```
Parsed JSON Documents
    ↓
TextChunker
    ↓
EmbeddingProvider (Local Ollama instance)
    ↓
PostgreSQL + pgvector (vector similarity search)
```

## Setup

```bash
cd /home/sinan/GitHub/reservix/ai-assistant

# Create .venv in project root
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Environment variables (`.env`):

```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=marigold_rag
DB_USER=postgres
DB_PASSWORD=postgres
```

## Notebooks

### 01_chunker.ipynb

Semantic chunking based on document sections with parent-child relationships.

- Max tokens: 500 (configurable)
- Output: `data/chunks/chunks.json`

### 01_chunker_primitive.ipynb

Fixed-size primitive chunking for baseline comparison.

- Fixed 500-token chunks
- Output: `data/chunks/chunks_primitive.json`

### 02_embedder.ipynb

Generate embeddings using local Ollama Instance with nomic-embed-text

- Embedding dimensions: 768
- Output: `data/chunks/chunks_embedded.json`

### 03_database.ipynb

Load embeddings and store in local PostgreSQL instance with pgvector.

- Creates schema with indexes
- Supports hierarchical queries
- Demo code stored as JSONB

## Data Flow

**Input** → Parsed JSON (from AST parser)  
**Processing** → Chunking → Embedding → Storage  
**Output** → PostgreSQL `chunks` table with vectors
