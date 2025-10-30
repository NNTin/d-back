# API Reference

This page provides complete API documentation for d-back, automatically generated from the source code docstrings. All classes and methods include detailed descriptions, parameters, return values, and examples.

## Introduction

The d-back API is organized into two main components:

- **WebSocketServer**: The main server class for handling WebSocket connections, HTTP requests, and message broadcasting
- **MockDataProvider**: Provides mock data and periodic background tasks for development and testing

All API documentation follows Google-style docstrings with comprehensive examples. For usage patterns and integration guides, see the [User Guide](user-guide/index.md).

## WebSocketServer

The main server class for handling WebSocket connections, HTTP requests, and message broadcasting. This is your primary interface to d-back functionality.

::: d_back.server.WebSocketServer
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      heading_level: 3

## MockDataProvider

Provides mock data and periodic background tasks for development and testing. This class is used automatically when custom callbacks are not registered.

::: d_back.mock.data.MockDataProvider
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      heading_level: 3

## Utility Functions

Helper functions for command-line interface and version management.

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

## Usage Examples

For practical examples of using these APIs, see:

- **[Getting Started](getting-started.md)**: Basic usage and first connection
- **[Configuration](user-guide/configuration.md)**: Server setup and configuration
- **[Callbacks & Customization](user-guide/callbacks.md)**: Callback usage examples
- **[Custom Data Providers](user-guide/custom-data-providers.md)**: Data provider implementation patterns

## Type Hints

All methods include comprehensive type hints for parameters and return values. When working with callbacks, import the necessary types:

```python
from typing import Dict, Any, Optional, Tuple, Callable, Awaitable
```

For more information about Python type hints, see the [official typing documentation](https://docs.python.org/3/library/typing.html).
