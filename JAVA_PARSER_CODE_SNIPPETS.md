# Java Parser - Key Code Snippets

## Complete Parser Class Signature

```python
class JavaDependencyParser(BaseDependencyParser):
    """Parser for Java/Maven/Gradle dependency files.

    Handles parsing of pom.xml (Maven), build.gradle (Gradle Groovy DSL),
    and build.gradle.kts (Gradle Kotlin DSL) files to extract dependency
    information in standardized format.
    """

    # Maven POM namespace
    MAVEN_NAMESPACE = "http://maven.apache.org/POM/4.0.0"

    # Supported dependency files
    SUPPORTED_FILES = ["pom.xml", "build.gradle", "build.gradle.kts"]

    # Gradle scope to Maven scope mapping
    SCOPE_MAPPING = {
        "implementation": "runtime",
        "api": "runtime",
        "compileOnly": "provided",
        "runtimeOnly": "runtime",
        "testImplementation": "test",
        "testCompileOnly": "test",
        "testRuntimeOnly": "test",
        "providedCompile": "provided",
        "providedRuntime": "provided",
    }
```

## Maven Parsing Regex Pattern

The Maven parser uses XML parsing, but here's the conceptual pattern:

```xml
<dependency>
    <groupId>org.springframework</groupId>
    <artifactId>spring-core</artifactId>
    <version>5.3.0</version>
    <scope>compile</scope>
</dependency>
```

XML extraction with namespace support:
```python
def _get_element_text(
    self,
    element: ET.Element,
    tag_name: str,
    namespaces: Dict[str, str],
) -> Optional[str]:
    # Try with namespace first
    ns_tag = f"{{{self.MAVEN_NAMESPACE}}}{tag_name}"
    child = element.find(ns_tag)

    if child is None:
        # Try without namespace
        child = element.find(tag_name)

    if child is not None and child.text:
        return child.text.strip()

    return None
```

## Gradle Groovy DSL Regex Pattern

```regex
(\w+)\s+['\"]([^'\":]+):([^'\":]+):([^'\"]+)['\"]
```

Matches:
- `implementation 'org.springframework:spring-core:5.3.0'`
- `testImplementation "junit:junit:4.13.2"`
- `api 'org.slf4j:slf4j-api:1.7.32'`

Implementation:
```python
def _parse_gradle(self, content: str, filename: str) -> List[Dict[str, Any]]:
    dependencies: List[Dict[str, Any]] = []

    gradle_pattern = r"(\w+)\s+['\"]([^'\":]+):([^'\":]+):([^'\"]+)['\"]"
    matches = re.finditer(gradle_pattern, content)

    for match in matches:
        scope_keyword = match.group(1)      # e.g., "implementation"
        group_id = match.group(2)           # e.g., "org.springframework"
        artifact_id = match.group(3)        # e.g., "spring-core"
        version = match.group(4)            # e.g., "5.3.0"

        scope = self.SCOPE_MAPPING.get(scope_keyword, "runtime")

        component = {
            "name": f"{group_id}:{artifact_id}",
            "version": version,
            "purl": f"pkg:maven/{group_id}/{artifact_id}@{version}",
            "package_type": "maven",
            "scope": scope,
            "direct": True,
            "source_file": filename,
        }

        dependencies.append(component)

    return dependencies
```

## Gradle Kotlin DSL Regex Pattern

```regex
(\w+)\(['\"]([^'\":]+):([^'\":]+):([^'\"]+)['\"]\)
```

Matches:
- `implementation("org.springframework:spring-core:5.3.0")`
- `testImplementation('junit:junit:4.13.2')`
- `api("org.slf4j:slf4j-api:1.7.32")`

Implementation:
```python
def _parse_gradle_kts(self, content: str, filename: str) -> List[Dict[str, Any]]:
    dependencies: List[Dict[str, Any]] = []

    kotlin_pattern = r"(\w+)\(['\"]([^'\":]+):([^'\":]+):([^'\"]+)['\"]\)"
    matches = re.finditer(kotlin_pattern, content)

    for match in matches:
        scope_keyword = match.group(1)      # e.g., "implementation"
        group_id = match.group(2)           # e.g., "org.springframework"
        artifact_id = match.group(3)        # e.g., "spring-core"
        version = match.group(4)            # e.g., "5.3.0"

        scope = self.SCOPE_MAPPING.get(scope_keyword, "runtime")

        component = {
            "name": f"{group_id}:{artifact_id}",
            "version": version,
            "purl": f"pkg:maven/{group_id}/{artifact_id}@{version}",
            "package_type": "maven",
            "scope": scope,
            "direct": True,
            "source_file": filename,
        }

        dependencies.append(component)

    return dependencies
```

## Maven Property Resolution

```python
def _resolve_maven_property(self, value: str, properties: Dict[str, str]) -> str:
    """Resolve Maven property references in values.

    Replaces ${property.name} references with actual values.

    Example:
        Input: "${project.version}"
        Output: "1.0.0" (from properties dict)
    """
    if not value:
        return value

    # Handle ${project.version} and similar built-in properties
    if value == "${project.version}":
        return properties.get("project.version", "unknown")

    # Handle custom property references like ${some.property}
    def replace_property(match: re.Match[str]) -> str:
        prop_name = match.group(1)
        return properties.get(prop_name, match.group(0))

    resolved = re.sub(r"\$\{([^}]+)\}", replace_property, value)
    return resolved if resolved else "unknown"
```

## Scope Normalization

```python
def _normalize_maven_scope(self, scope: str) -> str:
    """Normalize Maven scope to standard values.

    Maps Maven scope values to standard scope keywords:
    - compile → compile
    - provided → provided
    - runtime → runtime
    - test → test
    - system → provided
    - empty/None → compile (default)
    """
    scope = scope.lower().strip() if scope else "compile"

    # Normalize known scopes
    if scope in ("compile", "provided", "runtime", "test"):
        return scope

    # Map system to provided
    if scope == "system":
        return "provided"

    # Default to compile for unknown scopes
    return "compile"
```

## Dependency Component Structure

All parsers return dependencies in this standardized format:

```python
{
    "name": "org.springframework:spring-core",        # groupId:artifactId
    "version": "5.3.0",                              # version string
    "purl": "pkg:maven/org.springframework/spring-core@5.3.0",  # Package URL
    "package_type": "maven",                         # Always "maven" for Java
    "scope": "compile",                              # One of: compile, test, provided, runtime
    "direct": True,                                  # Always True for direct dependencies
    "source_file": "pom.xml",                        # Source filename
}
```

## Maven Property Extraction

```python
def _extract_maven_properties(
    self, root: ET.Element, namespaces: Dict[str, str]
) -> Dict[str, str]:
    """Extract Maven properties for variable substitution.

    Parses <properties> section to extract property definitions:
    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <spring.version>5.3.0</spring.version>
    </properties>
    """
    properties: Dict[str, str] = {}

    # Find properties element
    props_elem = root.find(f"{{{self.MAVEN_NAMESPACE}}}properties")
    if props_elem is None:
        props_elem = root.find("properties")

    if props_elem is None:
        return properties

    # Extract all property elements
    for prop in props_elem:
        # Strip namespace from tag name
        prop_name = prop.tag
        if "}" in prop_name:
            prop_name = prop_name.split("}", 1)[1]

        if prop.text:
            properties[prop_name] = prop.text.strip()

    return properties
```

## Main Parse Method Dispatcher

```python
def parse(self, content: str, filename: str) -> List[Dict[str, Any]]:
    """Parse Java dependency file and extract components.

    Routes to appropriate parser based on filename:
    - pom.xml → _parse_maven()
    - build.gradle → _parse_gradle()
    - build.gradle.kts → _parse_gradle_kts()
    """
    if not self.validate_content(content):
        raise ValueError(f"Empty or invalid content for {filename}")

    if filename == "pom.xml":
        return self._parse_maven(content, filename)
    elif filename == "build.gradle":
        return self._parse_gradle(content, filename)
    elif filename == "build.gradle.kts":
        return self._parse_gradle_kts(content, filename)
    else:
        raise ValueError(f"Unsupported file format: {filename}")
```

## Test Example - Maven Parsing

```python
def test_parse_maven_simple_pom(self, parser: JavaDependencyParser) -> None:
    """Test parsing simple pom.xml with basic dependencies."""
    pom_content = """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <dependencies>
        <dependency>
            <groupId>org.springframework</groupId>
            <artifactId>spring-core</artifactId>
            <version>5.3.0</version>
        </dependency>
        <dependency>
            <groupId>junit</groupId>
            <artifactId>junit</artifactId>
            <version>4.13.2</version>
            <scope>test</scope>
        </dependency>
    </dependencies>
</project>
"""
    deps = parser.parse(pom_content, "pom.xml")

    assert len(deps) == 2

    spring_dep = next((d for d in deps if d["name"] == "org.springframework:spring-core"), None)
    assert spring_dep is not None
    assert spring_dep["version"] == "5.3.0"
    assert spring_dep["purl"] == "pkg:maven/org.springframework/spring-core@5.3.0"
    assert spring_dep["package_type"] == "maven"
    assert spring_dep["scope"] == "compile"
    assert spring_dep["direct"] is True
    assert spring_dep["source_file"] == "pom.xml"
```

## Test Example - Gradle Parsing

```python
def test_parse_gradle_simple(self, parser: JavaDependencyParser) -> None:
    """Test parsing simple build.gradle with dependencies."""
    gradle_content = """
dependencies {
    implementation 'org.springframework:spring-core:5.3.0'
    testImplementation 'junit:junit:4.13.2'
    api 'org.slf4j:slf4j-api:1.7.32'
}
"""
    deps = parser.parse(gradle_content, "build.gradle")

    assert len(deps) == 3

    spring_dep = next((d for d in deps if d["name"] == "org.springframework:spring-core"), None)
    assert spring_dep is not None
    assert spring_dep["version"] == "5.3.0"
    assert spring_dep["scope"] == "runtime"
```

## Integration with SBOM Service

```python
from apps.api.services.sbom.service import SBOMService
from apps.api.services.sbom.parsers.java_parser import JavaDependencyParser

# Create service and register Java parser
service = SBOMService()
service.register_parser(JavaDependencyParser())

# Parse any supported Java dependency file
with open("pom.xml", "r") as f:
    dependencies = service.parse_dependency_file("pom.xml", f.read())

# Process dependencies
for dep in dependencies:
    print(f"{dep['name']} @ {dep['version']} ({dep['scope']})")
    print(f"  PURL: {dep['purl']}")
    print(f"  From: {dep['source_file']}")
```

## Error Handling Examples

```python
# Invalid XML
try:
    parser.parse("<project><unclosed>", "pom.xml")
except ValueError as e:
    print(f"Error: {e}")  # ValueError: Invalid XML in pom.xml: ...

# Empty content
try:
    parser.parse("", "pom.xml")
except ValueError as e:
    print(f"Error: {e}")  # ValueError: Empty or invalid content for pom.xml

# Unsupported file
try:
    parser.parse("content", "Gemfile")
except ValueError as e:
    print(f"Error: {e}")  # ValueError: Unsupported file format: Gemfile
```

---

All code snippets are from the actual implementation at:
- `/home/penguin/code/Elder/apps/api/services/sbom/parsers/java_parser.py`
- `/home/penguin/code/Elder/tests/unit/test_java_parser.py`
