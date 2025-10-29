# User Guide

Welcome to the d-back user guide! This comprehensive guide covers everything you need to effectively use d-back as a WebSocket server for your d-zone ambient life simulation or other real-time applications.

## Introduction

This guide is designed for users who have already completed the [Getting Started](../getting-started.md) tutorial and want to dive deeper into d-back's features and capabilities. Whether you're looking to customize server behavior, integrate with real Discord data, or optimize your setup, you'll find the information you need here.

The user guide is organized into three main areas:

- **Configuration**: Learn how to configure d-back through command-line options, environment variables, and programmatic settings
- **Callbacks & Customization**: Discover how to customize server behavior using callback functions for data retrieval, authentication, and more
- **Custom Data Providers**: Replace mock data with real Discord API integration or your own custom data sources

## Guide Structure

<div class="grid cards" markdown>

-   :material-cog:{ .lg .middle } **Configuration**

    ---

    Learn about command-line options, environment variables, and server settings

    [:octicons-arrow-right-24: Configuration Guide](configuration.md)

-   :material-code-braces:{ .lg .middle } **Callbacks & Customization**

    ---

    Customize server behavior with callback functions for data retrieval and authentication

    [:octicons-arrow-right-24: Callbacks Guide](callbacks.md)

-   :material-database:{ .lg .middle } **Custom Data Providers**

    ---

    Replace mock data with real Discord API integration or custom data sources

    [:octicons-arrow-right-24: Data Providers Guide](custom-data-providers.md)

</div>

## Common Use Cases

Need to accomplish a specific task? Here are quick links to common scenarios:

| Scenario | Where to Look |
|----------|---------------|
| I want to change the server port | [Configuration → Command-Line Options](configuration.md#command-line-options) |
| I want to serve my own static files | [Configuration → Static File Serving](configuration.md#static-file-serving) |
| I want to use real Discord data | [Custom Data Providers](custom-data-providers.md) |
| I want to add OAuth2 authentication | [Callbacks → OAuth2 Validation](callbacks.md#on_validate_discord_user-callback) |
| I want to broadcast custom messages | [Callbacks → Broadcasting Methods](callbacks.md#broadcasting-methods) |
| I want to customize user data format | [Callbacks → User Data Callback](callbacks.md#on_get_user_data-callback) |

## Quick Reference

Here's a summary of key concepts you'll encounter in this guide:

| Concept | Description |
|---------|-------------|
| **WebSocketServer** | Main server class that handles WebSocket connections, HTTP requests, and message broadcasting |
| **MockDataProvider** | Built-in test data generator that simulates Discord user activity |
| **Callbacks** | Customization hooks that allow you to override default behavior (e.g., `on_get_user_data`, `on_get_server_data`) |
| **Static File Serving** | Built-in HTTP server for delivering frontend assets like HTML, CSS, and JavaScript |
| **Broadcasting** | Methods for sending real-time updates to connected clients (presence, messages, etc.) |
| **OAuth2 Integration** | Support for Discord OAuth2 authentication and token validation |

!!! tip "Need API Details?"
    For detailed API documentation including method signatures, parameters, and return types, see the [API Reference](../api-reference.md).

## What's Next?

Ready to customize your d-back setup? Start with:

1. **[Configuration](configuration.md)** - Set up your server with the right settings
2. **[Callbacks & Customization](callbacks.md)** - Learn how to customize behavior
3. **[Custom Data Providers](custom-data-providers.md)** - Integrate real data sources

!!! question "Questions?"
    If you can't find what you're looking for, check the [API Reference](../api-reference.md) or visit our [GitHub Discussions](https://github.com/NNTin/d-back/discussions).
