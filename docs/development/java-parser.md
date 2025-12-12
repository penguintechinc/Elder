# Java/Maven/Gradle Dependency Parser

## Overview

The `JavaDependencyParser` is a comprehensive dependency parser that extracts component information from Java project files:

- **pom.xml** - Maven project file format
- **build.gradle** - Gradle Groovy DSL build file
- **build.gradle.kts** - Gradle Kotlin DSL build file

It's part of the SBOM (Software Bill of Materials) service and provides standardized component extraction for all Java-based package formats.

## Features

- **Maven Support**: Full pom.xml parsing with XML namespace handling
- **Gradle Support**: Both Groovy and Kotlin DSL parsing via regex-based extraction
- **Scope Mapping**: Correct mapping of scopes across different build systems
- **Property Resolution**: Maven property variable substitution (${property.name})
- **Error Handling**: Graceful handling of malformed files and missing fields
- **Type Hints**: Full type annotations for IDE support and type checking
- **PURL Generation**: Package URL format generation for all dependencies

## Supported Files

| Filename | Build System | Format |
|----------|---|---------|
| `pom.xml` | Maven | XML |
| `build.gradle` | Gradle | Groovy DSL |
| `build.gradle.kts` | Gradle | Kotlin DSL |

## Output Format

All dependencies are returned as a list of dictionaries with the following structure:

```python
{
    "name": str,           # "groupId:artifactId" format (e.g., "org.springframework:spring-core")
    "version": str,        # Semantic version or "unknown"
    "purl": str,          # Package URL format "pkg:maven/{groupId}/{artifactId}@{version}"
    "package_type": str,  # Always "maven" for Java dependencies
    "scope": str,         # "runtime", "test", "provided", "compile"
    "direct": bool,       # Always True (indicates direct dependency)
    "source_file": str,   # Filename of the parsed file
}
```

## Scope Mapping

### Maven Scopes

Maven has 6 standard scopes:

| Maven Scope | Description | Use Case |
|---|---|---|
| `compile` | Default scope | Included in all classpaths |
| `provided` | Required at compile time but provided at runtime | Servlet API, JDK modules |
| `runtime` | Not required for compilation | JDBC driver, SLF4J implementation |
| `test` | Only for testing | JUnit, Mockito |
| `system` | Like provided but from filesystem | Treated as `provided` |
| (none) | Defaults to `compile` | - |

### Gradle Scopes

Gradle uses a more flexible dependency configuration system. Common configurations mapped to Maven scopes:

| Gradle Configuration | Mapped Maven Scope | Purpose |
|---|---|---|
| `implementation` | `runtime` | Standard compile & runtime dependency |
| `api` | `runtime` | Exposed to consumers (like provided + implementation) |
| `compileOnly` | `provided` | Only needed for compilation |
| `runtimeOnly` | `runtime` | Only needed at runtime |
| `testImplementation` | `test` | Testing only |
| `testCompileOnly` | `test` | Testing compilation only |
| `testRuntimeOnly` | `test` | Testing runtime only |
| `providedCompile` | `provided` | Provided at compile time |
| `providedRuntime` | `provided` | Provided at runtime |

## Usage Examples

### Basic Usage

```python
from apps.api.services.sbom.parsers.java_parser import JavaDependencyParser

parser = JavaDependencyParser()

# Check if parser can handle a file
if parser.can_parse("pom.xml"):
    with open("pom.xml", "r") as f:
        content = f.read()

    dependencies = parser.parse(content, "pom.xml")
    for dep in dependencies:
        print(f"{dep['name']} @ {dep['version']}")
```

### Integration with SBOM Service

```python
from apps.api.services.sbom.service import SBOMService
from apps.api.services.sbom.parsers.java_parser import JavaDependencyParser

service = SBOMService()
service.register_parser(JavaDependencyParser())

# Parse a Maven pom.xml
with open("pom.xml", "r") as f:
    dependencies = service.parse_dependency_file("pom.xml", f.read())
```

### Maven Example

```xml
<!-- pom.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <groupId>com.example</groupId>
    <artifactId>my-app</artifactId>
    <version>1.0.0</version>

    <dependencies>
        <!-- Compile scope (default) -->
        <dependency>
            <groupId>org.springframework</groupId>
            <artifactId>spring-core</artifactId>
            <version>5.3.0</version>
        </dependency>

        <!-- Test scope -->
        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
            <version>4.13.2</version>
            <scope>test</scope>
        </dependency>

        <!-- Provided scope -->
        <dependency>
            <groupId>javax.servlet</groupId>
            <artifactId>javax.servlet-api</artifactId>
            <version>4.0.1</version>
            <scope>provided</scope>
        </dependency>
    </dependencies>
</project>
```

Parsed output:
```python
[
    {
        "name": "org.springframework:spring-core",
        "version": "5.3.0",
        "purl": "pkg:maven/org.springframework/spring-core@5.3.0",
        "package_type": "maven",
        "scope": "compile",
        "direct": True,
        "source_file": "pom.xml",
    },
    {
        "name": "junit:junit",
        "version": "4.13.2",
        "purl": "pkg:maven/junit/junit@4.13.2",
        "package_type": "maven",
        "scope": "test",
        "direct": True,
        "source_file": "pom.xml",
    },
    # ...
]
```

### Gradle Groovy DSL Example

```groovy
// build.gradle
dependencies {
    implementation 'org.springframework:spring-core:5.3.0'

    // Gradle maps to test scope
    testImplementation 'junit:junit:4.13.2'

    // Gradle API dependencies exposed to consumers
    api 'org.slf4j:slf4j-api:1.7.32'

    // Provided at compile time only
    compileOnly 'com.google.code.findbugs:annotations:3.0.1'
}
```

### Gradle Kotlin DSL Example

```kotlin
// build.gradle.kts
dependencies {
    implementation("org.springframework:spring-core:5.3.0")

    testImplementation("junit:junit:4.13.2")

    api("org.slf4j:slf4j-api:1.7.32")

    compileOnly("com.google.code.findbugs:annotations:3.0.1")
}
```

## Implementation Details

### Maven Parsing (pom.xml)

1. **XML Parsing**: Uses `xml.etree.ElementTree` for robust XML parsing
2. **Namespace Handling**: Properly handles Maven POM namespace (`http://maven.apache.org/POM/4.0.0`)
3. **Property Resolution**: Extracts and resolves `<properties>` section variables
4. **Version Fallback**: Uses "unknown" for missing versions
5. **Scope Normalization**: Validates and normalizes scope values

**Implementation Features**:
- Safe XML element text extraction with namespace support
- Property variable substitution (`${property.name}`)
- Graceful handling of malformed dependencies (skips incomplete entries)
- Exception handling with informative error messages

### Gradle Parsing (build.gradle)

Uses regex-based extraction to parse Groovy DSL:

```regex
(\w+)\s+['\"]([^'\":]+):([^'\":]+):([^'\"]+)['\"]
```

**Captures**:
1. Configuration name (e.g., `implementation`, `testImplementation`)
2. Group ID (e.g., `org.springframework`)
3. Artifact ID (e.g., `spring-core`)
4. Version (e.g., `5.3.0`)

**Features**:
- Supports both single and double quotes
- Handles whitespace variations
- Maps to standard Maven scopes

### Gradle Kotlin DSL Parsing (build.gradle.kts)

Uses regex-based extraction for Kotlin function calls:

```regex
(\w+)\(['\"]([^'\":]+):([^'\":]+):([^'\"]+)['\"]\)
```

**Captures**: Same as Groovy, but matching Kotlin function call syntax.

**Features**:
- Matches `configuration(...)` function call syntax
- Supports both single and double quotes
- Handles scope mapping identically to Groovy

## Error Handling

The parser implements robust error handling:

### ValueError Exceptions

**Empty Content**:
```python
raise ValueError(f"Empty or invalid content for {filename}")
```

**Invalid XML**:
```python
raise ValueError(f"Invalid XML in {filename}: {str(e)}")
```

**Unsupported Format**:
```python
raise ValueError(f"Unsupported file format: {filename}")
```

### Graceful Degradation

- Missing scope defaults to `compile` (Maven standard)
- Missing version uses `unknown`
- Malformed dependencies are silently skipped (logging not yet implemented)
- Invalid XML raises exception for safety

## Testing

Comprehensive unit tests cover:

- ✓ File type recognition (`can_parse()`)
- ✓ Maven pom.xml parsing with various scopes
- ✓ Gradle build.gradle parsing
- ✓ Gradle Kotlin DSL build.gradle.kts parsing
- ✓ Invalid XML handling
- ✓ Empty/missing fields
- ✓ Property resolution
- ✓ Scope normalization
- ✓ PURL generation
- ✓ Edge cases and whitespace handling

Run tests with:
```bash
pytest tests/unit/test_java_parser.py -v
```

## Performance Notes

- **Maven**: O(n) where n = number of dependencies (XML parsing)
- **Gradle**: O(n) where n = file size (regex matching)
- **Memory**: Minimal overhead for dependency storage
- **Suitable for**: Projects with hundreds of dependencies

## Known Limitations

1. **Gradle Properties**: Property substitution in Gradle files not yet implemented
2. **Transitive Dependencies**: Only direct dependencies are parsed (gradlelock/lock files not supported)
3. **BOM Import**: Maven `<dependencyManagement>` import POM items not yet resolved
4. **Custom Scopes**: Gradle custom configurations are treated as unknown
5. **Multiline Dependencies**: Gradle dependencies split across lines may not parse correctly

## Future Enhancements

- [ ] Support for `maven-metadata.xml` (transitive dependencies)
- [ ] Gradle `.lock` file parsing for complete dependency tree
- [ ] Maven `<dependencyManagement>` section parsing
- [ ] Property resolution in Gradle files
- [ ] Plugin dependency extraction
- [ ] Repository configuration tracking
- [ ] Classifier support (e.g., `classifier: "sources"`)
- [ ] Exclusion handling for transitive dependencies

## Related Files

- Parser: `/home/penguin/code/Elder/apps/api/services/sbom/parsers/java_parser.py`
- Tests: `/home/penguin/code/Elder/tests/unit/test_java_parser.py`
- Base Class: `/home/penguin/code/Elder/apps/api/services/sbom/base.py`
- SBOM Service: `/home/penguin/code/Elder/apps/api/services/sbom/service.py`

## References

- [Maven POM Reference](https://maven.apache.org/pom.html)
- [Gradle Dependencies Documentation](https://docs.gradle.org/current/userguide/dependency_management.html)
- [Package URL Specification](https://github.com/package-url/purl-spec)
