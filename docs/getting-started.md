# Getting Started

Welcome to d-back! This guide will help you get up and running with the WebSocket server that powers the d-zone ambient life simulation. By the end of this guide, you'll have d-back installed and serving mock Discord data through WebSocket connections.

## Prerequisites

Before you begin, ensure you have the following:

- **Python 3.8 or higher** installed on your system
- **pip package manager** (usually comes with Python)
- **Basic understanding of async/await in Python** (helpful but not required)
- **Git** (optional, only needed if installing from source)

## Installation

d-back can be installed in several ways. Choose the method that best fits your needs:

### From PyPI (Recommended)

The easiest way to install d-back is from the Python Package Index:

```bash
pip install d-back
```

### From Source

For the latest development version or if you want to contribute:

1. Clone the repository:
   ```bash
   git clone https://github.com/NNTin/d-back.git
   cd d-back
   ```

2. Create a virtual environment (recommended):

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

3. Install in development mode:
   ```bash
   pip install -e .
   ```

### With Documentation Dependencies

If you plan to build the documentation locally:

```bash
pip install d-back[docs]
```

Or from source:

```bash
pip install -e .[docs]
```

## Verify Installation

After installation, verify that d-back is correctly installed:

```bash
d_back --version
```

You should see output similar to:

```
d-back version 0.0.14
```

!!! tip "Troubleshooting"
    If the `d_back` command is not found, ensure your Python scripts directory is in your PATH. Alternatively, you can run d-back as a Python module: `python -m d_back --version`

## Quick Start

Now that d-back is installed, let's get it running!

### Command-Line Approach

The simplest way to start the server is with default settings:

```bash
# Start with defaults (localhost:3000)
d_back
```

Or run it as a Python module:

```bash
python -m d_back
```

You should see console output similar to:

```
WebSocket server started on ws://localhost:3000
Serving static files from: /path/to/d_back/dist
Press Ctrl+C to stop the server
```

!!! note "Default Settings"
    By default, d-back runs on `localhost:3000` and serves the built-in d-zone frontend from static files.

### Programmatic Approach

For more control, you can use d-back in your Python code:

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

Each step explained:
1. **Import modules**: Import asyncio for async execution and WebSocketServer class
2. **Create server**: Instantiate WebSocketServer with desired port and host
3. **Configure callbacks** (optional): Customize data sources with callback functions
4. **Start server**: Call `await server.start()` to begin accepting connections

## Your First WebSocket Connection

Once the server is running, you can test the WebSocket connection from a client.

### Using JavaScript/Browser

Open your browser console and run:

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

**Message Format**: The `get_user_data` request includes:
- `type`: Message type (`"get_user_data"`)
- `serverId`: Discord server ID (snowflake format)

**Expected Response**: You'll receive a JSON object containing user data:
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

### Using Python websockets Library

You can also connect using Python's `websockets` library:

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

### Expected Behavior

When you successfully connect, you should see:
1. **Connection established**: WebSocket opens successfully
2. **Server list received**: Initial message with available Discord servers
3. **User data returned**: Response with mock user presence and role information

## Understanding Mock Data

d-back comes with pre-configured mock Discord servers for development and testing. This means you can start building and testing immediately without setting up Discord API credentials!

The available mock servers are:

- **d-world server** (`232769614004748288`): Main development server with 50+ active users across different statuses
- **docs server** (`482241773318701056`): Documentation server with 10 users
- **oauth2 server** (`123456789012345678`): Protected server for testing OAuth2 authentication flows
- **my repos server** (`987654321098765432`): Repository showcase server with 5 users

!!! tip "Perfect for Development"
    Mock data is ideal for:
    
    - Frontend development without backend dependencies
    - Testing d-zone visualization with realistic data
    - Demonstrating the system without Discord API keys
    - CI/CD pipelines and automated testing

To use real Discord data in production, you'll need to implement custom data providers. See the [Custom Data Providers](user-guide/custom-data-providers.md) guide for details.

## Next Steps

Congratulations! You now have d-back up and running. Here's what to explore next:

- **[User Guide](user-guide/index.md)**: Learn about configuration options, callbacks, and customization
- **[Configuration](user-guide/configuration.md)**: Customize server settings, ports, and static file serving
- **[Callbacks & Customization](user-guide/callbacks.md)**: Replace mock data with your own data sources
- **[Custom Data Providers](user-guide/custom-data-providers.md)**: Integrate with Discord API or databases
- **[API Reference](api-reference.md)**: Detailed documentation of all classes and methods
- **[Developer Guide](developer-guide.md)**: Contributing guidelines and architecture overview

!!! question "Need Help?"
    If you encounter issues, check the [GitHub Issues](https://github.com/NNTin/d-back/issues) or start a [Discussion](https://github.com/NNTin/d-back/discussions).
