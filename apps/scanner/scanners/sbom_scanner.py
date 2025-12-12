"""SBOM scanner for analyzing git repositories and extracting dependencies."""

import asyncio
import logging
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import BaseScanner

logger = logging.getLogger("scanner.sbom")


class SBOMScanner(BaseScanner):
    """SBOM scanner that clones git repos and extracts dependencies using parsers."""

    # Mapping of file patterns to their package types
    DEPENDENCY_FILES = {
        # Python
        "requirements.txt": "python",
        "requirements-*.txt": "python",
        "pyproject.toml": "python",
        "Pipfile": "python",
        "Pipfile.lock": "python",
        "setup.py": "python",
        "setup.cfg": "python",
        "poetry.lock": "python",
        # Node.js
        "package.json": "node",
        "package-lock.json": "node",
        "yarn.lock": "node",
        "pnpm-lock.yaml": "node",
        # Go
        "go.mod": "go",
        "go.sum": "go",
        # Rust
        "Cargo.toml": "rust",
        "Cargo.lock": "rust",
        # Java
        "pom.xml": "java",
        "build.gradle": "java",
        "build.gradle.kts": "java",
        "gradle.lockfile": "java",
        # .NET
        "*.csproj": "dotnet",
        "*.fsproj": "dotnet",
        "packages.config": "dotnet",
        "Directory.Packages.props": "dotnet",
        # Ruby
        "Gemfile": "ruby",
        "Gemfile.lock": "ruby",
    }

    async def scan(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute SBOM scan on a git repository.

        Config schema:
        {
            "repository_url": "https://github.com/user/repo",  # Required
            "repository_branch": "main",                       # Optional, default: main
            "api_url": "http://api:5000",                      # Required for parser API
            "scan_id": 123,                                    # Scan job ID
        }

        Returns:
            {
                "success": true,
                "components": [
                    {
                        "name": "flask",
                        "version": "2.3.0",
                        "purl": "pkg:pypi/flask@2.3.0",
                        "package_type": "pypi",
                        "scope": "runtime",
                        "direct": true,
                        "source_file": "requirements.txt"
                    }
                ],
                "files_scanned": ["requirements.txt", "package.json"],
                "commit_hash": "abc123...",
                "scan_duration_ms": 5432
            }
        """
        self.validate_config(config, ["repository_url", "api_url", "scan_id"])

        start_time = time.time()
        repository_url = config["repository_url"]
        repository_branch = config.get("repository_branch", "main")
        api_url = config["api_url"].rstrip("/")

        # Create temp directory for clone
        temp_dir = tempfile.mkdtemp(prefix="sbom_scan_")

        try:
            logger.info(
                f"Cloning repository {repository_url} (branch: {repository_branch})"
            )

            # Clone repository (shallow for speed)
            clone_result = await self._clone_repository(
                repository_url, repository_branch, temp_dir
            )

            if not clone_result["success"]:
                return {
                    "success": False,
                    "error": clone_result.get("error", "Clone failed"),
                    "scan_duration_ms": int((time.time() - start_time) * 1000),
                }

            commit_hash = clone_result.get("commit_hash")

            # Find all dependency files
            logger.info(f"Scanning for dependency files in {temp_dir}")
            dependency_files = self._find_dependency_files(temp_dir)

            if not dependency_files:
                logger.warning("No dependency files found")
                return {
                    "success": True,
                    "components": [],
                    "files_scanned": [],
                    "commit_hash": commit_hash,
                    "scan_duration_ms": int((time.time() - start_time) * 1000),
                }

            logger.info(f"Found {len(dependency_files)} dependency file(s)")

            # Parse each file using API parsers
            all_components = []
            files_scanned = []

            for dep_file in dependency_files:
                logger.info(f"Parsing {dep_file['filename']}")

                # Read file content
                try:
                    with open(dep_file["path"], "r", encoding="utf-8") as f:
                        content = f.read()
                except Exception as e:
                    logger.error(f"Failed to read {dep_file['path']}: {e}")
                    continue

                # Parse using API
                components = await self._parse_file_via_api(
                    api_url, dep_file["filename"], content, dep_file["ecosystem"]
                )

                if components:
                    all_components.extend(components)
                    files_scanned.append(dep_file["filename"])

            # Deduplicate components by (name, version)
            unique_components = {}
            for comp in all_components:
                key = (comp["name"], comp.get("version"))
                if key not in unique_components:
                    unique_components[key] = comp

            scan_duration_ms = int((time.time() - start_time) * 1000)

            logger.info(
                f"Scan complete: {len(unique_components)} components from {len(files_scanned)} files"
            )

            return {
                "success": True,
                "components": list(unique_components.values()),
                "files_scanned": files_scanned,
                "commit_hash": commit_hash,
                "scan_duration_ms": scan_duration_ms,
            }

        except Exception as e:
            logger.error(f"SBOM scan failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "scan_duration_ms": int((time.time() - start_time) * 1000),
            }

        finally:
            # Cleanup temp directory
            if os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    logger.warning(f"Failed to cleanup temp dir {temp_dir}: {e}")

    async def _clone_repository(
        self, repo_url: str, branch: str, dest_dir: str
    ) -> Dict[str, Any]:
        """Clone git repository using subprocess.

        Returns:
            {"success": true, "commit_hash": "abc123"}
            or
            {"success": false, "error": "message"}
        """
        # Sanitize repository URL (remove embedded credentials)
        sanitized_url = self._sanitize_git_url(repo_url)

        cmd = [
            "git",
            "clone",
            "--depth=1",  # Shallow clone for speed
            "--branch",
            branch,
            "--single-branch",
            sanitized_url,
            dest_dir,
        ]

        try:
            # Run git clone
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_msg = stderr.decode("utf-8", errors="replace")
                logger.error(f"Git clone failed: {error_msg}")
                return {"success": False, "error": f"Git clone failed: {error_msg}"}

            # Get commit hash
            commit_hash = await self._get_commit_hash(dest_dir)

            return {"success": True, "commit_hash": commit_hash}

        except Exception as e:
            logger.error(f"Git clone exception: {e}")
            return {"success": False, "error": str(e)}

    async def _get_commit_hash(self, repo_dir: str) -> Optional[str]:
        """Get current commit hash from cloned repository."""
        try:
            process = await asyncio.create_subprocess_exec(
                "git",
                "-C",
                repo_dir,
                "rev-parse",
                "HEAD",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                return stdout.decode("utf-8").strip()

        except Exception as e:
            logger.warning(f"Failed to get commit hash: {e}")

        return None

    def _sanitize_git_url(self, url: str) -> str:
        """Remove embedded credentials from git URL.

        Example:
            https://user:pass@github.com/repo.git -> https://github.com/repo.git
        """
        # Match URLs with embedded credentials
        pattern = r"(https?://)[^@]+@(.*)"
        match = re.match(pattern, url)

        if match:
            protocol, rest = match.groups()
            return f"{protocol}{rest}"

        return url

    def _find_dependency_files(self, root_dir: str) -> List[Dict[str, Any]]:
        """Recursively find all dependency files in directory.

        Returns:
            [
                {
                    "path": "/path/to/requirements.txt",
                    "filename": "requirements.txt",
                    "ecosystem": "python"
                }
            ]
        """
        found_files = []
        root_path = Path(root_dir)

        for pattern, ecosystem in self.DEPENDENCY_FILES.items():
            # Handle wildcard patterns
            if "*" in pattern:
                # Convert to glob pattern
                glob_pattern = f"**/{pattern}"
                matches = root_path.glob(glob_pattern)
            else:
                # Exact filename match
                glob_pattern = f"**/{pattern}"
                matches = root_path.glob(glob_pattern)

            for match in matches:
                # Skip hidden directories and common exclusions
                parts = match.parts
                if any(
                    p.startswith(".")
                    or p
                    in ["node_modules", "vendor", ".git", "__pycache__", "venv", "env"]
                    for p in parts
                ):
                    continue

                found_files.append(
                    {
                        "path": str(match),
                        "filename": match.name,
                        "ecosystem": ecosystem,
                    }
                )

        return found_files

    async def _parse_file_via_api(
        self, api_url: str, filename: str, content: str, ecosystem: str
    ) -> List[Dict[str, Any]]:
        """Parse dependency file by calling Elder API parser endpoint.

        This delegates parsing to the API's parser service which has all
        the ecosystem-specific parsers available.

        Note: In a real implementation, this would make an HTTP request to
        an API endpoint that invokes the appropriate parser. For now, we'll
        import and use parsers directly.
        """
        try:
            # Import parsers dynamically
            from apps.api.services.sbom.parsers import (
                DotnetParser,
                GoParser,
                JavaDependencyParser,
                NodeDependencyParser,
                PythonDependencyParser,
                RustDependencyParser,
            )

            # Map ecosystems to parser classes
            parser_map = {
                "python": PythonDependencyParser,
                "node": NodeDependencyParser,
                "go": GoParser,
                "rust": RustDependencyParser,
                "java": JavaDependencyParser,
                "dotnet": DotnetParser,
            }

            parser_class = parser_map.get(ecosystem)
            if not parser_class:
                logger.warning(f"No parser available for ecosystem: {ecosystem}")
                return []

            parser = parser_class()

            if not parser.can_parse(filename):
                logger.warning(f"Parser cannot handle file: {filename}")
                return []

            components = parser.parse(content, filename)
            return components

        except Exception as e:
            logger.error(f"Parser failed for {filename}: {e}")
            return []
