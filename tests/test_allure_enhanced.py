"""
Enhanced test file with Allure reporting features.
This demonstrates how to add rich test reporting with descriptions, steps, and attachments.
"""

import asyncio
import json
import subprocess
import sys
import time
import traceback

try:
    import pytest
    import allure
    from allure import step, attach, attachment_type
    ALLURE_AVAILABLE = True
except ImportError:
    # Fallback decorators when allure is not available
    def step(title):
        def decorator(func):
            return func
        return decorator
    
    def attach(body, name=None, attachment_type=None):
        pass
    
    class allure:
        @staticmethod
        def epic(name):
            def decorator(func):
                return func
            return decorator
        
        @staticmethod
        def feature(name):
            def decorator(func):
                return func
            return decorator
            
        @staticmethod
        def story(name):
            def decorator(func):
                return func
            return decorator
        
        @staticmethod
        def title(name):
            def decorator(func):
                return func
            return decorator
        
        @staticmethod
        def description(text):
            def decorator(func):
                return func
            return decorator
        
        @staticmethod
        def severity(level):
            def decorator(func):
                return func
            return decorator
    
    ALLURE_AVAILABLE = False


@allure.epic("D-Back WebSocket Server")
@allure.feature("HTTP Server")
class TestHTTPServerAllure:
    """Enhanced HTTP server tests with Allure reporting."""
    
    @pytest.fixture(scope="class")
    def server_process(self):
        """Start the d_back server for testing."""
        with step("Starting d_back server"):
            server_proc = subprocess.Popen(
                [sys.executable, "-m", "d_back"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            time.sleep(2)
            attach(f"Server PID: {server_proc.pid}", "server_info.txt", attachment_type.TEXT)
        
        yield server_proc
        
        with step("Stopping d_back server"):
            server_proc.terminate()
            try:
                server_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_proc.kill()

    @allure.story("Static File Serving")
    @allure.title("Root page should load successfully")
    @allure.description("Test that the main HTTP page loads with correct content and headers")
    @allure.severity("critical")
    @pytest.mark.asyncio
    async def test_root_page_loads(self, server_process):
        """Test that the root HTTP page loads successfully."""
        try:
            import aiohttp
            
            with step("Making HTTP request to root page"):
                timeout = aiohttp.ClientTimeout(total=10)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get('http://localhost:3000/') as response:
                        status = response.status
                        headers = dict(response.headers)
                        content = await response.text()
                        
                        attach(json.dumps(headers, indent=2), "response_headers.json", attachment_type.JSON)
                        attach(content[:1000] + "..." if len(content) > 1000 else content, 
                               "response_body.html", attachment_type.HTML)
            
            with step("Validating response"):
                assert status == 200, f"Expected status 200, got {status}"
                assert 'text/html' in headers.get('content-type', ''), "Content-Type should be text/html"
                assert 'D-Back WebSocket Server' in content, "Page should contain server title"
                
        except ImportError:
            pytest.skip("aiohttp not available")

    @allure.story("API Endpoints")  
    @allure.title("Version API should return valid version data")
    @allure.description("Test that /api/version endpoint returns proper JSON with version information")
    @allure.severity("critical")
    @pytest.mark.asyncio
    async def test_api_version_endpoint(self, server_process):
        """Test that the /api/version endpoint returns valid data."""
        try:
            import aiohttp
            from packaging import version
            
            with step("Making request to version API"):
                timeout = aiohttp.ClientTimeout(total=10)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get('http://localhost:3000/api/version') as response:
                        status = response.status
                        headers = dict(response.headers)
                        data = await response.json()
                        
                        attach(json.dumps(headers, indent=2), "api_headers.json", attachment_type.JSON)
                        attach(json.dumps(data, indent=2), "api_response.json", attachment_type.JSON)
            
            with step("Validating API response"):
                assert status == 200, f"API should return 200, got {status}"
                assert 'application/json' in headers.get('content-type', ''), "Should return JSON content"
                assert 'version' in data, "Response should contain version field"
                assert isinstance(data['version'], str), "Version should be a string"
                assert len(data['version']) > 0, "Version should not be empty"
                
                # Validate version format
                try:
                    parsed_version = version.parse(data['version'])
                    attach(f"Parsed version: {parsed_version}", "version_info.txt", attachment_type.TEXT)
                except version.InvalidVersion as e:
                    attach(f"Version parsing error: {e}", "version_error.txt", attachment_type.TEXT)
                    raise AssertionError(f"Invalid version format: {data['version']}")
                    
        except ImportError:
            pytest.skip("Required packages not available")

    @allure.story("Error Handling")
    @allure.title("Missing files should return 404")
    @allure.description("Test that requests for non-existent files return proper 404 errors")
    @allure.severity("normal")
    @pytest.mark.asyncio
    async def test_404_error_handling(self, server_process):
        """Test that missing files return 404 status."""
        try:
            import aiohttp
            
            test_paths = ['/nonexistent.html', '/missing/file.txt', '/api/invalid']
            
            for path in test_paths:
                with step(f"Testing 404 for path: {path}"):
                    timeout = aiohttp.ClientTimeout(total=10)
                    async with aiohttp.ClientSession(timeout=timeout) as session:
                        async with session.get(f'http://localhost:3000{path}') as response:
                            status = response.status
                            content = await response.text()
                            
                            attach(f"Path: {path}\nStatus: {status}\nContent: {content[:500]}", 
                                   f"404_test_{path.replace('/', '_')}.txt", attachment_type.TEXT)
                            
                            assert status == 404, f"Path {path} should return 404, got {status}"
                            
        except ImportError:
            pytest.skip("aiohttp not available")


@allure.epic("D-Back WebSocket Server")
@allure.feature("WebSocket Server")
class TestWebSocketServerAllure:
    """Enhanced WebSocket server tests with Allure reporting."""
    
    @pytest.fixture(scope="class")
    def server_process(self):
        """Start the d_back server for testing."""
        with step("Starting d_back server for WebSocket tests"):
            server_proc = subprocess.Popen(
                [sys.executable, "-m", "d_back"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            time.sleep(2)
            attach(f"WebSocket Server PID: {server_proc.pid}", "ws_server_info.txt", attachment_type.TEXT)
        
        yield server_proc
        
        with step("Stopping WebSocket server"):
            server_proc.terminate()
            try:
                server_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_proc.kill()

    @allure.story("Connection Handling")
    @allure.title("WebSocket connection should establish successfully")
    @allure.description("Test that WebSocket connections can be established and receive initial messages")
    @allure.severity("critical")
    @pytest.mark.asyncio
    async def test_websocket_connection_establishment(self, server_process):
        """Test basic WebSocket connection establishment."""
        try:
            import websockets
            
            with step("Establishing WebSocket connection"):
                async with websockets.connect('ws://localhost:3000') as websocket:
                    # Test connection establishment
                    connection_info = {
                        "url": str(websocket.uri),
                        "state": "connected"
                    }
                    attach(json.dumps(connection_info, indent=2), "connection_info.json", attachment_type.JSON)
                    
                    with step("Receiving initial server-list message"):
                        message = await asyncio.wait_for(websocket.recv(), timeout=5)
                        data = json.loads(message)
                        
                        attach(json.dumps(data, indent=2), "server_list_message.json", attachment_type.JSON)
                        
                        assert data.get('type') == 'server-list', f"Expected server-list, got {data.get('type')}"
                        assert 'data' in data, "Server-list should contain data field"
                        assert isinstance(data['data'], dict), "Server data should be a dictionary"
                        
        except ImportError:
            pytest.skip("websockets not available")

    @allure.story("Server Interaction")
    @allure.title("Client should be able to join a server")
    @allure.description("Test the complete flow of joining a server through WebSocket")
    @allure.severity("critical")
    @pytest.mark.asyncio
    async def test_server_join_workflow(self, server_process):
        """Test the complete server join workflow."""
        try:
            import websockets
            
            async with websockets.connect('ws://localhost:3000') as websocket:
                with step("Receiving available servers"):
                    server_list_msg = await asyncio.wait_for(websocket.recv(), timeout=5)
                    server_list_data = json.loads(server_list_msg)
                    
                    servers = server_list_data['data']
                    attach(json.dumps(servers, indent=2), "available_servers.json", attachment_type.JSON)
                    
                    assert len(servers) > 0, "Should have at least one server available"
                
                with step("Joining first available server"):
                    first_server = next(iter(servers.values()))
                    server_id = first_server['id']
                    
                    connect_msg = {
                        "type": "connect",
                        "data": {"server": server_id}
                    }
                    
                    attach(json.dumps(connect_msg, indent=2), "connect_message.json", attachment_type.JSON)
                    await websocket.send(json.dumps(connect_msg))
                
                with step("Receiving server-join confirmation"):
                    response = await asyncio.wait_for(websocket.recv(), timeout=5)
                    join_data = json.loads(response)
                    
                    attach(json.dumps(join_data, indent=2), "join_response.json", attachment_type.JSON)
                    
                    assert join_data.get('type') == 'server-join', f"Expected server-join, got {join_data.get('type')}"
                    assert 'data' in join_data, "Join response should contain data"
                    
                    join_info = join_data['data']
                    assert 'server' in join_info, "Join data should contain server info"
                    assert 'users' in join_info, "Join data should contain users list"
                    assert join_info['server']['id'] == server_id, "Should join the requested server"
                        
        except ImportError:
            pytest.skip("websockets not available")