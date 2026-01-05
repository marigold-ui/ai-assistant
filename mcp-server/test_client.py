#!/usr/bin/env python3
"""
Simple MCP client test for the Marigold server
"""
import json
import sys
import asyncio
import subprocess
from mcp import ClientSession
from mcp.client.stdio import stdio_client


async def test_mcp_server():
    """Test the MCP server with basic queries"""
    
    server_path = "/home/sinan/GitHub/reservix/ai-assistant/mcp-server/server.py"
    
    class ServerConfig:
        def __init__(self):
            self.command = "python3"
            self.args = [server_path]
            self.env = {}
            self.cwd = None
    
    server_config = ServerConfig()
    
    async with stdio_client(server_config) as transport:
        async with ClientSession(transport) as session:
            await session.initialize()
            
            print("Available tools:")
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            print("\n1. Testing list_components...")
            result = await session.call_tool("list_components", {})
            data = json.loads(result.content[0].text)
            print(f"   Found {data['total']} components")
            print(f"   Components: {', '.join(data['components'][:5])}...")
            
            print("\n2. Testing get_stats...")
            result = await session.call_tool("get_stats", {})
            stats = json.loads(result.content[0].text)
            print(f"   Total chunks: {stats['total_chunks']}")
            print(f"   Unique components: {stats['unique_components']}")
            print(f"   Avg tokens/chunk: {stats['avg_token_count']}")
            
            print("\n3. Testing search_chunks...")
            result = await session.call_tool("search_chunks", {
                "query": "button styling",
                "limit": 3
            })
            results = json.loads(result.content[0].text)
            print(f"   Found {len(results)} results:")
            for i, r in enumerate(results, 1):
                print(f"     {i}. {r['component']} - {r['section_title']} (similarity: {r['similarity']:.3f})")
            
            print("\n✅ All tests passed!")


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
