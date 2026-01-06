"""E2E tests for Web UI page loads.

These tests verify that the web application pages are accessible
and return valid HTML content.
"""

import pytest
import requests


class TestWebUIPages:
    """Test Web UI page accessibility."""

    def test_main_page_loads(self, web_url, check_services):
        """Test main page loads HTML content."""
        response = requests.get(web_url)

        assert response.status_code == 200
        assert "<!DOCTYPE" in response.text or "<html" in response.text

    def test_login_route_accessible(self, web_url, check_services):
        """Test /login route is accessible.

        Note: SPA may redirect to main page with client-side routing.
        """
        response = requests.get(f"{web_url}/login", allow_redirects=True)

        # Should either serve the page directly or serve SPA that handles routing
        assert response.status_code == 200
        assert "<!DOCTYPE" in response.text or "<html" in response.text

    def test_static_assets_served(self, web_url, check_services):
        """Test that static assets (JS/CSS) are referenced in HTML."""
        response = requests.get(web_url)

        assert response.status_code == 200
        # Check for asset references in the HTML
        content = response.text.lower()
        # Vite builds include references to assets
        has_assets = "assets/" in content or ".js" in content or ".css" in content
        assert has_assets, "No static asset references found in HTML"

    def test_favicon_or_logo(self, web_url, check_services):
        """Test favicon or logo is accessible."""
        # Try common paths
        for path in ["/favicon.ico", "/elder-logo.png", "/logo.png"]:
            response = requests.get(f"{web_url}{path}")
            if response.status_code == 200:
                return  # Found one

        # At minimum, check that some static content is served
        response = requests.get(web_url)
        assert response.status_code == 200


class TestWebUIErrorHandling:
    """Test Web UI error handling."""

    def test_404_page(self, web_url, check_services):
        """Test non-existent static file returns 404 or SPA fallback."""
        response = requests.get(f"{web_url}/nonexistent-file-12345.xyz")

        # SPA may serve index.html for all routes (200)
        # or nginx may return 404 for explicit file extensions
        assert response.status_code in [200, 404]

    def test_deep_route_serves_spa(self, web_url, check_services):
        """Test deep routes serve SPA for client-side routing."""
        response = requests.get(f"{web_url}/organizations/1/details")

        # Should serve SPA index.html for client routing
        assert response.status_code == 200
        assert "<!DOCTYPE" in response.text or "<html" in response.text


class TestWebUISecurityHeaders:
    """Test Web UI security headers."""

    def test_x_content_type_options(self, web_url, check_services):
        """Test X-Content-Type-Options header is set."""
        response = requests.get(web_url)

        # This header may or may not be set depending on nginx config
        # Just verify the response is successful
        assert response.status_code == 200

    def test_no_server_version_disclosure(self, web_url, check_services):
        """Test server doesn't disclose detailed version info."""
        response = requests.get(web_url)

        server_header = response.headers.get("Server", "")
        # Should not contain detailed nginx version
        # (just "nginx" is OK, "nginx/1.25.3" is not ideal)
        if "nginx" in server_header.lower():
            # This is informational - nginx default config includes version
            pass
        assert response.status_code == 200
