# Marigold MCP Server

Python-based Model Context Protocol (MCP) server for semantic search over Marigold component documentation.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running

```bash
python server.py
```

## Tools

### search_chunks

Search for documentation chunks similar to a query using semantic similarity.

**Arguments:**

- `query` (string, required): The search query
- `limit` (number, optional): Max results (default: 5)
- `threshold` (number, optional): Min similarity score 0-1 (default: 0.5)

**Example:**

```json
{
  "query": "How do I create a button with custom styling?",
  "limit": 3,
  "threshold": 0.6
}
```

### get_chunk

Get a specific chunk by its ID.

**Arguments:**

- `id` (string, required): The chunk ID

### get_component_chunks

Get all chunks for a specific component.

**Arguments:**

- `component` (string, required): The component name (e.g., "button", "dialog")

### list_components

List all available components in the documentation.

### get_stats

Get statistics about the stored chunks.

**Returns:**

- total_chunks: Total number of stored chunks
- unique_components: Number of unique components
- avg_token_count: Average tokens per chunk

## Configuration

Configure via environment variables in `.env`:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=marigold_rag
DB_USER=postgres
DB_PASSWORD=postgres
```

## Architecture

- **server.py**: MCP server implementation and tool handlers
- **db.py**: PostgreSQL connection and query functions
- **embeddings.py**: Text embedding using sentence-transformers (uses notebooks venv as fallback)

## Claude for Desktop Integration

To use this MCP server with Claude for Desktop, add it to your `claude_desktop_config.json`:

**macOS/Linux:**

```bash
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows:**

```powershell
code $env:AppData\Claude\claude_desktop_config.json
```

Add the following configuration (replace `/ABSOLUTE/PATH` with actual path):

```json
{
  "mcpServers": {
    "marigold": {
      "command": "python",
      "args": ["/ABSOLUTE/PATH/TO/mcp-server/server.py"],
      "env": {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "marigold_rag",
        "DB_USER": "postgres",
        "DB_PASSWORD": "postgres"
      }
    }
  }
}
```

After saving, restart Claude for Desktop to activate the server.
