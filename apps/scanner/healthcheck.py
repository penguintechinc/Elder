# flake8: noqa: E501
#!/usr/bin/env python3
"""Health check script for Elder Scanner Service.

Verifies that:
1. Core scanner modules can be imported
2. API URL is configured
3. Scanner directory is writable

Exit codes:
    0 - Healthy
    1 - Unhealthy
"""

import os
import sys


def check_imports() -> bool:
    """Verify core modules can be imported."""
    try:
        import httpx  # noqa: F401
        from scanners.banner import BannerScanner  # noqa: F401
        from scanners.http_screenshot import \
            HTTPScreenshotScanner  # noqa: F401
        from scanners.network import NetworkScanner  # noqa: F401
        from scanners.sbom_scanner import SBOMScanner  # noqa: F401

        return True
    except ImportError as e:
        print(f"Import error: {e}", file=sys.stderr)
        return False


def check_api_url() -> bool:
    """Verify API URL is configured."""
    api_url = os.getenv("ELDER_API_URL", "")
    if not api_url:
        print("ELDER_API_URL not configured", file=sys.stderr)
        return False
    return True


def check_screenshot_dir() -> bool:
    """Verify screenshot directory is writable."""
    screenshot_dir = os.getenv("SCREENSHOT_DIR", "/app/screenshots")
    try:
        os.makedirs(screenshot_dir, exist_ok=True)
        test_file = os.path.join(screenshot_dir, ".health_check")
        with open(test_file, "w") as f:
            f.write("ok")
        os.remove(test_file)
        return True
    except Exception as e:
        print(f"Screenshot dir check failed: {e}", file=sys.stderr)
        return False


def main() -> int:
    """Run all health checks."""
    checks = [
        ("imports", check_imports),
        ("api_url", check_api_url),
        ("screenshot_dir", check_screenshot_dir),
    ]

    all_passed = True
    for name, check in checks:
        try:
            if not check():
                print(f"Check failed: {name}", file=sys.stderr)
                all_passed = False
        except Exception as e:
            print(f"Check error ({name}): {e}", file=sys.stderr)
            all_passed = False

    if all_passed:
        print("OK")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
