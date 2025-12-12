# Node.js Dependency Parser Guide

## Overview

The Node.js Dependency Parser (`NodeDependencyParser`) is a comprehensive dependency file parser for Node.js/npm-based projects. It extracts dependency information from multiple package manager lock file formats and provides standardized output for SBOM (Software Bill of Materials) analysis.

## Supported File Formats

### 1. package.json
The standard Node.js project manifest file.

**Supported Sections:**
- `dependencies` - Runtime dependencies (marked as `scope: "runtime"`)
- `devDependencies` - Development dependencies (marked as `scope: "dev"`)
- `peerDependencies` - Peer dependencies (marked as `scope: "runtime"`)
- `optionalDependencies` - Optional packages (marked as `scope: "runtime"`)

**Characteristics:**
- `direct: true` - All dependencies from package.json are direct
- Returns version specifications (ranges, constraints, etc.)

**Example:**
```json
{
  "dependencies": {
    "lodash": "^4.17.21",
    "@angular/core": "16.0.0"
  },
  "devDependencies": {
    "jest": "^29.0.0"
  }
}
```

### 2. package-lock.json
npm lock file for dependency resolution. Supports both v6 and v7+ formats.

**npm v6 Format:**
- Uses `dependencies` key with nested structure
- Direct and transitive dependencies mixed

**npm v7+ Format (Recommended):**
- Uses `packages` key with absolute paths as keys
- Format: `node_modules/@scope/package-name`
- Includes `dev` flag for development dependencies

**Characteristics:**
- `direct: false` - All dependencies are transitive (resolved)
- Returns exact, pinned versions
- Root package entry ("") is skipped

**Example (v7+):**
```json
{
  "lockfileVersion": 3,
  "packages": {
    "": {
      "name": "my-app",
      "version": "1.0.0"
    },
    "node_modules/lodash": {
      "version": "4.17.21"
    },
    "node_modules/@angular/core": {
      "version": "16.0.0"
    },
    "node_modules/jest": {
      "version": "29.0.0",
      "dev": true
    }
  }
}
```

### 3. yarn.lock
Yarn package manager lock file.

**Format:**
```
package-name@version-spec:
  version "resolved-version"
  resolved "URL"
  ...
```

**Characteristics:**
- `direct: false` - All dependencies are transitive
- Parses custom Yarn format (not JSON)
- Extracts version from `resolved` URL when available
- Handles both scoped and unscoped packages
- Version extracted from npm registry URLs or git references

**Example:**
```
lodash@^4.17.21:
  version "4.17.21"
  resolved "https://registry.npmjs.org/lodash/-/lodash-4.17.21.tgz#hash"

@angular/core@16.0.0:
  version "16.0.0"
  resolved "https://registry.npmjs.org/@angular/core/-/core-16.0.0.tgz#hash"
```

### 4. pnpm-lock.yaml
pnpm package manager lock file in YAML format.

**Format:**
- `packages` section with `package@version` keys
- Optional `dependencies` and `devDependencies` sections
- `dev: true` flag for development packages

**Characteristics:**
- `direct: false` for packages section
- `direct: true` for dependencies/devDependencies sections
- YAML format with proper parsing
- Handles scoped packages in key format

**Example:**
```yaml
packages:
  lodash@4.17.21:
    resolution:
      integrity: sha512-abc123
  "@angular/core@16.0.0":
    resolution:
      integrity: sha512-def456
dependencies:
  express:
    version: 4.18.2
devDependencies:
  jest:
    version: 29.0.0
```

## Output Format

All parsers return a list of dictionaries with the following structure:

```python
{
    "name": str,              # Package name (may include @scope prefix)
    "version": str,           # Version string (None if not available)
    "purl": str,             # Package URL: pkg:npm/{name}@{version}
    "package_type": str,     # Always "npm"
    "scope": str,            # "runtime" or "dev"
    "direct": bool,          # True for direct deps, False for transitive
    "source_file": str       # Filename that was parsed
}
```

### Package URL (PURL) Format

Package URLs follow the official PURL specification for npm packages:

```
pkg:npm/lodash@4.17.21
pkg:npm/@angular/core@16.0.0
pkg:npm/express  # Without version if not available
```

## Usage Examples

### Basic Usage

```python
from apps.api.services.sbom.parsers.node_parser import NodeDependencyParser

parser = NodeDependencyParser()

# Check if file is supported
if parser.can_parse("package.json"):
    with open("package.json", "r") as f:
        content = f.read()

    components = parser.parse(content, "package.json")
    for comp in components:
        print(f"{comp['name']} {comp['version']}")
```

### Integration with SBOM Service

```python
from apps.api.services.sbom.service import SBOMService
from apps.api.services.sbom.parsers.node_parser import NodeDependencyParser

# Register parser with service
sbom_service = SBOMService()
sbom_service.register_parser(NodeDependencyParser())

# Parse any supported Node.js file
components = sbom_service.parse_dependency_file("package.json", content)
```

### Handling Multiple Files

```python
files_to_parse = [
    ("package.json", package_json_content),
    ("package-lock.json", package_lock_content),
    ("yarn.lock", yarn_lock_content),
]

all_components = []
for filename, content in files_to_parse:
    components = parser.parse(content, filename)
    all_components.extend(components)

# Merge or analyze combined results
```

### Filtering by Scope

```python
components = parser.parse(content, "package.json")

# Get only runtime dependencies
runtime_deps = [c for c in components if c["scope"] == "runtime"]

# Get only dev dependencies
dev_deps = [c for c in components if c["scope"] == "dev"]
```

## Scoped Packages

The parser correctly handles npm scoped packages:

```
@angular/core      # Scope: angular, Package: core
@types/node        # Scope: types, Package: node
@babel/core        # Scope: babel, Package: core
```

These are returned with the full scoped name:

```python
{
    "name": "@angular/core",
    "purl": "pkg:npm/@angular/core@16.0.0",
    ...
}
```

## Error Handling

The parser raises `ValueError` for:

- Invalid JSON in package.json or package-lock.json
- Invalid YAML in pnpm-lock.yaml
- Empty or whitespace-only content
- Unsupported file formats

```python
try:
    components = parser.parse(content, "package.json")
except ValueError as e:
    print(f"Failed to parse: {e}")
```

## Implementation Details

### Parsing Logic

**package.json:**
1. Parse JSON content
2. Extract dependencies from each section (dependencies, devDependencies, etc.)
3. Create component for each package with `direct: true`

**package-lock.json:**
1. Detect format version (v6 vs v7+)
2. Parse JSON content
3. Extract packages from appropriate section
4. Skip root package entry ("")
5. Create component for each package with `direct: false`

**yarn.lock:**
1. Split content into lines
2. Match package entries with regex pattern
3. Extract name and version spec from key
4. Look ahead for `resolved` line
5. Extract actual version from URL
6. Create component for each dependency

**pnpm-lock.yaml:**
1. Parse YAML content
2. Process `packages` section (with version in key)
3. Process `dependencies` and `devDependencies` sections
4. Create component for each package

### Version Normalization

Versions are normalized to remove whitespace and handle various version specification formats:

- `1.2.3` → `1.2.3`
- `  1.2.3  ` → `1.2.3`
- `^1.2.3` → `^1.2.3` (preserved)
- Empty → `None`

## Testing

Comprehensive unit tests are provided in `tests/unit/services/sbom/test_node_parser.py`:

```bash
# Run all Node.js parser tests
pytest tests/unit/services/sbom/test_node_parser.py -v

# Run specific test class
pytest tests/unit/services/sbom/test_node_parser.py::TestNodeDependencyParser::test_parse_package_json_with_dependencies -v
```

### Test Coverage

- File format detection (can_parse)
- Parsing all supported file types
- Scoped and unscoped packages
- Runtime and dev dependency classification
- Direct vs transitive dependency marking
- Error handling for invalid content
- Version extraction and normalization
- Package URL generation
- Complex scenarios with mixed dependency types

## Performance Considerations

- **package.json**: O(n) where n = number of dependencies
- **package-lock.json**: O(n) where n = total packages (including transitive)
- **yarn.lock**: O(n) with regex parsing for each entry
- **pnpm-lock.yaml**: O(n) with YAML parsing

All parsers are streaming-compatible and process files in a single pass.

## Limitations and Future Enhancements

### Current Limitations

1. **Workspaces**: Monorepo workspace dependencies not yet handled
2. **Path dependencies**: Local path dependencies return relative paths
3. **Git dependencies**: Git URLs parsed as version strings
4. **Bundled dependencies**: Not separately tracked
5. **Shrinkwrap**: npm-shrinkwrap.json not supported (planned Phase 2)

### Future Enhancements

- npm-shrinkwrap.json support
- Monorepo workspace traversal
- Dependency resolution graph
- License extraction from lock files
- Vulnerability scanning integration
- Lock file consistency validation

## Related Documentation

- [SBOM Service Documentation](./sbom-service.md)
- [Dependency Parser Architecture](./dependency-parsers.md)
- [Python Dependency Parser](./python-parser-guide.md)
- [Go Dependency Parser](./go-parser-guide.md)

## API Reference

### NodeDependencyParser Class

#### Methods

**can_parse(filename: str) -> bool**
- Check if parser can handle the file
- Args: filename (str) - Name of the dependency file
- Returns: bool - True if file is supported

**get_supported_files() -> List[str]**
- Return list of supported filenames
- Returns: List of supported file names

**parse(content: str, filename: str) -> List[Dict[str, Any]]**
- Parse dependency file and extract components
- Args:
  - content (str) - Raw file content
  - filename (str) - Name of the file
- Returns: List of component dictionaries
- Raises: ValueError if content is invalid

**validate_content(content: str) -> bool**
- Validate that content is not empty
- Args: content (str) - Content to validate
- Returns: bool - True if valid

**normalize_version(version: str) -> str**
- Normalize version strings
- Args: version (str) - Version to normalize
- Returns: str - Normalized version

## Support and Issues

For issues with the Node.js parser:

1. Check error messages for specific parsing failures
2. Validate file format matches expected structure
3. Check for unsupported dependency types
4. Review test cases for similar scenarios
5. Report issues with example files

---

**Last Updated**: 2025-12-12
**Parser Version**: 1.0.0
**Supported npm Versions**: All (v6 and v7+)
