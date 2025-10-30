# d-back Dokumentation

**WebSocket-Server für Discord-Integration mit d-zone Ambient-Life-Simulation**

Willkommen zur offiziellen Dokumentation von **d-back** – dem intelligenten Backend-Service, der die magische **d-zone** Ambient-Life-Simulation antreibt! d-back dient als Echtzeit-Brücke zwischen Discord-Servern und dem schönen d-zone-Frontend und schafft ein immersives Erlebnis, bei dem jeder Discord-Benutzer Teil eines lebendigen, atmenden digitalen Ökosystems wird.

d-zone ist eine Ambient-Life-Simulation, bei der die Anwesenheit und Aktivität der Benutzer auf einem Discord-Server ein lebendes digitales Umfeld subtil beeinflussen. Stellen Sie es sich wie ein digitales Terrarium vor, das auf die Energie Ihrer Community reagiert! d-back stellt Echtzeit-Benutzerdaten über WebSocket-Verbindungen bereit und ermöglicht diese nahtlose Integration.

---

## Schnelllinks

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } __Erste Schritte__

    ---

    Installieren und starten Sie Ihren ersten WebSocket-Server in Minuten

    [:octicons-arrow-right-24: Beginnen](getting-started.md)

-   :material-book-open-variant:{ .lg .middle } __Benutzerhandbuch__

    ---

    Erfahren Sie, wie Sie d-back für Ihre Bedürfnisse konfigurieren und anpassen

    [:octicons-arrow-right-24: Benutzerhandbuch](user-guide/index.md)

-   :material-code-braces:{ .lg .middle } __API-Referenz__

    ---

    Erkunden Sie die vollständige API-Dokumentation mit detaillierten Beispielen

    [:octicons-arrow-right-24: API-Referenz](api-reference.md)

-   :material-hammer-wrench:{ .lg .middle } __Entwicklerhandbuch__

    ---

    Tragen Sie zum Projekt bei und erweitern Sie seine Funktionalität

    [:octicons-arrow-right-24: Entwicklerhandbuch](developer-guide.md)

</div>

---

## Hauptmerkmale

!!! success "WebSocket-Server"
    Bidirektionale Echtzeitkommunikation mit dem d-zone-Frontend, unterstützt mehrere gleichzeitige Verbindungen und effizientes Nachrichten-Broadcasting.

!!! success "Benutzeraktivitäts-Simulation"
    Ausgefeilte Mock-Discord-Benutzerdaten mit realistischen Präsenzzuständen (online, inaktiv, DND, offline), perfekt für Entwicklung und Tests.

!!! success "Multi-Server-Unterstützung"
    Verwalten Sie mehrere Discord-Server gleichzeitig, jeder mit eigenen Benutzerlisten und Konfigurationen.

!!! success "OAuth2-fähig"
    Integrierte Unterstützung für Discord-OAuth2-Authentifizierung, ermöglicht sichere Benutzervalidierung und Serverzugriffskontrolle.

!!! success "Statische Dateiauslieferung"
    Frontend-Assets direkt vom Backend ausliefern (websockets 10.0+), vereinfacht Bereitstellung und Hosting.

---

## Schnellbeispiel

Beginnen Sie mit d-back in nur wenigen Codezeilen:

```python
import asyncio
from d_back.server import WebSocketServer

async def main():
    # Create server instance
    server = WebSocketServer(port=3000, host="localhost")
    
    # Optional: Set up custom callbacks
    server.on_get_user_data(my_user_data_callback)
    server.on_get_server_data(my_server_data_callback)
    
    # Start the server
    print("Starting d-back server...")
    await server.start()

# Run the server
asyncio.run(main())
```

Oder verwenden Sie die Befehlszeilenschnittstelle:

```bash
# Start with default settings
python -m d_back

# Custom configuration
python -m d_back --port 8080 --host 0.0.0.0 --static-dir ./my-frontend
```

---

## Projektinformationen

![Last Commit](https://img.shields.io/github/last-commit/NNTin/d-back)
![Build Status](https://github.com/NNTin/d-back/actions/workflows/test.yml/badge.svg)
![PyPI](https://img.shields.io/pypi/v/d-back)
![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)

**Repository:** [NNTin/d-back](https://github.com/NNTin/d-back) auf GitHub  
**Paket:** [d-back](https://pypi.org/project/d-back/) auf PyPI  
**Lizenz:** MIT-Lizenz  
**Python:** 3.8 oder höher

---

## Nächste Schritte

Bereit einzutauchen? Hier ist, was Sie als Nächstes erkunden sollten:

1. **[Erste Schritte](getting-started.md)** - Installieren Sie d-back und starten Sie Ihren ersten Server
2. **Mock-Daten-Fähigkeiten** - Erfahren Sie mehr über das umfassende Mock-Daten-System für Tests ohne Discord-API-Zugriff
3. **[d-zone Frontend](https://nntin.github.io/d-zone/)** - Erkunden Sie das schöne Frontend, das Ihre Discord-Community zum Leben erweckt
4. **API-Dokumentation** - Entdecken Sie alle Callback-Hooks und Anpassungsoptionen

!!! tip "Entwicklungsbereit"
    d-back kommt mit vorkonfigurierten Mock-Discord-Servern und realistischen Benutzerdaten, ideal für Entwicklung, Tests und Demonstrationszwecke. Keine Discord-API-Schlüssel erforderlich, um loszulegen!

---

<p align="center">
  <em>Mit ❤️ für das d-world-Ökosystem erstellt</em>
</p>
