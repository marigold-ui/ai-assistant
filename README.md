# Marigold AI Assistant

A RAG system for semantic search and question answering over Marigold UI Component documentation using vector embeddings and PostgreSQL.

## Overview

This project implements a complete pipeline for converting Marigold UI Component documentation into a queryable knowledge base:

1. **Parse** - Convert MDX files to structured JSON with AST builder
2. **Chunk** - Split documents into semantic sections (hierarchical + flat)
3. **Embed** - Generate vector embeddings using Ollama
4. **Store** - Index embeddings in PostgreSQL with pgvector
5. **Query** - Semantic search via MCP server for Claude/VS Code integration

## Architecture

Data flows through two phases:

**Phase 1: Build (ETL)**

- Fetch Marigold documentation from GitHub
- Parse MDX to structured JSON with document hierarchy
- Split into semantic chunks (with parent relationships) and flat chunks
- Generate embeddings using Ollama
- Store in PostgreSQL with pgvector indexes

**Phase 2: Runtime (Query)**

- User query embedded by Ollama
- Vector similarity search finds matching chunks
- Parent documents retrieved for context
- Results formatted and returned to client

See [diagrams/architecture.png](diagrams/architecture.png) for detailed sequence diagram.

## Directory Structure

Each directory contains detailed documentation:

| Directory       | Purpose                                                            |
| --------------- | ------------------------------------------------------------------ |
| `etl/parser/`   | TypeScript AST parser for MDX documentation                        |
| `etl/pipeline/` | Python Jupyter notebooks for chunking, embedding, database storage |
| `etl/data/`     | Raw docs, processed JSON, generated embeddings                     |
| `mcp-server/`   | MCP service for semantic search queries                            |
| `db/`           | PostgreSQL + pgvector database service                             |
| `ollama/`       | Embedding model service (nomic-embed-text)                         |
| `diagrams/`     | Architecture and flow diagrams                                     |

See each directory's README.md for details.

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Git

### Quick Start (Complete Setup)

1. **Set up Python environment**

```bash
# Clone repository
git clone https://github.com/marigold-ui/ai-assistant.git
cd ai-assistant

# Create virtual environment at project root
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
```

2. **Parse documentation**

```bash
cd etl/parser
pnpm install
pnpm run dev  # Downloads and parses Marigold MDX files to JSON
```

3. **Start services**

```bash
# From project root
docker-compose up marigold-ollama marigold-postgres --build -d
```

4. **Run ETL pipeline** 

```bash
cd etl/pipeline
jupyter notebook
# Execute notebooks in order:
# - 01_chunker.ipynb (chunks documentation)
# - 02_embedder.ipynb (generates embeddings)
# - 03_database.ipynb (stores in PostgreSQL)
```

5. **Start MCP server**

```bash
# Recommended
docker compose up marigold-mcp --build -d

# Or manually
cd mcp-server
python server.py
```

Services available at:

- PostgreSQL: `localhost:5432`
- pgweb (Database UI): `http://localhost:8081`
- Ollama: `localhost:11434`

### VS Code Integration

The MCP server works with any MCP-compatible client. Example seup for VS Code:

**VS Code Agent**

1. Press `Ctrl+Shift+P` and search for "MCP: Add Server"

2. Select "stdio" as the connection type

3. Enter the server configuration (JSON format):

```json
{
  "servers": {
    "marigold-mcp": {
      "type": "stdio",
      "command": "docker",
      "args": ["exec", "-i", "marigold-mcp", "python3", "server.py"],
      "cwd": "/path/to/ai-assistant/mcp-server"
    }
  }
}
```

4. The tools will appear in VS Code Agent:

   - `marigold_documentation_lookup` - Semantic search with hierarchical context
   - `marigold_documentation_lookup_primitive` - Flat structure baseline

5. Start using in chat:
   - For example, ask questions like:
     - "How do I create a Button with Marigold?"
     -

## Services

### PostgreSQL + pgvector (db/)

Vector database for storing embeddings.

- Stores semantic and primitive chunks
- 768-dimensional vectors
- Runs on port 5432

See [db/README.md](db/README.md) for details.

### Ollama (ollama/)

Local embedding service using nomic-embed-text model.

- Generates embeddings
- Runs on port 11434

See [ollama/README.md](ollama/README.md) for details.

### ETL Pipeline (etl/)

Data processing layer with three main stages:

**Parser** - Extract documentation

- Fetches Marigold UI MDX from GitHub
- Converts to structured JSON with AST
- Preserves heading hierarchy and demo references

**Chunking** - Split and organize content

- Semantic chunking: respects document sections, maintains hierarchy
- Primitive chunking: fixed 500-token chunks (baseline comparison)
- Both preserve demo code and image references

**Embedding & Storage** - Generate vectors and index

- Generates embeddings for all chunks
- Stores in PostgreSQL with pgvector indexing
- Creates IVFFlat indexes for fast similarity search

See [etl/pipeline/README.md](etl/pipeline/README.md) for details.

### MCP Server (mcp-server/)

Model Context Protocol server providing two semantic search tools:

- **marigold_documentation_lookup** - Semantic search with hierarchical context
- **marigold_documentation_lookup_primitive** - Flat structure baseline

Integrates with Claude, VS Code, and other MCP-compatible clients.

See [mcp-server/README.md](mcp-server/README.md) for details.

## Configuration

### Environment Variables (.env)

```bash
# ==============================================
# PostgreSQL Database
# ==============================================
DB_HOST=marigold-postgres
DB_PORT=5432
DB_NAME=marigold_rag
DB_USER=postgres
DB_PASSWORD=postgres

# ==============================================
# pgweb (Database UI)
# ==============================================
PGWEB_PORT=8081

# ==============================================
# Ollama (Embedding Model)
# ==============================================
OLLAMA_KEEP_ALIVE=10m
OLLAMA_URL="http://marigold-ollama:11434/api/embed"
OLLAMA_MODEL=nomic-embed-text
```

### Chunking Parameters

Located in pipeline notebooks:

```python
# 01_chunker.ipynb
max_chunk_tokens = 500        # Maximum tokens per chunk
overlap_tokens = 50           # Overlap between chunks
```

### Vector Search

Located in mcp-server/db.py:

```python
# Search parameters
limit = 5                      # Results to return
```

### Comparing Approaches

Two chunking strategies available for evaluation:

- **Semantic (Recommended)**: Respects document structure, maintains hierarchy
- **Primitive (Baseline)**: Fixed tokens, shows limitations of naive chunking

Query same question with both tools to compare results.

## Troubleshooting

**Module not found errors**

- Ensure .venv is activated: `source .venv/bin/activate`
- Install requirements: `pip install -r requirements.txt`

**Database connection failed**

- Check PostgreSQL is running: `docker-compose up marigold-postgres`
- Verify credentials in .env match docker-compose.yml

**Ollama connection failed**

- Start Ollama: `docker-compose up marigold-ollama`
- Verify model: `ollama list` (should include nomic-embed-text)

## License

MIT License. See [LICENSE](LICENSE) for details.