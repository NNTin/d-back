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

## Dokumentationsübersetzung

### Übersicht

Die d-back-Dokumentation ist in mehreren Sprachen verfügbar (English, Spanish, German). Wir verwenden Crowdin zur kollaborativen Verwaltung von Übersetzungen. Englisch ist die Quellsprache — Änderungen müssen zunächst in den englischen Dateien vorgenommen werden. Übersetzungen werden mittels Crowdin und GitHub Actions synchronisiert. Das Projekt verwendet `mkdocs-static-i18n` mit der Suffix-Struktur (z. B. `index.es.md`, `index.de.md`).

### Crowdin-Projekt-Einrichtung

1. Erstellen Sie ein Crowdin-Projekt unter https://crowdin.com und wählen Sie **Markdown** als Dateityp.
2. Legen Sie English als Quellsprache fest und fügen Sie Spanish (`es`) und German (`de`) als Zielsprachen hinzu.
3. Installieren Sie die Crowdin GitHub App im Repository oder konfigurieren Sie Crowdin CLI mit GitHub Actions. Die `crowdin.yml` in der Repository-Root definiert die Dateimuster und Parser-Optionen.

Benötigte GitHub-Secrets (Repository → Settings → Secrets and variables → Actions):

- `CROWDIN_PROJECT_ID` — Crowdin-Projekt-ID
- `CROWDIN_PERSONAL_TOKEN` — Crowdin-Personal-Access-Token

### Übersetzungs-Workflow

1. Änderungen an den englischen Quelldateien (z. B. `docs/index.md`, `docs/getting-started.md`) vornehmen und einen Pull Request eröffnen.
2. Nach dem Merge in `main` erkennt Crowdin neue/geänderte Strings und benachrichtigt Übersetzer.
3. Übersetzer arbeiten im Crowdin-Editor; Crowdin bewahrt Codeblöcke, Inline-Code und Markdown-Formatierung.
4. Übersetzungen werden via Crowdin ↔ GitHub oder GitHub Actions zurück in das Repository synchronisiert. Crowdin erzeugt PRs mit Übersetzungs-Updates, die Maintainer prüfen und mergen.

### Dateistruktur

- Englisch (Quelle): `docs/index.md`, `docs/getting-started.md`, `docs/user-guide/configuration.md`
- Spanish: `docs/index.es.md`, `docs/getting-started.es.md`, `docs/user-guide/configuration.es.md`
- German: `docs/index.de.md`, `docs/getting-started.de.md`, `docs/user-guide/configuration.de.md`

### Was wird übersetzt

Zu übersetzen sind:

- Erläuternder Text, Überschriften und Titel
- Anwendernahe Meldungen und Anleitungen
- Beschreibungen von Beispielen (nicht die Codeblöcke)

Nicht zu übersetzen sind:

- Codeblöcke und Inline-Code
- Funktions- und Klassennamen
- Dateipfade und URLs
- Konfigurationsschlüssel und -werte
- Projekt- und Fachbegriffe (z. B. d-back, d-zone, WebSocket, OAuth2)

### Ausgeschlossene Dateien

Die folgenden Dateien sind von Crowdin-Übersetzungen ausgeschlossen:

- `docs/VERCEL_SETUP.md`
- `docs/TESTING_I18N.md`
- `docs/.pages`
- API-Referenzdateien (durch mkdocstrings generiert)

### Übersetzungen lokal testen

```bash
# Install documentation dependencies
pip install -e .[docs]

# Serve documentation locally with all languages
mkdocs serve

# Build documentation (generates site/ directory with all languages)
mkdocs build
```

Sprachspezifische Vorschau:

- English: `http://127.0.0.1:8000/`
- Spanish: `http://127.0.0.1:8000/es/`
- German: `http://127.0.0.1:8000/de/`

### Best Practices für Übersetzungen

- Verwenden Sie formale Anrede (Sie) im Nutzertext.
- Lassen Sie Fachbegriffe und Projektnamen im Englischen.
- Bewahren Sie Markdown-Formatierung, Codeblöcke und Inline-Code.
- Testen Sie Übersetzungen lokal vor Einreichen.

### Neue Sprachen hinzufügen

So fügen Sie eine neue Sprache hinzu:

1. Aktualisieren Sie `mkdocs.yml`, um die neue Sprache in der i18n-Konfiguration hinzuzufügen.
2. Ergänzen Sie `crowdin.yml` um den neuen `two_letters_code`.
3. Fügen Sie die Sprache in den Crowdin-Projekteinstellungen hinzu.
4. Erstellen Sie initiale Übersetzungsdateien nach dem Suffix-Pattern.
5. Aktualisieren Sie diese Dokumentationssektion mit Details zur neuen Sprache.

### Fehlerbehebung

Häufige Probleme:

- Übersetzungen erscheinen nicht in Crowdin: Prüfen Sie, ob die Muster in `crowdin.yml` mit den committeten Dateien übereinstimmen und ob Dateien nicht in `ignore` gelistet sind.
- Übersetzungen werden nicht nach GitHub synchronisiert: Prüfen Sie die Logs von GitHub Actions und die gesetzten Secrets `CROWDIN_PROJECT_ID` und `CROWDIN_PERSONAL_TOKEN`.
- Formatierungsprobleme: Überprüfen Sie die Übersetzung im Crowdin-Editor und stellen Sie sicher, dass Codeblöcke erhalten bleiben.

### Ressourcen

- Crowdin documentation: https://support.crowdin.com/
- mkdocs-static-i18n: https://github.com/ultrabug/mkdocs-static-i18n
- Material for MkDocs i18n: https://squidfunk.github.io/mkdocs-material/setup/changing-the-language/


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

### Dokumentationsversionierung

d-back verwendet mike für die Dokumentationsversionierung, das sich nahtlos in Material for MkDocs integriert und einen Versionsauswähler in der Dokumentation bereitstellt. Die Versionierungsstrategie verwendet drei Arten von Versionen:

- **Stabile Versionen**: Erstellt aus Git-Tags (z. B. 0.0.14, 0.1.0, 1.0.0)
- **Prerelease 'latest'**: Verfolgt den main-Branch (produktionsbereit, aber noch nicht getaggt)
- **Prerelease 'dev'**: Verfolgt den develop-Branch (Entwicklung/Tests)

Der Versionsauswähler erscheint in der oberen Navigationsleiste und ermöglicht es Benutzern, zwischen verschiedenen Dokumentationsversionen zu wechseln.

#### Versionierungsstrategie

**1. Stabile Versionen (aus Tags)**

Erstellt, wenn eine neue Version getaggt wird:

- Die Versionsnummer entspricht dem Git-Tag ohne das 'v'-Präfix
- Diese Versionen sind permanent und unveränderlich
- Beispiel: Tag v0.0.15 erstellt Dokumentationsversion 0.0.15
- Befehl: `mike deploy 0.0.15 --push`

**2. Latest Prerelease (main-Branch)**

Repräsentiert den aktuellen Zustand des main-Branches:

- Alias: 'latest'
- Wird bei jedem Push auf main aktualisiert
- Dies ist die Standardversion, die Benutzer sehen
- Befehl: `mike deploy <commit-sha> latest --push --update-aliases`

**3. Dev Prerelease (develop-Branch)**

Repräsentiert den aktuellen Zustand des develop-Branches:

- Alias: 'dev'
- Wird bei jedem Push auf develop aktualisiert
- Wird zum Testen von Dokumentationsänderungen vor der Veröffentlichung verwendet
- Befehl: `mike deploy <commit-sha> dev --push --update-aliases`

#### Lokales Testen

Testen Sie mike lokal vor dem Deployment:

```bash
# Dokumentationsabhängigkeiten installieren (beinhaltet mike)
pip install -e .[docs]

# Testversion lokal deployen (kein Push zum Remote)
mike deploy 0.0.14-test

# Mit einem Alias deployen
mike deploy 0.0.15-test latest --update-aliases

# Standardversion festlegen (was Benutzer sehen, wenn sie die Docs besuchen)
mike set-default latest

# Alle deployten Versionen auflisten
mike list

# Versionierte Dokumentation lokal bereitstellen
mike serve
# Besuchen Sie http://localhost:8000 zum Testen
# Verwenden Sie den Versionsauswähler in der oberen Navigation zum Wechseln zwischen Versionen

# Testversion löschen
mike delete 0.0.14-test
```

**Wichtige Hinweise für lokales Testen:**

- Mike erstellt lokal einen `gh-pages`-Branch zur Speicherung der versionierten Dokumentation
- Verwenden Sie Testversionsnamen (z. B. 0.0.14-test), um Konflikte mit Produktionsversionen zu vermeiden
- Das `--push`-Flag wird beim lokalen Testen weggelassen, um versehentliches Deployment zu verhindern
- Testen Sie immer die Funktionalität des Versionsauswählers vor dem Deployment
- Überprüfen Sie, dass alle drei Sprachen (English, Spanish, German) in jeder Version korrekt funktionieren

#### Versions-Aliase

Aliase sind symbolische Namen, die auf bestimmte Versionen verweisen:

- Gängige Aliase: 'latest' (main-Branch), 'dev' (develop-Branch), 'stable' (letzte stabile Version)
- Aliase können aktualisiert werden, um auf verschiedene Versionen zu verweisen
- Beispiel: Nach der Veröffentlichung von 0.1.0, 'stable'-Alias aktualisieren: `mike deploy 0.1.0 stable --update-aliases`
- Das `--update-aliases`-Flag aktualisiert bestehende Aliase, anstatt Duplikate zu erstellen

#### Deployment-Workflow

Manueller Deployment-Prozess (für lokale Tests oder wenn benötigt):

**Für stabile Releases:**
```bash
# Nach Erstellung eines Git-Tags (z. B. v0.0.15)
mike deploy 0.0.15 stable --push --update-aliases
mike set-default stable --push
```

**Für main-Branch-Updates:**
```bash
# Nach Merge zu main
mike deploy <commit-sha> latest --push --update-aliases
```

**Für develop-Branch-Updates:**
```bash
# Nach Merge zu develop
mike deploy <commit-sha> dev --push --update-aliases
```

**Hinweis:** Diese Befehle sind für manuelles Deployment. Automatisiertes Deployment über GitHub Actions ist der empfohlene Ansatz für Produktion (siehe "Automatisiertes Deployment mit GitHub Actions" unten).

#### Automatisiertes Deployment mit GitHub Actions

Das Deployment der Dokumentation ist über GitHub Actions automatisiert. Der Workflow ist in `.github/workflows/docs.yml` definiert und verwaltet alle Produktions-Deployments.

**Übersicht:**

- Dokumentation wird automatisch bei Pushes zu main, develop und Tag-Erstellung deployed
- Der Workflow verwaltet die Versionierung mit mike und deployed zu GitHub Pages
- Manuelles Deployment mit mike lokal ist weiterhin für Tests verfügbar
- Alle drei Sprachen (Englisch, Spanisch, Deutsch) werden zusammen gebaut und deployed

**Automatische Auslöser:**

1. **Tag-Erstellung (v*)**: Erstellt eine stabile Version
   - Beispiel: Tag `v0.0.15` deployed Version `0.0.15` mit Alias `stable`
   - Stabile Versionen sind permanent und unveränderlich
   - Wird als Standardversion festgelegt, die Benutzer sehen
   - Ausgeführter Befehl: `mike deploy 0.0.15 stable --push --update-aliases`
   - Ausgeführter Befehl: `mike set-default stable --push`

2. **Push zu main**: Deployed 'latest' Prerelease
   - Repräsentiert den aktuellen produktionsbereiten Zustand
   - Wird nicht als Standard festgelegt (stabile Releases bleiben die Standardversion)
   - Verwendet die stabile Versionskennung 'edge'
   - Ausgeführter Befehl: `mike deploy edge latest --push --update-aliases`

3. **Push zu develop**: Deployed 'dev' Prerelease
   - Repräsentiert den aktuellen Entwicklungszustand
   - Wird zum Testen von Dokumentationsänderungen vor der Veröffentlichung verwendet
   - Wird nicht als Standard festgelegt (dev ist nur zum Testen)
   - Verwendet die stabile Versionskennung 'dev'
   - Ausgeführter Befehl: `mike deploy dev dev --push --update-aliases`

4. **Manuelle Auslösung**: Verfügbar über `workflow_dispatch` in der GitHub Actions UI
   - Nützlich zum Testen oder erneuten Deployment von Dokumentation
   - Zugriff über: Repository → Actions tab → Documentation workflow → Run workflow

**Workflow-Prozess:**

1. **Checkout repository**: Holt die vollständige Git-Historie (erforderlich, damit mike auf den gh-pages-Branch zugreifen kann)
2. **Set up Python 3.11**: Installiert Python mit pip-Caching für schnellere Builds
3. **Install dependencies**: Führt `pip install -e .[docs]` aus, um mkdocs-material, mkdocs-static-i18n, mkdocstrings und mike aus setup.cfg zu installieren
4. **Configure git**: Richtet den Git-Benutzer für automatische Commits zum gh-pages-Branch ein
5. **Determine version**: Analysiert den Auslösertyp (tag, main oder develop), um die Deployment-Strategie zu bestimmen
6. **Deploy with mike**: Führt den entsprechenden mike-Befehl aus, um versionierte Dokumentation zum gh-pages-Branch zu deployen
7. **GitHub Pages stellt aktualisierte Dokumentation bereit**: Änderungen erscheinen innerhalb von 1-2 Minuten unter https://nntin.github.io/d-back/

**Versionsstrategie:**

- **Stabile Versionen** (von Tags): Permanent, unveränderlich, repräsentieren offizielle Releases; werden immer als Standard festgelegt
- **'latest' Alias**: Bei jedem Push zum main-Branch aktualisiert; im Versionsauswähler verfügbar, aber nicht als Standard festgelegt
- **'dev' Alias**: Bei jedem Push zum develop-Branch aktualisiert, nur zum Testen (wird nie als Standard festgelegt)
- Der Versionsauswähler in der Dokumentationsnavigation zeigt alle verfügbaren Versionen

**Deployments überwachen:**

- **Workflow-Ausführungen anzeigen**: Repository → Actions tab → Documentation workflow
- **Deployment-Status prüfen**: Siehe den Documentation Status Badge in README.md
- **Workflow-Logs**: Detaillierte Deployment-Informationen verfügbar in jeder Workflow-Ausführung
- **Fehlgeschlagene Deployments**: Fehlermeldungen erscheinen in Workflow-Logs mit Troubleshooting-Informationen

**GitHub Pages-Konfiguration:**

Erstmalige Einrichtung (nur einmal erforderlich):

1. Gehen Sie zu: Repository Settings → Pages
2. Setzen Sie Source: Deploy from a branch
3. Setzen Sie Branch: `gh-pages` (automatisch bei erster Workflow-Ausführung erstellt)
4. Klicken Sie auf Save
5. Dokumentation wird verfügbar sein unter: https://nntin.github.io/d-back/
6. Änderungen erscheinen innerhalb von 1-2 Minuten nach Abschluss des Workflows

**Manuelles Deployment (falls benötigt):**

Der automatisierte Workflow verwaltet die meisten Deployment-Szenarien. Manuelles Deployment kann erforderlich sein für:

- Testen von Dokumentationsänderungen lokal vor dem Pushen
- Beheben von Deployment-Problemen, die lokales Troubleshooting erfordern
- Deployment von einem lokalen Branch zu Testzwecken

Verwenden Sie die mike-Befehle, die im Unterabschnitt "Deployment-Workflow" oben dokumentiert sind, für manuelles Deployment.

**Workflow-Probleme beheben:**

**Problem:** Workflow schlägt bei git push zu gh-pages fehl
- **Lösung**: Überprüfen Sie, dass Actions Schreibberechtigungen haben
  - Gehen Sie zu: Settings → Actions → General → Workflow permissions
  - Wählen Sie: "Read and write permissions"
  - Klicken Sie auf Save

**Problem:** Deployed Version erscheint nicht im Versionsauswähler
- **Lösung**: Überprüfen Sie, dass die Auslöserbedingung mit dem erwarteten Branch oder Tag übereinstimmte
- **Lösung**: Prüfen Sie Workflow-Logs, um zu bestätigen, dass das Deployment erfolgreich abgeschlossen wurde
- **Lösung**: Stellen Sie sicher, dass mindestens zwei Versionen deployed sind, damit der Auswähler erscheint

**Problem:** Alter Inhalt erscheint in neu deployter Version
- **Lösung**: Leeren Sie den Browser-Cache und laden Sie neu
- **Lösung**: Überprüfen Sie, dass der Workflow erfolgreich im Actions tab abgeschlossen wurde
- **Lösung**: Überprüfen Sie, dass die korrekte Version deployed wurde, indem Sie die Workflow-Logs prüfen

**Problem:** gh-pages-Branch wurde nicht erstellt
- **Lösung**: Überprüfen Sie Workflow-Logs auf Fehler während des ersten Deployments
- **Lösung**: Überprüfen Sie, dass Actions Schreibberechtigungen haben (siehe erstes Problem oben)
- **Lösung**: Lösen Sie den Workflow manuell über workflow_dispatch aus, um es erneut zu versuchen

#### Best Practices

- Testen Sie immer lokal mit `mike serve` vor dem Deployment
- Verwenden Sie Semantic Versioning für stabile Releases (MAJOR.MINOR.PATCH)
- Behalten Sie 'latest' als Standardversion für Benutzer bei
- Dokumentieren Sie Breaking Changes in versionsspezifischen Release Notes
- Behalten Sie mindestens die letzten 3 stabilen Versionen als Referenz
- Löschen Sie sehr alte Versionen, um die Versionsliste überschaubar zu halten: `mike delete 0.0.1 --push`
- Überprüfen Sie, dass mehrsprachige Unterstützung in allen deployten Versionen funktioniert

#### Fehlerbehebung

**Problem:** Versionsauswähler erscheint nicht
- Lösung: Überprüfen Sie, dass `extra.version.provider: mike` in mkdocs.yml gesetzt ist (bereits konfiguriert in Zeile 137)
- Lösung: Stellen Sie sicher, dass mindestens zwei Versionen deployed sind
- Lösung: Prüfen Sie, dass das Material-Theme richtig konfiguriert ist

**Problem:** Versionen werden nicht deployed
- Lösung: Stellen Sie sicher, dass mike installiert ist: `pip install -e .[docs]`
- Lösung: Prüfen Sie, dass der gh-pages-Branch existiert
- Lösung: Überprüfen Sie, dass das Git-Remote richtig konfiguriert ist

**Problem:** Sprachauswähler kollidiert mit Versionsauswähler
- Lösung: Beide Auswähler sollten zusammenarbeiten; überprüfen Sie die mkdocs-static-i18n-Konfiguration
- Lösung: Testen Sie mit `mike serve`, um sicherzustellen, dass beide Auswähler erscheinen

**Problem:** Alter Inhalt erscheint in neuer Version
- Lösung: Verwenden Sie `mike deploy --update-aliases`, um Aliase zu aktualisieren
- Lösung: Browser-Cache leeren
- Lösung: Neu bauen mit `mkdocs build --clean` vor dem Deployment

#### Ressourcen

- Mike documentation: https://github.com/jimporter/mike
- Material for MkDocs versioning: https://squidfunk.github.io/mkdocs-material/setup/setting-up-versioning/
- Semantic Versioning: https://semver.org/

**Hinweis:** Das Deployment der Dokumentation ist vollständig über GitHub Actions automatisiert. Siehe den Abschnitt "Automatisiertes Deployment mit GitHub Actions" oben für Details darüber, wie der Workflow die Dokumentation bei Branch-Pushes und Tag-Erstellung deployed.

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
