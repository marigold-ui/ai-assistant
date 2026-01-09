# Marigold Design System AI Assistant (RAG)

> **🚧 Status: Work in Progress**

## Quick Start

```bash
docker-compose up
```
---

## Overview

This is a **Retrieval-Augmented Generation (RAG)** system for Marigold UI documentation.

**Pipeline:**

```
Marigold MDX Docs → Chunked → Embedded (Ollama) → PostgreSQL+pgvector → MCP-Server → Claude/VS Code
```
---

## Services

| Service    | Port  | Status  | Purpose                            |
| ---------- | ----- | ------- | ---------------------------------- |
| PostgreSQL | 5432  | Running | Vector database (1116 chunks)      |
| pgweb      | 8081  | Running | Database UI                        |
| Ollama     | 11434 | Running | Embedding model (nomic-embed-text) |
| MCP-Server | STDIO | Running | Claude/VS Code integration         |

---