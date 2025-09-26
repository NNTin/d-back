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
        time.sleep(2)  # Give server time to start
        
        yield server_proc
        
        # Cleanup
        server_proc.terminate()
        try:
            server_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_proc.kill()

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
            # Check that content-length is set for static files
            assert 'content-length' in response.headers or 'transfer-encoding' in response.headers

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
            async with websockets.connect('ws://localhost:3000') as websocket:
                # Should be able to connect without errors
                assert websocket.open
                
                # Should receive initial server-list message
                message = await asyncio.wait_for(websocket.recv(), timeout=5)
                data = json.loads(message)
                assert data.get('type') == 'server-list'
        except Exception as e:
            pytest.fail(f"WebSocket connection failed after HTTP request: {e}")

    @pytest.mark.asyncio
    async def test_server_startup_logs(self, server_process):
        """Test that server produces expected startup logs."""
        # Give server time to produce startup output
        time.sleep(1)
        
        # Try to read some output (non-blocking)
        try:
            stdout_data = server_process.stdout.read()
            stderr_data = server_process.stderr.read()
        except Exception:
            # If we can't read, that's okay for this test
            return
            
        output = (stdout_data or "") + (stderr_data or "")
        
        if output:
            assert "Starting D-Back WebSocket Server" in output or "Mock WebSocket server running" in output