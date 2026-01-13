# Marigold MCP Server

Model Context Protocol server that provides semantic search over Marigold UI documentation stored in PostgreSQL with vector embeddings.

## How It Works

1. User sends a query via MCP
2. Query is embedded using Ollama (`nomic-embed-text`)
3. Vector similarity search finds matching chunks in PostgreSQL
4. Formatted response returned to client

## Available Tools

Two search tools to compare RAG approaches:

**marigold_documentation_lookup**

- Semantic chunks with hierarchical relationships
- Recommended approach - better context and relevance

**marigold_documentation_lookup_primitive**

- Fixed-size flat chunks without hierarchy
- Baseline for comparison - demonstrates limitations of naive chunking

Both accept:

- `query` (str): Question about Marigold components
- `limit` (int, 1-20): Number of results (default: 5)
