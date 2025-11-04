"""
Comprehensive installation test suite for d_back package.

This module validates the complete uv-based installation workflow including:
- Development installation via `uv sync`
- Production build via `uv build`
- Wheel installation via `uv pip install`
- CLI entry point functionality
- Package metadata and version correctness

Tests are designed to be independent from pytest-based functional tests and
can be run standalone or through pytest.
"""

import subprocess
import sys
import os
import tempfile
import shutil
import json
import time
import zipfile
from pathlib import Path
from typing import Tuple, Optional

import pytest

# Conditional allure import (following pattern from test_websocket_server.py)
try:
    import allure
    ALLURE_AVAILABLE = True
except ImportError:
    ALLURE_AVAILABLE = False

# Module-level constants
PROJECT_ROOT = None
EXPECTED_VERSION = None


def get_project_root() -> Path:
    """Return the absolute path to the project root directory (parent of tests directory)."""
    global PROJECT_ROOT
    if PROJECT_ROOT is None:
        PROJECT_ROOT = Path(__file__).parent.parent.resolve()
    return PROJECT_ROOT


def get_expected_version() -> str:
    """Read and return the version from d_back/__init__.py by parsing the __version__ variable."""
    global EXPECTED_VERSION
    if EXPECTED_VERSION is None:
        init_file = get_project_root() / "d_back" / "__init__.py"
        with open(init_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Parse __version__ = "x.y.z" line
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("__version__") and "=" in line:
                # Extract version from __version__ = "0.0.18" format
                version_part = line.split("=", 1)[1].strip()
                EXPECTED_VERSION = version_part.strip('"\'')
                break
        
        if EXPECTED_VERSION is None:
            raise RuntimeError("Could not find __version__ in d_back/__init__.py")
    
    return EXPECTED_VERSION


def run_command(cmd: list, cwd: str, timeout: int = 300) -> Tuple[int, str, str]:
    """
    Execute a command using subprocess.run() with timeout.
    
    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    try:
        print(f"Running command: {' '.join(cmd)} in {cwd}")
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )
        
        stdout = result.stdout.strip() if result.stdout else ""
        stderr = result.stderr.strip() if result.stderr else ""
        
        print(f"Command exit code: {result.returncode}")
        if stdout:
            print(f"STDOUT:\n{stdout}")
        if stderr:
            print(f"STDERR:\n{stderr}")
            
        return result.returncode, stdout, stderr
        
    except subprocess.TimeoutExpired as e:
        print(f"Command timed out after {timeout} seconds: {' '.join(cmd)}")
        return -1, "", f"Command timed out after {timeout} seconds"
    except Exception as e:
        print(f"Error running command {' '.join(cmd)}: {e}")
        return -1, "", str(e)


def create_temp_venv(base_dir: Path) -> Path:
    """Create a temporary virtual environment using uv venv in the specified directory."""
    venv_path = base_dir / "test_venv"
    returncode, stdout, stderr = run_command(
        ["uv", "venv", str(venv_path)],
        cwd=str(base_dir)
    )
    
    if returncode != 0:
        raise RuntimeError(f"Failed to create venv: {stderr}")
    
    return venv_path


def get_venv_python(venv_path: Path) -> str:
    """Return the path to the Python executable in the virtual environment."""
    if sys.platform == "win32":
        return str(venv_path / "Scripts" / "python.exe")
    else:
        return str(venv_path / "bin" / "python")


def get_venv_bin_dir(venv_path: Path) -> Path:
    """Return the bin/Scripts directory path (handle Windows vs Unix)."""
    if sys.platform == "win32":
        return venv_path / "Scripts"
    else:
        return venv_path / "bin"


def setup_allure_installation_info(test_name: str):
    """If allure is available, attach test configuration information."""
    if ALLURE_AVAILABLE:
        allure.attach(
            f"Test: {test_name}\nPython: {sys.version}\nPlatform: {sys.platform}",
            name="Test Configuration",
            attachment_type=allure.attachment_type.TEXT
        )


class TestUvInstallation:
    """Test class for uv-based installation workflows."""
    
    @pytest.fixture(scope="class")
    def temp_install_dir(self):
        """Create a temporary directory for installation tests."""
        temp_dir = Path(tempfile.mkdtemp(prefix="d_back_install_test_"))
        yield temp_dir
        # Cleanup
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            print(f"Warning: Failed to cleanup temp directory {temp_dir}: {e}")
    
    @pytest.fixture(scope="class")
    def project_root(self):
        """Return the project root path for use in tests."""
        return get_project_root()
    
    @pytest.mark.slow
    @pytest.mark.installation
    @pytest.mark.timeout(600)
    def test_uv_sync_development_installation(self, temp_install_dir, project_root):
        """Verify that uv sync correctly installs all dependencies for development."""
        setup_allure_installation_info("test_uv_sync_development_installation")
        
        # Copy project files to temp directory (excluding .venv, __pycache__, .git)
        project_copy = temp_install_dir / "project"
        project_copy.mkdir()
        
        for item in project_root.iterdir():
            if item.name in {".venv", "__pycache__", ".git", ".pytest_cache", "dist", "build"}:
                continue
            if item.is_file():
                shutil.copy2(item, project_copy)
            elif item.is_dir():
                shutil.copytree(item, project_copy / item.name, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        
        # Run uv sync
        returncode, stdout, stderr = run_command(
            ["uv", "sync"],
            cwd=str(project_copy)
        )
        
        assert returncode == 0, f"uv sync failed: {stderr}"
        
        if ALLURE_AVAILABLE:
            allure.attach(stdout, name="uv sync output", attachment_type=allure.attachment_type.TEXT)
        
        # Check that uv.lock exists
        assert (project_copy / "uv.lock").exists(), "uv.lock not found after sync"
        
        # Verify package is importable and version is correct
        returncode, stdout, stderr = run_command(
            ["uv", "run", "python", "-c", "import d_back; print(d_back.__version__)"],
            cwd=str(project_copy)
        )
        
        assert returncode == 0, f"Failed to import d_back: {stderr}"
        version_output = stdout.strip()
        expected_version = get_expected_version()
        assert version_output == expected_version, f"Version mismatch: got {version_output}, expected {expected_version}"
        
        # Verify runtime dependencies installed
        returncode, stdout, stderr = run_command(
            ["uv", "run", "python", "-c", "import websockets; print(websockets.__version__)"],
            cwd=str(project_copy)
        )
        
        assert returncode == 0, f"Failed to import websockets: {stderr}"
        
        # Verify test dependencies installed
        returncode, stdout, stderr = run_command(
            ["uv", "run", "python", "-c", "import pytest; print(pytest.__version__)"],
            cwd=str(project_copy)
        )
        
        assert returncode == 0, f"Failed to import pytest: {stderr}"
        
        if ALLURE_AVAILABLE:
            allure.attach(f"d_back version: {version_output}\nwebsockets available: ✓\npytest available: ✓", 
                         name="Dependency verification", attachment_type=allure.attachment_type.TEXT)
    
    @pytest.mark.slow
    @pytest.mark.installation
    @pytest.mark.timeout(600)
    def test_uv_sync_with_dependency_groups(self, temp_install_dir, project_root):
        """Verify that dependency groups (test, dev, docs) are correctly installed."""
        setup_allure_installation_info("test_uv_sync_with_dependency_groups")
        
        # Copy project files
        project_copy = temp_install_dir / "project_groups"
        project_copy.mkdir()
        
        for item in project_root.iterdir():
            if item.name in {".venv", "__pycache__", ".git", ".pytest_cache", "dist", "build"}:
                continue
            if item.is_file():
                shutil.copy2(item, project_copy)
            elif item.is_dir():
                shutil.copytree(item, project_copy / item.name, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        
        # Test test dependencies
        returncode, stdout, stderr = run_command(
            ["uv", "sync", "--group", "test"],
            cwd=str(project_copy)
        )
        
        assert returncode == 0, f"uv sync --group test failed: {stderr}"
        
        # Verify test dependencies are available
        test_deps = ["pytest", "pytest-asyncio", "allure-pytest", "selenium"]
        for dep in test_deps:
            returncode, stdout, stderr = run_command(
                ["uv", "run", "python", "-c", f"import {dep.replace('-', '_')}; print('{dep} OK')"],
                cwd=str(project_copy)
            )
            assert returncode == 0, f"Failed to import {dep}: {stderr}"
        
        # Test docs dependencies
        returncode, stdout, stderr = run_command(
            ["uv", "sync", "--group", "docs"],
            cwd=str(project_copy)
        )
        
        assert returncode == 0, f"uv sync --group docs failed: {stderr}"
        
        # Verify docs dependencies are available
        docs_deps = ["mkdocs", "mkdocs_material"]
        for dep in docs_deps:
            returncode, stdout, stderr = run_command(
                ["uv", "run", "python", "-c", f"import {dep}; print('{dep} OK')"],
                cwd=str(project_copy)
            )
            assert returncode == 0, f"Failed to import {dep}: {stderr}"
        
        # Test all groups
        returncode, stdout, stderr = run_command(
            ["uv", "sync", "--all-groups"],
            cwd=str(project_copy)
        )
        
        if returncode == 0:  # Only test if --all-groups is supported
            # Verify all dependencies from all groups are available
            all_deps = test_deps + docs_deps
            for dep in all_deps:
                dep_import = dep.replace('-', '_')
                returncode, stdout, stderr = run_command(
                    ["uv", "run", "python", "-c", f"import {dep_import}; print('{dep} OK')"],
                    cwd=str(project_copy)
                )
                assert returncode == 0, f"Failed to import {dep} after --all-groups: {stderr}"
        
        if ALLURE_AVAILABLE:
            allure.attach("All dependency groups installed successfully", 
                         name="Dependency groups verification", attachment_type=allure.attachment_type.TEXT)
    
    @pytest.mark.slow
    @pytest.mark.installation
    @pytest.mark.timeout(600)
    def test_uv_build_package(self, temp_install_dir, project_root):
        """Verify that uv build successfully creates wheel and sdist packages."""
        setup_allure_installation_info("test_uv_build_package")
        
        # Copy project files
        project_copy = temp_install_dir / "project_build"
        project_copy.mkdir()
        
        for item in project_root.iterdir():
            if item.name in {".venv", "__pycache__", ".git", ".pytest_cache", "dist", "build"}:
                continue
            if item.is_file():
                shutil.copy2(item, project_copy)
            elif item.is_dir():
                shutil.copytree(item, project_copy / item.name, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        
        # Run uv build
        returncode, stdout, stderr = run_command(
            ["uv", "build"],
            cwd=str(project_copy)
        )
        
        assert returncode == 0, f"uv build failed: {stderr}"
        
        if ALLURE_AVAILABLE:
            allure.attach(stdout, name="uv build output", attachment_type=allure.attachment_type.TEXT)
        
        # Check that dist/ directory is created
        dist_dir = project_copy / "dist"
        assert dist_dir.exists(), "dist/ directory not created"
        
        # Verify wheel file exists
        expected_version = get_expected_version()
        wheel_pattern = f"d_back-{expected_version}-py3-none-any.whl"
        wheel_files = list(dist_dir.glob("d_back-*.whl"))
        assert len(wheel_files) > 0, f"No wheel file found in {dist_dir}"
        
        wheel_file = wheel_files[0]
        
        # Verify sdist file exists
        sdist_pattern = f"d_back-{expected_version}.tar.gz"
        sdist_files = list(dist_dir.glob("d_back-*.tar.gz"))
        assert len(sdist_files) > 0, f"No sdist file found in {dist_dir}"
        
        # Extract wheel metadata
        with zipfile.ZipFile(wheel_file, 'r') as zf:
            metadata_files = [f for f in zf.namelist() if f.endswith('METADATA')]
            assert len(metadata_files) > 0, "No METADATA file found in wheel"
            
            metadata_content = zf.read(metadata_files[0]).decode('utf-8')
            
            # Verify metadata contains correct information
            assert "Name: d_back" in metadata_content or "Name: d-back" in metadata_content, "Package name not found in metadata"
            assert f"Version: {expected_version}" in metadata_content, f"Version {expected_version} not found in metadata"
            assert "Author: Tin Nguyen" in metadata_content, "Author not found in metadata"
            assert "Requires-Python: >=3.8" in metadata_content, "Python requirement not found in metadata"
        
        if ALLURE_AVAILABLE:
            allure.attach(metadata_content, name="Wheel metadata", attachment_type=allure.attachment_type.TEXT)
    
    @pytest.mark.slow
    @pytest.mark.installation
    @pytest.mark.timeout(600)
    def test_uv_pip_install_from_wheel(self, temp_install_dir, project_root):
        """Verify that the built wheel can be installed via uv pip install and works correctly."""
        setup_allure_installation_info("test_uv_pip_install_from_wheel")
        
        # Build the package first
        project_copy = temp_install_dir / "project_install"
        project_copy.mkdir()
        
        for item in project_root.iterdir():
            if item.name in {".venv", "__pycache__", ".git", ".pytest_cache", "dist", "build"}:
                continue
            if item.is_file():
                shutil.copy2(item, project_copy)
            elif item.is_dir():
                shutil.copytree(item, project_copy / item.name, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        
        # Build
        returncode, stdout, stderr = run_command(
            ["uv", "build"],
            cwd=str(project_copy)
        )
        
        assert returncode == 0, f"uv build failed: {stderr}"
        
        # Get wheel path
        dist_dir = project_copy / "dist"
        wheel_files = list(dist_dir.glob("d_back-*.whl"))
        assert len(wheel_files) > 0, "No wheel file found"
        wheel_path = wheel_files[0]
        
        # Create fresh virtual environment
        venv_path = create_temp_venv(temp_install_dir)
        venv_python = get_venv_python(venv_path)
        
        # Install the wheel
        returncode, stdout, stderr = run_command(
            ["uv", "pip", "install", "--python", get_venv_python(venv_path), str(wheel_path)],
            cwd=str(temp_install_dir),
        )
        
        assert returncode == 0, f"uv pip install failed: {stderr}"
        
        # Set UV_PROJECT_ENVIRONMENT to point to our venv
        env = os.environ.copy()
        env["UV_PROJECT_ENVIRONMENT"] = str(venv_path)
        
        # Verify package is importable
        result = subprocess.run(
            [venv_python, "-c", "import d_back; print(d_back.__version__)"],
            capture_output=True,
            text=True,
            env=env
        )
        
        assert result.returncode == 0, f"Failed to import d_back: {result.stderr}"
        version_output = result.stdout.strip()
        expected_version = get_expected_version()
        assert version_output == expected_version, f"Version mismatch: got {version_output}, expected {expected_version}"
        
        # Verify main exports
        result = subprocess.run(
            [venv_python, "-c", "from d_back import WebSocketServer, MockDataProvider; print('OK')"],
            capture_output=True,
            text=True,
            env=env
        )
        
        assert result.returncode == 0, f"Failed to import main exports: {result.stderr}"
        
        # Check CLI entry point
        venv_bin_dir = get_venv_bin_dir(venv_path)
        cli_name = "d_back.exe" if sys.platform == "win32" else "d_back"
        cli_path = venv_bin_dir / cli_name
        
        assert cli_path.exists(), f"CLI entry point {cli_path} not found"
        
        if ALLURE_AVAILABLE:
            allure.attach(f"Package installed: ✓\nVersion: {version_output}\nExports available: ✓\nCLI installed: ✓", 
                         name="Installation verification", attachment_type=allure.attachment_type.TEXT)
    
    @pytest.mark.slow
    @pytest.mark.installation
    @pytest.mark.timeout(600)
    def test_cli_entry_point_functionality(self, temp_install_dir, project_root):
        """Verify that the d_back CLI entry point works correctly after installation."""
        setup_allure_installation_info("test_cli_entry_point_functionality")
        
        # Build and install package (reuse logic from previous test)
        project_copy = temp_install_dir / "project_cli"
        project_copy.mkdir()
        
        for item in project_root.iterdir():
            if item.name in {".venv", "__pycache__", ".git", ".pytest_cache", "dist", "build"}:
                continue
            if item.is_file():
                shutil.copy2(item, project_copy)
            elif item.is_dir():
                shutil.copytree(item, project_copy / item.name, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        
        # Build
        returncode, stdout, stderr = run_command(
            ["uv", "build"],
            cwd=str(project_copy)
        )
        assert returncode == 0, f"uv build failed: {stderr}"
        
        # Get wheel and install
        dist_dir = project_copy / "dist"
        wheel_files = list(dist_dir.glob("d_back-*.whl"))
        wheel_path = wheel_files[0]
        
        venv_path = create_temp_venv(temp_install_dir)
        
        returncode, stdout, stderr = run_command(
            ["uv", "pip", "install", "--python", get_venv_python(venv_path), str(wheel_path)],
            cwd=str(temp_install_dir)
        )
        assert returncode == 0, f"uv pip install failed: {stderr}"
        
        # Get CLI path
        venv_bin_dir = get_venv_bin_dir(venv_path)
        cli_name = "d_back.exe" if sys.platform == "win32" else "d_back"
        cli_path = venv_bin_dir / cli_name
        
        # Test --version
        env = os.environ.copy()
        env["UV_PROJECT_ENVIRONMENT"] = str(venv_path)
        
        result = subprocess.run(
            [str(cli_path), "--version"],
            capture_output=True,
            text=True,
            env=env
        )
        
        assert result.returncode == 0, f"CLI --version failed: {result.stderr}"
        version_output = result.stdout.strip()
        expected_version = get_expected_version()
        assert expected_version in version_output, f"Version {expected_version} not in output: {version_output}"
        
        # Test --help
        result = subprocess.run(
            [str(cli_path), "--help"],
            capture_output=True,
            text=True,
            env=env
        )
        
        assert result.returncode == 0, f"CLI --help failed: {result.stderr}"
        help_output = result.stdout
        
        # Verify help text contains expected arguments
        expected_args = ["--port", "--host", "--static-dir"]
        for arg in expected_args:
            assert arg in help_output, f"Expected argument {arg} not found in help text"
        
        # Start server with --port 0 (random available port) in background
        server_process = subprocess.Popen(
            [str(cli_path), "--port", "0"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        
        try:
            # Wait 2 seconds for server to start
            time.sleep(2)
            
            # Verify server process is running
            assert server_process.poll() is None, "Server process exited unexpectedly"
            
        finally:
            # Terminate server process gracefully
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
        
        if ALLURE_AVAILABLE:
            allure.attach(f"CLI version: {version_output}\nHelp output: OK\nServer startup: OK", 
                         name="CLI functionality verification", attachment_type=allure.attachment_type.TEXT)
    
    @pytest.mark.slow
    @pytest.mark.installation
    @pytest.mark.timeout(600)
    def test_production_installation_scenario(self, temp_install_dir, project_root):
        """Simulate a complete production installation workflow."""
        setup_allure_installation_info("test_production_installation_scenario")
        
        # Build package
        project_copy = temp_install_dir / "project_prod"
        project_copy.mkdir()
        
        for item in project_root.iterdir():
            if item.name in {".venv", "__pycache__", ".git", ".pytest_cache", "dist", "build"}:
                continue
            if item.is_file():
                shutil.copy2(item, project_copy)
            elif item.is_dir():
                shutil.copytree(item, project_copy / item.name, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        
        returncode, stdout, stderr = run_command(
            ["uv", "build"],
            cwd=str(project_copy)
        )
        assert returncode == 0, f"uv build failed: {stderr}"
        
        # Create fresh venv (simulating production environment)
        venv_path = create_temp_venv(temp_install_dir)
        venv_python = get_venv_python(venv_path)
        
        # Install only the wheel (no dev/test dependencies)
        dist_dir = project_copy / "dist"
        wheel_files = list(dist_dir.glob("d_back-*.whl"))
        wheel_path = wheel_files[0]
        
        returncode, stdout, stderr = run_command(
            ["uv", "pip", "install", "--python", get_venv_python(venv_path), str(wheel_path)],
            cwd=str(temp_install_dir)
        )
        assert returncode == 0, f"uv pip install failed: {stderr}"
        
        env = os.environ.copy()
        env["UV_PROJECT_ENVIRONMENT"] = str(venv_path)
        
        # Verify runtime dependencies are installed
        result = subprocess.run(
            [venv_python, "-c", "import websockets; print('websockets OK')"],
            capture_output=True,
            text=True,
            env=env
        )
        assert result.returncode == 0, f"Failed to import websockets: {result.stderr}"
        
        # Verify test dependencies are NOT installed
        result = subprocess.run(
            [venv_python, "-c", "import pytest; print('pytest found')"],
            capture_output=True,
            text=True,
            env=env
        )
        assert result.returncode != 0, "pytest should not be available in production install"
        
        # Verify dev dependencies are NOT installed
        result = subprocess.run(
            [venv_python, "-c", "import black; print('black found')"],
            capture_output=True,
            text=True,
            env=env
        )
        assert result.returncode != 0, "black should not be available in production install"
        
        # Verify CLI works
        venv_bin_dir = get_venv_bin_dir(venv_path)
        cli_name = "d_back.exe" if sys.platform == "win32" else "d_back"
        cli_path = venv_bin_dir / cli_name
        
        result = subprocess.run(
            [str(cli_path), "--version"],
            capture_output=True,
            text=True,
            env=env
        )
        assert result.returncode == 0, f"CLI --version failed: {result.stderr}"
        
        # Start server briefly to verify it runs
        server_process = subprocess.Popen(
            [str(cli_path), "--port", "0"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        
        try:
            time.sleep(3)
            assert server_process.poll() is None, "Server process exited unexpectedly"
        finally:
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
        
        if ALLURE_AVAILABLE:
            allure.attach("Production install verified: runtime deps only, CLI works, server runs", 
                         name="Production scenario verification", attachment_type=allure.attachment_type.TEXT)
    
    @pytest.mark.slow
    @pytest.mark.installation
    @pytest.mark.timeout(600)
    def test_package_metadata_verification(self, temp_install_dir, project_root):
        """Verify package metadata is correct after installation."""
        setup_allure_installation_info("test_package_metadata_verification")
        
        # Build and install package
        project_copy = temp_install_dir / "project_metadata"
        project_copy.mkdir()
        
        for item in project_root.iterdir():
            if item.name in {".venv", "__pycache__", ".git", ".pytest_cache", "dist", "build"}:
                continue
            if item.is_file():
                shutil.copy2(item, project_copy)
            elif item.is_dir():
                shutil.copytree(item, project_copy / item.name, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        
        returncode, stdout, stderr = run_command(
            ["uv", "build"],
            cwd=str(project_copy)
        )
        assert returncode == 0, f"uv build failed: {stderr}"
        
        venv_path = create_temp_venv(temp_install_dir)
        venv_python = get_venv_python(venv_path)
        
        dist_dir = project_copy / "dist"
        wheel_files = list(dist_dir.glob("d_back-*.whl"))
        wheel_path = wheel_files[0]
        
        returncode, stdout, stderr = run_command(
            ["uv", "pip", "install", "--python", get_venv_python(venv_path), str(wheel_path)],
            cwd=str(temp_install_dir)
        )
        assert returncode == 0, f"uv pip install failed: {stderr}"
        
        env = os.environ.copy()
        env["UV_PROJECT_ENVIRONMENT"] = str(venv_path)
        
        # Get installed version
        result = subprocess.run(
            [venv_python, "-c", "import importlib.metadata; print(importlib.metadata.version('d_back'))"],
            capture_output=True,
            text=True,
            env=env
        )
        assert result.returncode == 0, f"Failed to get version: {result.stderr}"
        installed_version = result.stdout.strip()
        expected_version = get_expected_version()
        assert installed_version == expected_version, f"Version mismatch: got {installed_version}, expected {expected_version}"
        
        # Get metadata
        result = subprocess.run(
            [venv_python, "-c", "import importlib.metadata; m = importlib.metadata.metadata('d_back'); print(f\"{m['Name']}|{m['Version']}|{m['Author']}|{m['Requires-Python']}\")"],
            capture_output=True,
            text=True,
            env=env
        )
        assert result.returncode == 0, f"Failed to get metadata: {result.stderr}"
        metadata_parts = result.stdout.strip().split("|")
        
        assert len(metadata_parts) == 4, f"Expected 4 metadata parts, got {len(metadata_parts)}"
        name, version, author, requires_python = metadata_parts
        
        assert name in ["d_back", "d-back"], f"Package name incorrect: {name}"
        assert version == expected_version, f"Metadata version mismatch: {version}"
        assert author == "Tin Nguyen", f"Author incorrect: {author}"
        assert requires_python == ">=3.8", f"Requires-Python incorrect: {requires_python}"
        
        # Get entry points
        result = subprocess.run(
            [venv_python, "-c", "import importlib.metadata; eps = importlib.metadata.entry_points(); ep = None; \
if hasattr(eps, 'select'): sel = eps.select(group='console_scripts', name='d_back'); ep = next(iter(sel), None); \
else: eps_map = getattr(eps, 'get', lambda k, d=None: None); group = eps_map('console_scripts', []); ep = next((e for e in group if e.name=='d_back'), None); \
print(ep.value if ep else 'NOT_FOUND')"],
            capture_output=True,
            text=True,
            env=env
        )
        assert result.returncode == 0, f"Failed to get entry points: {result.stderr}"
        entry_point = result.stdout.strip()
        
        assert entry_point != "NOT_FOUND", "d_back entry point not found"
        assert entry_point == "d_back.server:main_sync", f"Entry point incorrect: {entry_point}"
        
        if ALLURE_AVAILABLE:
            allure.attach(f"Version: {installed_version}\nName: {name}\nAuthor: {author}\nRequires-Python: {requires_python}\nEntry point: {entry_point}", 
                         name="Metadata verification", attachment_type=allure.attachment_type.TEXT)
    
    @pytest.mark.slow
    @pytest.mark.installation
    @pytest.mark.timeout(600)
    def test_reinstallation_and_upgrade(self, temp_install_dir, project_root):
        """Verify that the package can be reinstalled and upgraded correctly."""
        setup_allure_installation_info("test_reinstallation_and_upgrade")
        
        # Build package
        project_copy = temp_install_dir / "project_reinstall"
        project_copy.mkdir()
        
        for item in project_root.iterdir():
            if item.name in {".venv", "__pycache__", ".git", ".pytest_cache", "dist", "build"}:
                continue
            if item.is_file():
                shutil.copy2(item, project_copy)
            elif item.is_dir():
                shutil.copytree(item, project_copy / item.name, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        
        returncode, stdout, stderr = run_command(
            ["uv", "build"],
            cwd=str(project_copy)
        )
        assert returncode == 0, f"uv build failed: {stderr}"
        
        venv_path = create_temp_venv(temp_install_dir)
        venv_python = get_venv_python(venv_path)
        
        dist_dir = project_copy / "dist"
        wheel_files = list(dist_dir.glob("d_back-*.whl"))
        wheel_path = wheel_files[0]
        
        # Initial installation
        returncode, stdout, stderr = run_command(
            ["uv", "pip", "install", "--python", get_venv_python(venv_path), str(wheel_path)],
            cwd=str(temp_install_dir)
        )
        assert returncode == 0, f"Initial install failed: {stderr}"
        
        env = os.environ.copy()
        env["UV_PROJECT_ENVIRONMENT"] = str(venv_path)
        
        # Verify initial installation
        result = subprocess.run(
            [venv_python, "-c", "import d_back; print(d_back.__version__)"],
            capture_output=True,
            text=True,
            env=env
        )
        assert result.returncode == 0, f"Failed to verify initial install: {result.stderr}"
        
        # Force reinstall the same version
        returncode, stdout, stderr = run_command(
            ["uv", "pip", "install", "--force-reinstall", "--python", get_venv_python(venv_path), str(wheel_path)],
            cwd=str(temp_install_dir)
        )
        assert returncode == 0, f"Force reinstall failed: {stderr}"
        
        # Verify reinstallation works
        result = subprocess.run(
            [venv_python, "-c", "import d_back; print(d_back.__version__)"],
            capture_output=True,
            text=True,
            env=env
        )
        assert result.returncode == 0, f"Failed to verify reinstall: {result.stderr}"
        
        # Verify CLI still works after reinstallation
        venv_bin_dir = get_venv_bin_dir(venv_path)
        cli_name = "d_back.exe" if sys.platform == "win32" else "d_back"
        cli_path = venv_bin_dir / cli_name
        
        result = subprocess.run(
            [str(cli_path), "--version"],
            capture_output=True,
            text=True,
            env=env
        )
        assert result.returncode == 0, f"CLI failed after reinstall: {result.stderr}"
        
        # Uninstall the package
        returncode, stdout, stderr = run_command(
            ["uv", "pip", "uninstall", "--python", get_venv_python(venv_path), "d_back"],
            cwd=str(temp_install_dir)
        )
        assert returncode == 0, f"Uninstall failed: {stderr}"
        
        # Verify package is removed
        result = subprocess.run(
            [venv_python, "-c", "import d_back; print('d_back still available')"],
            capture_output=True,
            text=True,
            env=env
        )
        assert result.returncode != 0, "d_back should not be available after uninstall"
        
        # Reinstall and verify it works again
        returncode, stdout, stderr = run_command(
            ["uv", "pip", "install", "--python", get_venv_python(venv_path), str(wheel_path)],
            cwd=str(temp_install_dir)
        )
        assert returncode == 0, f"Final reinstall failed: {stderr}"
        
        result = subprocess.run(
            [venv_python, "-c", "import d_back; print(d_back.__version__)"],
            capture_output=True,
            text=True,
            env=env
        )
        assert result.returncode == 0, f"Failed to verify final reinstall: {result.stderr}"
        
        if ALLURE_AVAILABLE:
            allure.attach("Reinstall: ✓\nUninstall: ✓\nReinstall after uninstall: ✓", 
                         name="Reinstallation verification", attachment_type=allure.attachment_type.TEXT)


def main():
    """Run tests standalone without pytest."""
    print("=" * 80)
    print("D-Back Installation Test Suite")
    print("=" * 80)
    
    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp(prefix="d_back_install_test_"))
    project_root = get_project_root()
    
    print(f"Temporary directory: {temp_dir}")
    print(f"Project root: {project_root}")
    print(f"Expected version: {get_expected_version()}")
    print()
    
    # Create test instance
    test_instance = TestUvInstallation()
    
    # List of test methods to run
    test_methods = [
        ("Development Installation", test_instance.test_uv_sync_development_installation),
        ("Dependency Groups", test_instance.test_uv_sync_with_dependency_groups),
        ("Package Build", test_instance.test_uv_build_package),
        ("Wheel Installation", test_instance.test_uv_pip_install_from_wheel),
        ("CLI Functionality", test_instance.test_cli_entry_point_functionality),
        ("Production Scenario", test_instance.test_production_installation_scenario),
        ("Metadata Verification", test_instance.test_package_metadata_verification),
        ("Reinstallation", test_instance.test_reinstallation_and_upgrade),
    ]
    
    passed = 0
    failed = 0
    
    try:
        for test_name, test_method in test_methods:
            print(f"Running: {test_name}")
            print("-" * 40)
            
            try:
                # Create unique temp dir for each test
                test_temp_dir = temp_dir / f"test_{len(test_name)}"
                test_temp_dir.mkdir(exist_ok=True)
                
                test_method(test_temp_dir, project_root)
                print(f"✓ PASSED: {test_name}")
                passed += 1
                
            except Exception as e:
                print(f"✗ FAILED: {test_name}")
                print(f"  Error: {e}")
                failed += 1
            
            print()
    
    finally:
        # Cleanup
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            print(f"Warning: Failed to cleanup {temp_dir}: {e}")
    
    print("=" * 80)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 80)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())