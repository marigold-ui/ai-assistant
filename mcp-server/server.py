import os
import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from db import DatabaseConnector

load_dotenv()

mcp = FastMCP("marigold-mcp")
db = None
_components_cache = None

def get_db():
    global db
    if db is None:
        db = DatabaseConnector()
    return db

def get_components():
    """Get list of components from database (cached)"""
    global _components_cache
    if _components_cache is None:
        _components_cache = get_db().get_components()
    return _components_cache

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
async def marigold_documentation_lookup(query: str, limit: int = 5) -> str:
    """Search the official Marigold UI design system documentation using semantic similarity.
    
    Use this tool when users ask questions about:
    - Component usage and API documentation (Button, Dialog, Select, etc.)
    - Design patterns and best practices
    - Props, types, and component variations
    - Styling and theming in Marigold
    - How to implement specific UI patterns
    
    This tool searches against official documentation with semantic vector similarity.
    Results include component descriptions, usage examples, implementation details, and demo code.
    
    Args:
        query: The user's question about Marigold components or patterns (e.g., "How do I create a Button with custom styling?")
        limit: Number of most relevant documentation chunks to return (1-20, default: 5)
    
    Returns:
        Formatted documentation chunks with component, section path, similarity score, content, parent context, and demo code
    """
    # Try to extract component name from query by checking against available components
    component_filter = None
    query_lower = query.lower()
    for component in get_components():
        if component.lower() in query_lower:
            component_filter = component
            break
    
    embedding = embed_query(query)
    results = get_db().search_similar(embedding, limit, component_filter=component_filter)
    
    if not results:
        return "No documentation found for your query."
    
    formatted = []
    for r in results:
        # Build context string
        context = f"**{r['component']}** - {r['section_path']} (Similarity: {r['similarity']:.1%})\n"
        context += f"{r['content']}"
        
        # Add parent context if available
        if r['parent_context']:
            context += f"\n\n**Parent Context:** {r['parent_context']['section_path']}\n"
            context += f"{r['parent_context']['content']}"
        
        # Add demo code if available
        if r['demo_code']:
            context += f"\n\n**Example Code:**\n"
            for filename, code in r['demo_code'].items():
                context += f"```tsx\n{code}\n```\n"
        
        formatted.append(context)
    
    return "\n\n---\n\n".join(formatted)

if __name__ == "__main__":
    mcp.run(transport="stdio")