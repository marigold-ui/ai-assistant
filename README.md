# Marigold Design System AI Assistant (RAG)

> **🚧 Status: Work in Progress**

## Objective
This project aims to build a context-aware AI assistant for the **Marigold Design System**. Unlike standard coding assistants, this tool utilizes **Retrieval-Augmented Generation (RAG)** grounded in the official Marigold documentation.

The core goal is to solve the "context loss" problem in technical documentation by implementing a **Parent Document Retrieval** strategy. This ensures that the Large Language Model (LLM) understands the full context of complex components (like Props Tables or Guidelines) instead of retrieving fragmented text chunks.

## Architecture

The project follows a hybrid pipeline approach to leverage the best tools for each task:

1.  **Ingestion & Parsing (Node.js / TypeScript):**
    * Uses `unified`, `remark-mdx`, and `remark-gfm` to generate an **Abstract Syntax Tree (AST)** from the documentation.
    * *Why Node.js?* Because the Marigold documentation is written in MDX (React + Markdown). Node.js parsers offer superior fidelity for MDX syntax compared to Python-based parsers.

2.  **Analysis & Vectorization (Python / Jupyter):**
    * Processes the AST JSON data.
    * Implements the chunking strategy (splitting by logical nodes, not characters).
    * Handles embedding generation and vector database storage.

3.  **Inference (MCP Server):**
    *  A Model Context Protocol (MCP) server that connects the vector database to IDEs (like VS Code or Cursor).
