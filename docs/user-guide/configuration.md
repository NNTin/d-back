# Configuration

This guide covers all the ways you can configure d-back to suit your needs, from command-line options to programmatic settings and environment variables.

## Introduction

d-back offers flexible configuration options to adapt to different deployment scenarios. Whether you're running it from the command line during development or integrating it into a larger Python application, you have full control over server behavior, network settings, and static file serving.

## Command-Line Options

When running d-back from the command line, you can customize its behavior using various options:

### Available Options

| Option | Default | Description | Example |
|--------|---------|-------------|---------|
| `--port` | `3000` | Port to run the WebSocket server on | `d_back --port 8080` |
| `--host` | `localhost` | Host to bind the server to | `d_back --host 0.0.0.0` |
| `--static-dir` | Built-in | Directory to serve static files from | `d_back --static-dir ./my-frontend-build` |
| `--version` | - | Show version information | `d_back --version` |

### Usage Examples

**Default startup** (localhost:3000):
```bash
d_back
```

**Custom host and port**:
```bash
d_back --host 0.0.0.0 --port 8080
```

This makes the server accessible from other machines on your network.

**Custom static directory**:
```bash
d_back --static-dir ./my-frontend-build
```

Serve your own frontend files instead of the built-in d-zone interface.

**Get help**:
```bash
d_back --help
```

Display all available command-line options.

**Check version**:
```bash
d_back --version
```

!!! note "Running as a Module"
    You can also run d-back as a Python module with the same options:
    ```bash
    python -m d_back --host 0.0.0.0 --port 8080
    ```

## Programmatic Configuration

For more control and integration into your Python applications, you can configure d-back programmatically:

```python
import asyncio
from d_back.server import WebSocketServer

async def main():
    # Create server instance with custom settings
    server = WebSocketServer(port=3000, host="localhost")
    
    # Configure callbacks (optional)
    server.on_get_user_data = my_user_data_callback
    server.on_get_server_data = my_server_data_callback
    
    # Start the server
    print("Starting d-back server...")
    await server.start()

asyncio.run(main())
```

### Constructor Parameters

The `WebSocketServer` class accepts the following parameters:

- **`port`** (int, optional): The port number to listen on. Defaults to `3000`.
- **`host`** (str, optional): The hostname or IP address to bind to. Defaults to `"localhost"`.

### When to Use Programmatic Configuration

Use programmatic configuration when you:

- Need to integrate d-back into a larger Python application
- Want to dynamically configure settings based on runtime conditions
- Need to access server instance methods and attributes
- Want to implement custom startup/shutdown logic

### Accessing Server Attributes

Once you create a `WebSocketServer` instance, you can access various attributes:

```python
server = WebSocketServer(port=3000, host="localhost")

# Access configuration
print(f"Server will run on {server.host}:{server.port}")

# Access connections (set of connected WebSocket clients)
print(f"Active connections: {len(server.connections)}")

# Access data provider
print(f"Using data provider: {server.data_provider}")
```

## Environment Variables

While d-back doesn't use environment variables by default, you can easily extend it to support environment-based configuration:

```python
import os
from d_back.server import WebSocketServer

# Example: Use environment variables
port = int(os.getenv('D_BACK_PORT', 3000))
host = os.getenv('D_BACK_HOST', 'localhost')

server = WebSocketServer(port=port, host=host)
```

### Recommended Environment Variables

Here's a suggested pattern for environment variable naming:

| Environment Variable | Type | Default | Description |
|---------------------|------|---------|-------------|
| `D_BACK_PORT` | int | `3000` | Server port |
| `D_BACK_HOST` | str | `localhost` | Server host |
| `D_BACK_STATIC_DIR` | str | Built-in | Static files directory |

### Example: Full Environment Variable Integration

```python
import os
import asyncio
from pathlib import Path
from d_back.server import WebSocketServer

async def main():
    # Read configuration from environment
    port = int(os.getenv('D_BACK_PORT', 3000))
    host = os.getenv('D_BACK_HOST', 'localhost')
    static_dir = os.getenv('D_BACK_STATIC_DIR')
    
    # Create server
    server = WebSocketServer(port=port, host=host)
    
    # Configure static directory if provided
    if static_dir:
        server.static_dir = Path(static_dir)
    
    # Start server
    await server.start()

if __name__ == '__main__':
    asyncio.run(main())
```

!!! tip "Deployment Flexibility"
    Using environment variables makes it easy to deploy d-back across different environments (development, staging, production) without code changes.

## Static File Serving

d-back includes a built-in HTTP server for serving static files, making it easy to deliver your d-zone frontend or other web assets.

### Default Behavior

By default, d-back serves static files from its built-in `dist/` directory, which contains the d-zone frontend.

### Custom Static Directory

To serve your own static files:

**Command-line**:
```bash
d_back --static-dir ./my-frontend-build
```

**Programmatic**:
```python
from pathlib import Path
server = WebSocketServer(port=3000, host="localhost")
server.static_dir = Path("./my-frontend-build")
```

### Requirements

Static file serving requires **websockets version 10.0 or higher** for HTTP protocol support. This is automatically handled by d-back's dependencies.

### Security

d-back includes path traversal protection to prevent accessing files outside the static directory. Requests like `/../../../etc/passwd` are automatically blocked.

!!! warning "Security Note"
    Always ensure your static directory doesn't contain sensitive files. Only serve files that are intended to be publicly accessible.

### File Types

The server automatically detects content types based on file extensions:

- `.html` → `text/html`
- `.css` → `text/css`
- `.js` → `application/javascript`
- `.json` → `application/json`
- `.png`, `.jpg`, `.gif` → Appropriate image types
- And more...

## Mock Server Configuration

d-back comes with pre-configured mock Discord servers for development and testing. These servers provide realistic user data without requiring Discord API credentials.

### Available Mock Servers

| Server Name | Server ID | Description | User Count |
|-------------|-----------|-------------|------------|
| **d-world server** | `232769614004748288` | Main development server with diverse user activity | 50+ users |
| **docs server** | `482241773318701056` | Documentation server with moderate activity | 10 users |
| **oauth2 server** | `123456789012345678` | Protected server for testing OAuth2 flows | Varies |
| **my repos server** | `987654321098765432` | Repository showcase server | 5 users |

### Using Mock Servers

Mock servers are automatically available when you start d-back. You can request data for any of these servers using their server ID:

```javascript
// JavaScript WebSocket client example
socket.send(JSON.stringify({
    type: 'get_user_data',
    serverId: '232769614004748288'  // d-world server
}));
```

### Mock Data Characteristics

The mock data includes:

- **User statuses**: online, idle, dnd (do not disturb), offline
- **Role colors**: Hex color codes for visual representation
- **Realistic names**: Varied Discord-style usernames
- **Dynamic updates**: Status changes and messages occur periodically

!!! note "Development Only"
    Mock servers are designed for development and testing. For production deployments, implement custom data providers to use real Discord data. See the [Custom Data Providers](custom-data-providers.md) guide.

## Server Lifecycle

Understanding the server lifecycle helps you manage startup, operation, and shutdown effectively.

### Starting the Server

**Method 1: `start()`**
```python
await server.start()
```
Starts the WebSocket server and HTTP listener. This method returns immediately after startup, allowing you to perform additional operations.

**Method 2: `run_forever()`**
```python
await server.run_forever()
```
Starts the server and runs it indefinitely until interrupted. This is useful for simple server scripts.

### Stopping the Server

**Graceful shutdown:**
```python
await server.stop()
```
Closes all active connections and stops the server cleanly.

**Signal handling:**
The server automatically handles `Ctrl+C` (SIGINT) for graceful shutdown. When you press `Ctrl+C`, the server will:

1. Stop accepting new connections
2. Close existing connections gracefully
3. Clean up resources
4. Exit

### Complete Lifecycle Example

```python
import asyncio
import signal
from d_back.server import WebSocketServer

async def main():
    server = WebSocketServer(port=3000, host="localhost")
    
    # Setup signal handler for graceful shutdown
    loop = asyncio.get_event_loop()
    
    def signal_handler():
        print("\nReceived shutdown signal...")
        asyncio.create_task(server.stop())
    
    loop.add_signal_handler(signal.SIGINT, signal_handler)
    loop.add_signal_handler(signal.SIGTERM, signal_handler)
    
    # Start server
    print("Starting server...")
    await server.start()
    
    # Run forever
    await server.run_forever()

asyncio.run(main())
```

## Best Practices

Follow these recommendations for optimal d-back configuration:

### Network Configuration

!!! tip "Development vs Production"
    - **Development**: Use `localhost` to restrict access to your machine only
    - **Production**: Use `0.0.0.0` to accept connections from any network interface

!!! warning "Port Selection"
    - Avoid privileged ports (`<1024`) unless running with appropriate permissions
    - Common ports like `3000`, `8080`, or `8000` are good choices
    - Check that your chosen port isn't already in use

### Static Files

- **Organize**: Keep static files in a dedicated directory
- **Structure**: Use standard web project structure (`index.html`, `css/`, `js/`, etc.)
- **Build process**: If using a frontend framework, configure your build output to the static directory

### Configuration Management

- **Use environment variables** for deployment-specific settings
- **Use programmatic configuration** for complex or dynamic setups
- **Document your configuration** in README or deployment guides
- **Keep secrets secure**: Never hardcode API keys or tokens

### Performance

- **Connection limits**: Monitor the number of active connections
- **Resource usage**: Track memory and CPU usage under load
- **Logging**: Implement appropriate logging for debugging and monitoring

!!! example "Production Configuration Example"
    ```python
    import os
    from d_back.server import WebSocketServer
    
    # Production-ready configuration
    server = WebSocketServer(
        port=int(os.getenv('PORT', 3000)),
        host='0.0.0.0'  # Accept external connections
    )
    
    # Configure callbacks for real data
    server.on_get_user_data = real_discord_data_provider
    server.on_validate_discord_user = oauth2_validator
    
    # Start server
    await server.start()
    ```

## What's Next?

Now that you understand how to configure d-back, learn how to customize its behavior:

- **[Callbacks & Customization](callbacks.md)**: Override default behavior with custom callbacks
- **[Custom Data Providers](custom-data-providers.md)**: Replace mock data with real sources
- **[API Reference](../api-reference.md)**: Detailed API documentation
