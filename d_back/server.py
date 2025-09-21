import asyncio
import websockets
import json
import traceback
import random
from typing import Dict, Any, Optional


class WebSocketServer:
    """WebSocket server to manage connections and broadcast messages."""
    
    def __init__(self, port: int = 3000, host: str = "localhost", send_mock_data: bool = True):
        self.port = port
        self.host = host
        self.connection_paths: Dict[str, str] = {}
        self.connections: set = set()  # Store active connections
        self.server = None
        self.send_mock_data = send_mock_data
        
    def get_server_list(self) -> Dict[str, Any]:
        """Get the mock server list with users. Override this method with real discord data."""
        users_data = {
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
        
        users_with_random_color = {
            user_id: {
                **data,
                "roleColor": self._random_color()
            }
            for user_id, data in users_data.items()
        }
        
        return {
            "232769614004748288": {
                "id": "DS",
                "name": "Dev Server",
                "passworded": False,
                "users": users_data
            },
            "482241773318701056": {
                "id": "t",
                "name": "test",
                "default": True,
                "passworded": False,
                "users": users_with_random_color
            },
            "default": {
                "id": "t",
                "name": "test",
                "default": True,
                "passworded": False,
                "users": users_with_random_color
            }
        }

    def _random_color(self) -> str:
        """Generate a random color hex code."""
        return '#{:06x}'.format(random.randint(0, 0xFFFFFF))

    def _random_status(self) -> str:
        """Get a random user status."""
        return random.choice(["online", "idle", "dnd", "offline"])

    def _get_users(self, server_id="default") -> Dict[str, Any]:
        """Get the user list."""
        return self.get_server_list()[server_id]["users"]

    def _get_server_list_for_client(self) -> Dict[str, Any]:
        """Get the server list without users (for client communication)."""
        full_server_list = self.get_server_list()
        # Remove the users field from each server and the global users key
        client_server_list = {}
        for server_id, server_data in full_server_list.items():
            if server_id != "users":  # Skip the global users key
                # Create a copy without the users field
                client_server_list[server_id] = {
                    key: value for key, value in server_data.items() 
                    if key != "users"
                }
        return client_server_list

    async def process_request(self, path: str, request_headers) -> Optional[Any]:
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
            await websocket.send(json.dumps({
                "type": "server-list",
                "data": self._get_server_list_for_client()
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
        
        # Simulate server join
        print("[SEND] server-join")
        await websocket.send(json.dumps({
            "type": "server-join",
            "data": {
                "request": {"server": server_id, "password": password},
                "users": self._get_users(server_id),
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
        user_ids = list(self._get_users().keys())
        try:
            while True:
                await asyncio.sleep(4)
                uid = random.choice(user_ids)
                status = self._random_status()
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
        user_ids = list(self._get_users().keys())
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
                uid = random.choice(user_ids)
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

    async def broadcast_message(self, server: str, uid: str, message: str, channel: str) -> None:
        """Broadcast a message to all connected clients."""
        if not self.connections:
            print("[INFO] No connections to broadcast to")
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
        
        print(f"[BROADCAST] Sending message to {len(self.connections)} connections: {message}")
        
        # Create a copy of connections to avoid modification during iteration
        connections_copy = self.connections.copy()
        
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

    async def start(self) -> None:
        """Start the WebSocket server."""
        self.server = await websockets.serve(
            self._handler, 
            self.host, 
            self.port, 
            process_request=self.process_request
        )
        print(f"WebSocket server started on ws://{self.host}:{self.port}")
        await self.server.wait_closed()

    async def run_forever(self) -> None:
        """Run the server forever."""
        async with websockets.serve(
            self._handler, 
            self.host, 
            self.port, 
            process_request=self.process_request
        ):
            print(f"Mock WebSocket server running on ws://{self.host}:{self.port}")
            await asyncio.Future()  # run forever

    def run_sync(self) -> None:
        """Run the server synchronously."""
        asyncio.run(self.run_forever())

    async def stop(self) -> None:
        """Stop the WebSocket server."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            print("WebSocket server stopped")

PORT = 3000

async def main():
    server = WebSocketServer(port=PORT)
    await server.run_forever()

def main_sync():
    server = WebSocketServer(port=PORT)
    server.run_sync()

if __name__ == "__main__":
    main_sync()
