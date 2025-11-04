# D-Back Tests

This directory contains comprehensive tests for the d_back WebSocket server, covering both HTTP and WebSocket functionality.

## Test Files

1. **`test_http_server.py`** - Tests HTTP functionality including:
   - Root page serving
   - `/api/version` endpoint validation
   - 404 error handling
   - Multiple concurrent requests
   - HTTP/WebSocket coexistence

2. **`test_websocket_server.py`** - Tests WebSocket functionality including:
   - Basic connection establishment
   - Server-list message format
   - Server connection/joining
   - Multiple client connections
   - Message format validation
   - Invalid message handling
   - Binary message support

3. **`test_browser_integration.py`** - Tests browser integration functionality

4. **`test_installation.py`** - Tests installation and packaging workflow including:
   - Development installation with `uv sync`
   - Dependency group installation (test, dev, docs)
   - Package building with `uv build`
   - Wheel installation with `uv pip install`
   - CLI entry point functionality
   - Production installation scenario
   - Package metadata verification
   - Reinstallation and upgrade scenarios

5. **`helpers/mock_websocket_client.py`** - Mock client for testing

## Running Tests

### Option 1: With pytest (Recommended)

Install test dependencies:
```bash
pip install -r test-requirements.txt
```

Run all tests:
```bash
pytest tests/
```

Run specific test file:
```bash
pytest tests/test_http_server.py -v
pytest tests/test_websocket_server.py -v
pytest tests/test_installation.py -v
```

Run only installation tests:
```bash
pytest -m installation
```

Run all tests except installation tests:
```bash
pytest -m "not installation"
```

Run with coverage:
```bash
pytest tests/ --cov=d_back --cov-report=html
```

### Option 2: Installation Tests (Standalone)

The installation tests can be run independently to validate the uv-based installation workflow:

```bash
python tests/test_installation.py
```

These tests validate:
- Development installation with `uv sync`
- Dependency group installation (test, dev, docs)
- Package building with `uv build`
- Wheel installation with `uv pip install`
- CLI entry point functionality
- Production installation scenario
- Package metadata verification
- Reinstallation and upgrade scenarios

**Requirements**: `uv` must be installed and available in PATH.

**Isolation**: These tests run in isolated temporary directories and virtual environments, so they don't affect the development environment.

**Duration**: Installation tests are slower than functional tests (marked with `@pytest.mark.slow`) due to building and installing packages.

### Option 3: Simple test runner (No dependencies)

For environments without pytest, use the simple test runner:
```bash
python run_tests_simple.py
```

This runner:
- Doesn't require external dependencies beyond what's already needed for d_back
- Gracefully handles missing optional packages (aiohttp, websockets)
- Provides basic test functionality verification
- Works with the existing mock client

### Option 4: Manual testing

Start the server:
```bash
python -m d_back
```

In another terminal:
```bash
cd tests
python helpers/mock_websocket_client.py
```

Check HTTP endpoints in browser:
- http://localhost:3000/ - Main page
- http://localhost:3000/api/version - Version API

## Test Types

The test suite is organized into two main categories:

### Functional Tests
- **`test_websocket_server.py`**: Tests runtime WebSocket behavior
- **`test_browser_integration.py`**: Tests browser integration functionality
- **Purpose**: Validate that the application works correctly during runtime
- **Speed**: Fast (typically under 10 seconds)
- **Environment**: Uses the current development environment

### Installation Tests
- **`test_installation.py`**: Tests installation and packaging workflow
- **Purpose**: Validate that the package can be built and installed correctly
- **Speed**: Slower (marked with `@pytest.mark.slow`) due to building and installing packages
- **Environment**: Uses isolated temporary directories and virtual environments
- **CI Integration**: Should be run in CI to verify package can be built and installed before publishing

## Test Configuration

The tests are configured via `pyproject.toml` with settings for:
- Async test support
- Verbose output
- Test discovery patterns
- Logging configuration

## Requirements

### Core requirements (for d_back):
- Python 3.8+
- websockets

### Test requirements (optional):
- pytest >= 7.0.0
- pytest-asyncio >= 0.21.0
- aiohttp >= 3.8.0
- packaging >= 21.0

### Installation test requirements:
- uv (must be available in PATH)
- All dependencies are handled by uv during testing

## Test Coverage

The tests cover:

### HTTP Server:
- ✅ Static file serving
- ✅ JSON API endpoints
- ✅ Error handling (404s)
- ✅ Concurrent request handling
- ✅ Content-Type headers
- ✅ Version endpoint validation

### WebSocket Server:
- ✅ Connection establishment
- ✅ Initial server-list message
- ✅ Server joining workflow
- ✅ Multiple client support
- ✅ JSON message validation
- ✅ Binary message handling
- ✅ Invalid input handling
- ✅ Connection persistence

### Integration:
- ✅ HTTP and WebSocket on same port
- ✅ Existing mock client compatibility
- ✅ Server startup/shutdown

### Installation & Packaging:
- ✅ Development installation (`uv sync`)
- ✅ Dependency group installation (test, dev, docs)
- ✅ Package building (`uv build`)
- ✅ Wheel installation (`uv pip install`)
- ✅ CLI entry point functionality
- ✅ Production installation scenario
- ✅ Package metadata verification
- ✅ Reinstallation and upgrade workflows

## Debugging Failed Tests

If tests fail:

1. Check server startup logs
2. Verify port 3000 is available
3. Ensure dependencies are installed
4. Try the simple test runner for basic functionality
5. Run individual test methods for isolation

Example debug command:
```bash
pytest tests/test_http_server.py::TestHTTPServer::test_api_version_endpoint -v -s
```