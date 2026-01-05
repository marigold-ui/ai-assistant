import json
import asyncio
import logging
import sys
from typing import Any

from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
)

from db import DatabaseConnector
from embeddings import EmbeddingProvider

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

db = DatabaseConnector()
embedder = EmbeddingProvider()

server = Server("marigold-mcp-server")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_chunks",
            description="Search for chunks similar to a query using semantic similarity. Returns the most relevant documentation chunks for a given query text.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query text",
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results to return (default: 5)",
                        "default": 5,
                    },
                    "threshold": {
                        "type": "number",
                        "description": "Minimum similarity score (0-1) for results (default: 0.5)",
                        "default": 0.5,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_chunk",
            description="Get a specific chunk by its ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "The chunk ID",
                    },
                },
                "required": ["id"],
            },
        ),
        Tool(
            name="get_component_chunks",
            description="Get all chunks for a specific component (e.g., 'button', 'dialog')",
            inputSchema={
                "type": "object",
                "properties": {
                    "component": {
                        "type": "string",
                        "description": "The component name",
                    },
                },
                "required": ["component"],
            },
        ),
        Tool(
            name="list_components",
            description="List all available components in the documentation",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_stats",
            description="Get statistics about the stored chunks",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "search_chunks":
            query = arguments.get("query", "")
            limit = arguments.get("limit", 5)
            threshold = arguments.get("threshold", 0.5)

            logger.info(f"Generating embedding for query: {query}")
            embedding = embedder.embed(query)

            logger.info(f"Searching for similar chunks (limit: {limit}, threshold: {threshold})")
            results = db.search_similar(embedding, limit, threshold)

            return [TextContent(type="text", text=json.dumps([vars(r) for r in results], indent=2))]

        elif name == "get_chunk":
            chunk_id = arguments.get("id", "")
            chunk = db.get_chunk_by_id(chunk_id)

            if chunk:
                return [TextContent(type="text", text=json.dumps(vars(chunk), indent=2))]
            return [TextContent(type="text", text=f'Chunk with ID "{chunk_id}" not found')]

        elif name == "get_component_chunks":
            component = arguments.get("component", "")
            chunks = db.get_chunks_by_component(component)

            if chunks:
                return [TextContent(type="text", text=json.dumps([vars(c) for c in chunks], indent=2))]
            return [TextContent(type="text", text=f'No chunks found for component "{component}"')]

        elif name == "list_components":
            components = db.get_all_components()
            return [TextContent(type="text", text=json.dumps({"components": components, "total": len(components)}, indent=2))]

        elif name == "get_stats":
            stats = db.get_stats()
            return [TextContent(type="text", text=json.dumps(stats, indent=2))]

        return [TextContent(type="text", text=f"Unknown tool: {name}", isError=True)]

    except Exception as e:
        logger.error(f"Tool execution error: {str(e)}", exc_info=True)
        return [TextContent(type="text", text=f"Error: {str(e)}", isError=True)]


async def main():
    logger.info("Starting Marigold MCP Server...")
    tools = await list_tools()
    logger.info(f"Available tools: {[tool.name for tool in tools]}")
    
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as streams:
        await server.run(
            streams[0],
            streams[1],
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
