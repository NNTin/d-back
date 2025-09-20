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
        self.connection_paths: Dict[str, str] = {}
        self.server = None
        
    def get_server_list(self) -> Dict[str, Any]:
        """Get the mock server list."""
        return {
            "232769614004748288": {
                "id": "DS",
                "name": "Dev Server",
                "passworded": False
            },
            "482241773318701056": {
                "id": "t",
                "name": "test",
                "default": True,
                "passworded": False
            }
        }

    def random_color(self) -> str:
        """Generate a random color hex code."""
        return '#{:06x}'.format(random.randint(0, 0xFFFFFF))

    def random_status(self) -> str:
        """Get a random user status."""
        return random.choice(["online", "idle", "dnd", "offline"])

    def get_users(self) -> Dict[str, Any]:
        """Get the mock user list."""
        return {
            "77488778255540224": {
                "id": "77488778255540224",
                "username": "b6d",
                "status": "online",
                "roleColor": "#9b59b6"
            },
            "235148962103951360": {
                "id": "235148962103951360",
                "username": "Carl-bot",
                "status": "online",
                "roleColor": "#e67e22"
            },
            "301022161391452160": {
                "id": "301022161391452160",
                "username": "Music",
                "roleColor": "#3498db"
            },
            "484294583505649664": {
                "id": "484294583505649664",
                "username": "MeepoDev",
                "roleColor": "#2ecc71"
            },
            "492349095365705738": {
                "id": "492349095365705738",
                "username": "Dissentin",
                "status": "online",
                "roleColor": self.random_color()
            },
            "506432803173433344": {
                "id": "506432803173433344",
                "username": "Soundboard"
            },
            "518858360142168085": {
                "id": "518858360142168085",
                "username": "Red-kun",
                "roleColor": "#f11d1d"
            },
            "620253379083370516": {
                "id": "620253379083370516",
                "username": "Pastecord"
            }
        }

    async def process_request(self, path: str, request_headers) -> Optional[Any]:
        """Process incoming WebSocket connection requests."""
        print(f"[PROCESS_REQUEST] Incoming connection to path: {path}")
        # Optionally store or use the path for later
        # self.connection_paths[...] = path
        # Returning None means accept the connection
        return None

    async def handler(self, websocket) -> None:
        """Handle WebSocket connections and messages."""
        print("[CONNECT] Client connected")
        try:
            # Send server list on connect
            print("[SEND] server-list")
            await websocket.send(json.dumps({
                "type": "server-list",
                "data": self.get_server_list()
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
                "users": self.get_users()
            }
        }))
        
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
        user_ids = list(self.get_users().keys())
        try:
            while True:
                await asyncio.sleep(4)
                uid = random.choice(user_ids)
                status = self.random_status()
                presence_msg = {
                    "type": "presence",
                    "server": "482241773318701056",
                    "data": {"uid": uid, "status": status}
                }
                print(f"[SEND] presence update for {uid}: {status}")
                await websocket.send(json.dumps(presence_msg))
        except websockets.ConnectionClosed:
            print("[INFO] Presence update task stopped: connection closed")

    async def _periodic_messages(self, websocket) -> None:
        """Send periodic messages to the client."""
        user_ids = list(self.get_users().keys())
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

    async def start(self) -> None:
        """Start the WebSocket server."""
        self.server = await websockets.serve(
            self.handler, 
            self.host, 
            self.port, 
            process_request=self.process_request
        )
        print(f"WebSocket server started on ws://{self.host}:{self.port}")
        await self.server.wait_closed()

    async def run_forever(self) -> None:
        """Run the server forever."""
        async with websockets.serve(
            self.handler, 
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
