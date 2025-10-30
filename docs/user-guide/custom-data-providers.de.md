# Benutzerdefinierte Datenanbieter

Dieser Leitfaden erklärt, wie Sie die Mock-Daten von d-back durch echte Datenquellen wie die Discord-API, Datenbanken oder benutzerdefinierte Dienste ersetzen.

## Einführung

Standardmäßig verwendet d-back `MockDataProvider`, um simulierte Benutzer- und Serverdaten zu generieren. Dies ist perfekt für Entwicklung und Tests, aber für die Produktion möchten Sie echte Daten verwenden. Dieser Leitfaden zeigt, wie Sie benutzerdefinierte Datenquellen integrieren.

## Mock-Daten verstehen

Der integrierte `MockDataProvider` generiert:
- 4 vorkonfigurierte Discord-Server
- Benutzer mit realistischen Stati (online, idle, dnd, offline)
- Rollenfarben und verschiedene Benutzernamen
- Periodische Präsenzänderungen und Nachrichten

Um die Mock-Daten in Aktion zu sehen, starten Sie d-back und verbinden Sie sich über WebSocket mit dem Server.

## Benutzerdefinierten Benutzerdatenanbieter erstellen

Ersetzen Sie den Mock-Benutzerdatenanbieter durch Ihre eigene Funktion:

```python
from typing import Dict, Any
from d_back.server import WebSocketServer

async def get_user_data(server_id: str) -> Dict[str, Any]:
    # Your custom logic to fetch user data
    users = {
        "123456789": {
            "uid": "123456789",
            "username": "Echter Benutzer",
            "status": "online",
            "roleColor": "#5865F2"
        }
    }
    return users

server = WebSocketServer(port=3000, host="localhost")
server.on_get_user_data(get_user_data)
```

## Benutzerdefinierten Serverdatenanbieter erstellen

Ähnlich können Sie Ihre eigene Serverliste bereitstellen:

```python
from typing import Dict, Any, Optional

async def get_server_data(server_id: Optional[str] = None) -> Dict[str, Any]:
    servers = {
        "987654321": {
            "id": "987654321",
            "name": "Mein Discord-Server",
            "passworded": False,
            "is_default": True,
            "enabled": True
        }
    }
    
    if server_id:
        return {server_id: servers.get(server_id, {})}
    return servers

server.on_get_server_data(get_server_data)
```

## Discord-API-Integration

Um echte Discord-Daten zu verwenden, nutzen Sie die `discord.py`-Bibliothek oder direkte HTTP-Anfragen:

### Verwendung von discord.py

```python
import discord
from discord.ext import commands
from d_back.server import WebSocketServer

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
ws_server = WebSocketServer(port=3000, host="localhost")

async def get_discord_user_data(server_id: str) -> Dict[str, Any]:
    guild = bot.get_guild(int(server_id))
    if not guild:
        return {}
    
    users = {}
    for member in guild.members:
        users[str(member.id)] = {
            "uid": str(member.id),
            "username": member.display_name,
            "status": str(member.status),
            "roleColor": str(member.color) if member.color else "#000000"
        }
    return users

async def get_discord_servers(server_id: Optional[str] = None) -> Dict[str, Any]:
    servers = {}
    for guild in bot.guilds:
        servers[str(guild.id)] = {
            "id": str(guild.id),
            "name": guild.name,
            "passworded": False,
            "is_default": False,
            "enabled": True
        }
    
    if server_id:
        return {server_id: servers.get(server_id, {})}
    return servers

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
        await ws_server.broadcast_presence(
            str(after.guild.id),
            str(after.id),
            str(after.status)
        )

# Run bot
bot.run("YOUR_BOT_TOKEN")
```

## Datenbankintegration

Für persistente Daten verwenden Sie eine Datenbank:

### Verwendung von PostgreSQL mit asyncpg

```python
import asyncpg
from typing import Dict, Any, Optional

class DatabaseProvider:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.pool = None
    
    async def connect(self):
        self.pool = await asyncpg.create_pool(self.connection_string)
    
    async def get_user_data(self, server_id: str) -> Dict[str, Any]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT user_id, username, status, role_color FROM users WHERE server_id = $1",
                server_id
            )
            
            users = {}
            for row in rows:
                users[row['user_id']] = {
                    "uid": row['user_id'],
                    "username": row['username'],
                    "status": row['status'],
                    "roleColor": row['role_color']
                }
            return users
    
    async def get_server_data(self, server_id: Optional[str] = None) -> Dict[str, Any]:
        async with self.pool.acquire() as conn:
            if server_id:
                rows = await conn.fetch(
                    "SELECT * FROM servers WHERE server_id = $1",
                    server_id
                )
            else:
                rows = await conn.fetch("SELECT * FROM servers")
            
            servers = {}
            for row in rows:
                servers[row['server_id']] = {
                    "id": row['server_id'],
                    "name": row['name'],
                    "passworded": row['passworded'],
                    "is_default": row['is_default'],
                    "enabled": row['enabled']
                }
            return servers

# Usage
async def main():
    db = DatabaseProvider("postgresql://user:pass@localhost/d_back")
    await db.connect()
    
    # Create server with database callbacks
    server = WebSocketServer(port=3000, host="0.0.0.0")
    server.on_get_user_data(db.get_user_data)
    server.on_get_server_data(db.get_server_data)
    
    await server.start()
```

## Hybrider Ansatz

Kombinieren Sie mehrere Datenquellen:

```python
async def hybrid_user_data(server_id: str) -> Dict[str, Any]:
    # Try Discord API first
    discord_users = await get_discord_users(server_id)
    
    # Fall back to database if Discord unavailable
    if not discord_users:
        discord_users = await get_database_users(server_id)
    
    # Merge with cached data
    cached_users = await get_cached_users(server_id)
    discord_users.update(cached_users)
    
    return discord_users

server.on_get_user_data(hybrid_user_data)
```

## Echtzeit-Updates

Um Clients zu aktualisieren, wenn sich Daten ändern:

```python
# When user status changes
await server.broadcast_presence(server_id, user_id, new_status)

# When you want to trigger full data refresh
await server.broadcast_message({
    "type": "refresh_data",
    "serverId": server_id
})
```

## Benutzerdefinierte Anbieter testen

Testen Sie immer Ihre Datenanbieter:

```python
import pytest

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
        
        assert data["type"] == "user_data"
        assert "users" in data
```

## Leistungsoptimierung

### Caching

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedProvider:
    def __init__(self):
        self.cache = {}
        self.cache_timeout = timedelta(minutes=5)
    
    async def get_user_data(self, server_id: str) -> Dict[str, Any]:
        now = datetime.now()
        
        # Check cache
        if server_id in self.cache:
            cached_data, cached_time = self.cache[server_id]
            if now - cached_time < self.cache_timeout:
                return cached_data
        
        # Fetch fresh data
        data = await fetch_from_api(server_id)
        self.cache[server_id] = (data, now)
        return data
```

## Fehlerbehebung

### Häufige Probleme

**Datenformat-Diskrepanzen**:
```python
# Always validate and transform data
def validate_user_data(data: Dict) -> Dict:
    """Ensure user data has required fields."""
    required_fields = ["uid", "username", "status", "roleColor"]
    
    for user_id, user_data in data.items():
        for field in required_fields:
            if field not in user_data:
                user_data[field] = get_default_value(field)
    
    return data
```

## Was kommt als Nächstes?

- **[Callbacks & Anpassung](callbacks.md)**: Erfahren Sie mehr über das Callback-System
- **[Konfiguration](configuration.md)**: Konfigurieren Sie Serveroptionen
- **[API-Referenz](../api-reference.md)**: Vollständige API-Dokumentation
