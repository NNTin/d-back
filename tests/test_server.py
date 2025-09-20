import subprocess
import sys
import time
import os

def test_server_and_client_communication():
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
        if not output:
            # Print diagnostic info if output is empty
            server_out, server_err = server_proc.communicate(timeout=2)
            print("SERVER STDOUT:\n", server_out)
            print("SERVER STDERR:\n", server_err)
            print("CLIENT STDERR:\n", client_stderr)
        assert "Connected to ws://localhost:3000" in output
        assert "[RECV]" in output  # Should receive at least one message
        assert "[SEND]" in output  # Should send a connect message
    finally:
        server_proc.terminate()
        client_proc.terminate()

# To run: pytest tests/test_server.py
