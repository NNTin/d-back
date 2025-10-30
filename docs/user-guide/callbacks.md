# Callbacks & Customization

Learn how to customize d-back's behavior using callbacks to override default functionality, integrate with external data sources, and implement custom authentication logic.

## Introduction

d-back provides a powerful callback system that allows you to customize nearly every aspect of server behavior. Callbacks are async functions that you register with the server to replace default implementations, making it easy to:

- Replace mock data with real Discord API data
- Implement custom authentication and authorization
- Integrate with databases or other data sources
- Customize static file serving
- Add logging and monitoring

All callbacks are **async functions**, designed to work seamlessly with Python's asyncio framework. The callback system is defined in the `WebSocketServer` class and provides hooks at key points in the request lifecycle.

## Available Callbacks

### on_get_server_data Callback

**Purpose**: Provide a list of available Discord servers (guilds) to clients.

**Signature**:
```python
async def callback() -> Dict[str, Any]
```

**Expected Return Format**:
```python
{
    "server_id_1": {
        "id": "server_id_1",
        "name": "My Discord Server",
        "passworded": False,
        "default": True
    },
    "server_id_2": {
        "id": "server_id_2",
        "name": "Another Server",
        "passworded": True,
        "default": False
    }
}
```

**Example**:
```python
async def get_my_servers():
    """Fetch available Discord servers from a database."""
    # Your custom logic here
    return {
        "232769614004748288": {
            "id": "232769614004748288",
            "name": "d-world",
            "passworded": False,
            "default": True
        }
    }

server = WebSocketServer()
server.on_get_server_data(get_my_servers)
```

**Use Case**: Integrate with the Discord API to fetch the list of servers your bot is in, or fetch from a database of configured servers.

### on_get_user_data Callback

**Purpose**: Provide user data (presence, roles, etc.) for a specific Discord server.

**Signature**:
```python
async def callback(server_id: str) -> Dict[str, Any]
```

**Parameters**:
- `server_id` (str): Discord server snowflake ID

**Expected Return Format**:
```python
{
    "user_id_1": {
        "uid": "user_id_1",
        "username": "CoolUser",
        "status": "online",  # online, idle, dnd, offline
        "roleColor": "#ff6b6b"  # Hex color code
    },
    "user_id_2": {
        "uid": "user_id_2",
        "username": "AnotherUser",
        "status": "idle",
        "roleColor": "#5bc0de"
    }
}
```

**Example**:
```python
async def my_user_data_provider(server_id: str):
    """Fetch real user data from Discord API."""
    # Your custom logic here
    return {
        "user123": {
            "uid": "user123",
            "username": "MyUser",
            "status": "online",
            "roleColor": "#ff6b6b"
        }
    }

server = WebSocketServer()
server.on_get_user_data(my_user_data_provider)
```

**Use Case**: Fetch real Discord member data, query a database, or implement custom presence tracking.

### on_static_request Callback

**Purpose**: Handle custom static file requests with dynamic generation or custom routing.

**Signature**:
```python
async def callback(path: str) -> Optional[Tuple[str, str]]
```

**Parameters**:
- `path` (str): Requested file path (e.g., `"/index.html"`, `"/api/data"`)

**Expected Return**:
- `Tuple[str, str]`: (content_type, content) if handled - both strings
- `None`: Fall back to default static file serving

**Example**:
```python
async def custom_static_handler(path: str):
    """Dynamically generate or route static files."""
    if path == "/api/status":
        # Return dynamic JSON
        data = {"status": "ok", "version": "1.0.0"}
        return ("application/json", json.dumps(data))
    
    # Return None to use default static file serving
    return None

server = WebSocketServer()
server.on_static_request(custom_static_handler)
```

**Use Cases**:
- Dynamic file generation
- Custom API endpoints
- CDN integration
- A/B testing different frontend versions
- Server-side rendering

### on_validate_discord_user Callback

**Purpose**: Validate Discord OAuth2 tokens and verify user membership in a server.

**Signature**:
```python
async def callback(token: str, user_info: Dict[str, Any], server_id: str) -> bool
```

**Parameters**:
- `token` (str): Discord OAuth2 access token
- `user_info` (Dict[str, Any]): User information from Discord OAuth2
- `server_id` (str): Discord server ID to validate membership in

**Expected Return**:
- `bool`: True if the token is valid and user is a member, False otherwise

**Example**:
```python
import aiohttp

async def validate_token(token: str, user_info: Dict[str, Any], server_id: str) -> bool:
    """Validate Discord OAuth2 token and check server membership."""
    try:
        # Validate token with Discord API
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Check server membership
            async with session.get(f"https://discord.com/api/users/@me/guilds", headers=headers) as resp:
                if resp.status != 200:
                    return False
                guilds = await resp.json()
                
                # Check if user is in the requested server
                is_member = any(guild["id"] == server_id for guild in guilds)
                return is_member
    
    except Exception as e:
        print(f"Token validation error: {e}")
        return False

server = WebSocketServer()
server.on_validate_discord_user(validate_token)
```

**Use Case**: Implement real Discord OAuth2 validation for protected servers.

!!! warning "Security Note"
    Always validate tokens server-side. Never trust client-provided user IDs without token validation.

### on_get_client_id Callback

**Purpose**: Provide the Discord OAuth2 client ID for a specific server.

**Signature**:
```python
async def callback(server_id: str) -> str
```

**Parameters**:
- `server_id` (str): Discord server ID

**Expected Return**:
- `str`: OAuth2 client ID string

**Example**:
```python
async def get_client_id(server_id: str) -> str:
    """Return OAuth2 client ID for a server."""
    # Could fetch from database or configuration
    client_ids = {
        "232769614004748288": "123456789012345678",
        "482241773318701056": "987654321098765432"
    }
    return client_ids.get(server_id, "default_client_id")

server = WebSocketServer()
server.on_get_client_id(get_client_id)
```

**Use Case**: Support different OAuth2 applications per server for multi-tenant setups.

## Registering Callbacks

To register callbacks with d-back, call the callback method with your async function as an argument:

```python
server = WebSocketServer()
server.on_get_user_data(my_callback_function)
```

!!! note "Async Requirement"
    All callbacks **must** be async functions (defined with `async def`). Synchronous functions will cause errors.

### Complete Example with Multiple Callbacks

```python
import asyncio
from d_back.server import WebSocketServer

# Define callbacks
async def get_servers():
    return {
        "232769614004748288": {
            "id": "232769614004748288",
            "name": "d-world",
            "passworded": False,
            "default": True
        }
    }

async def get_users(server_id: str):
    # Fetch from database or Discord API
    return {
        "user123": {
            "uid": "user123",
            "username": "TestUser",
            "status": "online",
            "roleColor": "#ff6b6b"
        }
    }

async def validate_user(token: str, user_info: Dict[str, Any], server_id: str):
    # Implement real OAuth2 validation
    return True

# Create and configure server
async def main():
    server = WebSocketServer(port=3000, host="localhost")
    
    # Register callbacks
    server.on_get_server_data(get_servers)
    server.on_get_user_data(get_users)
    server.on_validate_discord_user(validate_user)
    
    # Start server
    await server.start()

asyncio.run(main())
```

## Broadcasting Methods

In addition to receiving data through callbacks, d-back provides methods to **broadcast** updates to all connected clients.

### broadcast_message

**Purpose**: Send chat messages to all clients subscribed to a server.

**Signature**:
```python
async def broadcast_message(
    server: str,
    uid: str,
    message: str,
    channel: str
)
```

**Parameters**:
- `server` (str): Discord server ID
- `uid` (str): User ID sending the message
- `message` (str): Message content
- `channel` (str): Channel ID where message was sent

**Example**:
```python
# When a Discord message is received
await server.broadcast_message(
    server="232769614004748288",
    uid="user123",
    message="Hello, d-zone!",
    channel="channel456"
)
```

### broadcast_presence

**Purpose**: Send user presence updates (status changes, online/offline events).

**Signature**:
```python
async def broadcast_presence(
    server: str,
    uid: str,
    status: str,
    username: Optional[str] = None,
    role_color: Optional[str] = None,
    delete: bool = False
)
```

**Parameters**:
- `server` (str): Discord server ID
- `uid` (str): User ID
- `status` (str): User status (`"online"`, `"idle"`, `"dnd"`, `"offline"`)
- `username` (Optional[str]): Username (required for new users)
- `role_color` (Optional[str]): Role color hex code
- `delete` (bool): Whether to remove the user (for offline/leave events)

**Example - User comes online**:
```python
await server.broadcast_presence(
    server="232769614004748288",
    uid="user123",
    status="online",
    username="CoolUser",
    role_color="#ff6b6b"
)
```

**Example - User goes offline**:
```python
await server.broadcast_presence(
    server="232769614004748288",
    uid="user123",
    status="offline",
    delete=True
)
```

### broadcast_client_id_update

**Purpose**: Send OAuth2 client ID updates to clients.

**Signature**:
```python
async def broadcast_client_id_update(
    server: str,
    client_id: str
)
```

**Parameters**:
- `server` (str): Discord server ID
- `client_id` (str): New OAuth2 client ID

**Example**:
```python
# When OAuth2 configuration changes
await server.broadcast_client_id_update(
    server="232769614004748288",
    client_id="new_client_id_here"
)
```

**Use Case**: Dynamic OAuth2 configuration updates without reconnecting clients.

## OAuth2 Integration

d-back includes built-in support for Discord OAuth2 authentication, allowing you to restrict access to specific servers.

### OAuth2 Flow

1. **Client requests connection** to a protected server
2. **Server checks** if the server requires authentication (passworded: true)
3. **Client obtains** OAuth2 token from Discord
4. **Client sends** token to d-back
5. **d-back validates** token using `on_validate_discord_user` callback
6. **Server grants** or denies access based on validation result

### Implementing OAuth2 Validation

```python
import aiohttp

async def oauth2_validator(token: str, user_info: Dict[str, Any], server_id: str) -> bool:
    """Validate Discord OAuth2 token."""
    try:
        async with aiohttp.ClientSession() as session:
            # Validate with Discord API
            headers = {"Authorization": f"Bearer {token}"}
            async with session.get("https://discord.com/api/users/@me/guilds", headers=headers) as resp:
                if resp.status == 200:
                    guilds = await resp.json()
                    # Check membership
                    for guild in guilds:
                        if guild["id"] == server_id:
                            return True
        
        return False
    
    except Exception as e:
        print(f"OAuth2 validation error: {e}")
        return False

server = WebSocketServer()
server.on_validate_discord_user(oauth2_validator)
```

### Security Considerations

!!! danger "Security Best Practices"
    - Always validate tokens server-side, never trust client claims
    - Use HTTPS in production to protect tokens in transit
    - Implement rate limiting to prevent token brute-forcing
    - Log authentication attempts for security monitoring
    - Rotate OAuth2 client secrets regularly
    - Set appropriate token expiration times

## Error Handling

Robust error handling in callbacks is essential for server stability.

### Best Practices

```python
import logging

logger = logging.getLogger(__name__)

async def safe_user_data_provider(server_id: str):
    """User data provider with comprehensive error handling."""
    try:
        # Your data fetching logic
        data = await fetch_user_data(server_id)
        
        # Validate data format
        if not isinstance(data, dict):
            logger.error(f"Invalid data format for server {server_id}")
            return {}
        
        return data
    
    except ConnectionError as e:
        logger.error(f"Connection error fetching user data: {e}")
        # Return empty dict or cached data
        return {}
    
    except Exception as e:
        logger.exception(f"Unexpected error in user data provider: {e}")
        # Return safe default
        return {}

server = WebSocketServer()
server.on_get_user_data(safe_user_data_provider)
```

### Error Handling Checklist

- ✅ **Use try-except** blocks to catch exceptions
- ✅ **Log errors** for debugging and monitoring
- ✅ **Return safe defaults** on error (empty dict, None, etc.)
- ✅ **Validate input parameters** before processing
- ✅ **Validate output format** before returning
- ✅ **Don't let exceptions propagate** to crash the server
- ✅ **Implement retries** for transient failures (with backoff)

## Best Practices

### Keep Callbacks Lightweight

Callbacks are called frequently, so performance matters:

```python
# ❌ Bad: Expensive operation on every call
async def slow_callback(server_id: str):
    # This queries the database every single time
    data = await database.query_all_users(server_id)
    return data

# ✅ Good: Use caching
from functools import lru_cache
import time

_cache = {}
_cache_ttl = 60  # seconds

async def fast_callback(server_id: str):
    # Check cache first
    if server_id in _cache:
        cached_data, cached_time = _cache[server_id]
        if time.time() - cached_time < _cache_ttl:
            return cached_data
    
    # Cache miss, fetch from database
    data = await database.query_all_users(server_id)
    _cache[server_id] = (data, time.time())
    return data
```

### Validate Input Parameters

```python
async def validated_callback(server_id: str):
    # Validate input
    if not server_id or not isinstance(server_id, str):
        logger.warning(f"Invalid server_id: {server_id}")
        return {}
    
    if not server_id.isdigit():
        logger.warning(f"server_id is not a snowflake: {server_id}")
        return {}
    
    # Proceed with valid input
    return await fetch_data(server_id)
```

### Return Consistent Data Structures

```python
# Always return the expected format
async def consistent_callback(server_id: str):
    try:
        data = await fetch_data(server_id)
        
        # Ensure correct format
        if not isinstance(data, dict):
            return {}
        
        # Validate required fields
        for user_id, user_data in data.items():
            required_fields = ["uid", "username", "status", "roleColor"]
            if not all(field in user_data for field in required_fields):
                logger.warning(f"User {user_id} missing required fields")
                # Fix or skip invalid user
                continue
        
        return data
    
    except Exception:
        # Always return expected type on error
        return {}
```

### Test Callbacks Independently

```python
import pytest

@pytest.mark.asyncio
async def test_user_data_callback():
    """Test user data callback returns correct format."""
    data = await my_user_data_provider("232769614004748288")
    
    # Check return type
    assert isinstance(data, dict)
    
    # Check user data format
    for user_id, user_data in data.items():
        assert "uid" in user_data
        assert "username" in user_data
        assert "status" in user_data
        assert user_data["status"] in ["online", "idle", "dnd", "offline"]
        assert "roleColor" in user_data
        assert user_data["roleColor"].startswith("#")
```

## What's Next?

Now that you understand callbacks, explore how to implement complete custom data providers:

- **[Custom Data Providers](custom-data-providers.md)**: Full Discord API integration examples
- **[API Reference](../api-reference.md)**: Detailed API documentation
- **[Configuration](configuration.md)**: Server configuration options
