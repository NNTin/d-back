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
        self.send_mock_data = False  # Whether to send mock data periodically
        self._on_get_server_data = None  # Callback for getting server data
        self._on_get_user_data = None  # Callback for getting user data
    
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
        server_connections = [ws for ws in self.connections if hasattr(ws, 'server_id') and ws.server_id == server]
        
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

    def _get_mock_user_data(self) -> Dict[str, Any]:
        """Get the mock user list."""
        self.send_mock_data = True
        return {
            "77488778255540224": {
                "id": "77488778255540224",
                "username": "b6d",
                "status": "online",
                "roleColor": "#ffffff"
            },
            "235148962103951360": {
                "id": "235148962103951360",
                "username": "Carl-bot",
                "status": "online",
                "roleColor": "#2c2f33"
            },
            "301022161391452160": {
                "id": "301022161391452160",
                "username": "Music",
                "roleColor": "#7289da"
            },
            "484294583505649664": {
                "id": "484294583505649664",
                "username": "MeepoDev",
                "roleColor": "#ffffff"
            },
            "492349095365705738": {
                "id": "492349095365705738",
                "username": "Dissentin",
                "status": "online",
                "roleColor": "#2c2f33"
            },
            "506432803173433344": {
                "id": "506432803173433344",
                "username": "Soundboard",
                "roleColor": "#7289da"
            },
            "518858360142168085": {
                "id": "518858360142168085",
                "username": "Red-kun",
                "roleColor": "#ffffff"
            },
            "620253379083370516": {
                "id": "620253379083370516",
                "username": "Pastecord",
                "roleColor": "#7289da"
            }
        }
        
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
            # Send server list on connect
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
            
            # Wait for connect message
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
        password = data["data"].get("password", None)
        print(f"[EVENT] Client requests connect to server: {server_id} with password: {password}")
        
        # Store the server_id in the websocket connection
        websocket.server_id = server_id
        
        if self._on_get_user_data:
            user_data = self._on_get_user_data(server_id)
        else:
            # simulate getting user data
            user_data = self._get_mock_user_data()
        
        print("[SEND] server-join")
        await websocket.send(json.dumps({
            "type": "server-join",
            "data": {
                "request": {"server": server_id, "password": password},
                "users": user_data
            }
        }))
        
        if self.send_mock_data:
            print("[SEND] presence")
            await websocket.send(json.dumps({
                "type": "presence",
                "data": {"uid": "77488778255540224", "status": "online"}
            }))
            
            # Start background tasks
            asyncio.create_task(self._periodic_messages(websocket))
            asyncio.create_task(self._periodic_status_updates(websocket))

    async def _periodic_status_updates(self, websocket) -> None:
        """Send periodic status updates to the client."""
        uids = list(self._get_mock_user_data().keys())
        try:
            while True:
                await asyncio.sleep(4)
                status = self._random_status()
                uid = random.choice(uids)
                presence_msg = {
                    "type": "presence",
                    "server": "482241773318701056",
                    "data": {"uid": uid, "status": status}
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
        uids = list(self._get_mock_user_data().keys())
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
                    "server": "482241773318701056",
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

PORT = 3000

async def main():
    server = WebSocketServer(port=PORT)
    await server.run_forever()

def main_sync():
    server = WebSocketServer(port=PORT)
    server.run_sync()

if __name__ == "__main__":
    main_sync()
