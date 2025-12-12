#!/usr/bin/env python3
"""Manual test script for Java parser."""

from apps.api.services.sbom.parsers.java_parser import JavaDependencyParser

# Test Maven parsing
parser = JavaDependencyParser()

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
print(f"✓ Maven parsing successful: {len(deps)} dependencies found")
for dep in deps:
    print(f"  - {dep['name']} {dep['version']} (scope: {dep['scope']})")

# Test Gradle parsing
gradle_content = """
dependencies {
    implementation 'org.springframework:spring-core:5.3.0'
    testImplementation 'junit:junit:4.13.2'
    api 'org.slf4j:slf4j-api:1.7.32'
}
"""

deps = parser.parse(gradle_content, "build.gradle")
print(f"✓ Gradle parsing successful: {len(deps)} dependencies found")
for dep in deps:
    print(f"  - {dep['name']} {dep['version']} (scope: {dep['scope']})")

# Test Gradle Kotlin DSL parsing
gradle_kts_content = """
dependencies {
    implementation("org.springframework:spring-core:5.3.0")
    testImplementation("junit:junit:4.13.2")
    api("org.slf4j:slf4j-api:1.7.32")
}
"""

deps = parser.parse(gradle_kts_content, "build.gradle.kts")
print(f"✓ Gradle Kotlin DSL parsing successful: {len(deps)} dependencies found")
for dep in deps:
    print(f"  - {dep['name']} {dep['version']} (scope: {dep['scope']})")

print("\n✓ All parser tests passed!")
