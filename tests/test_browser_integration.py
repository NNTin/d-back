"""
End-to-end browser tests using headless Chrome.
Tests the d_back server's web interface functionality.
"""

import os
import subprocess
import sys
import time
import pytest

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
    
    # Try to import webdriver-manager for automatic driver management
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        WEBDRIVER_MANAGER_AVAILABLE = True
    except ImportError:
        WEBDRIVER_MANAGER_AVAILABLE = False
        
except ImportError:
    SELENIUM_AVAILABLE = False
    WEBDRIVER_MANAGER_AVAILABLE = False

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


def _apply_allure_decorators_homepage(func):
    """Apply allure decorators for homepage test if available."""
    if ALLURE_AVAILABLE:
        func = allure.feature("Browser Integration")(func)
        func = allure.story("Homepage Loading")(func)
        func = allure.title("Test that homepage loads successfully in Chrome")(func)
    return func


def _apply_allure_decorators_content(func):
    """Apply allure decorators for content test if available."""
    if ALLURE_AVAILABLE:
        func = allure.feature("Browser Integration")(func)
        func = allure.story("Page Content")(func)
        func = allure.title("Test that page content displays correctly")(func)
    return func


def _apply_allure_decorators_version_api(func):
    """Apply allure decorators for version API test if available."""
    if ALLURE_AVAILABLE:
        func = allure.feature("Browser Integration")(func)
        func = allure.story("JavaScript API")(func)
        func = allure.title("Test that JavaScript version API call works")(func)
    return func


def _apply_allure_decorators_styling(func):
    """Apply allure decorators for styling test if available."""
    if ALLURE_AVAILABLE:
        func = allure.feature("Browser Integration")(func)
        func = allure.story("Page Styling")(func)
        func = allure.title("Test that page has proper styling and layout")(func)
    return func


class TestBrowserIntegration:
    """Browser integration tests for d_back server."""
    
    @pytest.fixture(scope="class")
    def server_process(self):
        """Start the d_back server for testing."""
        server_proc = subprocess.Popen(
            [sys.executable, "-m", "d_back"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Give server more time to start for browser tests
        time.sleep(3)
        
        # Verify server is still running
        if server_proc.poll() is not None:
            stdout, stderr = server_proc.communicate()
            raise RuntimeError(f"Server failed to start. stdout: {stdout}, stderr: {stderr}")
        
        yield server_proc
        
        # Cleanup with proper timeout handling
        if server_proc.poll() is None:
            server_proc.terminate()
            try:
                server_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_proc.kill()
                try:
                    server_proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    pass

    @pytest.fixture(scope="class")
    def chrome_driver(self):
        """Setup headless Chrome driver."""
        if not SELENIUM_AVAILABLE:
            pytest.skip("Selenium not available")
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        try:
            # Try to create the driver with webdriver-manager if available
            if WEBDRIVER_MANAGER_AVAILABLE:
                from webdriver_manager.chrome import ChromeDriverManager
                from selenium.webdriver.chrome.service import Service
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                # Fallback to default Chrome driver
                driver = webdriver.Chrome(options=chrome_options)
                
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(10)
            
            yield driver
            
        except WebDriverException as e:
            pytest.skip(f"Chrome WebDriver not available: {e}")
        finally:
            try:
                if 'driver' in locals():
                    driver.quit()
            except Exception:
                pass

    @pytest.mark.timeout(60)
    @_apply_allure_decorators_homepage
    def test_homepage_loads(self, server_process, chrome_driver):
        """Test that the homepage loads successfully in Chrome."""
        setup_allure_test_info()
        
        driver = chrome_driver
        
        try:
            # Navigate to the homepage
            driver.get("http://localhost:3000")
            
            if ALLURE_AVAILABLE:
                allure.attach(driver.get_screenshot_as_png(), "Homepage Screenshot", allure.attachment_type.PNG)
            
            # Wait for the page title to contain expected text
            WebDriverWait(driver, 20).until(
                EC.title_contains("D-Back WebSocket Server")
            )
            
            # Verify title
            assert "D-Back WebSocket Server" in driver.title
            
            # Verify page loaded completely by checking for key elements
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "h1"))
            )
            
            # Check that main heading is present
            h1_element = driver.find_element(By.TAG_NAME, "h1")
            assert "D-Back WebSocket Server" in h1_element.text
            
        except TimeoutException:
            # Get page source for debugging
            page_source = driver.page_source[:1000] if driver.page_source else "No page source"
            pytest.fail(f"Page load timeout. Page source: {page_source}")

    @pytest.mark.timeout(60)
    @_apply_allure_decorators_content
    def test_page_content_displayed(self, server_process, chrome_driver):
        """Test that page content displays correctly."""
        setup_allure_test_info()
        
        driver = chrome_driver
        
        try:
            driver.get("http://localhost:3000")
            
            # Wait for content to load
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "container"))
            )
            
            # Check for key content sections
            expected_sections = [
                "How to Run This Module",
                "WebSocket API", 
                "Features",
                "Package Information"
            ]
            
            for section in expected_sections:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{section}')]"))
                )
                assert element.is_displayed(), f"Section '{section}' should be visible"
            
            # Verify server status indicator
            status_elements = driver.find_elements(By.CLASS_NAME, "status")
            assert len(status_elements) > 0, "Status indicator should be present"
            
            # Check that WebSocket URL is displayed
            websocket_url_found = any("ws://localhost:3000" in element.text 
                                    for element in driver.find_elements(By.TAG_NAME, "*"))
            assert websocket_url_found, "WebSocket URL should be displayed on the page"
            
        except TimeoutException as e:
            pytest.fail(f"Content verification timeout: {e}")

    @pytest.mark.timeout(60)
    @_apply_allure_decorators_version_api
    def test_version_api_call(self, server_process, chrome_driver):
        """Test that the JavaScript version API call works."""
        setup_allure_test_info()
        
        driver = chrome_driver
        
        try:
            driver.get("http://localhost:3000")
            
            # Wait for the page to load and JavaScript to execute
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "version"))
            )
            
            # Give JavaScript time to make the API call and update the version
            time.sleep(3)
            
            # Check that version was loaded (should not be "Loading..." anymore)
            version_element = driver.find_element(By.ID, "version")
            version_text = version_element.text
            
            assert version_text != "Loading...", "Version should be loaded"
            assert version_text != "Unknown", "Version should not be Unknown"
            assert len(version_text) > 1, f"Version text should be meaningful: '{version_text}'"
            
            # Also check version-text element
            version_text_element = driver.find_element(By.ID, "version-text")
            version_text_content = version_text_element.text
            
            assert version_text_content != "Loading...", "Version text should be loaded"
            assert version_text_content != "Unknown", "Version text should not be Unknown"
            
        except TimeoutException as e:
            # Get current version elements content for debugging
            try:
                version_elem = driver.find_element(By.ID, "version")
                version_text_elem = driver.find_element(By.ID, "version-text")
                pytest.fail(f"Version API test timeout. Version: '{version_elem.text}', Version-text: '{version_text_elem.text}'. Error: {e}")
            except Exception:
                pytest.fail(f"Version API test timeout and could not find version elements: {e}")

    @pytest.mark.timeout(90)
    @_apply_allure_decorators_styling
    def test_page_styling_and_layout(self, server_process, chrome_driver):
        """Test that the page has proper styling and layout."""
        setup_allure_test_info()
        
        driver = chrome_driver
        
        try:
            driver.get("http://localhost:3000")
            
            # Wait for container to load
            container = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "container"))
            )
            
            # Check that container has proper styling
            assert container.is_displayed(), "Container should be visible"
            
            # Verify page has a reasonable size (not empty)
            body = driver.find_element(By.TAG_NAME, "body")
            body_rect = body.rect
            assert body_rect["height"] > 100, f"Page should have reasonable height: {body_rect['height']}"
            assert body_rect["width"] > 100, f"Page should have reasonable width: {body_rect['width']}"
            
            # Check for CSS styling by verifying background color changed from default
            container_bg = container.value_of_css_property("background-color")
            body_bg = body.value_of_css_property("background-color")
            
            # At least one should have custom styling (not default transparent/white)
            has_custom_styling = (
                container_bg not in ["rgba(0, 0, 0, 0)", "transparent", "white", "rgb(255, 255, 255)"] or
                body_bg not in ["rgba(0, 0, 0, 0)", "transparent", "white", "rgb(255, 255, 255)"]
            )
            
            assert has_custom_styling, f"Page should have custom styling. Container: {container_bg}, Body: {body_bg}"
            
            # Verify code blocks are present and styled
            code_elements = driver.find_elements(By.CLASS_NAME, "code")
            assert len(code_elements) > 0, "Should have code examples"
            
            # Check that first code element has monospace font styling
            if code_elements:
                first_code = code_elements[0]
                font_family = first_code.value_of_css_property("font-family")
                assert any(font in font_family.lower() for font in ["mono", "consolas", "courier"]), \
                    f"Code should use monospace font: {font_family}"
                    
        except TimeoutException as e:
            pytest.fail(f"Styling verification timeout: {e}")
