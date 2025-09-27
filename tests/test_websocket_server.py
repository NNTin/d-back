import subprocess
import sys
import time
import os

try:
    import allure
    ALLURE_AVAILABLE = True
except ImportError:
    ALLURE_AVAILABLE = False


def get_websockets_version():
    """Get websockets version from environment or actual package."""
    # First try environment variable set by tox
    env_version = os.environ.get('WEBSOCKETS_VERSION')
    if env_version:
        return env_version
    
    # Fallback to checking actual installed version
    try:
        import websockets
        return websockets.version
    except ImportError:
        return "unknown"


def get_python_version():
    """Get Python version from environment or sys.version_info."""
    # First try environment variable set by tox
    env_version = os.environ.get('PYTHON_VERSION')
    if env_version:
        return env_version
    
    # Fallback to actual Python version
    import sys
    return f"{sys.version_info.major}.{sys.version_info.minor}"


def get_test_env_name():
    """Get test environment name from tox."""
    return os.environ.get('TEST_ENV_NAME', 'unknown')


def setup_allure_test_info():
    """Setup allure test information with environment details."""
    if not ALLURE_AVAILABLE:
        return
    
    websockets_version = get_websockets_version()
    python_version = get_python_version()
    test_env = get_test_env_name()
    
    allure.dynamic.parameter("websockets_version", websockets_version)
    allure.dynamic.parameter("python_version", python_version)
    allure.dynamic.parameter("test_environment", test_env)
    allure.attach(f"Testing with Python {python_version}, websockets {websockets_version} in environment {test_env}", 
                 "Test Configuration", allure.attachment_type.TEXT)


def _apply_allure_decorators(func):
    """Apply allure decorators if available."""
    if ALLURE_AVAILABLE:
        func = allure.feature("WebSocket Server")(func)
        func = allure.story("Server-Client Communication")(func)
        func = allure.title("Test WebSocket server and client communication")(func)
    return func


@_apply_allure_decorators
def test_server_and_client_communication():
    setup_allure_test_info()
    
    # Start the server using module execution
    server_proc = subprocess.Popen(
        [sys.executable, "-m", "d_back"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1  # line buffered
    )
    time.sleep(1)  # Give server more time to start

    # Start the client and capture output
    client_proc = subprocess.Popen(
        [sys.executable, os.path.join("helpers", "mock_websocket_client.py")],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.path.dirname(__file__),  # Ensure working directory is tests/
        text=True
    )
    try:
        client_stdout, client_stderr = client_proc.communicate(timeout=10)
        output = client_stdout
        
        if ALLURE_AVAILABLE:
            allure.attach(output, "Client Output", allure.attachment_type.TEXT)
            if client_stderr:
                allure.attach(client_stderr, "Client Errors", allure.attachment_type.TEXT)
        
        if not output:
            # Print diagnostic info if output is empty
            server_out, server_err = server_proc.communicate(timeout=2)
            print("SERVER STDOUT:\n", server_out)
            print("SERVER STDERR:\n", server_err)
            print("CLIENT STDERR:\n", client_stderr)
            
            if ALLURE_AVAILABLE:
                allure.attach(server_out, "Server Output", allure.attachment_type.TEXT)
                allure.attach(server_err, "Server Errors", allure.attachment_type.TEXT)
        
        assert "Connected to ws://localhost:3000" in output
        assert "[RECV]" in output  # Should receive at least one message
        assert "[SEND]" in output  # Should send a connect message
    finally:
        server_proc.terminate()
        client_proc.terminate()

# To run: pytest tests/test_server.py