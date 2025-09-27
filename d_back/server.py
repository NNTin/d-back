import asyncio
import websockets
import json
import traceback
import random
import mimetypes
import argparse
from pathlib import Path
from typing import Dict, Any

from .mock import MockDataProvider


class WebSocketServer:
    """WebSocket server to manage connections and broadcast messages."""
    
    def __init__(self, port: int = 3000, host: str = "localhost"):
        self.port = port
        self.host = host
        self.server = None  # WebSocket server instance
        self.connections: set = set()  # Store active connections
        self._on_get_server_data = None  # Callback for getting server data
        self._on_get_user_data = None  # Callback for getting user data
        self._on_static_request = None  # Callback for custom static file handling
        self.static_dir = Path(__file__).parent / "dist"  # Default static directory
        self._on_validate_discord_user = None  # Callback for validating Discord OAuth users
        self._on_get_client_id = None  # Callback for getting OAuth2 client ID
        self.mock_provider = MockDataProvider(self)  # Mock data provider
    
    async def start(self) -> None:
        """Start the WebSocket server."""
        self.server = await websockets.serve(
            self._handler, 
            self.host, 
            self.port, 
            process_request=self._process_request
        )
        print(f"WebSocket server started on ws://{self.host}:{self.port}")
        await self.server.wait_closed()
  
    async def stop(self) -> None:
        """Stop the WebSocket server."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            print("WebSocket server stopped")

    async def broadcast_message(self, server: str, uid: str, message: str, channel: str) -> None:
        """Broadcast a message to all connected clients on the specified server."""
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

    def on_get_server_data(self, callback):
        """Allow external code to register a callback"""
        self._on_get_server_data = callback
    
    def on_get_user_data(self, callback):
        """Allow external code to register a callback"""
        self._on_get_user_data = callback

    def on_static_request(self, callback):
        """Allow external code to register a callback for custom static file handling.
        
        The callback should take a path parameter and return either:
        - None: Let default handler process the request
        - (content_type, content): Return custom content
        """
        self._on_static_request = callback

    def on_validate_discord_user(self, callback):
        """Allow external code to register a Discord user validation callback"""
        self._on_validate_discord_user = callback

    def on_get_client_id(self, callback):
        """Allow external code to register a callback to get OAuth2 client ID"""
        self._on_get_client_id = callback

    async def run_forever(self) -> None:
        """Run the server forever."""
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
        """Process incoming WebSocket connection requests and HTTP requests for static files."""
        
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
        """Serve static files for HTTP requests."""
        try:
            # Get HTTP classes for compatibility
            use_new_http, Response, Headers, websockets_version = self._get_http_classes()
            
            # Remove query parameters from path for routing
            clean_path = path.split('?')[0]
            
            # Handle custom static request callback first
            if self._on_static_request:
                result = self._on_static_request(clean_path)
                if result is not None:
                    content_type, content = result
                    return self._create_http_response(200, "OK", content_type, content.encode(), use_new_http, Response, Headers, websockets_version)
            
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
        """Serve version information as JSON API."""
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
        """Handle WebSocket connections and messages."""
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
        """Handle client connect requests."""
        server_id = data["data"].get("server", "default")
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
        
        print(f"[DEBUG] Looking for server with ID: {server_id}")
        print(f"[DEBUG] Available servers: {server_data}")
        
        # Look for exact server ID match or default server
        for discord_id, server in server_data.items():
            print(f"[DEBUG] Checking server {discord_id}: {server}")
            if server["id"] == server_id or (server.get("default") and server_id == "default"):
                server_info = server
                discord_server_id = discord_id
                print(f"[DEBUG] Found matching server: {server_info} with Discord ID: {discord_server_id}")
                break
        
        if not server_info:
            print(f"[ERROR] Unknown server: {server_id}")
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
            "request": request_data
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
        """Validate Discord OAuth2 token and check if user has access to the server."""
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
        """Broadcast a presence update to all connected clients on the specified server."""
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
        """Broadcast a client ID update to all connected clients on the specified server."""
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
    """Parse command-line arguments."""
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
    """Get the current version of d_back."""
    try:
        from . import __version__
        return __version__
    except ImportError:
        return "unknown"

async def main():
    """Main async entry point."""
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
    """Synchronous entry point for the server."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped by user")

if __name__ == "__main__":
    main_sync()
