# API-Referenz

Diese Seite bietet vollständige API-Dokumentation für d-back, automatisch aus den Docstrings des Quellcodes generiert. Alle Klassen und Methoden enthalten detaillierte Beschreibungen, Parameter, Rückgabewerte und Beispiele.

## Einführung

Die d-back-API ist in zwei Hauptkomponenten organisiert:

- **WebSocketServer**: Die Haupt-Serverklasse zur Verwaltung von WebSocket-Verbindungen, HTTP-Anfragen und Nachrichten-Broadcasting
- **MockDataProvider**: Stellt Mock-Daten und periodische Hintergrundaufgaben für Entwicklung und Tests bereit

Alle API-Dokumentation folgt Google-Style-Docstrings mit umfassenden Beispielen. Für Nutzungsmuster und Integrationsleitfäden siehe das [Benutzerhandbuch](user-guide/index.md).

## WebSocketServer

Die Haupt-Serverklasse zur Verwaltung von WebSocket-Verbindungen, HTTP-Anfragen und Nachrichten-Broadcasting. Dies ist Ihre primäre Schnittstelle zur d-back-Funktionalität.

::: d_back.server.WebSocketServer
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      heading_level: 3

## MockDataProvider

Stellt Mock-Daten und periodische Hintergrundaufgaben für Entwicklung und Tests bereit. Diese Klasse wird automatisch verwendet, wenn keine benutzerdefinierten Callbacks registriert sind.

::: d_back.mock.data.MockDataProvider
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      heading_level: 3

## Hilfsfunktionen

Hilfsfunktionen für Befehlszeilenschnittstelle und Versionsverwaltung.

### parse_args

::: d_back.server.parse_args
    options:
      show_root_heading: false
      heading_level: 4

### get_version

::: d_back.server.get_version
    options:
      show_root_heading: false
      heading_level: 4

### main

::: d_back.server.main
    options:
      show_root_heading: false
      heading_level: 4

### main_sync

::: d_back.server.main_sync
    options:
      show_root_heading: false
      heading_level: 4

## Verwendungsbeispiele

Für praktische Beispiele zur Verwendung dieser APIs siehe:

- **[Erste Schritte](getting-started.md)**: Grundlegende Verwendung und erste Verbindung
- **[Konfiguration](user-guide/configuration.md)**: Server-Einrichtung und -Konfiguration
- **[Callbacks & Anpassung](user-guide/callbacks.md)**: Callback-Verwendungsbeispiele
- **[Benutzerdefinierte Datenanbieter](user-guide/custom-data-providers.md)**: Datenanbieter-Implementierungsmuster

## Typhinweise

Alle Methoden enthalten umfassende Typhinweise für Parameter und Rückgabewerte. Beim Arbeiten mit Callbacks importieren Sie die erforderlichen Typen:

```python
from typing import Dict, Any, Optional, Tuple, Callable, Awaitable
```

Für weitere Informationen über Python-Typhinweise siehe die [offizielle typing-Dokumentation](https://docs.python.org/3/library/typing.html).
