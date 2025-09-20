import asyncio
import websockets
import json

ADDRESS = "ws://localhost:3000"

async def log_communication():
    async with websockets.connect(ADDRESS) as ws:
        print(f"Connected to {ADDRESS}", flush=True)
        # Log server-list
        response = await ws.recv()
        print(f"[RECV] {response}", flush=True)
        # Send connect message
        connect_msg = {
            "type": "connect",
            "data": {"server": "default"}
        }
        print(f"[SEND] {json.dumps(connect_msg)}", flush=True)
        await ws.send(json.dumps(connect_msg))
        # Log next 3 messages then exit
        try:
            for _ in range(3):
                msg = await ws.recv()
                print(f"[RECV] {msg}", flush=True)
        except websockets.ConnectionClosed:
            print("Connection closed by server.", flush=True)
        except Exception as e:
            print(f"Error: {e}", flush=True)

if __name__ == "__main__":
    asyncio.run(log_communication())
