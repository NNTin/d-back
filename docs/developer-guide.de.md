# Entwicklerhandbuch

Willkommen zum d-back-Entwicklerhandbuch! Dieser Leitfaden bietet alle Informationen, die Sie benötigen, um zum Projekt beizutragen, seine Architektur zu verstehen und Best Practices für die Entwicklung zu befolgen.

## Einführung

d-back ist ein Open-Source-WebSocket-Server für Discord-Integration mit d-zone Ambient-Life-Simulation. Wir begrüßen Beiträge aus der Community, und dieser Leitfaden hilft Ihnen beim Einstieg.

## Erste Schritte mit der Entwicklung

### Entwicklungsumgebung einrichten

1. **Repository forken und klonen**:
   ```bash
   git clone https://github.com/IHR_BENUTZERNAME/d-back.git
   cd d-back
   ```

2. **Virtuelle Umgebung erstellen**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Auf Windows: .venv\Scripts\activate
   ```

3. **Entwicklungsabhängigkeiten installieren**:
   ```bash
   pip install -e .[docs]
   pip install pytest pytest-asyncio websockets
   ```

4. **Installation überprüfen**:
   ```bash
   python -m d_back --version
   ```

## Projektarchitektur

### Verzeichnisstruktur

```
d-back/
├── d_back/               # Hauptquellcode
│   ├── __init__.py       # Paketmetadaten
│   ├── __main__.py       # CLI-Einstiegspunkt
│   ├── server.py         # Haupt-WebSocketServer-Klasse
│   └── mock/
│       ├── __init__.py
│       └── data.py       # MockDataProvider
├── docs/                 # MkDocs-Dokumentation
│   ├── index.md
│   ├── getting-started.md
│   ├── user-guide/
│   └── api-reference.md
├── tests/                # pytest-Tests
│   ├── test_dis_connect.py
│   └── helpers/
│       └── mock_websocket_client.py
├── pyproject.toml        # Projektmetadaten
├── setup.cfg             # setuptools-Konfiguration
├── mkdocs.yml            # MkDocs-Konfiguration
└── README.md
```

### Kernkomponenten

**WebSocketServer** (`d_back/server.py`):
- Verwaltet WebSocket-Verbindungen und HTTP-Anfragen
- Verwaltet anpassbare Callbacks für Datenabruf
- Stellt Broadcasting-Methoden für Echtzeit-Updates bereit
- Unterstützt statische Dateiauslieferung

**MockDataProvider** (`d_back/mock/data.py`):
- Generiert realistische simulierte Benutzer- und Serverdaten
- Führt periodische Hintergrundaufgaben aus (Präsenzänderungen, Nachrichten)
- Stellt 4 vorkonfigurierte Server mit verschiedenen Daten bereit
- Wird automatisch verwendet, wenn keine benutzerdefinierten Callbacks registriert sind

**CLI-Modul** (`d_back/__main__.py`):
- Befehlszeilenargument-Parsing
- Einstiegspunkt zum Ausführen des Servers
- Signal-Handling für ordnungsgemäßes Herunterfahren

## Testen

### Teststruktur

Tests sind im `tests/`-Verzeichnis organisiert:

- `test_dis_connect.py`: WebSocket-Konnektivitäts- und Nachrichtenfluss-Tests
- `helpers/mock_websocket_client.py`: Mock-WebSocket-Client für Tests

### Tests ausführen

Alle Tests ausführen:
```bash
pytest
```

Spezifische Tests ausführen:
```bash
pytest tests/test_dis_connect.py
```

Mit ausführlicher Ausgabe:
```bash
pytest -v
```

Mit Abdeckung:
```bash
pytest --cov=d_back
```

### Tests schreiben

Tests verwenden `pytest` und `pytest-asyncio` für asynchrone Funktionalität:

```python
import pytest
from d_back.server import WebSocketServer

@pytest.mark.asyncio
async def test_server_startup():
    """Test server starts and stops correctly."""
    server = WebSocketServer(port=3001, host="localhost")
    await server.start()
    
    # Test server is running
    assert server.websocket is not None
    
    # Clean shutdown
    await server.stop()
```

## Beitragsrichtlinien

### Git-Workflow

1. **Feature-Branch erstellen**:
   ```bash
   git checkout -b feature/meine-neue-funktion
   ```

2. **Änderungen vornehmen und committen**:
   ```bash
   git add .
   git commit -m "Add: Meine neue Funktion"
   ```

3. **Zu Ihrem Fork pushen**:
   ```bash
   git push origin feature/meine-neue-funktion
   ```

4. **Pull Request erstellen** auf GitHub

### Commit-Nachrichtenformat

Verwenden Sie klare und beschreibende Commit-Nachrichten:

- `Add: Neue Funktion oder Funktionalität`
- `Fix: Fehlerbehebung`
- `Update: Aktualisierung bestehender Funktionalität`
- `Docs: Dokumentationsänderungen`
- `Test: Tests hinzufügen oder aktualisieren`
- `Refactor: Code-Refactoring`

Beispiele:
```
Add: OAuth2 validation callback support
Fix: WebSocket connection timeout issue
Update: Improve mock data generator performance
Docs: Add custom data providers guide
```

### Code-Stil

- Folgen Sie [PEP 8](https://pep8.org/) für Python-Code-Stil
- Verwenden Sie Type Hints für Funktionsparameter und Rückgabewerte
- Schreiben Sie Google-Style-Docstrings für alle öffentlichen Funktionen
- Halten Sie Zeilen nach Möglichkeit unter 100 Zeichen

Beispiel-Docstring:
```python
async def on_get_user_data(self, server_id: str) -> Dict[str, Any]:
    """Retrieve user data for a Discord server.
    
    Args:
        server_id: Discord server ID (snowflake format)
    
    Returns:
        Dictionary mapping user IDs to user data objects
    
    Example:
        ```python
        users = await server.on_get_user_data("232769614004748288")
        ```
    """
    pass
```

## Entwicklungsworkflow

### Lokaler Entwicklungszyklus

1. **Code-Änderungen vornehmen**
2. **Tests ausführen**: `pytest`
3. **Dokumentation aktualisieren** bei Bedarf
4. **Lokal testen**: `python -m d_back`
5. **Änderungen committen und pushen**

### Dokumentation lokal erstellen

```bash
# Install docs dependencies
pip install -e .[docs]

# Serve docs with live reload
mkdocs serve

# Build docs
mkdocs build
```

Zugriff auf Docs unter `http://127.0.0.1:8000/`

## Fehlersuche

### Debug-Protokollierung

Fügen Sie Print-Anweisungen hinzu oder verwenden Sie Logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Starting WebSocket server...")
```

### WebSocket-Verbindungen debuggen

Verwenden Sie die Browser-Konsole oder WebSocket-Tools:

```javascript
const ws = new WebSocket('ws://localhost:3000');
ws.onopen = () => console.log('Connected');
ws.onmessage = (event) => console.log('Received:', event.data);
ws.onerror = (error) => console.error('Error:', error);
```

## Release-Prozess

Releases werden von Projekt-Maintainern verwaltet:

1. Versionsnummer in `setup.cfg` aktualisieren
2. CHANGELOG aktualisieren (falls vorhanden)
3. Git-Tag erstellen: `git tag v0.0.X`
4. Tag pushen: `git push origin v0.0.X`
5. GitHub Actions baut automatisch und veröffentlicht auf PyPI

## Zukünftige Verbesserungen

Bereiche, in denen wir Beiträge begrüßen:

- **Redis-Unterstützung**: Verteiltes Caching und Pub/Sub
- **Metriken und Monitoring**: Prometheus/Grafana-Integration
- **Verbesserte Authentifizierung**: Mehr OAuth2-Anbieter
- **Session-Management**: Session-Persistenz und -Erneuerung
- **Last-Tests**: Performance-Tests und Benchmarking
- **Internationalisierung**: Mehrsprachige Fehlermeldungen

## Hilfe erhalten

Benötigen Sie Hilfe bei der Entwicklung?

- **GitHub Issues**: Bugs melden oder Features anfragen
- **GitHub Discussions**: Fragen stellen oder Ideen diskutieren
- **Dokumentation**: [Benutzerhandbuch](../user-guide/index.md) und [API-Referenz](../api-reference.md) überprüfen
- **Quellcode**: Code auf [GitHub](https://github.com/NNTin/d-back) lesen

## Lizenz

d-back ist unter der MIT-Lizenz lizenziert. Siehe die LICENSE-Datei für Details.

## Was kommt als Nächstes?

- **[Benutzerhandbuch](../user-guide/index.md)**: Erfahren Sie, wie Sie d-back verwenden
- **[API-Referenz](../api-reference.md)**: Detaillierte API-Dokumentation
- **[Erste Schritte](../getting-started.md)**: Installieren und Ausführen von d-back
