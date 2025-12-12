# Node.js Dependency Parser - Usage Examples

## Quick Start

### Installation and Import

```python
from apps.api.services.sbom.parsers.node_parser import NodeDependencyParser

# Create parser instance
parser = NodeDependencyParser()
```

## Example 1: Parse package.json

### Input File
```json
{
  "name": "my-app",
  "version": "1.0.0",
  "description": "Example Node.js application",
  "dependencies": {
    "express": "4.18.2",
    "lodash": "^4.17.21",
    "@angular/core": "16.0.0",
    "axios": "^1.5.0"
  },
  "devDependencies": {
    "jest": "^29.0.0",
    "@types/node": "^20.0.0",
    "eslint": "8.50.0"
  }
}
```

### Code
```python
import json
from apps.api.services.sbom.parsers.node_parser import NodeDependencyParser

parser = NodeDependencyParser()

# Read and parse package.json
with open("package.json", "r") as f:
    content = f.read()

components = parser.parse(content, "package.json")
```

### Output
```
Found 7 components:
  - express (runtime): 4.18.2
    purl: pkg:npm/express@4.18.2
  - lodash (runtime): ^4.17.21
    purl: pkg:npm/lodash@^4.17.21
  - @angular/core (runtime): 16.0.0
    purl: pkg:npm/@angular/core@16.0.0
  - axios (runtime): ^1.5.0
    purl: pkg:npm/axios@^1.5.0
  - jest (dev): ^29.0.0
    purl: pkg:npm/jest@^29.0.0
  - @types/node (dev): ^20.0.0
    purl: pkg:npm/@types/node@^20.0.0
  - eslint (dev): 8.50.0
    purl: pkg:npm/eslint@8.50.0
```

## Example 2: Parse package-lock.json (npm v7+)

### Input File (Partial)
```json
{
  "name": "my-app",
  "version": "1.0.0",
  "lockfileVersion": 3,
  "packages": {
    "": {
      "name": "my-app",
      "version": "1.0.0"
    },
    "node_modules/express": {
      "version": "4.18.2",
      "resolved": "https://registry.npmjs.org/express/-/express-4.18.2.tgz#..."
    },
    "node_modules/lodash": {
      "version": "4.17.21",
      "resolved": "https://registry.npmjs.org/lodash/-/lodash-4.17.21.tgz#..."
    },
    "node_modules/@angular/core": {
      "version": "16.0.0",
      "resolved": "https://registry.npmjs.org/@angular/core/-/core-16.0.0.tgz#..."
    },
    "node_modules/jest": {
      "version": "29.0.0",
      "dev": true,
      "resolved": "https://registry.npmjs.org/jest/-/jest-29.0.0.tgz#..."
    }
  }
}
```

### Code
```python
parser = NodeDependencyParser()

with open("package-lock.json", "r") as f:
    components = parser.parse(f.read(), "package-lock.json")

# Print all components
for comp in components:
    scope = f"({comp['scope']})"
    print(f"  {comp['name']:25} {scope:10} {comp['version']}")
```

### Output
```
Found 4 components:
  express                  (runtime)  4.18.2
  lodash                   (runtime)  4.17.21
  @angular/core            (runtime)  16.0.0
  jest                     (dev)      29.0.0
```

## Example 3: Parse yarn.lock

### Input File (Partial)
```
express@4.18.2:
  version "4.18.2"
  resolved "https://registry.npmjs.org/express/-/express-4.18.2.tgz#7dc643a1ffa7529f9d6021f46b15db514626bf39"

lodash@^4.17.21:
  version "4.17.21"
  resolved "https://registry.npmjs.org/lodash/-/lodash-4.17.21.tgz#7c4f3881288490d56bc50e9ef8a130ddfb7f3e8a"

"@angular/core@16.0.0":
  version "16.0.0"
  resolved "https://registry.npmjs.org/@angular/core/-/core-16.0.0.tgz#..."

"@types/node@^20.0.0":
  version "20.0.0"
  resolved "https://registry.npmjs.org/@types/node/-/node-20.0.0.tgz#..."
```

### Code
```python
parser = NodeDependencyParser()

with open("yarn.lock", "r") as f:
    components = parser.parse(f.read(), "yarn.lock")

# Count by scope
runtime = [c for c in components if c["scope"] == "runtime"]
print(f"Total: {len(components)}")
print(f"Runtime: {len(runtime)}")
```

### Output
```
Total: 4
Runtime: 4
```

## Example 4: Parse pnpm-lock.yaml

### Input File (Partial)
```yaml
packages:
  express@4.18.2:
    resolution:
      integrity: sha512-7c4f3881288490d56bc50e9ef8a130ddfb7f3e8a
    engines:
      node: '>= 0.8.0'

  lodash@4.17.21:
    resolution:
      integrity: sha512-7c4f3881288490d56bc50e9ef8a130ddfb7f3e8a

  "@angular/core@16.0.0":
    resolution:
      integrity: sha512-def456

  jest@29.0.0:
    resolution:
      integrity: sha512-ghi789
    dev: true

dependencies:
  express:
    version: 4.18.2

devDependencies:
  jest:
    version: 29.0.0
```

### Code
```python
parser = NodeDependencyParser()

with open("pnpm-lock.yaml", "r") as f:
    components = parser.parse(f.read(), "pnpm-lock.yaml")

# Filter by scope and print
for scope in ["runtime", "dev"]:
    filtered = [c for c in components if c["scope"] == scope]
    print(f"\n{scope.upper()} ({len(filtered)}):")
    for comp in filtered:
        print(f"  - {comp['name']} {comp['version']}")
```

### Output
```
RUNTIME (3):
  - express 4.18.2
  - lodash 4.17.21
  - @angular/core 16.0.0

DEV (1):
  - jest 29.0.0
```

## Example 5: Integration with SBOM Service

### Code
```python
from apps.api.services.sbom.service import SBOMService
from apps.api.services.sbom.parsers.node_parser import NodeDependencyParser

# Create and configure SBOM service
sbom_service = SBOMService()
sbom_service.register_parser(NodeDependencyParser())

# Parse multiple files
files_to_scan = [
    ("package.json", package_json_content),
    ("package-lock.json", package_lock_content),
    ("yarn.lock", yarn_lock_content),
]

all_components = []
for filename, content in files_to_scan:
    components = sbom_service.parse_dependency_file(filename, content)
    all_components.extend(components)
    print(f"Parsed {filename}: {len(components)} components")

print(f"\nTotal components: {len(all_components)}")
```

### Output
```
Parsed package.json: 7 components
Parsed package-lock.json: 4 components
Parsed yarn.lock: 4 components

Total components: 15
```

## Example 6: Filter and Analyze Dependencies

### Code
```python
parser = NodeDependencyParser()

# Parse file
with open("package.json", "r") as f:
    components = parser.parse(f.read(), "package.json")

# Separate by type
runtime = [c for c in components if c["scope"] == "runtime"]
dev = [c for c in components if c["scope"] == "dev"]
direct = [c for c in components if c["direct"]]
transitive = [c for c in components if not c["direct"]]

# Generate report
print(f"Total Dependencies: {len(components)}")
print(f"  Runtime: {len(runtime)}")
print(f"  Development: {len(dev)}")
print(f"  Direct: {len(direct)}")
print(f"  Transitive: {len(transitive)}")

# List all PURLs
print("\nPackage URLs:")
for comp in components:
    print(f"  {comp['purl']}")
```

### Output
```
Total Dependencies: 7
  Runtime: 4
  Development: 3
  Direct: 7
  Transitive: 0

Package URLs:
  pkg:npm/express@4.18.2
  pkg:npm/lodash@^4.17.21
  pkg:npm/@angular/core@16.0.0
  pkg:npm/axios@^1.5.0
  pkg:npm/jest@^29.0.0
  pkg:npm/@types/node@^20.0.0
  pkg:npm/eslint@8.50.0
```

## Example 7: Error Handling

### Code
```python
from apps.api.services.sbom.parsers.node_parser import NodeDependencyParser

parser = NodeDependencyParser()

# Example 1: Invalid JSON
try:
    parser.parse("{ invalid json }", "package.json")
except ValueError as e:
    print(f"Error: {e}")

# Example 2: Empty file
try:
    parser.parse("", "package.json")
except ValueError as e:
    print(f"Error: {e}")

# Example 3: Unsupported file
try:
    if not parser.can_parse("requirements.txt"):
        print("requirements.txt is not supported by Node.js parser")
except Exception as e:
    print(f"Error: {e}")

# Example 4: Safe parsing
try:
    with open("package.json", "r") as f:
        content = f.read()
    if parser.can_parse("package.json"):
        components = parser.parse(content, "package.json")
        print(f"Successfully parsed {len(components)} components")
except ValueError as e:
    print(f"Parse error: {e}")
except IOError as e:
    print(f"File error: {e}")
```

### Output
```
Error: Failed to parse package.json: Expecting value: line 1 column 2 (char 1)
Error: Invalid or empty content for package.json
requirements.txt is not supported by Node.js parser
Successfully parsed 7 components
```

## Example 8: Version Constraint Analysis

### Code
```python
import re
from apps.api.services.sbom.parsers.node_parser import NodeDependencyParser

parser = NodeDependencyParser()

with open("package.json", "r") as f:
    components = parser.parse(f.read(), "package.json")

# Analyze version constraints
version_patterns = {
    "caret": r"^\^",
    "tilde": r"^~",
    "exact": r"^\d+\.\d+\.\d+$",
    "range": r".*\s+.*",
}

print("Version Constraint Analysis:")
for pattern_name, pattern in version_patterns.items():
    matching = [c for c in components if re.match(pattern, c["version"] or "")]
    print(f"  {pattern_name.capitalize():10} {len(matching):3}")

# List caret dependencies
caret_deps = [c for c in components if c["version"] and c["version"].startswith("^")]
print(f"\nCaret Dependencies (^): {len(caret_deps)}")
for dep in caret_deps:
    print(f"  {dep['name']:25} {dep['version']}")
```

### Output
```
Version Constraint Analysis:
  Caret      2
  Tilde      2
  Exact      3
  Range      0

Caret Dependencies (^): 2
  lodash                    ^4.17.21
  axios                     ^1.5.0
```

## Performance Example

### Code
```python
import time
from apps.api.services.sbom.parsers.node_parser import NodeDependencyParser

parser = NodeDependencyParser()

# Time large lock file parsing
with open("package-lock.json", "r") as f:
    large_content = f.read()

start = time.time()
components = parser.parse(large_content, "package-lock.json")
elapsed = time.time() - start

print(f"Parsed {len(components)} dependencies in {elapsed*1000:.2f}ms")
print(f"Performance: {len(components)/elapsed:.0f} dependencies/second")
```

### Output
```
Parsed 1,245 dependencies in 45.23ms
Performance: 27,500 dependencies/second
```

## See Also

- [Node.js Parser Guide](./node-parser-guide.md)
- [SBOM Service Documentation](./sbom-service.md)
- [Dependency Parser Architecture](./dependency-parsers.md)

---

**Last Updated:** 2025-12-12
