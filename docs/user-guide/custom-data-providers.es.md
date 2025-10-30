# Proveedores de Datos Personalizados

Esta guía explica cómo reemplazar los datos simulados de d-back con fuentes de datos reales como la API de Discord, bases de datos o servicios personalizados.

## Introducción

Por defecto, d-back usa `MockDataProvider` para generar datos de usuario y servidor simulados. Esto es perfecto para desarrollo y pruebas, pero para producción querrá usar datos reales. Esta guía muestra cómo integrar fuentes de datos personalizadas.

## Comprender Datos Simulados

El `MockDataProvider` integrado genera:
- 4 servidores de Discord preconfigurados
- Usuarios con estados realistas (online, idle, dnd, offline)
- Colores de roles y nombres de usuario variados
- Cambios periódicos de presencia y mensajes

Para ver los datos simulados en acción, inicie d-back y conéctese al servidor con su WebSocket.

## Crear un Proveedor de Datos de Usuario Personalizado

Reemplace el proveedor de datos de usuario simulados con su propia función:

```python
from typing import Dict, Any
from d_back.server import WebSocketServer

async def get_user_data(server_id: str) -> Dict[str, Any]:
    # Your custom logic to fetch user data
    users = {
        "123456789": {
            "uid": "123456789",
            "username": "Usuario Real",
            "status": "online",
            "roleColor": "#5865F2"
        }
    }
    return users

server = WebSocketServer(port=3000, host="localhost")
server.on_get_user_data(get_user_data)
```

## Crear un Proveedor de Datos de Servidor Personalizado

Similarmente, puede proporcionar su propia lista de servidores:

```python
from typing import Dict, Any, Optional

async def get_server_data(server_id: Optional[str] = None) -> Dict[str, Any]:
    servers = {
        "987654321": {
            "id": "987654321",
            "name": "Mi Servidor de Discord",
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

## Integración de API de Discord

Para usar datos reales de Discord, use la biblioteca `discord.py` o solicitudes HTTP directas:

### Usando discord.py

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

## Integración de Base de Datos

Para datos persistentes, use una base de datos:

### Usando PostgreSQL con asyncpg

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

## Enfoque Híbrido

Combine múltiples fuentes de datos:

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

## Actualizaciones en Tiempo Real

Para actualizar clientes cuando cambian datos:

```python
# When user status changes
await server.broadcast_presence(server_id, user_id, new_status)

# When you want to trigger full data refresh
await server.broadcast_message({
    "type": "refresh_data",
    "serverId": server_id
})
```

## Probar Proveedores Personalizados

Siempre pruebe sus proveedores de datos:

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

## Optimización de Rendimiento

### Cacheo

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

### Pooling de Conexiones

```python
from aiohttp import ClientSession

class PooledProvider:
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()
    
    async def get_user_data(self, server_id: str) -> Dict[str, Any]:
        async with self.session.get(f"https://api.example.com/users/{server_id}") as resp:
            return await resp.json()

# Usage
async def main():
    async with PooledProvider() as provider:
        server = WebSocketServer()
        server.on_get_user_data(provider.get_user_data)
        await server.start()
```

## Solución de Problemas

### Problemas Comunes

**Discrepancias de formato de datos**:
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

**Manejo de límites de tasa de API**:
```python
import asyncio

async def rate_limited_fetch(server_id: str) -> Dict[str, Any]:
    try:
        return await api.get_users(server_id)
    except RateLimitError as e:
        await asyncio.sleep(e.retry_after)
        return await api.get_users(server_id)
```

## ¿Qué Sigue?

- **[Callbacks y Personalización](callbacks.md)**: Aprenda más sobre el sistema de callbacks
- **[Configuración](configuration.md)**: Configure opciones de servidor
- **[Referencia de API](../api-reference.md)**: Documentación completa de la API
