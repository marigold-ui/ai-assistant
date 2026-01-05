import asyncio, requests
from mcp.server import Server
from mcp.types import Tool, TextContent
from db import DatabaseConnector

server = Server("marigold-rag")
db = DatabaseConnector()
OLLAMA_URL = "http://localhost:11434/api/embed"

def embed_query(query: str) -> list:
    response = requests.post(OLLAMA_URL, json={
        "model": "nomic-embed-text",
        "input": query
    })
    return response.json()["embeddings"][0]

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="marigold_documentation_lookup",
            description="Search Marigold documentation",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "number", "default": 5}
                },
                "required": ["query"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "marigold_documentation_lookup":
        query = arguments["query"]
        limit = arguments.get("limit", 5)
        
        embedding = embed_query(query)
        results = db.search_similar(embedding, limit)
        
        text = "\n\n".join([f"**{r['component']}** - {r['section_title']}\n{r['content']}" for r in results])
        return [TextContent(type="text", text=text)]
    
    return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    from mcp.server.stdio import stdio_server
    async with stdio_server() as streams:
        await server.run(streams[0], streams[1], server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())