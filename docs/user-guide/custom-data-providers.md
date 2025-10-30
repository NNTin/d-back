# Custom Data Providers

Learn how to replace d-back's mock data with real Discord API integration, database sources, or any custom data provider to power your d-zone deployment.

## Introduction

While d-back's mock data system is perfect for development and testing, production deployments require real data. Custom data providers allow you to:

- Integrate with the Discord API to fetch real user presence and server data
- Query databases for cached or processed user information
- Implement hybrid systems that combine multiple data sources
- Add custom business logic for data transformation

This guide provides complete examples for implementing production-ready data providers with error handling, caching, and performance optimization.

## Understanding Mock Data

Before replacing the mock system, let's understand what it provides.

### MockDataProvider Class

The `MockDataProvider` class (defined in `d_back/mock/data.py`) provides:

- **User data**: Mock Discord users with presence states (online, idle, dnd, offline)
- **Server data**: Pre-configured mock Discord servers
- **Periodic updates**: Background tasks that simulate status changes and messages

### Mock User Data Structure

```python
{
    "user_id": {
        "uid": "user_id",           # Discord user snowflake ID
        "username": "Username",      # Display name
        "status": "online",          # online, idle, dnd, offline
        "roleColor": "#ff6b6b"       # Hex color from highest role
    }
}
```

### Mock Server Data Structure

```python
{
    "server_id": {
        "id": "server_id",           # Discord server snowflake ID
        "name": "Server Name",       # Guild name
        "passworded": False,         # Whether OAuth2 is required
        "default": True              # Whether this is the default server
    }
}
```

!!! note "Automatic Fallback"
    If you don't register custom callbacks, d-back automatically uses the `MockDataProvider` for development convenience.

## Creating a Custom User Data Provider

Let's build a custom user data provider step by step.

### Step 1: Define the Function

```python
async def get_user_data(server_id: str) -> Dict[str, Any]:
    """
    Fetch user data for a Discord server.
    
    Args:
        server_id: Discord server snowflake ID
        
    Returns:
        Dictionary mapping user IDs to user objects
    """
    # Implementation here
    pass
```

### Step 2: Implement Data Fetching

```python
import aiohttp
from typing import Dict, Any

async def get_user_data(server_id: str) -> Dict[str, Any]:
    """Fetch real user data from Discord API."""
    try:
        # In production, use environment variables for secrets
        bot_token = os.getenv("DISCORD_BOT_TOKEN")
        
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bot {bot_token}"}
            
            # Fetch guild members
            url = f"https://discord.com/api/v10/guilds/{server_id}/members"
            params = {"limit": 1000}
            
            async with session.get(url, headers=headers, params=params) as resp:
                if resp.status != 200:
                    print(f"Error fetching members: {resp.status}")
                    return {}
                
                members = await resp.json()
                
                # Transform to d-back format
                users = {}
                for member in members:
                    user = member["user"]
                    user_id = user["id"]
                    
                    # Extract presence (requires gateway connection, simplified here)
                    status = "offline"  # Default
                    
                    # Get role color
                    role_color = get_highest_role_color(member.get("roles", []))
                    
                    users[user_id] = {
                        "uid": user_id,
                        "username": user.get("nick") or user["username"],
                        "status": status,
                        "roleColor": role_color or "#99AAB5"  # Default gray
                    }
                
                return users
    
    except Exception as e:
        print(f"Error in get_user_data: {e}")
        return {}

def get_highest_role_color(role_ids: list) -> str:
    """Get color from highest role (simplified)."""
    # In production, fetch role data from Discord API
    # This is a placeholder
    return "#5865F2"  # Discord blurple
```

### Step 3: Register the Callback

```python
from d_back.server import WebSocketServer

server = WebSocketServer(port=3000, host="localhost")
server.on_get_user_data(get_user_data)
```

## Creating a Custom Server Data Provider

### Basic Implementation

```python
async def get_server_data() -> Dict[str, Any]:
    """
    Fetch available Discord servers.
    
    Returns:
        Dictionary mapping server IDs to server objects
    """
    try:
        bot_token = os.getenv("DISCORD_BOT_TOKEN")
        
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bot {bot_token}"}
            url = "https://discord.com/api/v10/users/@me/guilds"
            
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    return {}
                
                guilds = await resp.json()
                
                servers = {}
                for guild in guilds:
                    servers[guild["id"]] = {
                        "id": guild["id"],
                        "name": guild["name"],
                        "passworded": False,  # Configure per server
                        "default": False
                    }
                
                # Set first server as default
                if servers:
                    first_id = next(iter(servers))
                    servers[first_id]["default"] = True
                
                return servers
    
    except Exception as e:
        print(f"Error in get_server_data: {e}")
        return {}

server = WebSocketServer()
server.on_get_server_data(get_server_data)
```

## Discord API Integration

### Complete Discord Bot Example

Here's a production-ready example using discord.py:

```python
import os
import asyncio
import discord
from discord.ext import commands
from d_back.server import WebSocketServer

# Create Discord bot
intents = discord.Intents.default()
intents.presences = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Create WebSocket server
ws_server = WebSocketServer(port=3000, host="0.0.0.0")

# Data provider functions
async def get_discord_user_data(server_id: str) -> Dict[str, Any]:
    """Fetch real-time user data from Discord bot."""
    try:
        guild = bot.get_guild(int(server_id))
        if not guild:
            return {}
        
        users = {}
        for member in guild.members:
            # Skip bots
            if member.bot:
                continue
            
            # Get status
            status_map = {
                discord.Status.online: "online",
                discord.Status.idle: "idle",
                discord.Status.dnd: "dnd",
                discord.Status.offline: "offline"
            }
            status = status_map.get(member.status, "offline")
            
            # Get role color
            role_color = "#99AAB5"  # Default gray
            if member.roles:
                # Get highest role with a color
                for role in reversed(member.roles):
                    if role.color.value != 0:
                        role_color = f"#{role.color.value:06x}"
                        break
            
            users[str(member.id)] = {
                "uid": str(member.id),
                "username": member.display_name,
                "status": status,
                "roleColor": role_color
            }
        
        return users
    
    except Exception as e:
        print(f"Error fetching user data: {e}")
        return {}

async def get_discord_servers() -> Dict[str, Any]:
    """Fetch Discord guilds from bot."""
    try:
        servers = {}
        for guild in bot.guilds:
            servers[str(guild.id)] = {
                "id": str(guild.id),
                "name": guild.name,
                "passworded": False,
                "default": False
            }
        
        # Set first server as default
        if servers:
            first_id = next(iter(servers))
            servers[first_id]["default"] = True
        
        return servers
    
    except Exception as e:
        print(f"Error fetching servers: {e}")
        return {}

# Register callbacks
ws_server.on_get_user_data(get_discord_user_data)
ws_server.on_get_server_data(get_discord_servers)

# Discord bot events
@bot.event
async def on_ready():
    """Start WebSocket server when bot is ready."""
    print(f"Bot logged in as {bot.user}")
    print(f"Starting WebSocket server...")
    await ws_server.start()

@bot.event
async def on_presence_update(before, after):
    """Broadcast presence changes to d-zone."""
    if before.status != after.status:
        status_map = {
            discord.Status.online: "online",
            discord.Status.idle: "idle",
            discord.Status.dnd: "dnd",
            discord.Status.offline: "offline"
        }
        
        await ws_server.broadcast_presence(
            server=str(after.guild.id),
            uid=str(after.id),
            status=status_map.get(after.status, "offline"),
            username=after.display_name,
            role_color=get_role_color(after)
        )

@bot.event
async def on_message(message):
    """Broadcast messages to d-zone."""
    if message.author.bot:
        return
    
    await ws_server.broadcast_message(
        server=str(message.guild.id),
        uid=str(message.author.id),
        message=message.content,
        channel=str(message.channel.id)
    )

def get_role_color(member) -> str:
    """Extract role color from member."""
    if member.roles:
        for role in reversed(member.roles):
            if role.color.value != 0:
                return f"#{role.color.value:06x}"
    return "#99AAB5"

# Main entry point
async def main():
    """Start both Discord bot and WebSocket server."""
    bot_token = os.getenv("DISCORD_BOT_TOKEN")
    if not bot_token:
        raise ValueError("DISCORD_BOT_TOKEN environment variable not set")
    
    # Start bot (this will trigger on_ready which starts WS server)
    await bot.start(bot_token)

if __name__ == "__main__":
    asyncio.run(main())
```

!!! tip "Prerequisites"
    Install discord.py: `pip install discord.py`

## Database Integration

### Using asyncpg with PostgreSQL

```python
import asyncpg
from typing import Dict, Any, Optional

class DatabaseProvider:
    """Database-backed data provider with caching."""
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Initialize database connection pool."""
        self.pool = await asyncpg.create_pool(self.db_url)
    
    async def get_user_data(self, server_id: str) -> Dict[str, Any]:
        """Fetch user data from database."""
        if not self.pool:
            return {}
        
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT user_id, username, status, role_color
                    FROM discord_users
                    WHERE server_id = $1 AND status != 'offline'
                """, server_id)
                
                users = {}
                for row in rows:
                    users[row["user_id"]] = {
                        "uid": row["user_id"],
                        "username": row["username"],
                        "status": row["status"],
                        "roleColor": row["role_color"]
                    }
                
                return users
        
        except Exception as e:
            print(f"Database error: {e}")
            return {}
    
    async def get_server_data(self) -> Dict[str, Any]:
        """Fetch server data from database."""
        if not self.pool:
            return {}
        
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT server_id, name, passworded, is_default
                    FROM discord_servers
                    WHERE enabled = true
                """)
                
                servers = {}
                for row in rows:
                    servers[row["server_id"]] = {
                        "id": row["server_id"],
                        "name": row["name"],
                        "passworded": row["passworded"],
                        "default": row["is_default"]
                    }
                
                return servers
        
        except Exception as e:
            print(f"Database error: {e}")
            return {}

# Usage
async def main():
    # Initialize database provider
    db = DatabaseProvider("postgresql://user:pass@localhost/d_back")
    await db.connect()
    
    # Create server with database callbacks
    server = WebSocketServer(port=3000, host="0.0.0.0")
    server.on_get_user_data(db.get_user_data)
    server.on_get_server_data(db.get_server_data)
    
    await server.start()
```

### Schema Example

```sql
CREATE TABLE discord_servers (
    server_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    passworded BOOLEAN DEFAULT FALSE,
    is_default BOOLEAN DEFAULT FALSE,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE discord_users (
    user_id VARCHAR(20),
    server_id VARCHAR(20) REFERENCES discord_servers(server_id),
    username VARCHAR(100) NOT NULL,
    status VARCHAR(10) NOT NULL,
    role_color VARCHAR(7) NOT NULL,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, server_id)
);

CREATE INDEX idx_users_server_status ON discord_users(server_id, status);
```

## Hybrid Approach

Combine mock and real data for gradual migration:

```python
async def hybrid_user_data(server_id: str) -> Dict[str, Any]:
    """Use real data for some servers, mock for others."""
    # Real data for production servers
    production_servers = ["232769614004748288", "482241773318701056"]
    
    if server_id in production_servers:
        # Fetch from Discord API
        return await get_discord_user_data(server_id)
    else:
        # Fall back to mock data
        from d_back.mock.data import MockDataProvider
        provider = MockDataProvider(server)
        return await provider.get_mock_user_data(server_id)

server = WebSocketServer()
server.on_get_user_data(hybrid_user_data)
```

### Fallback with Error Recovery

```python
async def resilient_user_data(server_id: str) -> Dict[str, Any]:
    """Try real data, fall back to mock on error."""
    try:
        # Try real data source
        data = await get_discord_user_data(server_id)
        
        # Validate data
        if data and isinstance(data, dict) and len(data) > 0:
            return data
        
        # Empty or invalid, use fallback
        raise ValueError("No data returned")
    
    except Exception as e:
        print(f"Falling back to mock data: {e}")
        
        # Use mock data as fallback
        from d_back.mock.data import MockDataProvider
        provider = MockDataProvider(server)
        return await provider.get_mock_user_data(server_id)

server = WebSocketServer()
server.on_get_user_data(resilient_user_data)
```

## Real-Time Updates

### Forwarding Discord Events

```python
import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
ws_server = WebSocketServer(port=3000, host="0.0.0.0")

@bot.event
async def on_presence_update(before, after):
    """Forward presence changes to connected clients."""
    # Only broadcast if status actually changed
    if before.status == after.status:
        return
    
    status_map = {
        discord.Status.online: "online",
        discord.Status.idle: "idle",
        discord.Status.dnd: "dnd",
        discord.Status.offline: "offline"
    }
    
    # Get role color
    role_color = "#99AAB5"
    for role in reversed(after.roles):
        if role.color.value != 0:
            role_color = f"#{role.color.value:06x}"
            break
    
    # Broadcast to all connected clients
    await ws_server.broadcast_presence(
        server=str(after.guild.id),
        uid=str(after.id),
        status=status_map.get(after.status, "offline"),
        username=after.display_name,
        role_color=role_color,
        delete=(after.status == discord.Status.offline)
    )

@bot.event
async def on_member_join(member):
    """Broadcast when a user joins."""
    await ws_server.broadcast_presence(
        server=str(member.guild.id),
        uid=str(member.id),
        status="online",
        username=member.display_name,
        role_color=get_role_color(member)
    )

@bot.event
async def on_member_remove(member):
    """Broadcast when a user leaves."""
    await ws_server.broadcast_presence(
        server=str(member.guild.id),
        uid=str(member.id),
        status="offline",
        delete=True
    )
```

### Performance Considerations

!!! warning "Rate Limiting"
    Discord's API has rate limits. Implement caching and batch requests to avoid hitting limits.

```python
import time
from functools import wraps

def rate_limit(calls_per_second=5):
    """Rate limiting decorator."""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            wait_time = min_interval - elapsed
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            
            last_called[0] = time.time()
            return await func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limit(calls_per_second=2)
async def fetch_discord_data(server_id: str):
    """Rate-limited Discord API calls."""
    # Implementation
    pass
```

## Testing Custom Providers

### Unit Testing

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_user_data_provider():
    """Test user data provider returns correct format."""
    # Mock Discord API response
    mock_response = [
        {
            "user": {"id": "123", "username": "TestUser"},
            "roles": [],
            "nick": None
        }
    ]
    
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        
        # Test provider
        data = await get_user_data("232769614004748288")
        
        # Assertions
        assert isinstance(data, dict)
        assert "123" in data
        assert data["123"]["username"] == "TestUser"
        assert data["123"]["status"] in ["online", "idle", "dnd", "offline"]
```

### Integration Testing

```python
@pytest.mark.asyncio
async def test_server_with_custom_provider():
    """Test WebSocketServer with custom data provider."""
    server = WebSocketServer(port=3001, host="localhost")
    server.on_get_user_data(get_user_data)
    
    # Start server
    await server.start()
    
    # Connect client and test
    async with websockets.connect("ws://localhost:3001") as websocket:
        # Request user data
        await websocket.send(json.dumps({
            "type": "get_user_data",
            "serverId": "232769614004748288"
        }))
        
        # Receive response
        response = await websocket.recv()
        data = json.loads(response)
        
        # Validate
        assert data["type"] == "user_data"
        assert "users" in data
    
    # Cleanup
    await server.stop()
```

## Performance Optimization

### Caching Strategy

```python
import time
from typing import Dict, Any, Tuple

class CachedDataProvider:
    """Data provider with intelligent caching."""
    
    def __init__(self, cache_ttl: int = 60):
        self.cache_ttl = cache_ttl
        self._user_cache: Dict[str, Tuple[Dict[str, Any], float]] = {}
        self._server_cache: Tuple[Dict[str, Any], float] = ({}, 0)
    
    async def get_user_data(self, server_id: str) -> Dict[str, Any]:
        """Get user data with caching."""
        # Check cache
        if server_id in self._user_cache:
            data, cached_time = self._user_cache[server_id]
            if time.time() - cached_time < self.cache_ttl:
                return data
        
        # Cache miss - fetch fresh data
        data = await self._fetch_user_data(server_id)
        self._user_cache[server_id] = (data, time.time())
        return data
    
    async def get_server_data(self) -> Dict[str, Any]:
        """Get server data with caching."""
        data, cached_time = self._server_cache
        
        if time.time() - cached_time < self.cache_ttl:
            return data
        
        # Cache miss
        data = await self._fetch_server_data()
        self._server_cache = (data, time.time())
        return data
    
    async def _fetch_user_data(self, server_id: str) -> Dict[str, Any]:
        """Actual data fetching logic."""
        # Implement Discord API call
        pass
    
    async def _fetch_server_data(self) -> Dict[str, Any]:
        """Actual server fetching logic."""
        # Implement Discord API call
        pass
    
    def invalidate_cache(self, server_id: Optional[str] = None):
        """Manually invalidate cache."""
        if server_id:
            self._user_cache.pop(server_id, None)
        else:
            self._user_cache.clear()
            self._server_cache = ({}, 0)
```

### Connection Pooling

```python
import aiohttp

class PooledProvider:
    """Provider with connection pooling."""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Create session on context enter."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close session on context exit."""
        if self.session:
            await self.session.close()
    
    async def get_user_data(self, server_id: str) -> Dict[str, Any]:
        """Fetch with persistent connection."""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        # Use existing session for requests
        async with self.session.get(f"https://api.example.com/users/{server_id}") as resp:
            return await resp.json()

# Usage
async def main():
    async with PooledProvider() as provider:
        server = WebSocketServer()
        server.on_get_user_data(provider.get_user_data)
        await server.start()
```

## Troubleshooting

### Common Issues

**Data format mismatches**:
```python
# Always validate and transform data
def validate_user_data(data: Dict) -> Dict:
    """Ensure user data has required fields."""
    required_fields = ["uid", "username", "status", "roleColor"]
    
    for user_id, user_data in data.items():
        for field in required_fields:
            if field not in user_data:
                # Provide default
                if field == "status":
                    user_data[field] = "offline"
                elif field == "roleColor":
                    user_data[field] = "#99AAB5"
                elif field == "uid":
                    user_data[field] = user_id
                elif field == "username":
                    user_data[field] = "Unknown"
    
    return data
```

**Async/await errors**:
```python
# ❌ Wrong: Not using await
data = get_user_data(server_id)  # Returns coroutine, not data

# ✅ Correct: Using await
data = await get_user_data(server_id)
```

**Connection timeouts**:
```python
async def get_user_data_with_timeout(server_id: str) -> Dict[str, Any]:
    """Fetch with timeout."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.example.com/users/{server_id}",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                return await resp.json()
    except asyncio.TimeoutError:
        print("Request timed out")
        return {}
```

### Debugging Tips

1. **Enable verbose logging**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **Log all callback invocations**:
```python
async def logged_callback(server_id: str):
    print(f"Callback invoked for server: {server_id}")
    data = await fetch_data(server_id)
    print(f"Returned {len(data)} users")
    return data
```

3. **Validate data before returning**:
```python
async def validated_callback(server_id: str):
    data = await fetch_data(server_id)
    
    # Log and validate
    if not isinstance(data, dict):
        print(f"ERROR: Expected dict, got {type(data)}")
        return {}
    
    for user_id, user_data in data.items():
        if not all(k in user_data for k in ["uid", "username", "status", "roleColor"]):
            print(f"WARNING: User {user_id} missing required fields")
    
    return data
```

## What's Next?

You now have the knowledge to implement production-ready custom data providers. Continue learning:

- **[Callbacks & Customization](callbacks.md)**: Deep dive into all callback types
- **[API Reference](../api-reference.md)**: Complete API documentation
- **[Developer Guide](../developer-guide.md)**: Contributing and architecture
