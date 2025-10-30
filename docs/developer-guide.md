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

#### Setting Up GitHub Secrets

Create the required secrets for Crowdin integration:

1. **Obtain Crowdin Credentials:**
   - **Project ID:** 
     - Log in to Crowdin
     - Navigate to your project
     - Go to Settings → API
     - Copy the Project ID (numeric value)
   - **Personal Access Token:**
     - Go to Account Settings → API
     - Click "New Token"
     - Name: "d-back GitHub Actions"
     - Scopes: Select "Projects" (read/write)
     - Click "Create"
     - Copy the token immediately (it won't be shown again)

2. **Add Secrets to GitHub Repository:**
   - Navigate to: Repository → Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Add `CROWDIN_PROJECT_ID`:
     - Name: `CROWDIN_PROJECT_ID`
     - Value: Your Crowdin project ID (numeric)
     - Click "Add secret"
   - Add `CROWDIN_PERSONAL_TOKEN`:
     - Name: `CROWDIN_PERSONAL_TOKEN`
     - Value: Your Crowdin personal access token
     - Click "Add secret"

3. **Verify Secrets:**
   - Secrets should appear in the repository secrets list
   - Secret values are hidden and cannot be viewed after creation
   - Only repository administrators can manage secrets

**Important Security Notes:**
- Never commit tokens or project IDs to the repository
- Tokens have full access to your Crowdin project - keep them secure
- Rotate tokens periodically for security
- Use repository secrets, not environment secrets (for repository-specific access)

#### GitHub Actions Workflow

**Overview:**

The Crowdin synchronization is automated via GitHub Actions. The workflow is defined in `.github/workflows/crowdin.yml` and handles:
- Uploading English source files to Crowdin when documentation is updated
- Downloading translations and creating pull requests for review

**Workflow Triggers:**

1. **Automatic Upload (Push to main):**
   - Triggers when documentation files are pushed to the main branch
   - Uploads new/changed English source files to Crowdin
   - Translators are notified of new content to translate
   - Runs automatically - no manual intervention needed

2. **Manual Download (workflow_dispatch):**
   - Triggered manually from GitHub Actions UI
   - Downloads completed translations from Crowdin
   - Creates a pull request with translation updates
   - Allows review before merging translations

**How It Works:**

1. **Source Upload Process:**
   - Developer merges documentation changes to main branch
   - GitHub Actions detects changes in `docs/**/*.md` files
   - Workflow uploads changed English files to Crowdin
   - Crowdin analyzes changes and notifies translators
   - Translators see new/modified strings in Crowdin editor

2. **Translation Download Process:**
   - Maintainer manually triggers the workflow from GitHub Actions UI
   - Workflow downloads completed translations from Crowdin
   - Creates a new branch: `crowdin-translations`
   - Creates a pull request with title: "docs: update translations from Crowdin"
   - PR includes labels: documentation, translations, crowdin
   - Maintainer reviews and merges the PR

**Testing the Workflow:**

1. **Test Source Upload:**
   - Make a small change to an English documentation file (e.g., add a sentence to `docs/index.md`)
   - Commit and push to main branch
   - Navigate to: Repository → Actions → Crowdin Sync workflow
   - Verify the workflow runs successfully
   - Check Crowdin project to confirm the new content appears

2. **Test Translation Download:**
   - Ensure some translations are completed in Crowdin
   - Navigate to: Repository → Actions → Crowdin Sync workflow
   - Click "Run workflow" button
   - Select "main" branch
   - Click "Run workflow"
   - Wait for workflow to complete
   - Check Pull Requests tab for new PR from Crowdin
   - Review the PR and merge if translations look correct

**Monitoring Workflow:**

- **View workflow runs:** Repository → Actions → Crowdin Sync
- **Check workflow status:** See status badge (can be added to README)
- **Workflow logs:** Click on any workflow run to see detailed logs
- **Failed workflows:** Error messages appear in logs with troubleshooting info

**Troubleshooting Workflow Issues:**

**Issue:** Workflow fails with "Authentication failed"
- **Solution:** Verify `CROWDIN_PROJECT_ID` and `CROWDIN_PERSONAL_TOKEN` secrets are set correctly
- **Solution:** Check that the personal access token has "Projects" scope enabled
- **Solution:** Ensure the token hasn't expired (tokens don't expire by default, but can be revoked)

**Issue:** Workflow runs but no files uploaded to Crowdin
- **Solution:** Check that changed files match the patterns in `crowdin.yml` (`/docs/**/*.md`)
- **Solution:** Verify files are not in the ignore list in `crowdin.yml`
- **Solution:** Check workflow logs for file detection messages

**Issue:** Translation PR not created
- **Solution:** Ensure workflow was triggered via workflow_dispatch (manual trigger)
- **Solution:** Verify there are completed translations in Crowdin to download
- **Solution:** Check that GitHub Actions has write permissions for pull requests
- **Solution:** Review workflow logs for PR creation errors

**Issue:** PR created but translations missing
- **Solution:** Verify translations are marked as "approved" in Crowdin (if approval workflow is enabled)
- **Solution:** Check that translation files match the pattern in `crowdin.yml`
- **Solution:** Ensure translators completed translations for all languages (Spanish and German)

**Localization Branch:**

The workflow creates a branch named `crowdin-translations` for translation updates:
- This branch is automatically created/updated by the workflow
- Each translation download overwrites this branch with latest translations
- The branch is used as the source for the pull request
- After merging the PR, the branch can be deleted (GitHub offers this option)
- The workflow will recreate the branch on the next translation download

**Best Practices:**
- Run translation downloads periodically (e.g., weekly) to keep translations up-to-date
- Review translation PRs carefully before merging
- Test the documentation build locally after merging translations
- Coordinate with translators about translation deadlines
- Use Crowdin's approval workflow for quality control (optional)

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

Manual deployment process (for local testing or when needed):

**For stable releases:**
```bash
# After creating a git tag (e.g., v0.0.15)
mike deploy 0.0.15 stable --push --update-aliases
mike set-default stable --push
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

**Note:** These commands are for manual deployment. Automated deployment via GitHub Actions is the recommended approach for production (see "Automated Deployment with GitHub Actions" below).

#### Automated Deployment with GitHub Actions

Documentation deployment is automated via GitHub Actions. The workflow is defined in `.github/workflows/docs.yml` and handles all production deployments.

**Overview:**

- Documentation deploys automatically on pushes to main, develop, and tag creation
- The workflow manages versioning with mike and deploys to GitHub Pages
- Manual deployment using mike locally is still available for testing
- All three languages (English, Spanish, German) are built and deployed together

**Automatic Triggers:**

1. **Tag creation (v*)**: Creates a stable version
   - Example: Tag `v0.0.15` deploys version `0.0.15` with alias `stable`
   - Stable versions are permanent and immutable
   - Set as the default version users see
   - Command executed: `mike deploy 0.0.15 stable --push --update-aliases`
   - Command executed: `mike set-default stable --push`

2. **Push to main**: Deploys 'latest' prerelease
   - Represents the current production-ready state
   - Not set as default (stable releases remain the default)
   - Uses stable version identifier 'edge'
   - Command executed: `mike deploy edge latest --push --update-aliases`

3. **Push to develop**: Deploys 'dev' prerelease
   - Represents the current development state
   - Used for testing documentation changes before release
   - Not set as default (dev is for testing only)
   - Uses stable version identifier 'development'
   - Command executed: `mike deploy development dev --push --update-aliases`

4. **Manual trigger**: Available via `workflow_dispatch` in GitHub Actions UI
   - Useful for testing or re-deploying documentation
   - Access via: Repository → Actions tab → Documentation workflow → Run workflow

**Workflow Process:**

1. **Checkout repository**: Fetches full git history (required for mike to access gh-pages branch)
2. **Set up Python 3.11**: Installs Python with pip caching for faster builds
3. **Install dependencies**: Runs `pip install -e .[docs]` to install mkdocs-material, mkdocs-static-i18n, mkdocstrings, and mike from setup.cfg
4. **Configure git**: Sets up git user for automated commits to gh-pages branch
5. **Determine version**: Analyzes the trigger type (tag, main, or develop) to decide deployment strategy
6. **Deploy with mike**: Executes appropriate mike command to deploy versioned documentation to gh-pages branch
7. **GitHub Pages serves updated documentation**: Changes appear within 1-2 minutes at https://nntin.github.io/d-back/

**Version Strategy:**

- **Stable versions** (from tags): Permanent, immutable, represent official releases; always set as default
- **'latest' alias**: Updated on every main branch push; available in version selector but not set as default
- **'dev' alias**: Updated on every develop branch push, for testing only (never set as default)
- The version selector in documentation navigation shows all available versions

**Monitoring Deployments:**

- **View workflow runs**: Repository → Actions tab → Documentation workflow
- **Check deployment status**: See the Documentation Status badge in README.md
- **Workflow logs**: Detailed deployment information available in each workflow run
- **Failed deployments**: Error messages appear in workflow logs with troubleshooting information

**GitHub Pages Configuration:**

First-time setup (only needed once):

1. Go to: Repository Settings → Pages
2. Set Source: Deploy from a branch
3. Set Branch: `gh-pages` (created automatically by first workflow run)
4. Click Save
5. Documentation will be available at: https://nntin.github.io/d-back/
6. Changes appear within 1-2 minutes after workflow completion

**Manual Deployment (if needed):**

The automated workflow handles most deployment scenarios. Manual deployment may be needed for:

- Testing documentation changes locally before pushing
- Fixing deployment issues that require local troubleshooting
- Deploying from a local branch for testing purposes

Use the mike commands documented in the "Deployment Workflow" subsection above for manual deployment.

**Troubleshooting Workflow Issues:**

**Issue:** Workflow fails on git push to gh-pages
- **Solution**: Check that Actions have write permissions
  - Go to: Settings → Actions → General → Workflow permissions
  - Select: "Read and write permissions"
  - Click Save

**Issue:** Deployed version not appearing in version selector
- **Solution**: Verify the trigger condition matched the expected branch or tag
- **Solution**: Check workflow logs to confirm deployment completed successfully
- **Solution**: Ensure at least two versions are deployed for selector to appear

**Issue:** Old content appearing in newly deployed version
- **Solution**: Clear browser cache and reload
- **Solution**: Check that workflow completed successfully in Actions tab
- **Solution**: Verify the correct version was deployed by checking workflow logs

**Issue:** gh-pages branch not created
- **Solution**: Check workflow logs for errors during first deployment
- **Solution**: Verify Actions have write permissions (see first issue above)
- **Solution**: Manually trigger workflow via workflow_dispatch to retry

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

**Note:** Documentation deployment is fully automated via GitHub Actions. See the "Automated Deployment with GitHub Actions" section above for details on how the workflow deploys documentation on branch pushes and tag creation.

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
