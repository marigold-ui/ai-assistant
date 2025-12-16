# Marigold RAG ETL Pipeline

Python ETL pipeline for processing Marigold UI documentation into vector embeddings and storing in PostgreSQL.

## Architecture

```
Parsed JSON Documents (from generate_ast.ts)
    ↓
TextChunker (chunker.py)
    ├─ Semantic text chunking based on document sections
    ├─ Token-based splitting with configurable overlap
    └─ Extracts demo files and images metadata
    ↓
EmbeddingProvider (embedder.py)
    ├─ OpenAI API (text-embedding-3-small, 1536 dims)
    └─ Local sentence-transformers (configurable models)
    ↓
DatabaseConnector (db.py)
    ├─ PostgreSQL with pgvector extension
    ├─ Vector similarity search with IVF indexing
    └─ Metadata tracking and statistics
    ↓
Pipeline Orchestration (main.py)
    └─ Coordinates loading, chunking, embedding, and storage
```

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL 12+ with pgvector extension installed
- OpenAI API key (optional, if using OpenAI embeddings)

### Setup
```bash
cd etl/pipeline

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### PostgreSQL Setup
```bash
# Install pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

# Create database
createdb marigold_rag
```

## Configuration

### Environment Variables

```bash
# Database
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=marigold_rag
export DB_USER=postgres
export DB_PASSWORD=your_password

# OpenAI (optional, if using OpenAI embeddings)
export OPENAI_API_KEY=sk-...
```

## Usage

### Run Full Pipeline
```bash
python main.py
```

### With Custom Configuration
```bash
python main.py \
  --embedder sentence-transformers \
  --model sentence-transformers/all-MiniLM-L6-v2 \
  --data-dir ../data \
  --chunk-size 512 \
  --skip button checkbox
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--embedder` | sentence-transformers | Embedding provider: "openai" or "sentence-transformers" |
| `--model` | all-MiniLM-L6-v2 | Model name for embeddings |
| `--data-dir` | ../data | Base data directory containing processed JSON |
| `--chunk-size` | 512 | Maximum tokens per chunk |
| `--skip` | - | Component names to skip |

## Modules

### chunker.py
Semantic text chunking based on document sections.

```python
from chunker import TextChunker, Chunk

chunker = TextChunker(max_chunk_tokens=512, overlap_tokens=50)
chunks = chunker.chunk_documents(documents)

for chunk in chunks:
    print(f"{chunk.component}: {chunk.section_title}")
    print(f"Tokens: {chunk.token_count}")
    print(f"Demos: {chunk.demo_files}")
```

### embedder.py
Flexible embedding provider supporting multiple backends.

```python
from embedder import create_embedder

# OpenAI embeddings (1536 dimensions)
embedder = create_embedder("openai")

# Or local sentence-transformers
embedder = create_embedder(
    "sentence-transformers",
    model="sentence-transformers/all-mpnet-base-v2"
)

embedding = embedder.embed_single("Sample text")
embeddings = embedder.embed(["text1", "text2"])
```

### db.py
PostgreSQL with pgvector for vector similarity search.

```python
from db import DatabaseConnector

db = DatabaseConnector()
db.connect()
db.create_tables()

# Store chunk with embedding
chunk_id = db.store_chunk(
    component="Button",
    section_title="Usage",
    section_path="Button > Usage",
    content="...",
    embedding=[...],
    demo_files=["demo.tsx"],
    token_count=45
)

# Search similar chunks
results = db.search_similar(embedding, limit=5, threshold=0.7)
for chunk_id, component, title, content, score in results:
    print(f"{component} - {title} (similarity: {score:.2f})")

# Get statistics
stats = db.get_stats()
print(f"Total chunks: {stats['total_chunks']}")
```

### main.py
Main orchestration pipeline.

```python
from main import Pipeline

pipeline = Pipeline(
    data_dir="../data",
    embedder_provider="sentence-transformers",
    db_host="localhost"
)

stats = pipeline.run(skip_components=["Button"])
```

## Data Flow

### Input
Parsed JSON files from `generate_ast.ts` located in `etl/data/processed/`:
```json
{
  "name": "Button",
  "description": "...",
  "sections": [
    {
      "title": "Usage",
      "path": "Button > Usage",
      "content": "...",
      "subsections": [...]
    }
  ]
}
```

### Processing
1. **Chunking**: Sections split into 512-token chunks with 50-token overlap
2. **Embedding**: Text embedded using selected provider (1536 or variable dims)
3. **Storage**: Chunks stored with embeddings in PostgreSQL

### Output
PostgreSQL `chunks` table with columns:
- `id`: Primary key
- `component`: Component name
- `section_title`: Section heading
- `section_path`: Full path (e.g., "Button > Usage > States")
- `content`: Chunk text content
- `embedding`: Vector (1536 or variable dimensions)
- `demo_files`: JSON array of demo file paths
- `images`: JSON array of image paths
- `token_count`: Token count for chunk
- `created_at`: Timestamp

## Performance Considerations

### Chunking
- Token estimation uses 4 chars per token approximation
- Overlap ensures context preservation between chunks
- Section boundaries respected when possible

### Embeddings
- **OpenAI**: API calls limited by rate limits, ideal for production
- **Sentence-transformers**: Local models, no API calls, faster batch processing
- Default model (all-MiniLM-L6-v2) produces 384-dimensional embeddings

### Vector Search
- IVF index created with 100 lists for ~500 chunks
- Cosine similarity threshold default 0.7
- Adjust based on embedding model output quality

## Troubleshooting

### Database Connection Error
```
ConnectionError: Failed to connect to database
```
- Check PostgreSQL is running
- Verify connection credentials
- Ensure database exists: `createdb marigold_rag`

### pgvector Extension Missing
```
ERROR: type "vector" does not exist
```
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### Memory Issues with Sentence-Transformers
- Reduce chunk size: `--chunk-size 256`
- Process components separately
- Use lighter model: `distiluse-base-multilingual-cased-v2`

### Slow Vector Search
- Increase IVF lists for larger datasets
- Create additional indexes on frequently searched columns
- Consider approximate nearest neighbor search alternatives

## Next Steps

1. **RAG Query Service**: Build API endpoint for similarity search + LLM context
2. **Multi-Language Support**: Extend to translate docs to other languages
3. **Real-time Updates**: Set up webhook for documentation changes
4. **Monitoring**: Add metrics for embedding quality and search performance
