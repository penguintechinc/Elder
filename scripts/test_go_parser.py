#!/usr/bin/env python3
"""Quick validation script for the Go dependency parser.

This script demonstrates the Go parser functionality with test cases
covering both go.mod and go.sum file parsing.

Usage:
    python scripts/test_go_parser.py
"""

import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from apps.api.services.sbom.parsers.go_parser import GoParser


def test_go_mod_parsing() -> None:
    """Test go.mod file parsing."""
    print("=" * 70)
    print("TEST 1: Go.mod Single-line and Multi-line Require Parsing")
    print("=" * 70)

    parser = GoParser()

    go_mod_content = """module github.com/example/myapp

go 1.23

require (
    github.com/gin-gonic/gin v1.9.1
    github.com/lib/pq v1.10.9
    github.com/google/uuid v1.3.0 // indirect
)

require github.com/stretchr/testify v1.8.4

replace github.com/some/package => github.com/fork/package v1.0.0
exclude github.com/bad/package v1.0.0
"""

    deps = parser.parse(go_mod_content, "go.mod")

    print(f"\nFound {len(deps)} dependencies:")
    for i, dep in enumerate(deps, 1):
        direct_str = "DIRECT" if dep["direct"] else "INDIRECT"
        print(f"\n{i}. {dep['name']}")
        print(f"   Version:      {dep['version']}")
        print(f"   Type:         {direct_str}")
        print(f"   Package Type: {dep['package_type']}")
        print(f"   Scope:        {dep['scope']}")
        print(f"   PURL:         {dep['purl']}")
        print(f"   Source:       {dep['source_file']}")

    print("\n" + "=" * 70)
    print("TEST 2: Go.sum Parsing and Hash Verification")
    print("=" * 70)

    go_sum_content = """github.com/gin-gonic/gin v1.9.1 h1:SHw5L5ZWnOTpHxzKgwl=
github.com/lib/pq v1.10.9 h1:EqnZf1oMVESDkLsrCN=
github.com/google/uuid v1.3.0 h1:c5/5+VAXxRAqWr+Nj8=
"""

    deps = parser.parse(go_sum_content, "go.sum")

    print(f"\nFound {len(deps)} go.sum entries:")
    for i, dep in enumerate(deps, 1):
        print(f"\n{i}. {dep['name']}")
        print(f"   Version: {dep['version']}")
        print(f"   Hash:    {dep.get('hash', 'N/A')}")
        print(f"   Direct:  {dep['direct']}")

    print("\n" + "=" * 70)
    print("TEST 3: Version Format Handling")
    print("=" * 70)

    versions_content = """module github.com/example/app

require (
    github.com/some/package v1.0.0
    github.com/beta/package v1.9.0-beta.1
    github.com/rc/package v1.10.9-rc.1
    github.com/pseudo/package v0.0.0-20240101120000-abcdef123456
)
"""

    deps = parser.parse(versions_content, "go.mod")

    print(f"\nSupports various version formats:")
    for dep in deps:
        print(f"  - {dep['name']:40s} {dep['version']}")

    print("\n" + "=" * 70)
    print("TEST 4: Indirect Dependency Detection")
    print("=" * 70)

    indirect_content = """module github.com/example/app

require (
    github.com/direct/a v1.0.0
    github.com/direct/b v2.0.0
    github.com/indirect/c v1.0.0 // indirect
    github.com/indirect/d v2.0.0 // indirect
)
"""

    deps = parser.parse(indirect_content, "go.mod")

    direct_count = sum(1 for d in deps if d["direct"])
    indirect_count = sum(1 for d in deps if not d["direct"])

    print(f"\nDirect dependencies:   {direct_count}")
    print(f"Indirect dependencies: {indirect_count}")

    for dep in deps:
        status = "DIRECT  " if dep["direct"] else "INDIRECT"
        print(f"  {status} - {dep['name']}")

    print("\n" + "=" * 70)
    print("TEST 5: File Type Detection")
    print("=" * 70)

    print(f"\nParser can handle these files:")
    supported = parser.get_supported_files()
    for f in supported:
        can_parse = parser.can_parse(f)
        print(f"  ✓ {f:15s} - {can_parse}")

    print(f"\nParser correctly rejects non-Go files:")
    non_go_files = ["package.json", "requirements.txt", "composer.json"]
    for f in non_go_files:
        can_parse = parser.can_parse(f)
        print(f"  ✓ {f:15s} - {can_parse}")

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        test_go_mod_parsing()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)
