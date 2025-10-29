# d-back Documentation

**WebSocket server for Discord integration with d-zone ambient life simulation**

Welcome to the official documentation for **d-back** – the intelligent backend service that powers the magical **d-zone** ambient life simulation! d-back serves as the real-time bridge between Discord servers and the beautiful d-zone frontend, creating an immersive experience where every Discord user becomes part of a living, breathing digital ecosystem.

d-zone is an ambient life simulation where the presence and activity of users in a Discord server subtly influence a living digital environment. Think of it as a digital terrarium that reacts to your community's energy! d-back provides real-time user data through WebSocket connections, making this seamless integration possible.

---

## Quick Links

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } __Getting Started__

    ---

    Install and run your first WebSocket server in minutes

    [:octicons-arrow-right-24: Get Started](getting-started.md)

-   :material-book-open-variant:{ .lg .middle } __User Guide__

    ---

    Learn how to configure and customize d-back for your needs

    [:octicons-arrow-right-24: User Guide](user-guide.md)

-   :material-code-braces:{ .lg .middle } __API Reference__

    ---

    Explore the complete API documentation with detailed examples

    [:octicons-arrow-right-24: API Reference](api-reference.md)

-   :material-hammer-wrench:{ .lg .middle } __Developer Guide__

    ---

    Contribute to the project and extend its functionality

    [:octicons-arrow-right-24: Developer Guide](developer-guide.md)

</div>

---

## Key Features

!!! success "WebSocket Server"
    Real-time bidirectional communication with the d-zone frontend, supporting multiple concurrent connections and efficient message broadcasting.

!!! success "User Activity Simulation"
    Sophisticated mock Discord user data with realistic presence states (online, idle, DND, offline) perfect for development and testing.

!!! success "Multi-Server Support"
    Handle multiple Discord servers simultaneously, each with their own user lists and configurations.

!!! success "OAuth2 Ready"
    Built-in support for Discord OAuth2 authentication, allowing secure user validation and server access control.

!!! success "Static File Serving"
    Serve frontend assets directly from the backend (websockets 10.0+), simplifying deployment and hosting.

---

## Quick Example

Get started with d-back in just a few lines of code:

```python
import asyncio
from d_back.server import WebSocketServer

async def main():
    # Create server instance
    server = WebSocketServer(port=3000, host="localhost")
    
    # Optional: Set up custom callbacks
    server.on_get_user_data = my_user_data_callback
    server.on_get_server_data = my_server_data_callback
    
    # Start the server
    print("Starting d-back server...")
    await server.start()

# Run the server
asyncio.run(main())
```

Or use the command-line interface:

```bash
# Start with default settings
python -m d_back

# Custom configuration
python -m d_back --port 8080 --host 0.0.0.0 --static-dir ./my-frontend
```

---

## Project Information

![Last Commit](https://img.shields.io/github/last-commit/NNTin/d-back)
![Build Status](https://github.com/NNTin/d-back/actions/workflows/test.yml/badge.svg)
![PyPI](https://img.shields.io/pypi/v/d-back)
![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)

**Repository:** [NNTin/d-back](https://github.com/NNTin/d-back) on GitHub  
**Package:** [d-back](https://pypi.org/project/d-back/) on PyPI  
**License:** MIT License  
**Python:** 3.8 or higher

---

## Next Steps

Ready to dive in? Here's what you should explore next:

1. **[Getting Started](getting-started.md)** - Install d-back and run your first server
2. **Mock Data Capabilities** - Learn about the comprehensive mock data system for testing without Discord API access
3. **[d-zone Frontend](https://nntin.github.io/d-zone/)** - Explore the beautiful frontend that brings your Discord community to life
4. **API Documentation** - Discover all the callback hooks and customization options

!!! tip "Development Ready"
    d-back comes with pre-configured mock Discord servers and realistic user data, making it perfect for development, testing, and demonstration purposes. No Discord API keys required to get started!

---

<p align="center">
  <em>Built with ❤️ for the d-world ecosystem</em>
</p>
