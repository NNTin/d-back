"""Mock data providers for D-Back WebSocket server testing.

This module provides mock data generators for testing the D-Back WebSocket
server without requiring actual Discord API connections. It includes mock
user data, server data, and periodic updates for simulating realistic
Discord user activity.

When to Use:
    - Development and testing without Discord API access
    - Automated integration tests
    - Demo environments
    - Load testing with predictable data

Warning:
    Mock data providers are intended for development and testing only.
    Do not use in production environments as they generate fake data
    and do not connect to actual Discord servers.

Examples:

    import asyncio
    from d_back.mock import MockDataProvider
    from d_back import WebSocketServer
    
    async def main():
        # Create server with mock data
        server = WebSocketServer(port=5555)
        mock_provider = MockDataProvider(server)
        
        # Register callbacks with mock data
        server.on_get_server_data(mock_provider.get_mock_server_data)
        server.on_get_user_data(mock_provider.get_mock_user_data)
        
        # Start server with mock data
        await server.run_forever()
    
    asyncio.run(main())
"""

from .data import MockDataProvider

__all__ = ['MockDataProvider']

