import os
import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from db import DatabaseConnector

load_dotenv()

mcp = FastMCP("marigold-mcp")
dbs = {}
components_cache = {}

def get_db(table: str):
    """Get or create database connector for given table"""
    if table not in dbs:
        dbs[table] = DatabaseConnector(table_name=table)
    return dbs[table]

def get_components(table: str):
    """Get list of components from table (cached)"""
    if table not in components_cache:
        components_cache[table] = get_db(table).get_components()
    return components_cache[table]

def embed_query(query: str) -> list:
    """Generate embedding for a query using Ollama"""
    response = requests.post(
        os.getenv("OLLAMA_URL", "http://localhost:11434/api/embed"),
        json={"model": os.getenv("OLLAMA_MODEL", "nomic-embed-text"), "input": query}
    )
    return response.json()["embeddings"][0]

def format_results(results: list, include_parent: bool = True) -> str:
    """Format search results into readable string"""
    if not results:
        return "No documentation found for your query."
    
    formatted = []
    for r in results:
        parts = [
            f"**{r['component']}** - {r['section_path']} (Similarity: {r['similarity']:.1%})",
            r['content']
        ]
        
        if include_parent and r.get('parent_context'):
            parts.extend([
                f"\n**Parent Context:** {r['parent_context']['section_path']}",
                r['parent_context']['content']
            ])
        
        if r.get('demo_code'):
            parts.append("\n**Example Code:**")
            for filename, code in r['demo_code'].items():
                parts.append(f"```tsx\n{code}\n```")
        
        formatted.append("\n".join(parts))
    
    return "\n\n---\n\n".join(formatted)

def extract_component_filter(query: str, table: str) -> str | None:
    """Extract component name from query if present"""
    query_lower = query.lower()
    for component in get_components(table):
        if component.lower() in query_lower:
            return component
    return None

@mcp.tool()
async def marigold_documentation_lookup(query: str, limit: int = 5) -> str:
    """Search the official Marigold UI design system documentation using semantic similarity (semantic chunks with parent-child relationships).
    
    Use this tool when users ask questions about:
    - Component usage and API documentation (Button, Dialog, Select, etc.)
    - Design patterns and best practices
    - Props, types, and component variations
    - Styling and theming in Marigold
    - How to implement specific UI patterns
    
    This tool searches against official documentation with semantic vector similarity.
    Results include component descriptions, usage examples, implementation details, and demo code.
    Uses hierarchical chunks with parent-child relationships for better context.
    
    Args:
        query: The user's question about Marigold components or patterns (e.g., "How do I create a Button with custom styling?")
        limit: Number of most relevant documentation chunks to return (1-20, default: 5)
    
    Returns:
        Formatted documentation chunks with component, section path, similarity score, content, parent context, and demo code
    """
    component_filter = extract_component_filter(query, "chunks")
    embedding = embed_query(query)
    results = get_db("chunks").search_similar(embedding, limit, component_filter=component_filter)
    return format_results(results, include_parent=True)

@mcp.tool()
async def marigold_documentation_lookup_primitive(query: str, limit: int = 5) -> str:
    """Search the official Marigold UI design system documentation using semantic similarity (primitive chunks - flat structure).
    
    Use this tool when users ask questions about:
    - Component usage and API documentation (Button, Dialog, Select, etc.)
    - Design patterns and best practices
    - Props, types, and component variations
    - Styling and theming in Marigold
    - How to implement specific UI patterns
    
    This tool searches against official documentation with semantic vector similarity.
    Uses flat primitive chunks without hierarchical relationships for direct, focused results.
    
    Args:
        query: The user's question about Marigold components or patterns (e.g., "How do I create a Button with custom styling?")
        limit: Number of most relevant documentation chunks to return (1-20, default: 5)
    
    Returns:
        Formatted documentation chunks with component, section path, similarity score, content, and demo code
    """
    component_filter = extract_component_filter(query, "chunks_primitive")
    embedding = embed_query(query)
    results = get_db("chunks_primitive").search_similar(embedding, limit, component_filter=component_filter)
    return format_results(results, include_parent=False)

if __name__ == "__main__":
    mcp.run(transport="stdio")