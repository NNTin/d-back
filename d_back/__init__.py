"""D-Back: WebSocket server for real-time Discord user presence and chat.

D-Back is a WebSocket server that provides real-time Discord user presence
information and chat messages. It integrates with Discord OAuth2 for user
authentication and serves a static web interface.

Main Components:
    - WebSocketServer: Core WebSocket server with HTTP static file serving
    - MockDataProvider: Mock data generator for testing and development
    - OAuth2 authentication: Discord user validation

Basic Usage:

    import asyncio
    from d_back import WebSocketServer
    
    async def main():
        server = WebSocketServer(port=5555, host='localhost')
        server.static_dir = './dist'
        
        # Register OAuth client ID provider
        async def get_client_id(server_id: str) -> str:
            return 'your_discord_client_id'
        
        server.on_get_client_id(get_client_id)
        
        await server.run_forever()
    
    asyncio.run(main())

Command Line Usage:

    # Start server with default settings
    python -m d_back
    
    # Start server with custom port
    python -m d_back --port 8080
    
    # Start server with custom static directory
    python -m d_back --static-dir /path/to/dist

For more information, see the documentation at:
https://github.com/nntin/d-back
"""

__version__ = "0.0.18"

from d_back.server import WebSocketServer
from d_back.mock.data import MockDataProvider

__all__ = [
    "WebSocketServer",
    "MockDataProvider",
    "__version__",
]

