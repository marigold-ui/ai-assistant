#!/usr/bin/env python3
"""
Direct JSON-RPC test for MCP server
"""
import json
import subprocess
import sys


def test_server():
    """Test server with direct JSON-RPC commands"""
    
    print("Starting MCP server...")
    server_process = subprocess.Popen(
        ["python3", "/home/sinan/GitHub/reservix/ai-assistant/mcp-server/server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    
    def send_request(method, params=None):
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        json_str = json.dumps(request) + "\n"
        print(f"Sending: {json_str.strip()}")
        server_process.stdin.write(json_str)
        server_process.stdin.flush()
        
        response = server_process.stdout.readline()
        if response:
            data = json.loads(response)
            print(f"Response: {json.dumps(data, indent=2)}")
            return data
        return None
    
    try:
        # Initialize
        print("\n1. Initializing server...")
        send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0"}
        })
        
        # List tools
        print("\n2. Listing tools...")
        send_request("tools/list")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        server_process.terminate()
        server_process.wait()


if __name__ == "__main__":
    test_server()
