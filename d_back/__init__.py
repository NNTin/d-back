"""D-Back: WebSocket server for real-time Discord user presence and chat.

D-Back is a WebSocket server that provides real-time Discord user presence
information and chat messages. It integrates with Discord OAuth2 for user
authentication and serves a static web interface.

Main Components:
    - WebSocketServer: Core WebSocket server with HTTP static file serving
    - MockDataProvider: Mock data generator for testing and development
    - OAuth2 authentication: Discord user validation

Basic Usage::

    from d_back import WebSocketServer
    
    server = WebSocketServer(
        port=5555,
        static_dir='./dist',
        client_id='your_discord_client_id'
    )
    server.start()

Command Line Usage::

    # Start server with default settings
    python -m d_back
    
    # Start server with custom port
    python -m d_back --port 8080
    
    # Start server with custom static directory
    python -m d_back --static-dir /path/to/dist

For more information, see the documentation at:
https://github.com/nntin/d-back
"""

__version__ = "0.0.14"

from d_back.server import WebSocketServer
from d_back.mock.data import MockDataProvider

__all__ = [
    "WebSocketServer",
    "MockDataProvider",
    "__version__",
]

