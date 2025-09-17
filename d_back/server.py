import asyncio
import websockets
import json
import traceback
import random

PORT = 3000

# Store paths for connections (for demonstration)
connection_paths = {}

# Mock server data
def get_server_list():
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

def random_color():
    return '#{:06x}'.format(random.randint(0, 0xFFFFFF))

def random_status():
    return random.choice(["online", "idle", "dnd", "offline"])

def get_users():
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
            "roleColor": random_color()
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

async def process_request(path, request_headers):
    print(f"[PROCESS_REQUEST] Incoming connection to path: {path}")
    # Optionally store or use the path for later
    # connection_paths[...] = path
    # Returning None means accept the connection
    return None

async def handler(websocket):
    print("[CONNECT] Client connected")
    try:
        # Send server list on connect
        print("[SEND] server-list")
        await websocket.send(json.dumps({
            "type": "server-list",
            "data": get_server_list()
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
                server_id = data["data"].get("server", "default")
                password = data["data"].get("password", None)
                print(f"[EVENT] Client requests connect to server: {server_id} with password: {password}")
                # Simulate server join
                print("[SEND] server-join")
                await websocket.send(json.dumps({
                    "type": "server-join",
                    "data": {
                        "request": {"server": server_id, "password": password},
                        "users": get_users()
                    }
                }))
                print("[SEND] presence")
                await websocket.send(json.dumps({
                    "type": "presence",
                    "data": {"uid": "77488778255540224", "status": "online"}
                }))
                
                async def periodic_status_updates():
                    user_ids = list(get_users().keys())
                    try:
                        while True:
                            await asyncio.sleep(4)
                            uid = random.choice(user_ids)
                            status = random_status()
                            presence_msg = {
                                "type": "presence",
                                "server": "482241773318701056",
                                "data": {"uid": uid, "status": status}
                            }
                            print(f"[SEND] presence update for {uid}: {status}")
                            await websocket.send(json.dumps(presence_msg))
                    except websockets.ConnectionClosed:
                        print("[INFO] Presence update task stopped: connection closed")
                async def periodic_messages():
                    user_ids = list(get_users().keys())
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
                # Run periodic_messages in the background
                asyncio.create_task(periodic_messages())
                asyncio.create_task(periodic_status_updates())
            else:
                print(f"[ERROR] Unknown event type: {data.get('type')}")
                await websocket.send(json.dumps({"type": "error", "data": {"message": "Unknown event type"}}))
    except websockets.ConnectionClosed as e:
        print(f"[DISCONNECT] Client disconnected: {e}")
    except Exception as e:
        print(f"[FATAL ERROR] {e}")
        traceback.print_exc()

async def start_server(port=3000):
    server = await websockets.serve(handler, "localhost", port, process_request=process_request)
    print(f"WebSocket server started on ws://localhost:{port}")
    await server.wait_closed()

async def main():
    async with websockets.serve(handler, "localhost", PORT, process_request=process_request):
        print(f"Mock WebSocket server running on ws://localhost:{PORT}")
        await asyncio.Future()  # run forever

def main_sync():
    import asyncio
    asyncio.run(main())

if __name__ == "__main__":
    main_sync()
