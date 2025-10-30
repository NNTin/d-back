# Developer Guide

Welcome to the d-back developer guide! Thank you for your interest in contributing to this project. This guide covers everything you need to know to get started with development, understand the architecture, run tests, and submit contributions.

## Introduction

d-back is an open-source project released under the MIT License. We welcome contributions of all kinds: bug fixes, new features, documentation improvements, and more. This guide will help you set up your development environment and understand how the project is structured.

**GitHub Repository**: [https://github.com/NNTin/d-back](https://github.com/NNTin/d-back)

**License**: MIT - See [LICENSE](https://github.com/NNTin/d-back/blob/main/LICENSE) for details

## Getting Started with Development

### Fork and Clone

1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/d-back.git
   cd d-back
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/NNTin/d-back.git
   ```

### Set Up Development Environment

1. **Create a virtual environment**:

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

2. **Install in development mode**:
   ```bash
   pip install -e .
   ```

3. **Install test dependencies**:
   ```bash
   pip install pytest pytest-asyncio websockets
   ```

4. **Install documentation dependencies** (optional):
   ```bash
   pip install -e .[docs]
   ```

5. **Verify installation**:
   ```bash
   d_back --version
   pytest tests/
   ```

## Project Architecture

Understanding the codebase structure will help you navigate and contribute effectively.

### Directory Structure

```
d-back/
├── d_back/                 # Main package directory
│   ├── __init__.py         # Package initialization and exports
│   ├── __main__.py         # CLI entry point (python -m d_back)
│   ├── server.py           # WebSocketServer implementation
│   └── mock/               # Mock data providers
│       ├── __init__.py     # Mock package initialization
│       └── data.py         # MockDataProvider class
├── tests/                  # Test suite
│   ├── test_websocket_server.py # WebSocket functionality tests
│   ├── test_browser_integration.py # Browser integration tests
│   ├── helpers/            # Test utilities
│   │   └── mock_websocket_client.py
│   └── README.md           # Testing documentation
├── docs/                   # Documentation source files (MkDocs)
│   ├── index.md            # Documentation homepage
│   ├── getting-started.md  # Installation and setup guide
│   ├── user-guide/         # User guide sections
│   ├── api-reference.md    # API documentation
│   └── developer-guide.md  # This file
├── setup.cfg               # Package configuration
├── pyproject.toml          # Build system configuration
├── mkdocs.yml              # Documentation configuration
├── requirements.txt        # Runtime dependencies
└── README.md               # Project readme

```

### Core Components

#### WebSocketServer (`d_back/server.py`)

The main server class responsible for:

- **Connection Management**: Maintains a set of active WebSocket connections
- **Callback System**: Provides hooks for customizing behavior:
  - `on_get_user_data`: Fetch user data for a server
  - `on_get_server_data`: Fetch list of available servers
  - `on_static_request`: Handle custom static file requests
  - `on_validate_discord_user`: Validate OAuth2 tokens
  - `on_get_client_id`: Provide OAuth2 client IDs
- **HTTP Static File Serving**: Uses websockets 10.0+ support for serving files
- **Message Broadcasting**: Methods for sending updates to all connected clients:
  - `broadcast_message`: Send chat messages
  - `broadcast_presence`: Send presence updates (status changes)
  - `broadcast_client_id_update`: Send OAuth2 configuration changes
- **OAuth2 Authentication**: Built-in flow for Discord authentication

**Key Methods**:
- `start()`: Initialize and start the server
- `stop()`: Gracefully shutdown the server
- `run_forever()`: Run the server indefinitely
- `_handle_connection()`: Process incoming WebSocket connections
- `_serve_static_file()`: Serve HTTP static files with security

#### MockDataProvider (`d_back/mock/data.py`)

Provides mock data for development and testing:

- **Mock User Data**: Generates realistic Discord user objects with various statuses
- **Mock Server Configurations**: Pre-configured test servers (d-world, docs, oauth2, my repos)
- **Periodic Background Tasks**: Simulates user activity:
  - Random status changes
  - Random chat messages
  - Realistic timing patterns

**Key Methods**:
- `get_mock_server_data(server_id)`: Returns mock users for a server
- `get_mock_servers()`: Returns list of available mock servers
- `_start_background_tasks()`: Initiates periodic updates
- `_random_status_change()`: Simulates presence changes
- `_random_message()`: Simulates chat activity

### Message Protocol

WebSocket messages use JSON format with a `type` field to determine the message kind.

#### Client → Server Messages

**get_user_data**:
```json
{
  "type": "get_user_data",
  "serverId": "232769614004748288"
}
```

**authenticate** (OAuth2):
```json
{
  "type": "authenticate",
  "token": "oauth2_access_token",
  "serverId": "232769614004748288"
}
```

#### Server → Client Messages

**connect** (initial connection):
```json
{
  "type": "connect",
  "servers": {
    "232769614004748288": {
      "id": "232769614004748288",
      "name": "d-world",
      "passworded": false,
      "default": true
    }
  }
}
```

**user_data**:
```json
{
  "type": "user_data",
  "serverId": "232769614004748288",
  "users": {
    "user123": {
      "uid": "user123",
      "username": "TestUser",
      "status": "online",
      "roleColor": "#ff6b6b"
    }
  }
}
```

**message** (chat message):
```json
{
  "type": "message",
  "server": "232769614004748288",
  "uid": "user123",
  "message": "Hello!",
  "channel": "channel456"
}
```

**presence** (status update):
```json
{
  "type": "presence",
  "server": "232769614004748288",
  "uid": "user123",
  "status": "idle",
  "username": "TestUser",
  "roleColor": "#ff6b6b",
  "delete": false
}
```

**client_id_update**:
```json
{
  "type": "client_id_update",
  "server": "232769614004748288",
  "clientId": "123456789012345678"
}
```

### HTTP Support

d-back includes HTTP support for serving static files (requires websockets 10.0+):

- **Version Detection**: Checks websockets library version at runtime
- **Fallback Behavior**: Logs warning if HTTP not supported
- **Static File Serving**: Serves files from `dist/` directory by default
- **Security**: Path traversal protection prevents accessing files outside static directory
- **Content Types**: Automatically detects MIME types based on file extensions

**API Endpoints**:
- `/api/version`: Returns server version information (if implemented)
- All other paths: Serve from static directory

## Testing

Comprehensive testing ensures d-back remains stable and reliable.

### Test Structure

```
tests/
├── test_websocket_server.py  # WebSocket functionality tests
├── test_browser_integration.py # Browser integration tests
├── helpers/
│   └── mock_websocket_client.py  # Mock client for testing
└── README.md                 # Detailed testing documentation
```

### Test Coverage

The test suite covers:

- ✅ WebSocket server initialization and startup
- ✅ Client connection and disconnection
- ✅ Message sending and receiving
- ✅ User data requests and responses
- ✅ Server list retrieval
- ✅ OAuth2 authentication flow
- ✅ Error handling and edge cases
- ✅ Callback customization
- ✅ Broadcasting functionality
- ✅ Static file serving
- ✅ Path traversal protection
- ✅ Graceful shutdown

### Running Tests

#### Option 1: pytest (Recommended)

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_websocket_server.py

# Run specific test
pytest tests/test_websocket_server.py::test_server_startup

# Run with coverage
pytest --cov=d_back --cov-report=html
```

#### Option 2: Simple Test Runner

For Python 3.8+ without pytest:

```bash
python -m tests.test_websocket_server
```

#### Option 3: Manual Testing

Start the server and test manually:

```bash
# Terminal 1: Start server
d_back

# Terminal 2: Test with Python client
python test_client.py
```

### Writing Tests

Tests use pytest and pytest-asyncio for async support:

```python
import pytest
import websockets
import json
from d_back.server import WebSocketServer

@pytest.mark.asyncio
async def test_my_feature():
    """Test description."""
    # Setup
    server = WebSocketServer(port=3001, host="localhost")
    await server.start()
    
    try:
        # Test
        async with websockets.connect("ws://localhost:3001") as websocket:
            # Send request
            await websocket.send(json.dumps({
                "type": "get_user_data",
                "serverId": "232769614004748288"
            }))
            
            # Receive response
            response = await websocket.recv()
            data = json.loads(response)
            
            # Assertions
            assert data["type"] == "user_data"
            assert "users" in data
    
    finally:
        # Cleanup
        await server.stop()
```

### Test Configuration

Test settings are defined in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
```

## Contributing Guidelines

### Code Style

Follow these conventions to maintain code quality:

- **PEP 8**: Follow Python style guide
- **Type Hints**: Add type annotations to all functions
- **Docstrings**: Use Google-style docstrings
- **Function Size**: Keep functions focused and under 50 lines when possible
- **Variable Names**: Use descriptive names (avoid single letters except loops)

**Example**:
```python
async def fetch_user_data(server_id: str, include_offline: bool = False) -> Dict[str, Any]:
    """
    Fetch user data for a Discord server.
    
    Args:
        server_id: Discord server snowflake ID.
        include_offline: Whether to include offline users.
    
    Returns:
        Dictionary mapping user IDs to user objects.
    
    Examples:
        >>> data = await fetch_user_data("123456789")
        >>> print(data.keys())
        dict_keys(['user1', 'user2'])
    """
    # Implementation
    pass
```

### Documentation

Document your changes thoroughly:

- **Docstrings**: Add to all public classes and methods
- **Examples**: Include usage examples in docstrings
- **User Guide**: Update relevant documentation pages
- **CHANGELOG**: Add entry describing your change

**Test documentation builds**:
```bash
mkdocs serve
```

Visit `http://127.0.0.1:8000` to preview.

## Documentation Translation

### Overview

The d-back documentation is available in multiple languages (English, Spanish, German). We use Crowdin to manage translations collaboratively. English is the source language — make changes to English files first. Translations are synchronized using Crowdin and GitHub Actions. The project uses `mkdocs-static-i18n` with the suffix structure (e.g., `index.es.md`, `index.de.md`).

### Crowdin Project Setup

1. Create a Crowdin project at https://crowdin.com and select **Markdown** as the file type.
2. Set English as the source language and add Spanish (`es`) and German (`de`) as target languages.
3. Install the Crowdin GitHub App on the repository, or configure Crowdin CLI with GitHub Actions. The repository root `crowdin.yml` defines file patterns and parser options used by Crowdin.

Required GitHub secrets (Repository → Settings → Secrets and variables → Actions):

- `CROWDIN_PROJECT_ID` — Crowdin project ID
- `CROWDIN_PERSONAL_TOKEN` — Crowdin personal access token

### Translation Workflow

1. Edit English source files (for example: `docs/index.md`, `docs/getting-started.md`) and submit a pull request.
2. After the PR is merged into `main`, Crowdin will detect changed strings and notify translators.
3. Translators translate content in the Crowdin editor. Crowdin preserves code blocks, inline code, and markdown formatting.
4. Translations are synced back to the repository via Crowdin GitHub integration or through GitHub Actions. Crowdin will create PRs with translation updates for maintainers to review and merge.

### File Structure and Naming

- English (source): `docs/index.md`, `docs/getting-started.md`, `docs/user-guide/configuration.md`
- Spanish: `docs/index.es.md`, `docs/getting-started.es.md`, `docs/user-guide/configuration.es.md`
- German: `docs/index.de.md`, `docs/getting-started.de.md`, `docs/user-guide/configuration.de.md`

This suffix-based convention matches `mkdocs-static-i18n` configuration in `mkdocs.yml`.

### What Gets Translated

Translated content includes:

- Explanatory text, section headings, and titles
- User-facing messages and instructions
- Non-code examples' descriptions

Not translated:

- Code blocks and inline code
- Function and class names
- File paths and URLs
- Configuration keys and values
- Project names and technical terms (e.g., d-back, d-zone, WebSocket, OAuth2)

### Excluded Files

The following files are intentionally excluded from Crowdin translation:

- `docs/VERCEL_SETUP.md` (internal Vercel deployment docs)
- `docs/TESTING_I18N.md` (internal i18n testing docs)
- `docs/.pages` (navigation configuration)
- API reference files (auto-generated by `mkdocstrings`)

### Testing Translations Locally

```bash
# Install documentation dependencies
pip install -e .[docs]

# Serve documentation locally with all languages
mkdocs serve

# Build documentation (generates site/ directory with all languages)
mkdocs build
```

Check specific language previews:

- English: `http://127.0.0.1:8000/`
- Spanish: `http://127.0.0.1:8000/es/`
- German: `http://127.0.0.1:8000/de/`

### Translation Best Practices

- Use a formal tone for user-facing content (Spanish: "usted", German: "Sie").
- Keep technical terms and project names in English.
- Preserve markdown formatting, code blocks, and inline code.
- Test translations locally before submitting them.

### Adding New Languages

To add a new language:

1. Update `mkdocs.yml` i18n configuration to include the new language.
2. Update `crowdin.yml` with the new `two_letters_code`.
3. Add the language in the Crowdin project settings.
4. Create initial translation files following the suffix pattern.
5. Update this section with the new language details.

### Troubleshooting

Common issues:

- Translations not appearing in Crowdin: ensure file patterns in `crowdin.yml` match committed files and they are not listed in `ignore`.
- Translations not syncing to GitHub: check GitHub Actions logs and verify `CROWDIN_PROJECT_ID` and `CROWDIN_PERSONAL_TOKEN` are set.
- Broken formatting: review translations in Crowdin editor and verify code blocks are preserved.

### Resources

- Crowdin documentation: https://support.crowdin.com/
- mkdocs-static-i18n: https://github.com/ultrabug/mkdocs-static-i18n
- Material for MkDocs i18n: https://squidfunk.github.io/mkdocs-material/setup/changing-the-language/


### Pull Request Process

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/my-awesome-feature
   ```

2. **Make your changes**:
   - Write code
   - Add tests
   - Update documentation

3. **Ensure tests pass**:
   ```bash
   pytest
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add awesome feature"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/my-awesome-feature
   ```

6. **Create Pull Request** on GitHub:
   - Provide clear description
   - Link related issues
   - Explain motivation and changes

7. **Respond to review feedback**:
   - Address comments
   - Push additional commits
   - Request re-review

### Commit Message Format

Use conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Maintenance tasks

**Examples**:
```
feat: add OAuth2 token validation callback

Implement on_validate_discord_user callback to support
Discord OAuth2 authentication flow.

Closes #123
```

```
fix: handle connection errors gracefully

Add try-except block to prevent server crash when
client disconnects unexpectedly.
```

```
docs: update API reference with examples

Add comprehensive examples to WebSocketServer methods
in API documentation.
```

## Development Workflow

### Day-to-Day Development

1. **Sync with upstream**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Create feature branch**:
   ```bash
   git checkout -b feature/my-feature
   ```

3. **Make changes and test**:
   ```bash
   # Edit files
   pytest
   mkdocs serve  # If updating docs
   ```

4. **Commit and push**:
   ```bash
   git add .
   git commit -m "feat: add my feature"
   git push origin feature/my-feature
   ```

5. **Create Pull Request** on GitHub

### Debugging

#### Enable Verbose Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Use Python Debugger

```python
import pdb

async def my_function():
    # Set breakpoint
    pdb.set_trace()
    # Code here
```

#### Test with Mock Client

```python
from tests.helpers.mock_websocket_client import MockWebSocketClient

async def test_manually():
    client = MockWebSocketClient("ws://localhost:3000")
    await client.connect()
    await client.send_message({"type": "get_user_data", "serverId": "123"})
    response = await client.receive_message()
    print(response)
```

#### Check Browser Console

When testing frontend integration, open browser DevTools and check:
- Console for errors
- Network tab for WebSocket messages
- Application tab for connection status

#### WebSocket Inspection Tools

Use tools like:
- **Chrome DevTools**: Network → WS tab
- **Postman**: WebSocket request feature
- **wscat**: Command-line WebSocket client

## Release Process

### Version Numbering

d-back follows [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes

### Version Location

Version is defined in `setup.cfg`:

```ini
[metadata]
name = d_back
version = 0.0.14
```

### Creating a Release

1. **Update version** in `setup.cfg`
2. **Update CHANGELOG.md** with release notes
3. **Commit changes**:
   ```bash
   git commit -am "chore: bump version to 0.0.15"
   ```
4. **Create git tag**:
   ```bash
   git tag v0.0.15
   git push origin v0.0.15
   ```
5. **GitHub Actions** automatically builds and publishes to PyPI

### Documentation Versioning

d-back uses mike for documentation versioning, which integrates seamlessly with Material for MkDocs to provide a version selector in the documentation. The versioning strategy uses three types of versions:

- **Stable versions**: Created from git tags (e.g., 0.0.14, 0.1.0, 1.0.0)
- **Prerelease 'latest'**: Tracks the main branch (production-ready but not yet tagged)
- **Prerelease 'dev'**: Tracks the develop branch (development/testing)

The version selector appears in the top navigation bar, allowing users to switch between different documentation versions.

#### Versioning Strategy

**1. Stable Versions (from tags)**

Created when a new version is tagged:

- Version number matches the git tag without the 'v' prefix
- These versions are permanent and immutable
- Example: Tag v0.0.15 creates documentation version 0.0.15
- Command: `mike deploy 0.0.15 --push`

**2. Latest Prerelease (main branch)**

Represents the current state of the main branch:

- Alias: 'latest'
- Updated on every push to main
- This is the default version users see
- Command: `mike deploy <commit-sha> latest --push --update-aliases`

**3. Dev Prerelease (develop branch)**

Represents the current state of the develop branch:

- Alias: 'dev'
- Updated on every push to develop
- Used for testing documentation changes before release
- Command: `mike deploy <commit-sha> dev --push --update-aliases`

#### Local Testing

Test mike locally before deploying:

```bash
# Install documentation dependencies (includes mike)
pip install -e .[docs]

# Deploy a test version locally (doesn't push to remote)
mike deploy 0.0.14-test

# Deploy with an alias
mike deploy 0.0.15-test latest --update-aliases

# Set the default version (what users see when visiting the docs)
mike set-default latest

# List all deployed versions
mike list

# Serve the versioned documentation locally
mike serve
# Visit http://localhost:8000 to test
# Use the version selector in the top navigation to switch between versions

# Delete a test version
mike delete 0.0.14-test
```

**Important notes for local testing:**

- Mike creates a `gh-pages` branch locally to store versioned documentation
- Use test version names (e.g., 0.0.14-test) to avoid conflicts with production versions
- The `--push` flag is omitted during local testing to prevent accidental deployment
- Always test the version selector functionality before deploying
- Verify that all three languages (English, Spanish, German) work correctly in each version

#### Version Aliases

Aliases are symbolic names that point to specific versions:

- Common aliases: 'latest' (main branch), 'dev' (develop branch), 'stable' (latest stable release)
- Aliases can be updated to point to different versions
- Example: After releasing 0.1.0, update 'stable' alias: `mike deploy 0.1.0 stable --update-aliases`
- The `--update-aliases` flag updates existing aliases instead of creating duplicates

#### Deployment Workflow

Manual deployment process (GitHub Actions will automate this in a future phase):

**For stable releases:**
```bash
# After creating a git tag (e.g., v0.0.15)
mike deploy 0.0.15 stable --push --update-aliases
mike set-default latest --push
```

**For main branch updates:**
```bash
# After merging to main
mike deploy <commit-sha> latest --push --update-aliases
```

**For develop branch updates:**
```bash
# After merging to develop
mike deploy <commit-sha> dev --push --update-aliases
```

#### Best Practices

- Always test locally with `mike serve` before deploying
- Use semantic versioning for stable releases (MAJOR.MINOR.PATCH)
- Keep 'latest' as the default version for users
- Document breaking changes in version-specific release notes
- Maintain at least the last 3 stable versions for reference
- Delete very old versions to keep the version list manageable: `mike delete 0.0.1 --push`
- Verify multilingual support works in all deployed versions

#### Troubleshooting

**Issue:** Version selector not appearing
- Solution: Verify `extra.version.provider: mike` is set in mkdocs.yml (already configured at line 137)
- Solution: Ensure at least two versions are deployed
- Solution: Check that Material theme is properly configured

**Issue:** Versions not deploying
- Solution: Ensure mike is installed: `pip install -e .[docs]`
- Solution: Check that gh-pages branch exists
- Solution: Verify git remote is configured correctly

**Issue:** Language selector conflicts with version selector
- Solution: Both selectors should work together; verify mkdocs-static-i18n configuration
- Solution: Test with `mike serve` to ensure both selectors appear

**Issue:** Old content appearing in new version
- Solution: Use `mike deploy --update-aliases` to refresh aliases
- Solution: Clear browser cache
- Solution: Rebuild with `mkdocs build --clean` before deploying

#### Resources

- Mike documentation: https://github.com/jimporter/mike
- Material for MkDocs versioning: https://squidfunk.github.io/mkdocs-material/setup/setting-up-versioning/
- Semantic Versioning: https://semver.org/

**Note:** GitHub Actions will automate this process in a future phase, automatically deploying 'dev' on develop branch pushes, 'latest' on main branch pushes, and stable versions on tag creation.

## Future Enhancements

We welcome contributions in these areas:

### Real Discord API Integration

- Discord.py integration examples
- Gateway event forwarding
- Presence tracking improvements
- Voice channel support

### Additional Authentication Methods

- GitHub OAuth
- Google OAuth
- Custom JWT tokens
- API key authentication

### Performance Optimizations

- Connection pooling
- Redis caching layer
- Load balancing support
- Horizontal scaling

### Test Coverage

- Integration tests with Discord API
- Load testing and benchmarks
- Security testing
- Frontend integration tests

### Documentation

- Video tutorials
- Interactive examples
- Additional language translations (Spanish, German, etc.)
- Architecture diagrams

### Plugin System

- Extensibility framework
- Community plugins
- Plugin marketplace

## Getting Help

### Resources

- **GitHub Issues**: [Report bugs](https://github.com/NNTin/d-back/issues)
- **GitHub Discussions**: [Ask questions](https://github.com/NNTin/d-back/discussions)
- **API Reference**: [Complete API docs](api-reference.md)
- **User Guide**: [Usage patterns](user-guide/index.md)

### Contact

- **Repository**: [github.com/NNTin/d-back](https://github.com/NNTin/d-back)
- **Issues**: [github.com/NNTin/d-back/issues](https://github.com/NNTin/d-back/issues)
- **Email**: See GitHub profile

## Thank You!

Thank you for contributing to d-back! Your efforts help make this project better for everyone. We appreciate your time and dedication.

Happy coding! 🚀
