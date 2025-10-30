"""Mock data provider and periodic task generators for WebSocket server testing.

This module provides the MockDataProvider class which generates test data for the
D-Back WebSocket server during development and testing. It includes mock user data,
server configurations, and background tasks for simulating user presence updates
and message broadcasts.

The mock data simulates a Discord-like environment with multiple servers, users,
and realistic status updates. This is useful for:
    - Testing WebSocket server functionality without real Discord integration
    - Demonstrating server capabilities in development environments
    - Running integration tests with predictable data

Examples:
    Using mock data provider:

        from d_back.mock import MockDataProvider
        from d_back.server import WebSocketServer
        
        server = WebSocketServer()
        mock = MockDataProvider(server)
        users = mock.get_mock_user_data("232769614004748288")

Warning:
    This module is intended for development and testing only. Do not use mock
    data in production environments. Register custom data providers using the
    WebSocketServer callback methods for production use.
"""

import asyncio
import json
import random
import websockets
from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from websockets.server import WebSocketServerProtocol
    from d_back.server import WebSocketServer


class MockDataProvider:
    """Provides mock data and periodic background tasks for WebSocket server testing.

    This class generates test data that simulates a Discord-like server environment
    with multiple servers, users, and real-time updates. It provides both static
    data (user lists, server configurations) and dynamic behaviors (status updates,
    message broadcasts) for development and testing purposes.

    The mock provider includes predefined data for several test servers:
        - D-World: Main test server with 4 users
        - Docs (WIP): Documentation server with 1 user
        - OAuth2 Protected Server: Authentication testing server
        - My Repos: Repository showcase server with 21 users

    Attributes:
        server: Reference to the WebSocketServer instance using this provider.

    Examples:
        Basic usage:

            server = WebSocketServer()
            mock_provider = MockDataProvider(server)
            
            # Get user data for a specific server
            users = mock_provider.get_mock_user_data("232769614004748288")
            # Returns: {"uid1": {"uid": "...", "username": "...", ...}, ...}
            
            # Get all available servers
            servers = mock_provider.get_mock_server_data()
            # Returns: {"server_id": {"id": "...", "name": "...", ...}, ...}

    Note:
        The mock data provider is automatically instantiated by WebSocketServer.
        You typically don't need to create instances manually unless testing
        the provider in isolation.
    """

    def __init__(self, server_instance: 'WebSocketServer'):
        """Initialize the mock data provider.

        Args:
            server_instance: The WebSocketServer instance that owns this provider.
                Used for accessing server methods like _random_status().
        """
        self.server = server_instance

    def get_mock_user_data(self, discord_server_id: str = None) -> Dict[str, Any]:
        """Get mock user data for a specific Discord server.

        Returns a dictionary of mock users with their profile information including
        user ID, username, online status, and role color. Each server has a predefined
        set of users for consistent testing.

        Args:
            discord_server_id: Optional Discord server ID to get users for.
                Supported IDs:
                - "232769614004748288": D-World server (4 users)
                - "482241773318701056": Docs (WIP) server (1 user)
                - "123456789012345678": OAuth2 Protected server (1 user)
                - "987654321098765432": My Repos server (21 users)
                If None or unknown, returns empty dict.

        Returns:
            Dict[str, Any]: Dictionary mapping user IDs to user data objects.
                Each user object contains:
                - uid (str): Unique user identifier
                - username (str): Display name
                - status (str): Online status ("online", "idle", "dnd", "offline")
                - roleColor (str): Hex color code for user's role (e.g., "#ff6b6b")

        Examples:

            provider = MockDataProvider(server)
            users = provider.get_mock_user_data("232769614004748288")
            # Returns:
            # {
            #     "123456789012345001": {
            #         "uid": "123456789012345001",
            #         "username": "vegeta897",
            #         "status": "online",
            #         "roleColor": "#ff6b6b"
            #     },
            #     ...
            # }
        """
        
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
        """Get mock server data with all available Discord servers.

        Returns a dictionary mapping Discord server IDs to server configuration
        objects. Used for testing server selection, display, and navigation features.

        Returns:
            Dict[str, Dict[str, Any]]: Dictionary mapping Discord server snowflake IDs
                to server configuration objects. Each server object contains:
                - id (str): Internal server identifier
                - name (str): Server display name
                - passworded (bool): Whether OAuth2 authentication is required
                - default (bool, optional): Whether this is the default server

        Examples:

            provider = MockDataProvider(server)
            servers = provider.get_mock_server_data()
            # Returns:
            # {
            #     "232769614004748288": {
            #         "id": "dworld",
            #         "name": "D-World",
            #         "default": True,
            #         "passworded": False
            #     },
            #     "482241773318701056": {
            #         "id": "docs",
            #         "name": "Docs (WIP)",
            #         "passworded": False
            #     },
            #     ...
            # }
            
            for snowflake_id, server_info in servers.items():
                print(f"{server_info['name']} (ID: {snowflake_id})")
        """
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

    async def periodic_status_updates(self, websocket: 'WebSocketServerProtocol') -> None:
        """Periodically send mock user status changes to a connected client.

        Background task that continuously generates random user status updates
        and sends them to the specified WebSocket connection. Simulates realistic
        user activity by randomly changing user statuses every 4 seconds.

        This method runs until the WebSocket connection is closed or the task
        is cancelled. It selects random users from the current server and updates
        their online status (online, idle, dnd, offline).

        Args:
            websocket: WebSocket connection to send updates to. Must have a
                discordServer attribute identifying which server's users to update.

        Note:
            This is a coroutine that runs indefinitely for the lifetime of the
            WebSocket connection. It automatically handles ConnectionClosed
            exceptions gracefully.

        Examples:

            # Called automatically by the server for each connection
            task = asyncio.create_task(
                mock_provider.periodic_status_updates(websocket)
            )
            
            # Updates will be sent in this format:
            # {
            #     "type": "presence",
            #     "server": "232769614004748288",
            #     "data": {
            #         "uid": "123456789012345001",
            #         "status": "online"
            #     }
            # }

        Raises:
            websockets.ConnectionClosed: When the WebSocket connection is closed.
                This exception is caught and handled gracefully.
        """
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

    async def periodic_messages(self, websocket: 'WebSocketServerProtocol') -> None:
        """Periodically send mock chat messages to a connected client.

        Background task that continuously generates random chat messages from
        mock users and sends them to the specified WebSocket connection. Simulates
        realistic chat activity by sending messages every 5 seconds.

        This method runs until the WebSocket connection is closed or the task
        is cancelled. It selects random users from the current server and random
        messages from a predefined list to create chat events.

        Args:
            websocket: WebSocket connection to send messages to. Must have a
                discordServer attribute identifying which server's users to use.

        Note:
            This is a coroutine that runs indefinitely for the lifetime of the
            WebSocket connection. It automatically handles ConnectionClosed
            exceptions gracefully.

        Examples:

            # Called automatically by the server for each connection
            task = asyncio.create_task(
                mock_provider.periodic_messages(websocket)
            )
            
            # Messages will be sent in this format:
            # {
            #     "type": "message",
            #     "server": "232769614004748288",
            #     "data": {
            #         "uid": "123456789012345001",
            #         "message": "hello",
            #         "channel": "527964146659229701"
            #     }
            # }

        Raises:
            websockets.ConnectionClosed: When the WebSocket connection is closed.
                This exception is caught and handled gracefully.
        """
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