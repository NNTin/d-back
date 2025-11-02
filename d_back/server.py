"""WebSocket Server Implementation for D-Zone/D-World Discord Integration.

This module provides the core WebSocket server functionality for real-time communication
with Discord-like applications. It handles WebSocket connections, HTTP static file serving,
message broadcasting, user presence updates, and OAuth2 authentication.

The server supports:
    - WebSocket connections for real-time bidirectional communication
    - HTTP static file serving on the same port (websockets 10.0+)
    - Multiple Discord server configurations
    - User authentication via Discord OAuth2
    - Custom callback registration for data providers
    - Mock data generation for testing and development

Example:
    Basic server setup::

        from d_back.server import WebSocketServer
        
        server = WebSocketServer(port=3000, host="localhost")
        await server.run_forever()

    With custom callbacks::

        def get_servers():
            return {"server_id": {"id": "server_id", "name": "My Server"}}
        
        def get_users(server_id):
            return {"user123": {"uid": "user123", "username": "TestUser"}}
        
        server = WebSocketServer()
        server.on_get_server_data(get_servers)
        server.on_get_user_data(get_users)
        await server.run_forever()
"""
import asyncio
import websockets
import json
import traceback
import random
import mimetypes
import argparse
from pathlib import Path
from typing import Dict, Any, Callable, Awaitable, Optional, Tuple

from .mock import MockDataProvider


class WebSocketServer:
    """WebSocket server for managing real-time connections and broadcasting messages.

    This server handles WebSocket connections for Discord-like applications, providing
    real-time communication, user presence management, message broadcasting, and
    static file serving. It supports custom data providers through callback registration
    and includes mock data functionality for testing.

    The server automatically detects websockets library version and enables HTTP support
    when available (websockets 10.0+ with Python 3.8+).

    Attributes:
        port (int): The port number the server listens on.
        host (str): The hostname or IP address the server binds to.
        server: The websockets server instance.
        connections (set): Set of active WebSocket connections.
        static_dir (Path): Directory path for serving static files.
        mock_provider (MockDataProvider): Provider for mock test data.

    Example:
        Basic usage::

            server = WebSocketServer(port=3000, host="localhost")
            await server.run_forever()

        With custom data callbacks::

            def get_servers():
                return {
                    "server1": {"id": "server1", "name": "My Server", "default": True}
                }
            
            def get_users(server_id):
                return {
                    "user123": {
                        "uid": "user123",
                        "username": "JohnDoe",
                        "status": "online",
                        "roleColor": "#3498db"
                    }
                }
            
            server = WebSocketServer()
            server.on_get_server_data(get_servers)
            server.on_get_user_data(get_users)
            await server.run_forever()
    """
    
    def __init__(self, port: int = 3000, host: str = "localhost"):
        """Initialize the WebSocket server.

        Args:
            port: The port number to listen on. Defaults to 3000.
            host: The hostname or IP address to bind to. Defaults to "localhost".
                  Use "0.0.0.0" to accept connections from any interface.

        Note:
            The server initializes with mock data provider by default. Register custom
            callbacks using on_get_server_data() and on_get_user_data() to override
            mock data behavior.
        """
        self.port = port
        self.host = host
        self.server = None  # WebSocket server instance
        self.connections: set = set()  # Store active connections
        self._on_get_server_data: Optional[Callable[[], Awaitable[Dict[str, Dict[str, Any]]]]] = None
        self._on_get_user_data: Optional[Callable[[str], Awaitable[Dict[str, Dict[str, Any]]]]] = None
        self._on_static_request: Optional[Callable[[str], Awaitable[Optional[Tuple[str, str]]]]] = None
        self.static_dir = Path(__file__).parent / "dist"  # Default static directory
        self._on_validate_discord_user: Optional[Callable[[str, Dict[str, Any], str], Awaitable[bool]]] = None
        self._on_get_client_id: Optional[Callable[[str], Awaitable[str]]] = None
        self.mock_provider = MockDataProvider(self)  # Mock data provider
    
    async def start(self) -> None:
        """Start the WebSocket server and wait for it to close.

        This method initializes the websockets server with the configured host and port,
        registers the connection handler and HTTP request processor, and then waits
        for the server to close.

        Returns:
            None

        Raises:
            OSError: If the port is already in use or network binding fails.
            Exception: For other server startup failures.

        Note:
            This method blocks until the server is stopped. Use run_forever() for
            a more convenient async context manager approach.
        """
        self.server = await websockets.serve(
            self._handler, 
            self.host, 
            self.port, 
            process_request=self._process_request
        )
        print(f"WebSocket server started on ws://{self.host}:{self.port}")
        await self.server.wait_closed()
  
    async def stop(self) -> None:
        """Gracefully stop the WebSocket server.

        This method closes the server and waits for all existing connections to terminate.
        Active connections are allowed to finish their current operations before shutdown.

        Returns:
            None

        Note:
            After calling this method, the server can be restarted by calling start() again.
        """
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            print("WebSocket server stopped")

    async def broadcast_message(self, server: str, uid: str, message: str, channel: str) -> None:
        """Broadcast a chat message to all clients connected to the specified server.

        Sends a message from a user to all WebSocket clients currently connected to
        the same Discord server. Automatically handles connection failures and removes
        closed connections.

        Args:
            server: The Discord server ID where the message is sent.
            uid: The user ID of the message sender.
            message: The text content of the message.
            channel: The channel ID where the message is posted.

        Returns:
            None

        Raises:
            websockets.ConnectionClosed: When attempting to send to a closed connection
                (handled internally, connection is removed).

        Examples:

            await server.broadcast_message(
                server="232769614004748288",
                uid="user123",
                message="Hello everyone!",
                channel="general"
            )
        """
        # Filter connections to only include those connected to the specified server
        # Use discordServer like the original implementation
        server_connections = [ws for ws in self.connections if hasattr(ws, 'discordServer') and ws.discordServer == server]
        
        if not server_connections:
            print(f"[INFO] No connections to broadcast to for server: {server}")
            return
            
        msg = {
            "type": "message",
            "server": server,
            "data": {
                "uid": uid,
                "message": message,
                "channel": channel
            }
        }

        print(f"[BROADCAST] Sending message to {len(server_connections)} connections on server {server}: {message}")
        
        # Create a copy to avoid modification during iteration
        connections_copy = server_connections.copy()
        
        for websocket in connections_copy:
            try:
                await websocket.send(json.dumps(msg))
            except websockets.ConnectionClosed:
                print("[INFO] Removed closed connection during broadcast")
                # Remove closed connections
                self.connections.discard(websocket)
            except Exception as e:
                print(f"[ERROR] Failed to send message to connection: {e}")
                # Optionally remove problematic connections
                self.connections.discard(websocket)

    def on_get_server_data(self, callback: Callable[[], Awaitable[Dict[str, Dict[str, Any]]]]) -> None:
        """Register a callback to provide server configuration data.

        The callback function will be called to retrieve the list of available Discord
        servers and their configurations. This overrides the default mock data provider.

        Args:
            callback: An async callable that returns a dictionary of server configurations.
                Expected signature: async def callback() -> Dict[str, Dict[str, Any]]
                Each server dict should contain: id, name, default (bool), passworded (bool)

        Returns:
            None

        Examples:

            async def get_servers():
                return {
                    "server1": {
                        "id": "server1",
                        "name": "My Server",
                        "default": True,
                        "passworded": False
                    }
                }
            
            server.on_get_server_data(get_servers)
        """
        self._on_get_server_data = callback
    
    def on_get_user_data(self, callback: Callable[[str], Awaitable[Dict[str, Dict[str, Any]]]]) -> None:
        """Register a callback to provide user data for a specific server.

        The callback function will be called to retrieve user information for clients
        connecting to a Discord server. This overrides the default mock data provider.

        Args:
            callback: An async callable that takes a server ID and returns user data.
                Expected signature: async def callback(server_id: str) -> Dict[str, Dict[str, Any]]
                Each user dict should contain: uid, username, status, roleColor

        Returns:
            None

        Examples:

            async def get_users(server_id):
                return {
                    "user123": {
                        "uid": "user123",
                        "username": "JohnDoe",
                        "status": "online",
                        "roleColor": "#3498db"
                    }
                }
            
            server.on_get_user_data(get_users)
        """
        self._on_get_user_data = callback

    def on_static_request(self, callback: Callable[[str], Awaitable[Optional[Tuple[str, str]]]]) -> None:
        """Register a callback for custom static file handling.
        
        The callback function allows you to serve custom content for specific paths,
        overriding the default static file handler. Return None to use default handling.

        Args:
            callback: An async callable that takes a path and returns custom content.
                Expected signature: async def callback(path: str) -> Optional[Tuple[str, str]]
                Return None to let default handler process the request, or
                return (content_type, content) to serve custom content.

        Returns:
            None

        Examples:

            async def custom_handler(path):
                if path == "/api/custom":
                    return "application/json", '{"status": "ok"}'
                return None  # Let default handler take over
            
            server.on_static_request(custom_handler)
        """
        self._on_static_request = callback

    def on_validate_discord_user(self, callback: Callable[[str, Dict[str, Any], str], Awaitable[bool]]) -> None:
        """Register a callback to validate Discord OAuth users.

        The callback function will be called to verify Discord OAuth tokens and
        validate user permissions for accessing the WebSocket server.

        Args:
            callback: An async callable that validates a Discord OAuth token and user info.
                Expected signature: async def callback(token: str, user_info: Dict[str, Any], server_id: str) -> bool
                Should return True if the user is valid and authorized.

        Returns:
            None

        Examples:

            async def validate_user(token, user_info, server_id):
                # Verify token with Discord API
                # Check user permissions for the specific server
                return is_valid and is_authorized
            
            server.on_validate_discord_user(validate_user)
        """
        self._on_validate_discord_user = callback

    def on_get_client_id(self, callback: Callable[[str], Awaitable[str]]) -> None:
        """Register a callback to provide the OAuth2 client ID.

        The callback function should return the Discord OAuth2 application client ID
        used for authentication. This is sent to connecting clients for OAuth flow.

        Args:
            callback: An async callable that returns the OAuth2 client ID for a server.
                Expected signature: async def callback(server_id: str) -> str
                Should return the Discord application client ID string.

        Returns:
            None

        Examples:

            async def get_client_id(server_id):
                return "123456789012345678"
            
            server.on_get_client_id(get_client_id)
        """
        self._on_get_client_id = callback

    async def run_forever(self) -> None:
        """Run the server forever with automatic HTTP support detection.

        This method starts the WebSocket server and automatically detects whether
        HTTP static file serving is supported based on the Python version and websockets
        library version. Falls back to WebSocket-only mode if HTTP support is unavailable.

        HTTP support requires:
            - Python 3.8 or higher
            - websockets 10.0 or higher
            - Available HTTP import modules (websockets.http11 or websockets.http)

        Returns:
            None

        Raises:
            Exception: If server fails to start on the configured host and port.
            KeyboardInterrupt: When server is interrupted by user (handled gracefully).

        Examples:

            server = WebSocketServer(port=3000)
            await server.run_forever()  # Runs until interrupted

        Note:
            This method runs indefinitely until interrupted. Use asyncio.create_task()
            if you need to run other async operations concurrently.
        """
        # For Python 3.8+ compatibility, start with WebSocket-only mode
        # and only try HTTP if we're confident it will work
        has_http_support = False
        
        try:
            import websockets
            # Check websockets version
            websockets_version = tuple(map(int, websockets.__version__.split('.')[:2]))
            
            # Try HTTP support on Python 3.8+ with websockets 10.0+
            import sys
            python_version = sys.version_info[:2]
            
            if python_version >= (3, 8) and websockets_version >= (10, 0):
                try:
                    # Quick test of HTTP imports
                    from websockets.http11 import Response  # noqa: F401
                    from websockets.http import Headers  # noqa: F401
                    has_http_support = True
                    print(f"[DEBUG] HTTP support enabled (Python {python_version}, websockets {websockets.__version__})")
                except ImportError:
                    try:
                        from websockets.http import Response, Headers  # noqa: F401
                        has_http_support = True
                        print("[DEBUG] HTTP support enabled with fallback imports")
                    except ImportError:
                        print("[DEBUG] HTTP imports not available, using WebSocket-only mode")
            else:
                print(f"[DEBUG] WebSocket-only mode (Python {python_version}, websockets {websockets.__version__} - version too old for HTTP)")
                
        except Exception as e:
            print(f"[WARNING] Error checking HTTP support, falling back to WebSocket-only: {e}")
            has_http_support = False
            
        if has_http_support:
            try:
                async with websockets.serve(
                    self._handler, 
                    self.host, 
                    self.port, 
                    process_request=self._process_request
                ):
                    print(f"Mock WebSocket server running on ws://{self.host}:{self.port} (with HTTP support)")
                    await asyncio.Future()  # run forever
            except Exception as e:
                print(f"[WARNING] Failed to start with HTTP support: {e}")
                print("[INFO] Falling back to WebSocket-only mode")
                has_http_support = False
        
        if not has_http_support:
            async with websockets.serve(
                self._handler, 
                self.host, 
                self.port
            ):
                print(f"Mock WebSocket server running on ws://{self.host}:{self.port} (WebSocket-only mode)")
                await asyncio.Future()  # run forever

    def _random_color(self) -> str:
        """Generate a random color hex code."""
        return '#{:06x}'.format(random.randint(0, 0xFFFFFF))

    def _random_status(self) -> str:
        """Get a random user status."""
        return random.choice(["online", "idle", "dnd", "offline"])

    def _get_http_classes(self):
        """Get HTTP classes for websockets compatibility.
        
        Returns:
            tuple: (use_new_http: bool, Response, Headers, websockets_version) 
        """
        try:
            import websockets
            websockets_version = tuple(map(int, websockets.__version__.split('.')[:2]))
            
            # HTTP support is available from websockets 10.0+
            if websockets_version >= (10, 0):
                Response = None
                Headers = None
                
                # Try to get Response class for websockets 11+ (but prioritize http11 for 12+)
                if websockets_version >= (12, 0):
                    # For websockets 12+, try http11.Response first
                    try:
                        from websockets.http11 import Response
                        print(f"[DEBUG] Found http11.Response for websockets {websockets.__version__}")
                    except ImportError:
                        print(f"[DEBUG] No http11.Response found for websockets {websockets.__version__}")
                elif websockets_version >= (11, 0):
                    # For websockets 11.x, try http.Response 
                    try:
                        from websockets.http import Response
                        print(f"[DEBUG] Found http.Response for websockets {websockets.__version__}")
                    except ImportError:
                        print(f"[DEBUG] No http.Response found for websockets {websockets.__version__}")
                
                # Try to get Headers class for all versions 10+
                try:
                    from websockets.http import Headers
                    print(f"[DEBUG] Found http.Headers for websockets {websockets.__version__}")
                except ImportError:
                    try:
                        from websockets.datastructures import Headers
                        print(f"[DEBUG] Found datastructures.Headers for websockets {websockets.__version__}")
                    except ImportError:
                        print(f"[DEBUG] No Headers class found for websockets {websockets.__version__}")
                        Headers = None
                
                print(f"[DEBUG] HTTP support enabled (websockets {websockets.__version__})")
                return True, Response, Headers, websockets_version
            else:
                # Very old versions without HTTP support
                print(f"[DEBUG] HTTP support disabled (websockets {websockets.__version__} < 10.0)")
                return False, None, None, websockets_version
        except Exception as e:
            print(f"[ERROR] Error detecting websockets version: {e}")
            return False, None, None, (0, 0)

    def _create_http_response(self, status_code, reason, content_type, body, use_new_http, Response, Headers, websockets_version):
        """Create an HTTP response compatible with different websockets versions."""
        try:
            print(f"[DEBUG] Creating HTTP response for websockets {websockets_version}, use_new_http={use_new_http}")
            
            if not use_new_http:
                # For very old versions without HTTP support
                print("[DEBUG] No HTTP support available, returning None")
                return None
            
            import http
            status = http.HTTPStatus(status_code)
            body_bytes = body if isinstance(body, bytes) else body.encode('utf-8')
            
            # For websockets 10-13, use tuple format (HTTPResponse)
            # HTTPResponse = Tuple[Union[HTTPStatus, int], HeadersLike, bytes]
            if websockets_version[0] <= 13:
                print(f"[DEBUG] Using tuple format (HTTPResponse) for websockets {websockets_version[0]}.x")
                
                # Create headers - prefer Headers class if available, otherwise use list of tuples
                if Headers is not None:
                    headers = Headers([("Content-Type", content_type)])
                    print(f"[DEBUG] Using Headers class: {headers}")
                else:
                    # Fallback to list of tuples
                    headers = [("Content-Type", content_type)]
                    print(f"[DEBUG] Using list of tuples for headers: {headers}")
                
                # Return tuple format: (HTTPStatus, HeadersLike, bytes)
                response_tuple = (status, headers, body_bytes)
                print(f"[DEBUG] Created tuple response: status={status}, headers={len(headers) if hasattr(headers, '__len__') else 'N/A'}, body_len={len(body_bytes)}")
                return response_tuple
            
            # For websockets 14+, try to use Response class
            elif websockets_version >= (14, 0):
                print("[DEBUG] Using Response object for websockets 14+")
                
                if Response is not None:
                    try:
                        # For websockets 14+, Response constructor expects:
                        # Response(status_code: int, reason_phrase: str, headers: Headers, body: bytes)
                        status_code = status.value  # Convert HTTPStatus to int
                        reason_phrase = status.phrase  # Get reason phrase string
                        headers_obj = Headers([("Content-Type", content_type)]) if Headers else [("Content-Type", content_type)]
                        response = Response(status_code, reason_phrase, headers_obj, body_bytes)
                        print(f"[DEBUG] Successfully created Response: status={status_code}, reason='{reason_phrase}', headers={headers_obj}, body_len={len(body_bytes)}")
                        return response
                    except Exception as e:
                        print(f"[DEBUG] Response creation failed: {e}")
                        # Fallback to tuple format
                        print("[DEBUG] Falling back to tuple format")
                        headers = Headers([("Content-Type", content_type)]) if Headers else [("Content-Type", content_type)]
                        return (status, headers, body_bytes)
                else:
                    print("[DEBUG] No Response class available, using tuple format")
                    headers = Headers([("Content-Type", content_type)]) if Headers else [("Content-Type", content_type)]
                    return (status, headers, body_bytes)
            else:
                print("[DEBUG] Using basic format for older websockets")
                return None
                
        except Exception as e:
            print(f"[ERROR] Failed to create HTTP response: {e}")
            traceback.print_exc()
            return None

    async def _process_request(self, path, request_headers):
        """Process incoming HTTP and WebSocket upgrade requests.

        Determines whether an incoming request is a WebSocket upgrade or HTTP request
        and routes it appropriately. Handles different parameter formats across various
        websockets library versions (10.x, 13.x, 15.x).

        Args:
            path: Request path string or connection object (version-dependent)
            request_headers: Headers object or Request object (version-dependent)

        Returns:
            Response: HTTP response object for static file requests
            None: For WebSocket upgrade requests (allows handshake to proceed)

        Raises:
            Exception: Logs errors but attempts fallback to static file serving
        """
        
        # Handle different parameter types across websockets versions
        actual_path = path
        actual_headers = request_headers
        
        # Debug the actual parameters we received
        print(f"[DEBUG] path parameter type: {type(path)}")
        print(f"[DEBUG] request_headers parameter type: {type(request_headers)}")
        
        # Different websockets versions pass parameters differently:
        # - websockets 15.x: path might be connection, request_headers is Request object with .path
        # - websockets 13.x: path is Headers object, request_headers is missing/None  
        # - websockets 10.x: path is string, request_headers is Headers
        try:
            if hasattr(request_headers, 'path'):
                # websockets 15.x: request_headers is actually a Request object
                actual_path = request_headers.path
                actual_headers = request_headers.headers
                print(f"[PROCESS_REQUEST] Incoming request to path: {actual_path} (from Request object)")
            elif hasattr(path, 'get') and hasattr(path, 'items'):
                # websockets 13.x: path is actually Headers object, there's no separate path
                # We need to extract path from the request line or default to "/"
                actual_path = "/"  # Default path since it's not provided separately
                actual_headers = path  # path parameter is actually the headers
                print(f"[PROCESS_REQUEST] Incoming request to path: {actual_path} (Headers as path parameter)")
                print(f"[DEBUG] Request object type: {type(path)}")
                print(f"[DEBUG] Request attributes: {[attr for attr in dir(path) if not attr.startswith('_')]}")
            elif isinstance(path, str):
                # websockets 10.x: Standard case with string path and Headers
                actual_path = path  
                actual_headers = request_headers
                print(f"[PROCESS_REQUEST] Incoming request to path: {actual_path} (standard)")
            else:
                # Fallback: try to extract info from objects
                actual_path = getattr(request_headers, 'path', str(path))
                actual_headers = getattr(request_headers, 'headers', request_headers)
                print(f"[PROCESS_REQUEST] Incoming request to path: {actual_path} (fallback extraction)")
                
            print(f"[DEBUG] Final headers type: {type(actual_headers)}")
            
            # Try to convert headers to dict for logging (safely)
            try:
                if hasattr(actual_headers, 'items'):
                    headers_dict = dict(actual_headers.items())
                elif hasattr(actual_headers, '__iter__') and not isinstance(actual_headers, str):
                    headers_dict = dict(actual_headers)  
                else:
                    headers_dict = str(actual_headers)
                print(f"[DEBUG] Request headers: {headers_dict}")
            except Exception as e:
                print(f"[DEBUG] Could not convert headers to dict: {e}")
                print(f"[DEBUG] Headers object: {actual_headers}")
        except Exception as e:
            # Ultimate fallback
            print(f"[ERROR] Error parsing request parameters: {e}")
            actual_path = "/"
            actual_headers = request_headers
        
        # Check if this is a WebSocket upgrade request by checking headers
        try:
            # Handle different header access methods
            if hasattr(actual_headers, 'get'):
                upgrade = actual_headers.get("Upgrade", "").lower()
                connection = actual_headers.get("Connection", "").lower()
            elif hasattr(actual_headers, '__getitem__'):
                try:
                    upgrade = actual_headers["Upgrade"].lower()
                except (KeyError, AttributeError):
                    upgrade = ""
                try:
                    connection = actual_headers["Connection"].lower() 
                except (KeyError, AttributeError):
                    connection = ""
            else:
                upgrade = ""
                connection = ""
            
            print(f"[DEBUG] Upgrade header: '{upgrade}', Connection header: '{connection}'")
            
            # If this has WebSocket upgrade headers, let it proceed as WebSocket
            if upgrade == "websocket" and "upgrade" in connection:
                print("[PROCESS_REQUEST] WebSocket upgrade request detected")
                return None  # Let websocket handshake proceed
            
            # Otherwise, serve as HTTP static file
            print(f"[HTTP] Serving static content for path: {actual_path}")
            http_response = await self._serve_static_file(actual_path)
            print(f"[DEBUG] HTTP response created: {type(http_response)}")
            return http_response
            
        except Exception as e:
            print(f"[ERROR] Error in _process_request: {e}")
            traceback.print_exc()
            # If something goes wrong, serve as static file
            http_response = await self._serve_static_file(actual_path)
            print(f"[DEBUG] Fallback HTTP response: {type(http_response)}")
            return http_response

    async def _serve_static_file(self, path: str):
        """Serve static files and handle special API endpoints via HTTP.

        Serves files from the static directory, processes custom static request callbacks,
        and handles the /api/version endpoint. Includes security checks to prevent
        directory traversal attacks.

        Args:
            path: URL path requested by the client

        Returns:
            Response: HTTP response object with appropriate status, headers, and content

        Raises:
            Exception: Returns 500 Internal Server Error response on failures
        """
        try:
            # Get HTTP classes for compatibility
            use_new_http, Response, Headers, websockets_version = self._get_http_classes()
            
            # Remove query parameters from path for routing
            clean_path = path.split('?')[0]
            
            # Handle custom static request callback first
            if self._on_static_request:
                result = await self._on_static_request(clean_path)
                if result is not None:
                    content_type, file_path = result
                    file_path = Path(file_path).resolve()
                    # Check if file exists
                    if not file_path.exists() or not file_path.is_file():
                        return self._create_http_response(404, "Not Found", "text/html", b"<h1>404 Not Found</h1><p>The requested file was not found.</p>", use_new_http, Response, Headers, websockets_version)
                    
                    with open(file_path, "rb") as f:
                        content = f.read()
                        
                    return self._create_http_response(200, "OK", content_type, content, use_new_http, Response, Headers, websockets_version)
            
            # Handle special API endpoints
            if clean_path == "/api/version":
                
                return await self._serve_version_api()
            
            # Default file serving
            if clean_path == "/" or clean_path == "":
                clean_path = "/index.html"
            
            # Remove leading slash and resolve file path
            file_path = self.static_dir / clean_path.lstrip("/")
            
            # Security check - ensure we're not serving files outside static_dir
            try:
                file_path = file_path.resolve()
                self.static_dir.resolve()
                if not str(file_path).startswith(str(self.static_dir.resolve())):
                    return self._create_http_response(403, "Forbidden", "text/plain", b"Forbidden", use_new_http, Response, Headers, websockets_version)
            except (OSError, ValueError):
                return self._create_http_response(403, "Forbidden", "text/plain", b"Forbidden", use_new_http, Response, Headers, websockets_version)
            
            # Check if file exists
            if not file_path.exists() or not file_path.is_file():
                return self._create_http_response(404, "Not Found", "text/html", b"<h1>404 Not Found</h1><p>The requested file was not found.</p>", use_new_http, Response, Headers, websockets_version)
            
            # Determine content type
            content_type, _ = mimetypes.guess_type(str(file_path))
            if content_type is None:
                content_type = "application/octet-stream"
            
            # Read and return file
            with open(file_path, "rb") as f:
                content = f.read()
            
            return self._create_http_response(200, "OK", content_type, content, use_new_http, Response, Headers, websockets_version)
            
        except Exception as e:
            print(f"[ERROR] Failed to serve static file {path}: {e}")
            traceback.print_exc()
            # Get HTTP classes again for error response
            use_new_http, Response, Headers, websockets_version = self._get_http_classes()
            return self._create_http_response(500, "Internal Server Error", "text/plain", b"Internal Server Error", use_new_http, Response, Headers, websockets_version)

    async def _serve_version_api(self):
        """Serve package version information as JSON API endpoint.

        Handles GET requests to /api/version and returns the current package
        version in JSON format.

        Returns:
            Response: HTTP response with JSON containing {"version": "x.y.z"}

        Raises:
            Exception: Returns 500 Internal Server Error response on failures
        """
        try:
            # Get HTTP classes for compatibility
            use_new_http, Response, Headers, websockets_version = self._get_http_classes()
            
            try:
                from . import __version__
                version_data = {"version": __version__}
            except ImportError as e:
                print(f"[WARNING] Could not import version: {e}")
                version_data = {"version": "unknown"}
            
            return self._create_http_response(200, "OK", "application/json", json.dumps(version_data).encode(), use_new_http, Response, Headers, websockets_version)
        
        except Exception as e:
            print(f"[ERROR] Failed to serve version API: {e}")
            # Get HTTP classes again for error response
            use_new_http, Response, Headers, websockets_version = self._get_http_classes()
            return self._create_http_response(500, "Internal Server Error", "text/plain", b"Internal Server Error", use_new_http, Response, Headers, websockets_version)

    async def _handler(self, websocket, path=None) -> None:
        """Handle WebSocket connections, authentication, and message routing.

        Main WebSocket connection handler that manages the connection lifecycle,
        sends initial server list, processes incoming messages, and handles errors.
        Automatically cleans up connections on disconnect.

        Args:
            websocket: WebSocket connection object
            path: Optional URL path from the connection (may be None)

        Returns:
            None

        Raises:
            websockets.ConnectionClosed: Handled gracefully on disconnect
            Exception: Logged and cleaned up
        """
        print(f"[CONNECT] Client connected to path: {path}")
        # Store the connection
        self.connections.add(websocket)
        
        try:
            # Send server list immediately on connect (like the original)
            print("[SEND] server-list")
            
            if self._on_get_server_data:
                server_data = await self._on_get_server_data()
            else:
                # simulate getting server data
                server_data = self.mock_provider.get_mock_server_data()

            await websocket.send(json.dumps({
                "type": "server-list",
                "data": server_data
            }))
            
            # Wait for messages from client
            async for message in websocket:
                # Accept both text and binary messages
                if isinstance(message, bytes):
                    try:
                        message = message.decode('utf-8')
                        print(f"[RECV] Decoded binary message: {message}")
                    except Exception as e:
                        print(f"[ERROR] Failed to decode binary message: {e}")
                        traceback.print_exc()
                        await websocket.send(json.dumps({"type": "error", "data": {"message": "Invalid binary encoding"}}))
                        continue
                else:
                    print(f"[RECV] Raw message: {message}")
                
                try:
                    data = json.loads(message)
                    print(f"[PARSE] Parsed message: {data}")
                except Exception as e:
                    print(f"[ERROR] Failed to parse JSON: {e}")
                    traceback.print_exc()
                    await websocket.send(json.dumps({"type": "error", "data": {"message": "Invalid JSON"}}))
                    continue
                
                if data.get("type") == "connect":
                    await self._handle_connect(websocket, data)
                else:
                    print(f"[ERROR] Unknown event type: {data.get('type')}")
                    await websocket.send(json.dumps({"type": "error", "data": {"message": "Unknown event type"}}))
                    
        except websockets.ConnectionClosed as e:
            print(f"[DISCONNECT] Client disconnected: {e}")
        except Exception as e:
            print(f"[FATAL ERROR] {e}")
            traceback.print_exc()
        finally:
            # Remove the connection when it's closed
            self.connections.discard(websocket)

    async def _handle_connect(self, websocket, data: Dict[str, Any]) -> None:
        """Handle client connection requests to Discord servers with authentication.

        Processes connection requests, validates authentication (OAuth2 or legacy password),
        retrieves user data for the requested server, and sends join confirmation. Starts
        mock data providers if using default mock data.

        Args:
            websocket: WebSocket connection object
            data: Connection request data containing:
                - server: Server ID to connect to
                - password: Optional legacy password
                - discordToken: Optional OAuth2 access token
                - discordUser: Optional OAuth2 user information

        Returns:
            None

        Raises:
            Exception: Sends error message to client on failure
        """
        server_id = data["data"].get("server", "default")
        
        # Normalize incoming server_id: coerce to string, strip whitespace, treat empty/None as 'default'
        if server_id is None or (isinstance(server_id, str) and not server_id.strip()):
            server_id = "default"
        else:
            server_id = str(server_id).strip()
        
        password = data["data"].get("password", None)  # Legacy password support
        discord_token = data["data"].get("discordToken", None)  # OAuth2 token
        discord_user = data["data"].get("discordUser", None)    # OAuth2 user info
        
        print(f"[EVENT] Client requests connect to server: {server_id}")
        if password:
            print("[AUTH] Using legacy password authentication")
        elif discord_token:
            print(f"[AUTH] Using Discord OAuth2 authentication for user: {discord_user.get('username') if discord_user else 'unknown'}")
        
        # Get server and user data using callbacks or mock data
        if self._on_get_server_data:
            server_data = await self._on_get_server_data()
        else:
            server_data = self.mock_provider.get_mock_server_data()
            
        # Find the server (similar to inbox.js getUsers logic)
        server_info = None
        discord_server_id = None
        
        # Before the loop: Log search criteria and available data
        print(f"[DEBUG] Looking for server with ID: '{server_id}' (type: {type(server_id).__name__})")
        print(f"[DEBUG] Search type: {'DEFAULT SERVER LOOKUP' if server_id == 'default' else 'EXACT ID MATCH'}")
        print(f"[DEBUG] Total servers available: {len(server_data)}")
        print(f"[DEBUG] Available servers: {server_data}")
        
        # Look for exact server ID match or default server
        for discord_id, server in server_data.items():
            # Inside the loop: Detailed logging for each server check
            server_id_value = server.get("id", "MISSING")
            default_flag = server.get("default", False)
            exact_match = server_id_value == server_id
            default_match = default_flag and server_id == "default"
            
            print(f"[DEBUG] Checking server discord_id='{discord_id}':")
            print(f"  - server['id']='{server_id_value}' (type: {type(server_id_value).__name__})")
            print(f"  - server.get('default')={default_flag}")
            print(f"  - Exact match (server['id'] == server_id): {exact_match}")
            print(f"  - Default match (default={default_flag} AND server_id=='default'): {default_match}")
            print(f"  - Overall condition result: {exact_match or default_match}")
            
            if server_id_value == server_id or (server.get("default") and server_id == "default"):
                server_info = server
                discord_server_id = discord_id
                match_reason = "EXACT ID MATCH" if exact_match else "DEFAULT SERVER MATCH"
                print(f"[DEBUG] ✓ MATCH FOUND via {match_reason}: {server_info} with Discord ID: {discord_server_id}")
                break
        
        # After the loop: Enhanced error logging if no match found
        if not server_info:
            available_ids = [s.get("id", "MISSING") for s in server_data.values()]
            default_servers = [s.get("id", "MISSING") for s in server_data.values() if s.get("default")]
            print(f"[ERROR] Unknown server: '{server_id}'")
            print(f"[ERROR] Requested server_id: '{server_id}' (type: {type(server_id).__name__})")
            print(f"[ERROR] Available server IDs in data: {available_ids}")
            print(f"[ERROR] Servers with default=True: {default_servers if default_servers else 'NONE'}")
            print(f"[ERROR] Total servers checked: {len(server_data)}")
            await websocket.send(json.dumps({
                "type": "error", 
                "data": {"message": "Sorry, couldn't connect to that Discord server."}
            }))
            return
            
        # Check authentication for passworded servers
        if server_info.get("passworded"):
            auth_valid = False
            
            # Try Discord OAuth2 first (preferred method)
            if discord_token and discord_user:
                print(f"[AUTH] Attempting OAuth2 validation for user: {discord_user.get('username')} ({discord_user.get('id')}) on server {discord_server_id}")
                auth_valid = await self._validate_discord_oauth(discord_token, discord_user, discord_server_id)
                if not auth_valid:
                    print(f"[ERROR] Discord OAuth2 validation failed for server {server_id}")
                    await websocket.send(json.dumps({
                        "type": "error", 
                        "data": {"message": "Discord authentication failed. Please try logging in again."}
                    }))
                    return
                else:
                    print(f"[AUTH] Discord OAuth2 validation successful for user {discord_user.get('username')}")
            # Fallback to legacy password (for backward compatibility)
            elif password and server_info.get("password") == password:
                auth_valid = True
                print("[AUTH] Legacy password authentication successful")
            
            if not auth_valid:
                print(f"[ERROR] Authentication failed for passworded server {server_id}")
                print(f"[DEBUG] discord_token present: {bool(discord_token)}")
                print(f"[DEBUG] discord_user present: {bool(discord_user)}")
                print(f"[DEBUG] password present: {bool(password)}")
                await websocket.send(json.dumps({
                    "type": "error", 
                    "data": {"message": "This server requires Discord authentication. Please login with Discord."}
                }))
                return
        
        # Store the Discord server ID in the websocket connection (like original)
        websocket.discordServer = discord_server_id
        websocket.server_id = server_id  # Keep for compatibility
        
        # Get user data for this server
        if self._on_get_user_data:
            user_data = await self._on_get_user_data(discord_server_id)
        else:
            user_data = self.mock_provider.get_mock_user_data(discord_server_id)
        
        print(f"[SUCCESS] Client joined server {server_info['name']}")
        print("[SEND] server-join")
        
        # Prepare request data for response (don't include sensitive auth info)
        request_data = {"server": server_id}
        if password:  # Only include password for legacy compatibility
            request_data["password"] = password
        
        # Get the client ID for this server
        client_id = None
        if self._on_get_client_id:
            try:
                client_id = await self._on_get_client_id(discord_server_id)
                print(f"[DEBUG] Got client ID for server {discord_server_id}: {client_id}")
            except Exception as e:
                print(f"[ERROR] Failed to get client ID: {e}")
        
        response_data = {
            "users": user_data,
            "request": request_data,
            "serverName": server_info['name']
        }
        
        # Include client ID if available
        if client_id:
            response_data["clientId"] = client_id
            
        await websocket.send(json.dumps({
            "type": "server-join",
            "data": response_data
        }))
        
        # Only start mock data if using mock data (not when using real callbacks)
        if not self._on_get_user_data and not self._on_get_server_data:
            # Start background tasks for mock data
            asyncio.create_task(self.mock_provider.periodic_messages(websocket))
            asyncio.create_task(self.mock_provider.periodic_status_updates(websocket))

    async def _validate_discord_oauth(self, token: str, user_info: Dict[str, Any], discord_server_id: str) -> bool:
        """Validate Discord OAuth2 token and verify user server membership.

        Checks OAuth2 token validity and user information. Uses custom validation
        callback if registered, otherwise provides mock validation for testing.

        Args:
            token: Discord OAuth2 access token
            user_info: Discord user information dict containing id, username, etc.
            discord_server_id: Discord server ID to validate access for

        Returns:
            bool: True if token is valid and user has access, False otherwise

        Raises:
            Exception: Returns False on validation errors
        """
        try:
            # In a real implementation, you would:
            # 1. Validate the token with Discord API
            # 2. Check if the user is a member of the Discord server
            # 3. Verify the token hasn't expired
            
            # For now, we'll do a basic validation
            if not token or not user_info:
                return False
                
            # Check if user_info has required fields
            if not user_info.get('id') or not user_info.get('username'):
                return False
            
            # Special case: if this is the mock OAuth protected server, allow any valid OAuth user
            if discord_server_id == "123456789012345678":
                print(f"[AUTH] Mock OAuth server: accepting user {user_info.get('username')} ({user_info.get('id')})")
                return True
                
            # If we have callbacks (real Discord bot), we can validate the user
            if self._on_validate_discord_user:
                return await self._on_validate_discord_user(token, user_info, discord_server_id)
            
            # For other mock/testing purposes, accept any valid-looking token and user
            print(f"[AUTH] Mock validation: accepting user {user_info.get('username')} ({user_info.get('id')})")
            return True
            
        except Exception as e:
            print(f"[ERROR] OAuth validation error: {e}")
            return False

    async def broadcast_presence(self, server: str, uid: str, status: str, username: str = None, role_color: str = None, delete: bool = False) -> None:
        """Broadcast a user presence update to all clients connected to a server.

        Sends presence information (online status, username, role color) to all
        WebSocket connections associated with the specified Discord server. Used
        to notify clients when users come online, go offline, or change status.

        Args:
            server: Discord server ID to broadcast to
            uid: User ID whose presence is being updated
            status: User's current status ("online", "idle", "dnd", "offline")
            username: Optional username to include in the update
            role_color: Optional hex color code for the user's role (e.g., "#ff6b6b")
            delete: If True, indicates the user should be removed from the presence list

        Returns:
            None

        Examples:

            # Broadcast user coming online
            await server.broadcast_presence(
                server="232769614004748288",
                uid="123456789012345001",
                status="online",
                username="vegeta897",
                role_color="#ff6b6b"
            )
            
            # Broadcast user going offline
            await server.broadcast_presence(
                server="232769614004748288",
                uid="123456789012345001",
                status="offline",
                delete=True
            )
        """
        # Filter connections to only include those connected to the specified server
        server_connections = [ws for ws in self.connections if hasattr(ws, 'discordServer') and ws.discordServer == server]
        
        if not server_connections:
            print(f"[INFO] No connections to broadcast presence to for server: {server}")
            return
            
        presence_data = {
            "uid": uid,
            "status": status
        }
        
        if username:
            presence_data["username"] = username
        if role_color:
            presence_data["roleColor"] = role_color
        if delete:
            presence_data["delete"] = True
            
        msg = {
            "type": "presence",
            "server": server,
            "data": presence_data
        }

        print(f"[BROADCAST] Sending presence update to {len(server_connections)} connections on server {server}: {uid} -> {status}")
        
        # Create a copy to avoid modification during iteration
        connections_copy = server_connections.copy()
        
        for websocket in connections_copy:
            try:
                await websocket.send(json.dumps(msg))
            except websockets.ConnectionClosed:
                print("[INFO] Removed closed connection during presence broadcast")
                # Remove closed connections
                self.connections.discard(websocket)
            except Exception as e:
                print(f"[ERROR] Failed to send presence update to connection: {e}")
                # Optionally remove problematic connections
                self.connections.discard(websocket)

    async def broadcast_client_id_update(self, server: str, client_id: str) -> None:
        """Broadcast an OAuth2 client ID update to all clients connected to a server.

        Sends the Discord OAuth2 application client ID to all WebSocket connections
        associated with the specified Discord server. Used to dynamically update
        the client ID for OAuth authentication flows.

        Args:
            server: Discord server ID to broadcast to
            client_id: Discord OAuth2 application client ID to send

        Returns:
            None

        Examples:

            # Update client ID for all connections to a server
            await server.broadcast_client_id_update(
                server="232769614004748288",
                client_id="123456789012345678"
            )
        """
        # Filter connections to only include those connected to the specified server
        server_connections = [ws for ws in self.connections if hasattr(ws, 'discordServer') and ws.discordServer == server]
        
        if not server_connections:
            print(f"[INFO] No connections to broadcast client ID update to for server: {server}")
            return
            
        msg = {
            "type": "update-clientid",
            "server": server,
            "data": {
                "clientId": client_id
            }
        }

        print(f"[BROADCAST] Sending client ID update to {len(server_connections)} connections on server {server}: {client_id}")
        
        # Create a copy to avoid modification during iteration
        connections_copy = server_connections.copy()
        
        for websocket in connections_copy:
            try:
                await websocket.send(json.dumps(msg))
            except websockets.ConnectionClosed:
                print("[INFO] Removed closed connection during client ID broadcast")
                # Remove closed connections
                self.connections.discard(websocket)
            except Exception as e:
                print(f"[ERROR] Failed to send client ID update to connection: {e}")
                # Optionally remove problematic connections
                self.connections.discard(websocket)


def parse_args():
    """Parse command-line arguments for the D-Back WebSocket server.

    Provides command-line interface for configuring server parameters including
    port, host, static file directory, and version information.

    Returns:
        argparse.Namespace: Parsed arguments containing:
            - port (int): Server port number (default: 3000)
            - host (str): Server hostname (default: 'localhost')
            - static_dir (str): Custom static files directory (default: None)

    Examples:

        $ python -m d_back --port 8080 --host 0.0.0.0
        $ python -m d_back --static-dir ./my-static-files
        $ python -m d_back --version
    """
    parser = argparse.ArgumentParser(
        description='D-Back WebSocket Server',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--port', 
        type=int, 
        default=3000, 
        help='Port to run the WebSocket server on'
    )
    parser.add_argument(
        '--host', 
        type=str, 
        default='localhost', 
        help='Host to bind the WebSocket server to'
    )
    parser.add_argument(
        '--static-dir',
        type=str,
        default=None,
        help='Directory to serve static files from (default: built-in dist directory)'
    )
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {get_version()}'
    )
    return parser.parse_args()

def get_version():
    """Get the current version of the d_back package.

    Attempts to retrieve the version from the package's __version__ attribute.
    Falls back to "unknown" if the version cannot be determined.

    Returns:
        str: The package version string (e.g., "0.0.12") or "unknown".

    Examples:

        >>> get_version()
        '0.0.12'
    """
    try:
        from . import __version__
        return __version__
    except ImportError:
        return "unknown"

async def main():
    """Main async entry point for the D-Back WebSocket server.

    Parses command-line arguments, initializes the WebSocket server with the
    specified configuration, and starts the server in run-forever mode.

    This function handles:
        - Argument parsing for port, host, and static directory
        - Server initialization and configuration
        - Static directory validation
        - Server startup and lifecycle management

    Returns:
        None

    Raises:
        Exception: If server fails to start or encounters fatal errors.
        KeyboardInterrupt: Propagated from server interruption.

    Examples:

        # Run with default settings
        await main()

    Note:
        This is the primary entry point when running d_back as a module.
        Use main_sync() for synchronous execution from __main__.
    """
    args = parse_args()
    
    print(f"Starting D-Back WebSocket Server v{get_version()}")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    
    server = WebSocketServer(port=args.port, host=args.host)
    
    # Set custom static directory if provided
    if args.static_dir:
        static_path = Path(args.static_dir)
        if static_path.exists() and static_path.is_dir():
            server.static_dir = static_path
            print(f"Static directory: {static_path}")
        else:
            print(f"Warning: Static directory '{args.static_dir}' does not exist or is not a directory")
            print(f"Using default static directory: {server.static_dir}")
    else:
        print(f"Static directory: {server.static_dir}")
    
    await server.run_forever()

def main_sync():
    """Synchronous entry point wrapper for the D-Back WebSocket server.

    Wraps the async main() function in asyncio.run() to provide a synchronous
    entry point. Handles KeyboardInterrupt gracefully for clean server shutdown.

    Returns:
        None

    Examples:

        if __name__ == "__main__":
            main_sync()

    Note:
        This is the entry point used when running as a script or via setuptools
        console_scripts. It ensures proper async context management.
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped by user")

if __name__ == "__main__":
    main_sync()
