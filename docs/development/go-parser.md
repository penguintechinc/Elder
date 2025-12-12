# Go Dependency Parser Documentation

## Overview

The Go dependency parser (`GoParser`) is a component of the Elder SBOM (Software Bill of Materials) service that parses and extracts dependency information from Go module files (`go.mod` and `go.sum`).

## Supported Files

- **go.mod**: Go module definition file containing module declaration, version requirements, and directives
- **go.sum**: Go checksum file containing module versions and their cryptographic hashes for verification

## Features

### go.mod Parsing

The parser handles both single-line and multi-line `require` blocks:

**Single-line format:**
```go
require github.com/gin-gonic/gin v1.9.1
```

**Multi-line block format:**
```go
require (
    github.com/gin-gonic/gin v1.9.1
    github.com/stretchr/testify v1.8.4 // indirect
)
```

### Indirect Dependency Detection

Dependencies marked with the `// indirect` comment are automatically detected and flagged as indirect:

```go
require github.com/google/uuid v1.3.0 // indirect
```

The parser sets the `direct` field to `False` for these dependencies.

### Version Format Support

The parser handles various Go version formats:

- **Semantic versions**: `v1.9.1`, `v0.1.0`
- **Pre-release versions**: `v1.9.0-beta.1`, `v1.10.9-rc.1`
- **Pseudo-versions**: `v0.0.0-20240101120000-abcdef123456`

### go.sum Parsing

The go.sum file is parsed for hash verification. Each entry is extracted with:
- Module path
- Version
- Cryptographic hash (h1:...)

### Package URL (PURL) Generation

Dependencies are converted to Package URL (PURL) format for standardized identification:

```
pkg:golang/github.com/gin-gonic/gin@v1.9.1
```

## Output Format

The parser returns a list of dictionaries with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `name` | str | Module path (e.g., `github.com/gin-gonic/gin`) |
| `version` | str | Semantic version with v prefix (e.g., `v1.9.1`) |
| `purl` | str | Package URL in format `pkg:golang/{name}@{version}` |
| `package_type` | str | Always `"go"` |
| `scope` | str | Always `"runtime"` (Go has no dev/prod distinction) |
| `direct` | bool | `True` for direct requires, `False` for indirect |
| `source_file` | str | Source filename (`"go.mod"` or `"go.sum"`) |
| `hash` | str | (Optional) Cryptographic hash from go.sum |

## Implementation Details

### Class: GoParser

```python
from apps.api.services.sbom.parsers.go_parser import GoParser

parser = GoParser()
```

### Methods

#### `can_parse(filename: str) -> bool`

Checks if the parser can handle a given file.

```python
parser.can_parse("go.mod")   # Returns True
parser.can_parse("go.sum")   # Returns True
parser.can_parse("go.yaml")  # Returns False
```

#### `get_supported_files() -> List[str]`

Returns the list of supported files.

```python
files = parser.get_supported_files()
# Returns: ['go.mod', 'go.sum']
```

#### `parse(content: str, filename: str) -> List[Dict[str, Any]]`

Parses file content and returns dependency information.

```python
content = open('go.mod').read()
dependencies = parser.parse(content, 'go.mod')

for dep in dependencies:
    print(f"{dep['name']} {dep['version']}")
```

## Integration with SBOMService

The parser integrates with the SBOM service for standardized dependency parsing:

```python
from apps.api.services.sbom.service import SBOMService
from apps.api.services.sbom.parsers.go_parser import GoParser

# Initialize service
service = SBOMService()
service.register_parser(GoParser())

# Parse go.mod file
deps = service.parse_dependency_file('go.mod', content)
```

## Usage Examples

### Parsing go.mod

```python
from apps.api.services.sbom.parsers.go_parser import GoParser

parser = GoParser()

go_mod_content = """
module github.com/example/myapp

require (
    github.com/gin-gonic/gin v1.9.1
    github.com/lib/pq v1.10.9
    github.com/google/uuid v1.3.0 // indirect
)
"""

dependencies = parser.parse(go_mod_content, "go.mod")

for dep in dependencies:
    print(f"Name: {dep['name']}")
    print(f"Version: {dep['version']}")
    print(f"Direct: {dep['direct']}")
    print(f"PURL: {dep['purl']}")
    print()
```

### Parsing go.sum

```python
go_sum_content = """
github.com/gin-gonic/gin v1.9.1 h1:SHw5L5ZWnOTpHxzKgwl=
github.com/lib/pq v1.10.9 h1:EqnZf1oMVESDkLsrCN=
"""

dependencies = parser.parse(go_sum_content, "go.sum")

for dep in dependencies:
    print(f"{dep['name']} {dep['version']}")
    print(f"Hash: {dep.get('hash', 'N/A')}")
```

## Directives Handling

The parser recognizes these go.mod directives:

| Directive | Action |
|-----------|--------|
| `require` | Parsed and included in output |
| `replace` | Parsed but not included in output (informational) |
| `exclude` | Parsed but not included in output (informational) |
| `go` | Ignored (version statement) |

## Error Handling

The parser raises `ValueError` in these cases:

- Empty or whitespace-only content
- Unsupported file type
- Malformed file content

```python
try:
    parser.parse("", "go.mod")
except ValueError as e:
    print(f"Error: {e}")
```

## Testing

The parser includes comprehensive unit tests in `tests/unit/test_sbom_go_parser.py`:

- File type detection
- Single-line and multi-line parsing
- Indirect dependency detection
- PURL generation
- Version format handling
- Error cases
- Integration with SBOMService

### Running Tests

```bash
# Run all Go parser tests
docker compose exec api python -m pytest tests/unit/test_sbom_go_parser.py -v

# Run specific test class
docker compose exec api python -m pytest tests/unit/test_sbom_go_parser.py::TestGoParserParseGoMod -v

# Run specific test method
docker compose exec api python -m pytest tests/unit/test_sbom_go_parser.py::TestGoParserParseGoMod::test_parse_require_block -v
```

## Performance Considerations

- **go.mod files**: Typical go.mod files parse in milliseconds using regex-based parsing
- **go.sum files**: Large go.sum files (thousands of entries) parse efficiently with single-pass regex matching
- **Memory**: Minimal memory usage - dependencies stored as simple dictionaries

## Future Enhancements

Potential improvements for future versions:

1. **Go version handling**: Parse and validate `go` directive for Go version compatibility
2. **Replace directive analysis**: Track and report module replacements for build debugging
3. **Pseudo-version expansion**: Decode timestamp and commit hash from pseudo-versions
4. **Dependency graph analysis**: Build and analyze module dependency graph
5. **Version constraint validation**: Parse version constraints (if added to go.mod)
6. **Cache optimization**: Implement caching for large repository scans

## Related Files

- **Parser implementation**: `/home/penguin/code/Elder/apps/api/services/sbom/parsers/go_parser.py`
- **Base class**: `/home/penguin/code/Elder/apps/api/services/sbom/base.py`
- **SBOM service**: `/home/penguin/code/Elder/apps/api/services/sbom/service.py`
- **Unit tests**: `/home/penguin/code/Elder/tests/unit/test_sbom_go_parser.py`

## References

- [Go Modules Documentation](https://golang.org/doc/modules)
- [go.mod File Format](https://golang.org/doc/modules/gomod-ref)
- [go.sum Format](https://golang.org/cmd/go/#hdr-Module_authentication_using_go_sum)
- [Package URL (PURL) Specification](https://github.com/package-url/purl-spec)
