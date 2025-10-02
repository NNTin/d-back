# d-back  

![Last Commit](https://img.shields.io/github/last-commit/NNTin/d-back) 
![Open Pull Requests](https://img.shields.io/github/issues-pr/NNTin/d-back)
![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Stars](https://img.shields.io/github/stars/NNTin/d-back)
![Contributors](https://img.shields.io/github/contributors/NNTin/d-back)
![Build Status](https://github.com/NNTin/d-back/actions/workflows/test.yml/badge.svg)
![PyPI](https://img.shields.io/pypi/v/d-back)



Welcome to **d-back** – the backend service that powers the magical **d-zone** ambient life simulation!

## 🎯 Project Overview

**d-zone** is an ambient life simulation where the presence and activity of users in a Discord server subtly influence a living digital environment. Think of it as a digital terrarium that reacts to your community's energy!

**d-back** serves as the intelligent bridge between Discord servers and the beautiful [d-zone frontend](https://nntin.github.io/d-zone/).  
It provides real-time user data through WebSocket connections, creating an immersive experience where every Discord user becomes part of a living, breathing digital ecosystem.

Currently, d-back uses sophisticated mock data to simulate user activity, making it perfect for development, testing, and demonstration purposes.

## ✨ Features

- 🔌 **WebSocket Server**: Real-time communication with the d-zone frontend
- 👥 **User Activity Simulation**: Mock Discord user data with realistic presence states
- 🎨 **Role Color Support**: Beautiful user representation with Discord role colors  
- 🌐 **Multi-Server Support**: Handle multiple Discord servers simultaneously
- 📊 **Status Tracking**: Monitor online, idle, DND, and offline user states
- 🔒 **OAuth2 Ready**: Built-in support for Discord OAuth2 authentication
- 📁 **Static File Serving**: Serve frontend assets directly from the backend
- 🚀 **Easy Configuration**: Simple command-line options and programmatic setup
- 🧪 **Development Friendly**: Comprehensive mock data for testing and development

## 🛠️ Installation

### Step-by-Step Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/NNTin/d-back.git
   cd d-back
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   # On Windows
   python -m venv .venv
   .venv\Scripts\activate

   # On macOS/Linux  
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install the package:**
   ```bash
   # Install in development mode (recommended for contributors)
   pip install -e .

   # Or install directly from requirements
   pip install -r requirements.txt
   ```

4. **Verify installation:**
   ```bash
   d_back --version
   ```

## 🚀 Usage

### Quick Start

The simplest way to get d-back running:

```bash
# Start the server with default settings (localhost:3000)
d_back

# Or run as a Python module
python -m d_back
```

### Command Line Options

```bash
# Custom host and port
d_back --host 0.0.0.0 --port 8080

# Serve custom static files
d_back --static-dir ./my-frontend-build

# Get help
d_back --help
```

### Programmatic Usage

Use d-back in your Python projects:

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

### Testing the WebSocket Connection

You can test the server using any WebSocket client:

```javascript
// JavaScript example for testing
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

## ⚙️ Configuration

### Command Line Arguments

| Option | Default | Description |
|--------|---------|-------------|
| `--port` | `3000` | Port to run the WebSocket server on |
| `--host` | `localhost` | Host to bind the server to |
| `--static-dir` | Built-in | Directory to serve static files from |
| `--version` | - | Show version information |

### Mock Server Configuration

d-back comes with pre-configured mock Discord servers for testing:

- **D-World Server** (`232769614004748288`): Main development server with active users
- **Docs Server** (`482241773318701056`): Documentation server  
- **OAuth2 Server** (`123456789012345678`): Protected server for OAuth testing
- **My Repos Server** (`987654321098765432`): Repository showcase server

### Environment Variables

While d-back doesn't currently use environment variables for configuration, you can extend it easily:

```python
import os
from d_back.server import WebSocketServer

# Example: Use environment variables
port = int(os.getenv('D_BACK_PORT', 3000))
host = os.getenv('D_BACK_HOST', 'localhost')

server = WebSocketServer(port=port, host=host)
```

### Custom Data Providers

Replace mock data with your own:

```python
from d_back.server import WebSocketServer

async def my_user_data_provider(server_id):
    # Your custom logic here
    return {
        "user123": {
            "uid": "user123",
            "username": "MyUser",
            "status": "online",
            "roleColor": "#ff6b6b"
        }
    }

server = WebSocketServer()
server.on_get_user_data = my_user_data_provider
```

## 📜 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
