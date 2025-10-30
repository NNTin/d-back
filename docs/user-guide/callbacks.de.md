# Callbacks & Anpassung

Dieser Leitfaden erklärt, wie Sie das Verhalten von d-back mithilfe von Callback-Funktionen für Datenabruf, Authentifizierung und Nachrichten-Broadcasting anpassen.

## Einführung

d-back bietet ein flexibles Callback-System, das es Ihnen ermöglicht, das Standardverhalten des Servers zu überschreiben. Callbacks sind asynchrone Funktionen, die an bestimmten Punkten im Server-Lebenszyklus aufgerufen werden und Ihnen Folgendes ermöglichen:

- Benutzerdefinierte Benutzer- und Serverdaten bereitzustellen
- Benutzerdefinierte Authentifizierung zu implementieren
- Anfragen für statische Dateien zu verwalten
- Discord-Benutzer und OAuth2-Tokens zu validieren

Alle Callbacks sind optional. Wenn kein Callback bereitgestellt wird, verwendet d-back sein Standardverhalten (normalerweise unter Verwendung von MockDataProvider).

## Verfügbare Callbacks

### on_get_server_data Callback

**Zweck**: Die Liste der verfügbaren Discord-Server bereitstellen.

**Signatur**:
```python
async def on_get_server_data(server_id: Optional[str] = None) -> Dict[str, Any]
```

**Parameter**:
- `server_id` (str, optional): Spezifische Server-ID zum Abrufen oder None für alle Server

**Rückgabe**: Dictionary, das Server-IDs auf Serverdaten abbildet

**Beispiel**:
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

### on_get_user_data Callback

**Zweck**: Benutzerdaten für einen bestimmten Discord-Server bereitstellen.

**Signatur**:
```python
async def on_get_user_data(server_id: str) -> Dict[str, Any]
```

**Parameter**:
- `server_id` (str): Discord-Server-ID, für die Benutzerdaten abgerufen werden sollen

**Rückgabe**: Dictionary, das Benutzer-IDs auf Benutzerdaten abbildet

**Anwendungsfall**: Mock-Daten durch echte Discord-Benutzer, Datenbankdaten oder benutzerdefinierte Quellen ersetzen.

**Beispiel**:
```python
async def my_user_data_provider(server_id: str) -> Dict[str, Any]:
    return {
        "user123": {
            "uid": "user123",
            "username": "Hans",
            "status": "online",
            "roleColor": "#3498db"
        }
    }

server.on_get_user_data(my_user_data_provider)
```

### on_static_request Callback

**Zweck**: Benutzerdefinierte statische Dateianfragen verwalten.

**Signatur**:
```python
async def on_static_request(path: str) -> Optional[Tuple[str, str]]
```

**Parameter**:
- `path` (str): Angeforderter Dateipfad (z.B. `/index.html`)

**Rückgabe**: Tupel von `(content_type, content)` beides Strings, oder None für Standardverarbeitung

**Anwendungsfall**: Inhalte dynamisch generieren, von benutzerdefinierten Standorten ausliefern oder benutzerdefinierte Routing-Logik implementieren.

**Beispiel**:
```python
async def custom_static_handler(path: str) -> Optional[Tuple[str, str]]:
    if path == "/api/status":
        return ("application/json", '{"status": "ok"}')
    return None  # Use default handler

server.on_static_request(custom_static_handler)
```

### on_validate_discord_user Callback

**Zweck**: Discord-Benutzer während OAuth2-Authentifizierungsabläufen validieren.

**Signatur**:
```python
async def on_validate_discord_user(token: str, user_info: Dict[str, Any], server_id: str) -> bool
```

**Parameter**:
- `token` (str): Discord-OAuth2-Zugriffstoken
- `user_info` (Dict): Discord-Benutzerinformationen von der API
- `server_id` (str): ID des Discord-Servers, auf den zugegriffen wird

**Rückgabe**: True, wenn der Benutzer Zugriff haben sollte, False andernfalls

**Anwendungsfall**: Rollenbasierte Zugriffskontrolle implementieren, Server-Mitgliedschaftsvalidierung oder benutzerdefinierte Autorisierungslogik.

**Beispiel**:
```python
async def validate_user(token: str, user_info: Dict[str, Any], server_id: str) -> bool:
    # Check if user is member of the server
    user_id = user_info.get("id")
    # Your validation logic here
    return True  # or False

server.on_validate_discord_user(validate_user)
```

### on_get_client_id Callback

**Zweck**: Discord-OAuth2-Client-ID bereitstellen.

**Signatur**:
```python
async def on_get_client_id(server_id: str) -> str
```

**Parameter**:
- `server_id` (str): Discord-Server-ID

**Rückgabe**: Discord-OAuth2-Client-ID als String

**Anwendungsfall**: OAuth2-Authentifizierung für geschützten Serverzugriff aktivieren.

**Beispiel**:
```python
async def get_client_id(server_id: str) -> str:
    return "YOUR_DISCORD_CLIENT_ID"

server.on_get_client_id(get_client_id)
```

## Callbacks registrieren

Callbacks werden durch Aufrufen der entsprechenden Methode auf der Serverinstanz registriert:

```python
from d_back.server import WebSocketServer

server = WebSocketServer(port=3000, host="localhost")

# Register callbacks
server.on_get_user_data(my_user_data_callback)
server.on_get_server_data(my_server_data_callback)
server.on_validate_discord_user(my_validation_callback)
```

## Vollständiges Beispiel

```python
import asyncio
from typing import Dict, Any, Optional, Tuple
from d_back.server import WebSocketServer

async def get_servers(server_id: Optional[str] = None) -> Dict[str, Any]:
    servers = {
        "232769614004748288": {
            "id": "232769614004748288",
            "name": "Mein Server",
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
            "username": "Hans",
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

## Broadcasting-Methoden

d-back stellt Methoden bereit, um Echtzeit-Updates an verbundene Clients zu broadcasten.

### broadcast_message

Eine benutzerdefinierte Nachricht an alle verbundenen Clients broadcasten.

```python
await server.broadcast_message({
    "type": "custom_event",
    "data": {"message": "Hallo, Welt!"}
})
```

### broadcast_presence

Präsenzstatusänderung eines Benutzers broadcasten.

```python
await server.broadcast_presence("232769614004748288", "user123", "dnd")
```

### broadcast_client_id_update

OAuth2-Client-ID-Aktualisierung broadcasten.

```python
await server.broadcast_client_id_update("232769614004748288", "YOUR_CLIENT_ID")
```

## OAuth2-Integration

Um OAuth2-Authentifizierung zu aktivieren:

1. Registrieren Sie einen `on_get_client_id`-Callback, um Ihre Discord-Client-ID bereitzustellen
2. Registrieren Sie einen `on_validate_discord_user`-Callback, um Benutzer zu validieren
3. Konfigurieren Sie Ihre Discord-Anwendung mit der entsprechenden Redirect-URI

**OAuth2-Ablauf**:
1. Client fordert Client-ID an
2. Client leitet Benutzer zu Discord zur Authentifizierung weiter
3. Discord leitet zurück mit Autorisierungscode
4. Client tauscht Code gegen Zugriffstoken aus
5. d-back validiert Token und Benutzer mit Ihrem Callback

## Fehlerbehandlung

Implementieren Sie immer angemessene Fehlerbehandlung in Ihren Callbacks:

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

## Best Practices

- **Halten Sie Callbacks asynchron**: Alle Callbacks müssen `async`-Funktionen sein
- **Behandeln Sie Fehler elegant**: Verwenden Sie immer try/except
- **Geben Sie korrekt formatierte Daten zurück**: Folgen Sie den erwarteten Datenstrukturen
- **Dokumentieren Sie Ihr Verhalten**: Fügen Sie Docstrings zu benutzerdefinierten Callback-Funktionen hinzu
- **Testen Sie gründlich**: Testen Sie Callbacks mit verschiedenen Eingaben

## Was kommt als Nächstes?

- **[Benutzerdefinierte Datenanbieter](custom-data-providers.md)**: Erfahren Sie, wie Sie echte Discord-API oder Datenbanken integrieren
- **[Konfiguration](configuration.md)**: Konfigurieren Sie Serveroptionen und Bereitstellung
- **[API-Referenz](../api-reference.md)**: Detaillierte API-Dokumentation
