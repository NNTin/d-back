# Callbacks y Personalización

Esta guía explica cómo personalizar el comportamiento de d-back usando funciones callback para recuperación de datos, autenticación y difusión de mensajes.

## Introducción

d-back proporciona un sistema de callback flexible que le permite anular el comportamiento predeterminado del servidor. Los callbacks son funciones asíncronas que se invocan en puntos específicos del ciclo de vida del servidor, permitiéndole:

- Proporcionar datos de usuario y servidor personalizados
- Implementar autenticación personalizada
- Manejar solicitudes de archivos estáticos
- Validar usuarios y tokens de Discord OAuth2

Todos los callbacks son opcionales. Si no se proporciona un callback, d-back usa su comportamiento predeterminado (generalmente usando MockDataProvider).

## Callbacks Disponibles

### Callback on_get_server_data

**Propósito**: Proporcionar la lista de servidores de Discord disponibles.

**Signatura**:
```python
async def on_get_server_data(server_id: Optional[str] = None) -> Dict[str, Any]
```

**Parámetros**:
- `server_id` (str, opcional): ID de servidor específico a recuperar, o None para todos los servidores

**Retorna**: Diccionario mapeando IDs de servidor a datos de servidor

**Ejemplo**:
```python
async def get_my_servers(server_id: Optional[str] = None) -> Dict[str, Any]:
    servers = {
        "232769614004748288": {
            "id": "232769614004748288",
            "name": "d-world",
            "passworded": False,
            "is_default": True,
            "enabled": True
        }
    }
    
    if server_id:
        return {server_id: servers.get(server_id, {})}
    return servers

server.on_get_server_data(get_my_servers)
```

### Callback on_get_user_data

**Propósito**: Proporcionar datos de usuario para un servidor de Discord específico.

**Signatura**:
```python
async def on_get_user_data(server_id: str) -> Dict[str, Any]
```

**Parámetros**:
- `server_id` (str): ID del servidor de Discord para el cual recuperar datos de usuario

**Retorna**: Diccionario mapeando IDs de usuario a datos de usuario

**Caso de Uso**: Reemplazar datos simulados con usuarios reales de Discord, datos de base de datos o fuentes personalizadas.

**Ejemplo**:
```python
async def my_user_data_provider(server_id: str) -> Dict[str, Any]:
    return {
        "user123": {
            "uid": "user123",
            "username": "Juan",
            "status": "online",
            "roleColor": "#3498db"
        }
    }

server.on_get_user_data(my_user_data_provider)
```

### Callback on_static_request

**Propósito**: Manejar solicitudes de archivos estáticos personalizados.

**Signatura**:
```python
async def on_static_request(path: str) -> Optional[Tuple[str, str]]
```

**Parámetros**:
- `path` (str): Ruta del archivo solicitado (e.g., `/index.html`)

**Retorna**: Tupla de `(content_type, content)` ambos strings, o None para usar manejo predeterminado

**Caso de Uso**: Generar contenido dinámicamente, servir desde ubicaciones personalizadas o implementar lógica de enrutamiento personalizada.

**Ejemplo**:
```python
async def custom_static_handler(path: str) -> Optional[Tuple[str, str]]:
    if path == "/api/status":
        return ("application/json", '{"status": "ok"}')
    return None  # Use default handler

server.on_static_request(custom_static_handler)
```

### Callback on_validate_discord_user

**Propósito**: Validar usuarios de Discord durante flujos de autenticación OAuth2.

**Signatura**:
```python
async def on_validate_discord_user(token: str, user_info: Dict[str, Any], server_id: str) -> bool
```

**Parámetros**:
- `token` (str): Token de acceso de Discord OAuth2
- `user_info` (Dict): Información de usuario de Discord de la API
- `server_id` (str): ID del servidor de Discord que se está accediendo

**Retorna**: True si el usuario debe tener acceso, False de lo contrario

**Caso de Uso**: Implementar control de acceso basado en roles, validación de membresía de servidor o lógica de autorización personalizada.

**Ejemplo**:
```python
async def validate_user(token: str, user_info: Dict[str, Any], server_id: str) -> bool:
    # Check if user is member of the server
    user_id = user_info.get("id")
    # Your validation logic here
    return True  # or False

server.on_validate_discord_user(validate_user)
```

### Callback on_get_client_id

**Propósito**: Proporcionar el ID de cliente de Discord OAuth2.

**Signatura**:
```python
async def on_get_client_id(server_id: str) -> str
```

**Parámetros**:
- `server_id` (str): ID del servidor de Discord

**Retorna**: ID de cliente de Discord OAuth2 como string

**Caso de Uso**: Habilitar autenticación OAuth2 para acceso protegido al servidor.

**Ejemplo**:
```python
async def get_client_id(server_id: str) -> str:
    return "YOUR_DISCORD_CLIENT_ID"

server.on_get_client_id(get_client_id)
```

## Registrar Callbacks

Los callbacks se registran llamando al método correspondiente en la instancia del servidor:

```python
from d_back.server import WebSocketServer

server = WebSocketServer(port=3000, host="localhost")

# Register callbacks
server.on_get_user_data(my_user_data_callback)
server.on_get_server_data(my_server_data_callback)
server.on_validate_discord_user(my_validation_callback)
```

## Ejemplo Completo

```python
import asyncio
from typing import Dict, Any, Optional, Tuple
from d_back.server import WebSocketServer

async def get_servers(server_id: Optional[str] = None) -> Dict[str, Any]:
    servers = {
        "232769614004748288": {
            "id": "232769614004748288",
            "name": "Mi Servidor",
            "passworded": False,
            "is_default": True,
            "enabled": True
        }
    }
    if server_id:
        return {server_id: servers.get(server_id, {})}
    return servers

async def get_users(server_id: str) -> Dict[str, Any]:
    return {
        "user1": {
            "uid": "user1",
            "username": "Juan",
            "status": "online",
            "roleColor": "#3498db"
        }
    }

async def main():
    server = WebSocketServer(port=3000, host="localhost")
    
    # Register callbacks
    server.on_get_server_data(get_servers)
    server.on_get_user_data(get_users)
    
    await server.start()

asyncio.run(main())
```

## Métodos de Difusión

d-back proporciona métodos para difundir actualizaciones en tiempo real a clientes conectados.

### broadcast_message

Difundir un mensaje personalizado a todos los clientes conectados.

```python
await server.broadcast_message({
    "type": "custom_event",
    "data": {"message": "¡Hola, mundo!"}
})
```

### broadcast_presence

Difundir cambio de estado de presencia de usuario.

```python
await server.broadcast_presence("232769614004748288", "user123", "dnd")
```

### broadcast_client_id_update

Difundir actualización de ID de cliente OAuth2.

```python
await server.broadcast_client_id_update("232769614004748288", "YOUR_CLIENT_ID")
```

## Integración OAuth2

Para habilitar autenticación OAuth2:

1. Registre un callback `on_get_client_id` para proporcionar su ID de cliente de Discord
2. Registre un callback `on_validate_discord_user` para validar usuarios
3. Configure su aplicación de Discord con el URI de redirección apropiado

**Flujo OAuth2**:
1. Cliente solicita ID de cliente
2. Cliente redirige al usuario a Discord para autenticación
3. Discord redirige de vuelta con código de autorización
4. Cliente intercambia código por token de acceso
5. d-back valida token y usuario usando su callback

## Manejo de Errores

Siempre implemente manejo de errores apropiado en sus callbacks:

```python
async def safe_user_data_provider(server_id: str) -> Dict[str, Any]:
    try:
        # Your data retrieval logic
        data = await fetch_user_data(server_id)
        return data
    except Exception as e:
        print(f"Error fetching user data: {e}")
        return {}  # Return empty dict on error

server.on_get_user_data(safe_user_data_provider)
```

## Mejores Prácticas

- **Mantenga callbacks asíncronos**: Todos los callbacks deben ser funciones `async`
- **Maneje errores graciosamente**: Siempre use try/except
- **Retorne datos correctamente formateados**: Siga las estructuras de datos esperadas
- **Documente su comportamiento**: Agregue docstrings a funciones callback personalizadas
- **Pruebe completamente**: Pruebe callbacks con varios inputs

## ¿Qué Sigue?

- **[Proveedores de Datos Personalizados](custom-data-providers.md)**: Aprenda cómo integrar API de Discord real o bases de datos
- **[Configuración](configuration.md)**: Configure opciones de servidor y despliegue
- **[Referencia de API](../api-reference.md)**: Documentación detallada de API
