"""
Mock data and periodic tasks for the WebSocket server.
"""

import asyncio
import json
import random
import websockets
from typing import Dict, Any


class MockDataProvider:
    """Provides mock data and periodic tasks for testing the WebSocket server."""

    def __init__(self, server_instance):
        self.server = server_instance

    def get_mock_user_data(self, discord_server_id: str = None) -> Dict[str, Any]:
        """Get the mock user list."""
        
        # D-World server users (default)
        if discord_server_id == "232769614004748288":
            return {
                "123456789012345001": {
                    "uid": "123456789012345001",
                    "username": "vegeta897",
                    "status": "online",
                    "roleColor": "#ff6b6b"
                },
                "123456789012345002": {
                    "uid": "123456789012345002",
                    "username": "Cog-Creators",
                    "status": "idle",
                    "roleColor": "#4ecdc4"
                },
                "123456789012345003": {
                    "uid": "123456789012345003",
                    "username": "d-zone-org",
                    "status": "dnd",
                    "roleColor": "#45b7d1"
                },
                "123456789012345004": {
                    "uid": "123456789012345004",
                    "username": "NNTin",
                    "status": "online",
                    "roleColor": "#96ceb4"
                }
            }
        
        # Docs (WIP) server users
        elif discord_server_id == "482241773318701056":
            return {
                "223456789012345001": {
                    "uid": "223456789012345001",
                    "username": "nntin.xyz/me",
                    "status": "online",
                    "roleColor": "#feca57"
                }
            }
        
        # OAuth2 Protected server users
        elif discord_server_id == "123456789012345678":
            return {
                "323456789012345001": {
                    "uid": "323456789012345001",
                    "username": "NNTin",
                    "status": "online",
                    "roleColor": "#ff9ff3"
                }
            }
        
        # My Repos server users
        elif discord_server_id == "987654321098765432":
            return {
                "423456789012345001": {
                    "uid": "423456789012345001",
                    "username": "me",
                    "status": "online",
                    "roleColor": "#54a0ff"
                },
                "423456789012345002": {
                    "uid": "423456789012345002",
                    "username": "nntin.github.io",
                    "status": "idle",
                    "roleColor": "#5f27cd"
                },
                "423456789012345003": {
                    "uid": "423456789012345003",
                    "username": "d-zone",
                    "status": "online",
                    "roleColor": "#00d2d3"
                },
                "423456789012345004": {
                    "uid": "423456789012345004",
                    "username": "d-back",
                    "status": "dnd",
                    "roleColor": "#ff6348"
                },
                "423456789012345005": {
                    "uid": "423456789012345005",
                    "username": "d-cogs",
                    "status": "online",
                    "roleColor": "#ff4757"
                },
                "423456789012345006": {
                    "uid": "423456789012345006",
                    "username": "Cubify-Reddit",
                    "status": "offline",
                    "roleColor": "#3742fa"
                },
                "423456789012345007": {
                    "uid": "423456789012345007",
                    "username": "Dota-2-Emoticons",
                    "status": "idle",
                    "roleColor": "#2ed573"
                },
                "423456789012345008": {
                    "uid": "423456789012345008",
                    "username": "Dota-2-Reddit-Flair-Mosaic",
                    "status": "online",
                    "roleColor": "#ffa502"
                },
                "423456789012345009": {
                    "uid": "423456789012345009",
                    "username": "Red-kun",
                    "status": "dnd",
                    "roleColor": "#ff3838"
                },
                "423456789012345010": {
                    "uid": "423456789012345010",
                    "username": "Reply-Dota-2-Reddit",
                    "status": "online",
                    "roleColor": "#ff9f43"
                },
                "423456789012345011": {
                    "uid": "423456789012345011",
                    "username": "Reply-LoL-Reddit",
                    "status": "idle",
                    "roleColor": "#0abde3"
                },
                "423456789012345012": {
                    "uid": "423456789012345012",
                    "username": "crosku",
                    "status": "online",
                    "roleColor": "#006ba6"
                },
                "423456789012345013": {
                    "uid": "423456789012345013",
                    "username": "dev-tracker-reddit",
                    "status": "offline",
                    "roleColor": "#8e44ad"
                },
                "423456789012345014": {
                    "uid": "423456789012345014",
                    "username": "discord-logo",
                    "status": "online",
                    "roleColor": "#7289da"
                },
                "423456789012345015": {
                    "uid": "423456789012345015",
                    "username": "discord-twitter-bot",
                    "status": "idle",
                    "roleColor": "#1da1f2"
                },
                "423456789012345016": {
                    "uid": "423456789012345016",
                    "username": "discord-web-bridge",
                    "status": "dnd",
                    "roleColor": "#2c2f33"
                },
                "423456789012345017": {
                    "uid": "423456789012345017",
                    "username": "pasteindex",
                    "status": "online",
                    "roleColor": "#f39c12"
                },
                "423456789012345018": {
                    "uid": "423456789012345018",
                    "username": "pasteview",
                    "status": "idle",
                    "roleColor": "#e74c3c"
                },
                "423456789012345019": {
                    "uid": "423456789012345019",
                    "username": "shell-kun",
                    "status": "online",
                    "roleColor": "#1abc9c"
                },
                "423456789012345020": {
                    "uid": "423456789012345020",
                    "username": "tracker-reddit-discord",
                    "status": "offline",
                    "roleColor": "#9b59b6"
                },
                "423456789012345021": {
                    "uid": "423456789012345021",
                    "username": "twitter-backend",
                    "status": "online",
                    "roleColor": "#1da1f2"
                }
            }
        
        # Fallback: return empty if unknown server
        return {}
        
    def get_mock_server_data(self) -> Dict[str, Any]:
        """Get the mock server list."""
        return {
            "232769614004748288": {
                "id": "dworld",
                "name": "D-World",
                "default": True,
                "passworded": False
            },
            "482241773318701056": {
                "id": "docs", 
                "name": "Docs (WIP)",
                "passworded": False
            },
            "123456789012345678": {
                "id": "oauth",
                "name": "OAuth2 Protected Server",
                "passworded": True
            },
            "987654321098765432": {
                "id": "repos",
                "name": "My Repos",
                "passworded": False
            }
        }

    async def periodic_status_updates(self, websocket) -> None:
        """Send periodic status updates to the client."""
        uids = list(self.get_mock_user_data(websocket.discordServer).keys())
        try:
            while True:
                await asyncio.sleep(4)
                status = self.server._random_status()
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
            self.server.connections.discard(websocket)
        except Exception as e:
            print(f"[ERROR] Failed to send message to connection: {e}")
            # Optionally remove problematic connections
            self.server.connections.discard(websocket)

    async def periodic_messages(self, websocket) -> None:
        """Send periodic messages to the client."""
        uids = list(self.get_mock_user_data(websocket.discordServer).keys())
        messages = [
            "hello",
            "how are you?",
            "this is a test message",
            "D-Zone rocks!",
            "what's up?"
        ]
        try:
            while True:
                await asyncio.sleep(5)
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
            self.server.connections.discard(websocket)
        except Exception as e:
            print(f"[ERROR] Failed to send message to connection: {e}")
            # Optionally remove problematic connections
            self.server.connections.discard(websocket)