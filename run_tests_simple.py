#!/usr/bin/env python3
"""
Simple test runner for d_back that doesn't require pytest installation.
Runs basic functionality tests for HTTP and WebSocket features.
"""

import asyncio
import json
import subprocess
import sys
import time
import traceback
from pathlib import Path


class SimpleTestRunner:
    """Simple test runner without external dependencies."""
    
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.server_process = None
        
    def start_server(self):
        """Start the d_back server for testing."""
        print("Starting d_back server...")
        self.server_process = subprocess.Popen(
            [sys.executable, "-m", "d_back"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        time.sleep(3)  # Give server time to start
        print("Server started (PID: {})".format(self.server_process.pid))
        
    def stop_server(self):
        """Stop the d_back server."""
        if self.server_process:
            print("Stopping server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            print("Server stopped")
    
    def assert_true(self, condition, message="Assertion failed"):
        """Simple assertion."""
        if condition:
            self.tests_passed += 1
            print(f"  ✓ {message}")
        else:
            self.tests_failed += 1 
            print(f"  ✗ {message}")
            
    def run_test(self, test_func, test_name):
        """Run a single test function."""
        print(f"\n--- {test_name} ---")
        try:
            if asyncio.iscoroutinefunction(test_func):
                asyncio.run(test_func())
            else:
                test_func()
            print(f"✓ {test_name} PASSED")
        except Exception as e:
            print(f"✗ {test_name} FAILED: {e}")
            traceback.print_exc()
            self.tests_failed += 1

    async def test_http_basic(self):
        """Test basic HTTP functionality."""
        try:
            # Try to import aiohttp, fall back to urllib if not available
            try:
                import aiohttp
                
                timeout = aiohttp.ClientTimeout(total=10)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    # Test root page
                    async with session.get('http://localhost:3000/') as response:
                        self.assert_true(response.status == 200, "Root page returns 200")
                        content = await response.text()
                        self.assert_true('D-Back WebSocket Server' in content, "Root page contains title")
                    
                    # Test API version endpoint
                    async with session.get('http://localhost:3000/api/version') as response:
                        self.assert_true(response.status == 200, "API version returns 200")
                        data = await response.json()
                        self.assert_true('version' in data, "API version contains version field")
                        self.assert_true(len(data['version']) > 0, "Version is not empty")
                    
                    # Test 404 for missing file
                    async with session.get('http://localhost:3000/nonexistent.html') as response:
                        self.assert_true(response.status == 404, "Missing file returns 404")
                        
            except ImportError:
                print("aiohttp not available, skipping HTTP tests")
                
        except Exception as e:
            print(f"HTTP test error: {e}")
            raise

    async def test_websocket_basic(self):
        """Test basic WebSocket functionality.""" 
        try:
            # Try to import websockets
            try:
                import websockets
                
                # Add timeout to connection itself
                websocket = await asyncio.wait_for(
                    websockets.connect('ws://localhost:3000'),
                    timeout=10.0
                )
                
                async with websocket:
                    # Check if connection is established (different methods for different versions)
                    is_open = True
                    try:
                        is_open = websocket.open
                    except AttributeError:
                        # websockets >= 11.0 doesn't have .open, check if we can send/receive
                        try:
                            await asyncio.wait_for(websocket.ping(), timeout=2.0)
                            is_open = True
                        except Exception:
                            is_open = False
                    
                    self.assert_true(is_open, "WebSocket connection established")
                    
                    # Should receive initial server-list message
                    message = await asyncio.wait_for(websocket.recv(), timeout=5)
                    data = json.loads(message)
                    self.assert_true(data.get('type') == 'server-list', "Received server-list message")
                    self.assert_true('data' in data, "Server-list has data field")
                    
                    # Test connect to server
                    servers = data['data']
                    if servers:
                        first_server_id = next(iter(servers.values()))['id']
                        connect_msg = {
                            "type": "connect",
                            "data": {"server": first_server_id}
                        }
                        await websocket.send(json.dumps(connect_msg))
                        
                        # Should receive server-join message
                        response = await asyncio.wait_for(websocket.recv(), timeout=5)
                        join_data = json.loads(response)
                        self.assert_true(join_data.get('type') == 'server-join', "Received server-join message")
                    
            except ImportError:
                print("websockets not available, skipping WebSocket tests")
        except asyncio.TimeoutError:
            print("WebSocket test timed out")
            raise
        except Exception as e:
            print(f"WebSocket test error: {e}")
            raise

    def test_existing_client(self):
        """Test using the existing mock WebSocket client."""
        try:
            tests_dir = Path(__file__).parent / "tests"
            client_script = tests_dir / "helpers" / "mock_websocket_client.py"
            
            if client_script.exists():
                print("Running existing mock client...")
                client_proc = subprocess.Popen(
                    [sys.executable, str(client_script)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                stdout, stderr = client_proc.communicate(timeout=10)
                
                self.assert_true("Connected to ws://localhost:3000" in stdout, "Client connected successfully")
                self.assert_true("[RECV]" in stdout, "Client received messages")
                self.assert_true("[SEND]" in stdout, "Client sent messages")
            else:
                print("Mock client not found, skipping")
                
        except Exception as e:
            print(f"Existing client test error: {e}")
            raise

    def run_all_tests(self):
        """Run all tests."""
        print("=" * 50)
        print("D-Back Test Suite")
        print("=" * 50)
        
        try:
            self.start_server()
            
            # Run tests
            self.run_test(self.test_http_basic, "HTTP Basic Tests")
            self.run_test(self.test_websocket_basic, "WebSocket Basic Tests") 
            self.run_test(self.test_existing_client, "Existing Client Test")
            
        finally:
            self.stop_server()
        
        # Print summary
        print("\n" + "=" * 50)
        print("Test Summary")
        print("=" * 50)
        total_tests = self.tests_passed + self.tests_failed
        print(f"Total assertions: {total_tests}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_failed}")
        
        if self.tests_failed == 0:
            print("🎉 All tests passed!")
            return 0
        else:
            print("❌ Some tests failed!")
            return 1


if __name__ == "__main__":
    runner = SimpleTestRunner()
    sys.exit(runner.run_all_tests())