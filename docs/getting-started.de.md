# Erste Schritte

Willkommen bei d-back! Diese Anleitung hilft Ihnen, den WebSocket-Server, der die d-zone Ambient-Life-Simulation antreibt, in Betrieb zu nehmen. Am Ende dieser Anleitung haben Sie d-back installiert und bereitstellen Mock-Discord-Daten über WebSocket-Verbindungen.

## Voraussetzungen

Bevor Sie beginnen, stellen Sie sicher, dass Sie Folgendes haben:

- **Python 3.8 oder höher** auf Ihrem System installiert
- **pip-Paketmanager** (kommt normalerweise mit Python)
- **Grundverständnis von async/await in Python** (hilfreich, aber nicht erforderlich)
- **Git** (optional, nur bei Installation aus dem Quellcode erforderlich)

## Installation

d-back kann auf verschiedene Arten installiert werden. Wählen Sie die Methode, die am besten zu Ihren Bedürfnissen passt:

### Von PyPI (Empfohlen)

Der einfachste Weg, d-back zu installieren, ist über den Python Package Index:

```bash
pip install d-back
```

### Aus dem Quellcode

Für die neueste Entwicklungsversion oder wenn Sie beitragen möchten:

1. Repository klonen:
   ```bash
   git clone https://github.com/NNTin/d-back.git
   cd d-back
   ```

2. Virtuelle Umgebung erstellen (empfohlen):

   === "Windows"
       ```bash
       python -m venv .venv
       .venv\Scripts\activate
       ```

   === "macOS/Linux"
       ```bash
       python3 -m venv .venv
       source .venv/bin/activate
       ```

3. Im Entwicklungsmodus installieren:
   ```bash
   pip install -e .
   ```

### Mit Dokumentationsabhängigkeiten

Wenn Sie planen, die Dokumentation lokal zu erstellen:

```bash
pip install d-back[docs]
```

Oder aus dem Quellcode:

```bash
pip install -e .[docs]
```

## Installation überprüfen

Nach der Installation überprüfen Sie, ob d-back korrekt installiert ist:

```bash
d_back --version
```

Sie sollten eine Ausgabe ähnlich wie diese sehen:

```
d-back version 0.0.14
```

!!! tip "Fehlerbehebung"
    Wenn der Befehl `d_back` nicht gefunden wird, stellen Sie sicher, dass Ihr Python-Skriptverzeichnis in Ihrem PATH ist. Alternativ können Sie d-back als Python-Modul ausführen: `python -m d_back --version`

## Schnellstart

Jetzt, da d-back installiert ist, lassen Sie es uns starten!

### Befehlszeilen-Ansatz

Der einfachste Weg, den Server zu starten, ist mit Standardeinstellungen:

```bash
# Start with defaults (localhost:3000)
d_back
```

Oder führen Sie es als Python-Modul aus:

```bash
python -m d_back
```

Sie sollten eine Konsolenausgabe ähnlich wie diese sehen:

```
WebSocket server started on ws://localhost:3000
Serving static files from: /path/to/d_back/dist
Press Ctrl+C to stop the server
```

!!! note "Standardeinstellungen"
    Standardmäßig läuft d-back auf `localhost:3000` und liefert das integrierte d-zone-Frontend aus statischen Dateien.

### Programmatischer Ansatz

Für mehr Kontrolle können Sie d-back in Ihrem Python-Code verwenden:

```python
import asyncio
from d_back.server import WebSocketServer

async def main():
    # Create server instance
    server = WebSocketServer(port=3000, host="localhost")
    
    # Optional: Set up custom callbacks
    # server.on_get_user_data(my_user_data_callback)
    # server.on_get_server_data(my_server_data_callback)
    
    # Start the server
    print("Starting d-back server...")
    await server.start()

# Run the server
asyncio.run(main())
```

Jeder Schritt erklärt:
1. **Module importieren**: Importieren Sie asyncio für asynchrone Ausführung und die WebSocketServer-Klasse
2. **Server erstellen**: Instanziieren Sie WebSocketServer mit gewünschtem Port und Host
3. **Callbacks konfigurieren** (optional): Passen Sie Datenquellen mit Callback-Funktionen an
4. **Server starten**: Rufen Sie `await server.start()` auf, um Verbindungen zu akzeptieren

## Ihre erste WebSocket-Verbindung

Sobald der Server läuft, können Sie die WebSocket-Verbindung von einem Client aus testen.

### Mit JavaScript/Browser

Öffnen Sie Ihre Browser-Konsole und führen Sie aus:

```javascript
// Connect to d-back
const socket = new WebSocket('ws://localhost:3000');

socket.onopen = () => {
    console.log('Connected to d-back!');
    // Request user data for a mock server
    socket.send(JSON.stringify({
        type: 'get_user_data',
        serverId: '232769614004748288'
    }));
};

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};
```

**Nachrichtenformat**: Die `get_user_data`-Anfrage umfasst:
- `type`: Nachrichtentyp (`"get_user_data"`)
- `serverId`: Discord-Server-ID (Snowflake-Format)

**Erwartete Antwort**: Sie erhalten ein JSON-Objekt mit Benutzerdaten:
```json
{
  "type": "user_data",
  "serverId": "232769614004748288",
  "users": {
    "user123": {
      "uid": "user123",
      "username": "ExampleUser",
      "status": "online",
      "roleColor": "#ff6b6b"
    }
  }
}
```

### Mit der Python-websockets-Bibliothek

Sie können sich auch mit der Python-`websockets`-Bibliothek verbinden:

```python
import asyncio
import json
import websockets

async def test_connection():
    uri = "ws://localhost:3000"
    async with websockets.connect(uri) as websocket:
        print("Connected to d-back!")
        
        # Request user data
        request = {
            "type": "get_user_data",
            "serverId": "232769614004748288"
        }
        await websocket.send(json.dumps(request))
        
        # Receive response
        response = await websocket.recv()
        data = json.loads(response)
        print("Received:", data)

asyncio.run(test_connection())
```

### Erwartetes Verhalten

Wenn Sie sich erfolgreich verbinden, sollten Sie sehen:
1. **Verbindung hergestellt**: WebSocket öffnet sich erfolgreich
2. **Serverliste empfangen**: Anfangsnachricht mit verfügbaren Discord-Servern
3. **Benutzerdaten zurückgegeben**: Antwort mit Mock-Benutzerpräsenz und Rolleninformationen

## Mock-Daten verstehen

d-back kommt mit vorkonfigurierten Mock-Discord-Servern für Entwicklung und Tests. Das bedeutet, Sie können sofort mit dem Erstellen und Testen beginnen, ohne Discord-API-Anmeldeinformationen einzurichten!

Die verfügbaren Mock-Server sind:

- **d-world-Server** (`232769614004748288`): Haupt-Entwicklungsserver mit 4 aktiven Benutzern in verschiedenen Stati
- **docs-Server** (`482241773318701056`): Dokumentationsserver mit 1 Benutzer
- **oauth2-Server** (`123456789012345678`): Geschützter Server zum Testen von OAuth2-Authentifizierungsabläufen mit 1 Benutzer
- **my repos-Server** (`987654321098765432`): Repository-Showcase-Server mit 21 Benutzern

!!! tip "Perfekt für Entwicklung"
    Mock-Daten sind ideal für:
    
    - Frontend-Entwicklung ohne Backend-Abhängigkeiten
    - Testen der d-zone-Visualisierung mit realistischen Daten
    - Demonstrieren des Systems ohne Discord-API-Schlüssel
    - CI/CD-Pipelines und automatisierte Tests

Um echte Discord-Daten in der Produktion zu verwenden, müssen Sie benutzerdefinierte Datenanbieter implementieren. Siehe die Anleitung [Benutzerdefinierte Datenanbieter](user-guide/custom-data-providers.md) für Details.

## Nächste Schritte

Herzlichen Glückwunsch! Sie haben jetzt d-back in Betrieb. Hier ist, was Sie als Nächstes erkunden sollten:

- **[Benutzerhandbuch](user-guide/index.md)**: Erfahren Sie mehr über Konfigurationsoptionen, Callbacks und Anpassung
- **[Konfiguration](user-guide/configuration.md)**: Passen Sie Servereinstellungen, Ports und statische Dateiauslieferung an
- **[Callbacks & Anpassung](user-guide/callbacks.md)**: Ersetzen Sie Mock-Daten durch Ihre eigenen Datenquellen
- **[Benutzerdefinierte Datenanbieter](user-guide/custom-data-providers.md)**: Integrieren Sie Discord-API oder Datenbanken
- **[API-Referenz](api-reference.md)**: Detaillierte Dokumentation aller Klassen und Methoden
- **[Entwicklerhandbuch](developer-guide.md)**: Beitragsrichtlinien und Architekturübersicht

!!! question "Hilfe benötigt?"
    Wenn Sie auf Probleme stoßen, überprüfen Sie die [GitHub Issues](https://github.com/NNTin/d-back/issues) oder starten Sie eine [Diskussion](https://github.com/NNTin/d-back/discussions).
