import asyncio
import json
import subprocess
import sys
import time

try:
    import pytest
except ImportError:
    pytest = None


class TestWebSocketServer:
    """Test WebSocket functionality of the d_back server."""
    
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

    @pytest.mark.asyncio
    async def test_websocket_connection(self, server_process):
        """Test basic WebSocket connection."""
        import websockets
        
        try:
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
                    # websockets >= 11.0 doesn't have .open, try ping instead
                    try:
                        await asyncio.wait_for(websocket.ping(), timeout=2.0)
                        is_open = True
                    except Exception:
                        is_open = False
                
                assert is_open, "WebSocket connection should be established"
                
                # Should receive initial server-list message
                message = await asyncio.wait_for(websocket.recv(), timeout=5)
                data = json.loads(message)
                assert data.get('type') == 'server-list'
                assert 'data' in data
                assert isinstance(data['data'], dict)
        except asyncio.TimeoutError:
            pytest.fail("WebSocket connection or operations timed out")

    @pytest.mark.asyncio
    async def test_websocket_server_list(self, server_process):
        """Test that server-list message contains expected data."""
        import websockets
        
        async with websockets.connect('ws://localhost:3000') as websocket:
            # Receive initial server-list message
            message = await asyncio.wait_for(websocket.recv(), timeout=5)
            data = json.loads(message)
            
            assert data['type'] == 'server-list'
            servers = data['data']
            
            # Should have at least one server (default servers)
            assert len(servers) > 0
            
            # Check structure of a server entry
            for server_id, server_info in servers.items():
                assert 'id' in server_info
                assert 'name' in server_info
                assert isinstance(server_info['id'], str)
                assert isinstance(server_info['name'], str)

    @pytest.mark.asyncio
    async def test_websocket_connect_to_server(self, server_process):
        """Test connecting to a specific server."""
        import websockets
        
        try:
            # Add timeout to connection
            websocket = await asyncio.wait_for(
                websockets.connect('ws://localhost:3000'),
                timeout=10.0
            )
            
            async with websocket:
                # Receive initial server-list message
                server_list_msg = await asyncio.wait_for(websocket.recv(), timeout=5)
                server_list_data = json.loads(server_list_msg)
                
                # Get first available server
                servers = server_list_data['data']
                first_server_id = next(iter(servers.values()))['id']
                
                # Send connect message
                connect_msg = {
                    "type": "connect",
                    "data": {"server": first_server_id}
                }
                await websocket.send(json.dumps(connect_msg))
                
                # Should receive server-join message
                response = await asyncio.wait_for(websocket.recv(), timeout=5)
                data = json.loads(response)
                
                assert data.get('type') == 'server-join'
                assert 'data' in data
                
                join_data = data['data']
                assert 'server' in join_data
                assert 'users' in join_data
                assert join_data['server']['id'] == first_server_id
        except asyncio.TimeoutError:
            pytest.fail("WebSocket operations timed out")

    @pytest.mark.asyncio
    async def test_websocket_invalid_server_connection(self, server_process):
        """Test connecting to a non-existent server."""
        import websockets
        
        async with websockets.connect('ws://localhost:3000') as websocket:
            # Skip server-list message
            await asyncio.wait_for(websocket.recv(), timeout=5)
            
            # Send connect message to non-existent server
            connect_msg = {
                "type": "connect",
                "data": {"server": "nonexistent_server"}
            }
            await websocket.send(json.dumps(connect_msg))
            
            # Should receive an error message
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            data = json.loads(response)
            
            assert data.get('type') == 'error'
            assert 'message' in data

    @pytest.mark.asyncio
    async def test_websocket_multiple_clients(self, server_process):
        """Test that multiple WebSocket clients can connect simultaneously."""
        import websockets
        
        async def client_session(client_id):
            async with websockets.connect('ws://localhost:3000') as websocket:
                # Receive server-list message
                message = await asyncio.wait_for(websocket.recv(), timeout=5)
                data = json.loads(message)
                assert data.get('type') == 'server-list'
                return client_id, True
        
        # Create multiple concurrent client connections
        tasks = [client_session(i) for i in range(3)]
        results = await asyncio.gather(*tasks)
        
        # All clients should have connected successfully
        assert len(results) == 3
        for client_id, success in results:
            assert success

    @pytest.mark.asyncio
    async def test_websocket_message_format(self, server_process):
        """Test that all messages follow the expected JSON format."""
        import websockets
        
        async with websockets.connect('ws://localhost:3000') as websocket:
            # Collect first few messages
            messages = []
            for _ in range(2):  # server-list and potentially others
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5)
                    messages.append(message)
                except asyncio.TimeoutError:
                    break
            
            # Verify all messages are valid JSON with required structure
            for message in messages:
                data = json.loads(message)  # Should not raise exception
                assert 'type' in data
                assert isinstance(data['type'], str)
                assert len(data['type']) > 0
                
                if 'data' in data:
                    assert data['data'] is not None

    @pytest.mark.asyncio 
    async def test_websocket_send_invalid_json(self, server_process):
        """Test server handling of invalid JSON messages."""
        import websockets
        
        async with websockets.connect('ws://localhost:3000') as websocket:
            # Skip initial server-list message
            await asyncio.wait_for(websocket.recv(), timeout=5)
            
            # Send invalid JSON
            await websocket.send("invalid json message")
            
            # Server should handle gracefully - either ignore or send error
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=3)
                # If we get a response, it should be valid JSON
                data = json.loads(response)
                # If it's an error message, that's expected
                if data.get('type') == 'error':
                    assert 'message' in data
            except asyncio.TimeoutError:
                # No response is also acceptable - server might ignore invalid messages
                pass

    @pytest.mark.asyncio
    async def test_websocket_connection_persistence(self, server_process):
        """Test that WebSocket connections remain stable."""
        import websockets
        
        async with websockets.connect('ws://localhost:3000') as websocket:
            # Initial connection and message
            initial_msg = await asyncio.wait_for(websocket.recv(), timeout=5)
            data = json.loads(initial_msg)
            assert data.get('type') == 'server-list'
            
            # Wait a bit to ensure connection stability
            await asyncio.sleep(2)
            
            # Connection should still be open
            assert websocket.open
            
            # Should be able to send a message
            test_msg = {
                "type": "connect", 
                "data": {"server": "dworld"}
            }
            await websocket.send(json.dumps(test_msg))
            
            # Should receive a response
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            data = json.loads(response)
            assert 'type' in data

    @pytest.mark.asyncio
    async def test_websocket_binary_message_handling(self, server_process):
        """Test that the server can handle binary WebSocket messages."""
        import websockets
        
        async with websockets.connect('ws://localhost:3000') as websocket:
            # Skip initial server-list message
            await asyncio.wait_for(websocket.recv(), timeout=5)
            
            # Send binary message (JSON as bytes)
            test_msg = {
                "type": "connect",
                "data": {"server": "dworld"}
            }
            binary_msg = json.dumps(test_msg).encode('utf-8')
            await websocket.send(binary_msg)
            
            # Should receive a response
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            data = json.loads(response)
            assert 'type' in data
            # Should be server-join or error
            assert data['type'] in ['server-join', 'error']

    def test_websocket_integration_with_existing_client(self, server_process):
        """Test WebSocket functionality using the existing mock client."""
        # Run the existing mock websocket client
        client_proc = subprocess.Popen(
            [sys.executable, "helpers/mock_websocket_client.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd="tests",
            text=True
        )
        
        try:
            stdout, stderr = client_proc.communicate(timeout=10)
            
            # Verify expected output patterns
            assert "Connected to ws://localhost:3000" in stdout
            assert "[RECV]" in stdout  # Should receive messages
            assert "[SEND]" in stdout  # Should send connect message
            
            # Should receive server-list and server-join messages
            assert "server-list" in stdout or "server-join" in stdout
            
        finally:
            client_proc.terminate()