import os
import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from db import DatabaseConnector

load_dotenv()

mcp = FastMCP("marigold-mcp")
db = None

def get_db():
    global db
    if db is None:
        db = DatabaseConnector()
    return db

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/embed")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "nomic-embed-text")

def embed_query(query: str) -> list:
    """Generate embedding for a query using Ollama"""
    response = requests.post(OLLAMA_URL, json={
        "model": OLLAMA_MODEL,
        "input": query
    })
    return response.json()["embeddings"][0]

@mcp.tool()
async def documentation_lookup(query: str, limit: int = 5) -> str:
    """Search the official Marigold UI design system documentation using semantic similarity.
    
    Use this tool when users ask questions about:
    - Component usage and API documentation (Button, Dialog, Select, etc.)
    - Design patterns and best practices
    - Props, types, and component variations
    - Styling and theming in Marigold
    - How to implement specific UI patterns
    
    This tool searches against official documentation with semantic vector similarity.
    Results include component descriptions, usage examples, and implementation details.
    
    Args:
        query: The user's question about Marigold components or patterns (e.g., "How do I create a Button with custom styling?")
        limit: Number of most relevant documentation chunks to return (1-20, default: 5)
    
    Returns:
        Formatted documentation chunks with component name, section title, similarity score, and content
    """
    embedding = embed_query(query)
    results = get_db().search_similar(embedding, limit)
    
    if not results:
        return "No documentation found for your query."
    
    formatted = []
    for r in results:
        formatted.append(f"**{r['component']}** - {r['section_title']} (Similarity: {r['similarity']:.1%})\n{r['content']}")
    
    return "\n\n---\n\n".join(formatted)

if __name__ == "__main__":
    mcp.run(transport="stdio")