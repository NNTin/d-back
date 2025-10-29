"""Entry point for running D-Back as a module.

This module allows D-Back to be executed directly using Python's -m flag.
It provides a convenient command-line interface for starting the WebSocket
server with customizable configuration options.

Usage:

    # Start with default settings (port 3000, host localhost)
    python -m d_back
    
    # Start with custom port
    python -m d_back --port 8080
    
    # Start with custom host
    python -m d_back --host 0.0.0.0
    
    # Start with custom static directory
    python -m d_back --static-dir /path/to/dist
    
    # Show version information
    python -m d_back --version
    
    # Show help message
    python -m d_back --help

Command Line Arguments:
    --port PORT: WebSocket server port (default: 3000)
    --host HOST: Host to bind the WebSocket server to (default: localhost)
    --static-dir DIR: Directory containing static files to serve (optional, uses built-in dist if not provided)
    --version: Display version information and exit
    --help: Display help message and exit

Examples:

    # Start server on port 8080 with custom static files
    python -m d_back --port 8080 --static-dir /var/www/d-zone
    
    # The server will be accessible at:
    # - WebSocket: ws://localhost:8080
    # - HTTP: http://localhost:8080
    # - Version API: http://localhost:8080/api/version

See Also:
    server.main_sync: The main entry point function
    server.parse_args: Command line argument parser
"""

from .server import main_sync

if __name__ == "__main__":
    main_sync()

