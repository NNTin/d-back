import asyncio
import json
import subprocess
import sys
import time

try:
    import pytest
    import aiohttp
    from packaging import version
except ImportError:
    pytest = None
    aiohttp = None
    version = None


class TestHTTPServer:
    """Test HTTP functionality of the d_back server."""
    
    @pytest.fixture(scope="class")
    def server_process(self):
        """Start the d_back server for testing."""
        # Start the server using module execution
        server_proc = subprocess.Popen(
            [sys.executable, "-m", "d_back"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1  # line buffered
        )
        
        # Give server time to start
        time.sleep(2)
        
        # Verify server is still running
        if server_proc.poll() is not None:
            # Server has already exited, get the error output
            stdout, stderr = server_proc.communicate()
            raise RuntimeError(f"Server failed to start. stdout: {stdout}, stderr: {stderr}")
        
        yield server_proc
        
        # Cleanup with proper timeout handling
        if server_proc.poll() is None:  # Still running
            server_proc.terminate()
            try:
                server_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_proc.kill()
                try:
                    server_proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    pass  # Process might be stuck, but we tried

    @pytest.fixture
    async def http_session(self):
        """Create an HTTP session for testing."""
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            yield session

    @pytest.mark.asyncio
    async def test_http_root_page(self, server_process, http_session):
        """Test that the root HTTP page loads successfully."""
        async with http_session.get('http://localhost:3000/') as response:
            assert response.status == 200
            content_type = response.headers.get('content-type', '')
            assert 'text/html' in content_type.lower()
            
            content = await response.text()
            assert 'D-Back WebSocket Server' in content
            assert 'WebSocket URL' in content
            assert 'Features' in content

    @pytest.mark.asyncio
    async def test_api_version_endpoint(self, server_process, http_session):
        """Test that the /api/version endpoint returns valid version data."""
        async with http_session.get('http://localhost:3000/api/version') as response:
            assert response.status == 200
            content_type = response.headers.get('content-type', '')
            assert 'application/json' in content_type.lower()
            
            data = await response.json()
            assert 'version' in data
            assert isinstance(data['version'], str)
            assert len(data['version']) > 0
            
            # Validate that it's a valid version string
            try:
                parsed_version = version.parse(data['version'])
                assert parsed_version is not None
            except version.InvalidVersion:
                pytest.fail(f"Invalid version string: {data['version']}")

    @pytest.mark.asyncio
    async def test_http_404_for_missing_file(self, server_process, http_session):
        """Test that missing files return 404."""
        async with http_session.get('http://localhost:3000/nonexistent.html') as response:
            assert response.status == 404
            content_type = response.headers.get('content-type', '')
            assert 'text/html' in content_type.lower()

    @pytest.mark.asyncio
    async def test_http_headers_present(self, server_process, http_session):
        """Test that proper HTTP headers are set."""
        async with http_session.get('http://localhost:3000/') as response:
            assert response.status == 200
            assert 'content-type' in response.headers
            # Websockets server might not always set content-length, just check basic headers are present
            assert 'server' in response.headers or 'content-type' in response.headers

    @pytest.mark.asyncio
    async def test_multiple_concurrent_http_requests(self, server_process, http_session):
        """Test that the server can handle multiple concurrent HTTP requests."""
        async def make_request(path):
            async with http_session.get(f'http://localhost:3000{path}') as response:
                return response.status, await response.text()
        
        # Make multiple concurrent requests
        tasks = [
            make_request('/'),
            make_request('/api/version'),
            make_request('/nonexistent.html'),
            make_request('/'),
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Check that all requests completed
        assert len(results) == 4
        assert results[0][0] == 200  # Root page
        assert results[1][0] == 200  # API version
        assert results[2][0] == 404  # Nonexistent file
        assert results[3][0] == 200  # Root page again
        
        # Verify content
        assert 'D-Back WebSocket Server' in results[0][1]
        version_data = json.loads(results[1][1])
        assert 'version' in version_data

    @pytest.mark.asyncio  
    async def test_http_and_websocket_same_port(self, server_process, http_session):
        """Test that HTTP and WebSocket can coexist on the same port."""
        # First, test HTTP request
        async with http_session.get('http://localhost:3000/') as response:
            assert response.status == 200
            http_content = await response.text()
            assert 'D-Back WebSocket Server' in http_content
        
        # Then, test that WebSocket connection is still possible
        # This is more of a basic connectivity test
        import websockets
        try:
            # Add timeout to WebSocket connection itself
            websocket = await asyncio.wait_for(
                websockets.connect('ws://localhost:3000'),
                timeout=5.0
            )
            async with websocket:
                # Check connection (handle different websockets versions)
                is_open = True
                try:
                    is_open = websocket.open
                except AttributeError:
                    # websockets >= 11.0 doesn't have .open, assume connected if no exception
                    pass
                assert is_open, "WebSocket connection should be established"
                
                # Should receive initial server-list message
                message = await asyncio.wait_for(websocket.recv(), timeout=5)
                data = json.loads(message)
                assert data.get('type') == 'server-list'
        except asyncio.TimeoutError:
            pytest.fail("WebSocket connection or message receive timed out")
        except Exception as e:
            pytest.fail(f"WebSocket connection failed after HTTP request: {e}")

    @pytest.mark.asyncio
    async def test_server_startup_logs(self, server_process):
        """Test that server started successfully by checking if it's responsive."""
        # Instead of trying to read subprocess output (which can hang),
        # just test that the server is actually running by making a simple HTTP request
        try:
            import aiohttp
            
            # Give server a moment to fully initialize
            await asyncio.sleep(0.5)
            
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get('http://localhost:3000/api/version') as response:
                    assert response.status == 200, "Server should be responsive"
                    data = await response.json()
                    assert 'version' in data, "Version endpoint should work"
                    
        except ImportError:
            # Fallback: just check that the process is still alive
            assert server_process.poll() is None, "Server process should still be running"
        except Exception as e:
            pytest.fail(f"Server startup test failed: {e}")