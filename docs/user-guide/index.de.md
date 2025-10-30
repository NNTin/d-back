# Benutzerhandbuch

Willkommen zum d-back-Benutzerhandbuch! Dieser umfassende Leitfaden deckt alles ab, was Sie benötigen, um d-back effektiv als WebSocket-Server für Ihre d-zone Ambient-Life-Simulation oder andere Echtzeitanwendungen zu nutzen.

## Einführung

Dieses Handbuch ist für Benutzer konzipiert, die bereits das Tutorial [Erste Schritte](../getting-started.md) abgeschlossen haben und tiefer in die Funktionen und Möglichkeiten von d-back eintauchen möchten. Egal, ob Sie das Serververhalten anpassen, echte Discord-Daten integrieren oder Ihre Einrichtung optimieren möchten, Sie finden hier die benötigten Informationen.

Das Benutzerhandbuch ist in drei Hauptbereiche unterteilt:

- **Konfiguration**: Erfahren Sie, wie Sie d-back über Befehlszeilenoptionen, Umgebungsvariablen und programmatische Einstellungen konfigurieren
- **Callbacks & Anpassung**: Entdecken Sie, wie Sie das Serververhalten mit Callback-Funktionen für Datenabruf, Authentifizierung und mehr anpassen
- **Benutzerdefinierte Datenanbieter**: Ersetzen Sie Mock-Daten durch echte Discord-API-Integration oder Ihre eigenen benutzerdefinierten Datenquellen

## Handbuch-Struktur

<div class="grid cards" markdown>

-   :material-cog:{ .lg .middle } **Konfiguration**

    ---

    Erfahren Sie mehr über Befehlszeilenoptionen, Umgebungsvariablen und Servereinstellungen

    [:octicons-arrow-right-24: Konfigurationsleitfaden](configuration.md)

-   :material-code-braces:{ .lg .middle } **Callbacks & Anpassung**

    ---

    Passen Sie das Serververhalten mit Callback-Funktionen für Datenabruf und Authentifizierung an

    [:octicons-arrow-right-24: Callbacks-Leitfaden](callbacks.md)

-   :material-database:{ .lg .middle } **Benutzerdefinierte Datenanbieter**

    ---

    Ersetzen Sie Mock-Daten durch echte Discord-API-Integration oder benutzerdefinierte Datenquellen

    [:octicons-arrow-right-24: Datenanbieter-Leitfaden](custom-data-providers.md)

</div>

## Häufige Anwendungsfälle

Müssen Sie eine bestimmte Aufgabe erfüllen? Hier sind Schnelllinks zu häufigen Szenarien:

| Szenario | Wo suchen |
|----------|---------------|
| Ich möchte den Serverport ändern | [Konfiguration → Befehlszeilenoptionen](configuration.md#command-line-options) |
| Ich möchte meine eigenen statischen Dateien ausliefern | [Konfiguration → Statische Dateiauslieferung](configuration.md#static-file-serving) |
| Ich möchte echte Discord-Daten verwenden | [Benutzerdefinierte Datenanbieter](custom-data-providers.md) |
| Ich möchte OAuth2-Authentifizierung hinzufügen | [Callbacks → OAuth2-Validierung](callbacks.md#on_validate_discord_user-callback) |
| Ich möchte benutzerdefinierte Nachrichten broadcasten | [Callbacks → Broadcasting-Methoden](callbacks.md#broadcasting-methods) |
| Ich möchte das Benutzerdatenformat anpassen | [Callbacks → Benutzerdaten-Callback](callbacks.md#on_get_user_data-callback) |

## Schnellreferenz

Hier ist eine Zusammenfassung der Schlüsselkonzepte, denen Sie in diesem Handbuch begegnen werden:

| Konzept | Beschreibung |
|---------|-------------|
| **WebSocketServer** | Haupt-Serverklasse, die WebSocket-Verbindungen, HTTP-Anfragen und Nachrichten-Broadcasting verwaltet |
| **MockDataProvider** | Integrierter Testdatengenerator, der Discord-Benutzeraktivität simuliert |
| **Callbacks** | Anpassungs-Hooks, die es ermöglichen, Standardverhalten zu überschreiben (z.B. `on_get_user_data`, `on_get_server_data`) |
| **Statische Dateiauslieferung** | Integrierter HTTP-Server für die Bereitstellung von Frontend-Assets wie HTML, CSS und JavaScript |
| **Broadcasting** | Methoden zum Senden von Echtzeit-Updates an verbundene Clients (Präsenz, Nachrichten, etc.) |
| **OAuth2-Integration** | Unterstützung für Discord-OAuth2-Authentifizierung und Token-Validierung |

!!! tip "API-Details benötigt?"
    Für detaillierte API-Dokumentation einschließlich Methodensignaturen, Parametern und Rückgabetypen siehe die [API-Referenz](../api-reference.md).

## Was kommt als Nächstes?

Bereit, Ihre d-back-Einrichtung anzupassen? Beginnen Sie mit:

1. **[Konfiguration](configuration.md)** - Richten Sie Ihren Server mit den richtigen Einstellungen ein
2. **[Callbacks & Anpassung](callbacks.md)** - Erfahren Sie, wie Sie Verhalten anpassen
3. **[Benutzerdefinierte Datenanbieter](custom-data-providers.md)** - Integrieren Sie echte Datenquellen

!!! question "Fragen?"
    Wenn Sie nicht finden, wonach Sie suchen, überprüfen Sie die [API-Referenz](../api-reference.md) oder besuchen Sie unsere [GitHub Discussions](https://github.com/NNTin/d-back/discussions).
