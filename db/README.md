# PostgreSQL + pgvector Database

PostgreSQL 16 with pgvector extension for vector similarity search in the Marigold RAG system.

## Setup

```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE DATABASE marigold_rag;
```

## Tables

- **chunks** - Semantic chunks with parent-child relationships (hierarchical)
- **chunks_primitive** - Fixed-size primitive chunks (flat structure)

## Vector Search

IVFFlat index for cosine similarity queries:

```sql
SELECT * FROM chunks
ORDER BY embedding <=> query_vector
LIMIT 5;
```

## Docker

Built automatically via `docker-compose.yml`.
