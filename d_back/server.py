import asyncio
import websockets
import json
import traceback
import random
from typing import Dict, Any, Optional


class WebSocketServer:
    """WebSocket server to manage connections and broadcast messages."""
    
    def __init__(self, port: int = 3000, host: str = "localhost"):
        self.port = port
        self.host = host
        self.server = None  # WebSocket server instance
        self.connections: set = set()  # Store active connections
        self._on_get_server_data = None  # Callback for getting server data
        self._on_get_user_data = None  # Callback for getting user data
        self._on_validate_discord_user = None  # Callback for validating Discord OAuth users
    
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

    def on_validate_discord_user(self, callback):
        """Allow external code to register a Discord user validation callback"""
        self._on_validate_discord_user = callback

    async def run_forever(self) -> None:
        """Run the server forever."""
        async with websockets.serve(
            self._handler, 
            self.host, 
            self.port, 
            process_request=self._process_request
        ):
            print(f"Mock WebSocket server running on ws://{self.host}:{self.port}")
            await asyncio.Future()  # run forever

    def run_sync(self) -> None:
        """Run the server synchronously."""
        asyncio.run(self.run_forever())

    def _get_mock_user_data(self, discord_server_id: str = None) -> Dict[str, Any]:
        """Get the mock user list."""
        base_users = {
            "77488778255540224": {
                "uid": "77488778255540224",
                "username": "b6d",
                "status": "online",
                "roleColor": "#ffffff"
            },
            "235148962103951360": {
                "uid": "235148962103951360",
                "username": "Carl-bot",
                "status": "online",
                "roleColor": "#2c2f33"
            },
            "301022161391452160": {
                "uid": "301022161391452160",
                "username": "Music",
                "status": "online",
                "roleColor": "#7289da"
            },
            "484294583505649664": {
                "uid": "484294583505649664",
                "username": "MeepoDev",
                "status": "online",
                "roleColor": "#ffffff"
            },
            "492349095365705738": {
                "uid": "492349095365705738",
                "username": "Dissentin",
                "status": "online",
                "roleColor": "#2c2f33"
            },
            "506432803173433344": {
                "uid": "506432803173433344",
                "username": "Soundboard",
                "status": "online",
                "roleColor": "#7289da"
            },
            "518858360142168085": {
                "uid": "518858360142168085",
                "username": "Red-kun",
                "status": "online",
                "roleColor": "#ffffff"
            },
            "620253379083370516": {
                "uid": "620253379083370516",
                "username": "Pastecord",
                "status": "online",
                "roleColor": "#7289da"
            }
        }
        
        # If this is the "Mock with random colors" server, generate random colors
        if discord_server_id == "482241773318701056":
            for user in base_users.values():
                user["roleColor"] = self._random_color()
                
        if discord_server_id == "123456789012345678":
            # Simulate a larger server with more users
            for i in range(20):
                uid = str(600000000000000000 + i)
                base_users[uid] = {
                    "uid": uid,
                    "username": f"User{i}",
                    "status": self._random_status(),
                    "roleColor": self._random_color()
                }
        
        return base_users
        
    def _get_mock_server_data(self) -> Dict[str, Any]:
        """Get the mock server list."""
        return {
            "232769614004748288": {
                "id": "D",
                "name": "Mock Server",
                "passworded": False
            },
            "482241773318701056": {
                "id": "T", 
                "name": "Mock with random colors",
                "default": True,
                "passworded": False
            },
            "123456789012345678": {
                "id": "P",
                "name": "OAuth Protected Server",
                "passworded": True
            }
        }
    
    def _random_color(self) -> str:
        """Generate a random color hex code."""
        return '#{:06x}'.format(random.randint(0, 0xFFFFFF))

    def _random_status(self) -> str:
        """Get a random user status."""
        return random.choice(["online", "idle", "dnd", "offline"])

    async def _process_request(self, path: str, request_headers) -> Optional[Any]:
        """Process incoming WebSocket connection requests."""
        print(f"[PROCESS_REQUEST] Incoming connection to path: {path}")
        # Note: websocket connection will be stored in handler method
        # TODO: Validate discord oauth token, depends on https://github.com/NNTin/d-zone/issues/4
        return None

    async def _handler(self, websocket) -> None:
        """Handle WebSocket connections and messages."""
        print("[CONNECT] Client connected")
        # Store the connection
        self.connections.add(websocket)
        
        try:
            # Send server list immediately on connect (like the original)
            print("[SEND] server-list")
            
            if self._on_get_server_data:
                server_data = self._on_get_server_data()
            else:
                # simulate getting server data
                server_data = self._get_mock_server_data()

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
            print(f"[AUTH] Using legacy password authentication")
        elif discord_token:
            print(f"[AUTH] Using Discord OAuth2 authentication for user: {discord_user.get('username') if discord_user else 'unknown'}")
        
        # Get server and user data using callbacks or mock data
        if self._on_get_server_data:
            server_data = self._on_get_server_data()
        else:
            server_data = self._get_mock_server_data()
            
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
                print(f"[AUTH] Legacy password authentication successful")
            
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
            user_data = self._on_get_user_data(discord_server_id)
        else:
            user_data = self._get_mock_user_data(discord_server_id)
        
        print(f"[SUCCESS] Client joined server {server_info['name']}")
        print("[SEND] server-join")
        
        # Prepare request data for response (don't include sensitive auth info)
        request_data = {"server": server_id}
        if password:  # Only include password for legacy compatibility
            request_data["password"] = password
            
        await websocket.send(json.dumps({
            "type": "server-join",
            "data": {
                "users": user_data,
                "request": request_data
            }
        }))
        
        # Only start mock data if using mock data (not when using real callbacks)
        if not self._on_get_user_data and not self._on_get_server_data:
            # Start background tasks for mock data
            asyncio.create_task(self._periodic_messages(websocket))
            asyncio.create_task(self._periodic_status_updates(websocket))

    async def _periodic_status_updates(self, websocket) -> None:
        """Send periodic status updates to the client."""
        uids = list(self._get_mock_user_data(websocket.discordServer).keys())
        try:
            while True:
                await asyncio.sleep(4)
                status = self._random_status()
                uid = random.choice(uids)
                presence_msg = {
                    "type": "presence",
                    "server": websocket.discordServer,
                    "data": {
                        "uid": uid,
                        "status": status
                    }
                }
                print(f"[SEND] presence update for {uid}: {status}")
                await websocket.send(json.dumps(presence_msg))
        except websockets.ConnectionClosed:
            print("[INFO] Presence update task stopped: connection closed")
            # Remove closed connections
            self.connections.discard(websocket)
        except Exception as e:
            print(f"[ERROR] Failed to send message to connection: {e}")
            # Optionally remove problematic connections
            self.connections.discard(websocket)

    async def _periodic_messages(self, websocket) -> None:
        """Send periodic messages to the client."""
        uids = list(self._get_mock_user_data(websocket.discordServer).keys())
        messages = [
            "hello",
            "how are you?",
            "this is a test message",
            "D-Zone rocks!",
            "what's up?"
        ]
        try:
            while True:
                await asyncio.sleep(2.5)
                uid = random.choice(uids)
                msg_text = random.choice(messages)
                msg = {
                    "type": "message",
                    "server": websocket.discordServer,
                    "data": {
                        "uid": uid,
                        "message": msg_text,
                        "channel": "527964146659229701"
                    }
                }
                print(f"[SEND] periodic message from {uid}: {msg_text}")
                await websocket.send(json.dumps(msg))
        except websockets.ConnectionClosed:
            print("[INFO] Periodic message task stopped: connection closed")
            # Remove closed connections
            self.connections.discard(websocket)
        except Exception as e:
            print(f"[ERROR] Failed to send message to connection: {e}")
            # Optionally remove problematic connections
            self.connections.discard(websocket)

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

PORT = 3000

async def main():
    server = WebSocketServer(port=PORT)
    await server.run_forever()

def main_sync():
    server = WebSocketServer(port=PORT)
    server.run_sync()

if __name__ == "__main__":
    main_sync()
