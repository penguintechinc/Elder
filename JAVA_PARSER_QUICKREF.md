# Java Parser Quick Reference

## Overview

The `JavaDependencyParser` extracts dependencies from Java build files:
- **pom.xml** (Maven)
- **build.gradle** (Gradle Groovy DSL)
- **build.gradle.kts** (Gradle Kotlin DSL)

## Quick Start

```python
from apps.api.services.sbom.parsers.java_parser import JavaDependencyParser

parser = JavaDependencyParser()

# Parse any supported file
dependencies = parser.parse(file_content, "pom.xml")

# Each dependency is a dict with:
# {
#     "name": "groupId:artifactId",
#     "version": "1.0.0",
#     "purl": "pkg:maven/groupId/artifactId@1.0.0",
#     "package_type": "maven",
#     "scope": "compile|test|provided|runtime",
#     "direct": True,
#     "source_file": "pom.xml"
# }
```

## File Support

| File | Parser Status | Format |
|------|---|---------|
| pom.xml | ✓ Fully supported | XML |
| build.gradle | ✓ Fully supported | Groovy DSL |
| build.gradle.kts | ✓ Fully supported | Kotlin DSL |

## Scope Mapping

### Maven → Standard
- `compile` → `compile`
- `provided` → `provided`
- `runtime` → `runtime`
- `test` → `test`
- (none) → `compile` (default)
- `system` → `provided`

### Gradle → Standard
- `implementation` → `runtime`
- `api` → `runtime`
- `compileOnly` → `provided`
- `runtimeOnly` → `runtime`
- `testImplementation` → `test`
- `testCompileOnly` → `test`
- `testRuntimeOnly` → `test`
- `providedCompile` → `provided`
- `providedRuntime` → `provided`

## Parsing Examples

### Maven (pom.xml)
```xml
<dependency>
    <groupId>org.springframework</groupId>
    <artifactId>spring-core</artifactId>
    <version>5.3.0</version>
    <scope>compile</scope>
</dependency>
```

Result:
```python
{
    "name": "org.springframework:spring-core",
    "version": "5.3.0",
    "purl": "pkg:maven/org.springframework/spring-core@5.3.0",
    "package_type": "maven",
    "scope": "compile",
    "direct": True,
    "source_file": "pom.xml"
}
```

### Gradle (build.gradle)
```groovy
implementation 'org.springframework:spring-core:5.3.0'
testImplementation 'junit:junit:4.13.2'
```

### Gradle Kotlin (build.gradle.kts)
```kotlin
implementation("org.springframework:spring-core:5.3.0")
testImplementation("junit:junit:4.13.2")
```

## Key Methods

### can_parse(filename: str) → bool
Check if parser supports the filename.

```python
parser.can_parse("pom.xml")          # True
parser.can_parse("build.gradle")     # True
parser.can_parse("package.json")     # False
```

### get_supported_files() → List[str]
Returns list of supported filenames.

```python
parser.get_supported_files()
# ['pom.xml', 'build.gradle', 'build.gradle.kts']
```

### parse(content: str, filename: str) → List[Dict]
Parse dependency file and return component list.

```python
with open("pom.xml", "r") as f:
    deps = parser.parse(f.read(), "pom.xml")
```

## Error Handling

### ValueError: Empty or invalid content
- File is empty or contains only whitespace
- Solution: Check file exists and is readable

### ValueError: Invalid XML in pom.xml
- XML is malformed
- Solution: Validate XML syntax

### ValueError: Unsupported file format
- File type not recognized
- Solution: Use supported filenames (pom.xml, build.gradle, build.gradle.kts)

## Features

✓ Full Maven namespace support
✓ Property variable resolution (${property.name})
✓ Gradle Groovy and Kotlin DSL parsing
✓ Correct scope mapping across systems
✓ Package URL (PURL) generation
✓ Type hints and docstrings
✓ Comprehensive error handling
✓ Edge case handling (missing versions, incomplete entries)

## Integration with SBOM Service

```python
from apps.api.services.sbom.service import SBOMService
from apps.api.services.sbom.parsers.java_parser import JavaDependencyParser

service = SBOMService()
service.register_parser(JavaDependencyParser())

# Now the service can handle all Java files
deps = service.parse_dependency_file("pom.xml", content)
```

## Testing

Run tests:
```bash
pytest tests/unit/test_java_parser.py -v
```

Test coverage includes:
- File type recognition
- Maven XML parsing
- Gradle Groovy DSL parsing
- Gradle Kotlin DSL parsing
- Scope normalization
- Property resolution
- Error handling
- Edge cases

## Known Limitations

- No transitive dependency resolution
- Maven dependencyManagement not parsed
- Gradle properties not resolved
- No gradle.lock support
- Custom Gradle configurations treated as unknown

## Files

- **Parser**: `/home/penguin/code/Elder/apps/api/services/sbom/parsers/java_parser.py`
- **Tests**: `/home/penguin/code/Elder/tests/unit/test_java_parser.py`
- **Documentation**: `/home/penguin/code/Elder/docs/development/java-parser.md`

## Need Help?

See the full documentation: [java-parser.md](docs/development/java-parser.md)
