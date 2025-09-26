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

3. **`helpers/mock_websocket_client.py`** - Mock client for testing

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
```

Run with coverage:
```bash
pytest tests/ --cov=d_back --cov-report=html
```

### Option 2: Simple test runner (No dependencies)

For environments without pytest, use the simple test runner:
```bash
python run_tests_simple.py
```

This runner:
- Doesn't require external dependencies beyond what's already needed for d_back
- Gracefully handles missing optional packages (aiohttp, websockets)
- Provides basic test functionality verification
- Works with the existing mock client

### Option 3: Manual testing

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