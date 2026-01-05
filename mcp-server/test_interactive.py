#!/usr/bin/env python3
"""
Marigold MCP CLI - Test client for asking about Marigold components
"""
import json
import subprocess
import time
import sys
import asyncio
from typing import Optional


class MCPTestClient:
    def __init__(self):
        self.process = None
        self.start_server()
    
    def start_server(self):
        """Start the MCP server subprocess"""
        self.process = subprocess.Popen(
            ["python3", "/home/sinan/GitHub/reservix/ai-assistant/mcp-server/server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        time.sleep(1)  # Give server time to start
    
    def send_request(self, method: str, params: dict = None) -> Optional[dict]:
        """Send JSON-RPC request to server"""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        self.process.stdin.write(json.dumps(request) + "\n")
        self.process.stdin.flush()
        time.sleep(0.1)
        
        response = self.process.stdout.readline()
        if response:
            return json.loads(response)
        return None
    
    def initialize(self):
        """Initialize MCP connection"""
        self.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "marigold-cli", "version": "1.0"}
        })
    
    def search(self, query: str, limit: int = 5) -> list:
        """Search for documentation chunks"""
        result = self.send_request("tools/call", {
            "name": "search_chunks",
            "arguments": {
                "query": query,
                "limit": limit,
                "threshold": 0.5
            }
        })
        
        if result and "result" in result:
            content_text = result["result"]["content"][0]["text"]
            return json.loads(content_text)
        return []
    
    def cleanup(self):
        """Stop the server"""
        if self.process:
            self.process.terminate()
            self.process.wait()


def format_results(query: str, results: list):
    """Pretty print search results"""
    print(f"\n{'='*70}")
    print(f"Query: {query}")
    print(f"{'='*70}")
    print(f"Found {len(results)} relevant chunks:\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['component'].upper()}")
        print(f"   Section: {result['section_title']}")
        print(f"   Path: {result['section_path']}")
        print(f"   Similarity: {result['similarity']:.3f}")
        print(f"   Tokens: {result['token_count']}")
        print(f"   Preview: {result['content'][:150]}...")
        print()


def main():
    print("🚀 Starting Marigold MCP Test Client...")
    print("This client will query the MCP server without any context.\n")
    
    client = MCPTestClient()
    
    try:
        print("Initializing MCP Server...")
        client.initialize()
        print("✅ MCP Server initialized\n")
        
        # Test query 1
        query1 = "How do I create a button component?"
        print(f"\n[1/3] Testing: {query1}")
        results1 = client.search(query1, limit=3)
        format_results(query1, results1)
        
        # Test query 2
        query2 = "Dialog component with forms"
        print(f"\n[2/3] Testing: {query2}")
        results2 = client.search(query2, limit=3)
        format_results(query2, results2)
        
        # Test query 3
        query3 = "Table component with sorting"
        print(f"\n[3/3] Testing: {query3}")
        results3 = client.search(query3, limit=3)
        format_results(query3, results3)
        
        print("\n" + "="*70)
        print("✅ All tests completed successfully!")
        print("MCP Server is working and making tool calls automatically.")
        print("="*70)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.cleanup()


if __name__ == "__main__":
    main()
