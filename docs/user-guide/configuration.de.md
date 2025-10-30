# Konfiguration

Dieser Leitfaden behandelt alle Möglichkeiten, wie Sie d-back an Ihre Bedürfnisse anpassen können, von Befehlszeilenoptionen bis hin zu programmatischen Einstellungen und Umgebungsvariablen.

## Einführung

d-back bietet flexible Konfigurationsoptionen zur Anpassung an verschiedene Bereitstellungsszenarien. Egal, ob Sie es während der Entwicklung über die Befehlszeile ausführen oder in eine größere Python-Anwendung integrieren, Sie haben volle Kontrolle über Serververhalten, Netzwerkeinstellungen und statische Dateiauslieferung.

## Befehlszeilenoptionen

Beim Ausführen von d-back über die Befehlszeile können Sie sein Verhalten mit verschiedenen Optionen anpassen:

### Verfügbare Optionen

| Option | Standard | Beschreibung | Beispiel |
|--------|---------|-------------|---------|
| `--port` | `3000` | Port, auf dem der WebSocket-Server ausgeführt werden soll | `d_back --port 8080` |
| `--host` | `localhost` | Host, an den der Server gebunden werden soll | `d_back --host 0.0.0.0` |
| `--static-dir` | Integriert | Verzeichnis, von dem statische Dateien ausgeliefert werden | `d_back --static-dir ./my-frontend-build` |
| `--version` | - | Versionsinformationen anzeigen | `d_back --version` |

### Verwendungsbeispiele

**Standardstart** (localhost:3000):
```bash
d_back
```

**Benutzerdefinierter Host und Port**:
```bash
d_back --host 0.0.0.0 --port 8080
```

Dies macht den Server von anderen Maschinen in Ihrem Netzwerk aus zugänglich.

**Benutzerdefiniertes statisches Verzeichnis**:
```bash
d_back --static-dir ./my-frontend-build
```

Liefern Sie Ihre eigenen Frontend-Dateien anstelle der integrierten d-zone-Oberfläche aus.

**Hilfe erhalten**:
```bash
d_back --help
```

Alle verfügbaren Befehlszeilenoptionen anzeigen.

**Version prüfen**:
```bash
d_back --version
```

!!! note "Als Modul ausführen"
    Sie können d-back auch als Python-Modul mit denselben Optionen ausführen:
    ```bash
    python -m d_back --host 0.0.0.0 --port 8080
    ```

## Programmatische Konfiguration

Für mehr Kontrolle und Integration in Ihre Python-Anwendungen können Sie d-back programmatisch konfigurieren:

```python
import asyncio
from d_back.server import WebSocketServer

async def main():
    # Create server instance with custom settings
    server = WebSocketServer(port=3000, host="localhost")
    
    # Configure callbacks (optional)
    server.on_get_user_data(my_user_data_callback)
    server.on_get_server_data(my_server_data_callback)
    
    # Start the server
    print("Starting d-back server...")
    await server.start()

asyncio.run(main())
```

### Konstruktorparameter

Die `WebSocketServer`-Klasse akzeptiert die folgenden Parameter:

- **`port`** (int, optional): Die Portnummer, auf der gelauscht werden soll. Standard ist `3000`.
- **`host`** (str, optional): Der Hostname oder die IP-Adresse, an die gebunden werden soll. Standard ist `"localhost"`.

### Wann programmatische Konfiguration verwenden

Verwenden Sie programmatische Konfiguration, wenn Sie:

- d-back in eine größere Python-Anwendung integrieren müssen
- Einstellungen basierend auf Laufzeitbedingungen dynamisch konfigurieren möchten
- Auf Server-Instanzmethoden und -Attribute zugreifen müssen
- Benutzerdefinierte Start-/Stopp-Logik implementieren möchten

## Umgebungsvariablen

Obwohl d-back standardmäßig keine Umgebungsvariablen verwendet, können Sie es leicht erweitern, um umgebungsbasierte Konfiguration zu unterstützen:

```python
import os
from d_back.server import WebSocketServer

# Example: Use environment variables
port = int(os.getenv('D_BACK_PORT', 3000))
host = os.getenv('D_BACK_HOST', 'localhost')

server = WebSocketServer(port=port, host=host)
```

## Statische Dateiauslieferung

d-back enthält einen integrierten HTTP-Server für die Auslieferung statischer Dateien, was die Bereitstellung Ihres d-zone-Frontends oder anderer Web-Assets vereinfacht.

### Standardverhalten

Standardmäßig liefert d-back statische Dateien aus seinem integrierten `dist/`-Verzeichnis aus, das das d-zone-Frontend enthält.

### Benutzerdefiniertes statisches Verzeichnis

Um Ihre eigenen statischen Dateien auszuliefern:

**Befehlszeile**:
```bash
d_back --static-dir ./my-frontend-build
```

**Programmatisch**:
```python
from pathlib import Path
server = WebSocketServer(port=3000, host="localhost")
server.static_dir = Path("./my-frontend-build")
```

## Mock-Server-Konfiguration

d-back kommt mit vorkonfigurierten Mock-Discord-Servern für Entwicklung und Tests. Diese Server bieten realistische Benutzerdaten ohne Discord-API-Anmeldeinformationen zu benötigen.

### Verfügbare Mock-Server

| Servername | Server-ID | Beschreibung | Benutzeranzahl |
|-------------|-----------|-------------|------------|
| **d-world-Server** | `232769614004748288` | Haupt-Entwicklungsserver mit vielfältiger Benutzeraktivität | 4 Benutzer |
| **docs-Server** | `482241773318701056` | Dokumentationsserver mit moderater Aktivität | 1 Benutzer |
| **oauth2-Server** | `123456789012345678` | Geschützter Server zum Testen von OAuth2-Flows | 1 Benutzer |
| **my repos-Server** | `987654321098765432` | Repository-Showcase-Server | 21 Benutzer |

## Server-Lebenszyklus

### Server starten

**Methode 1: `start()`**
```python
await server.start()
```
Startet den WebSocket-Server und HTTP-Listener.

**Methode 2: `run_forever()`**
```python
await server.run_forever()
```
Startet den Server und führt ihn unbegrenzt aus, bis er unterbrochen wird.

### Server stoppen

**Ordnungsgemäßes Herunterfahren:**
```python
await server.stop()
```
Schließt alle aktiven Verbindungen und stoppt den Server sauber.

## Best Practices

### Netzwerkkonfiguration

!!! tip "Entwicklung vs Produktion"
    - **Entwicklung**: Verwenden Sie `localhost`, um den Zugriff nur auf Ihren Rechner zu beschränken
    - **Produktion**: Verwenden Sie `0.0.0.0`, um Verbindungen von jeder Netzwerkschnittstelle zu akzeptieren

### Konfigurationsverwaltung

- **Verwenden Sie Umgebungsvariablen** für bereitstellungsspezifische Einstellungen
- **Verwenden Sie programmatische Konfiguration** für komplexe oder dynamische Setups
- **Dokumentieren Sie Ihre Konfiguration** in README oder Bereitstellungsleitfäden
- **Halten Sie Geheimnisse sicher**: Niemals API-Schlüssel oder Tokens fest codieren

## Was kommt als Nächstes?

Jetzt, da Sie verstehen, wie Sie d-back konfigurieren, lernen Sie, wie Sie sein Verhalten anpassen:

- **[Callbacks & Anpassung](callbacks.md)**: Standardverhalten mit benutzerdefinierten Callbacks überschreiben
- **[Benutzerdefinierte Datenanbieter](custom-data-providers.md)**: Mock-Daten durch echte Quellen ersetzen
- **[API-Referenz](../api-reference.md)**: Detaillierte API-Dokumentation
