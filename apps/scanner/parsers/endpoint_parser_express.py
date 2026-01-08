"""
Express.js endpoint parser for detecting routes in JavaScript/TypeScript source code.
"""

# flake8: noqa: E501


import re
from typing import Dict, List, Optional


class ExpressEndpointParser:
    """Parser for Express.js route definitions."""

    def __init__(self):
        """Initialize the Express endpoint parser."""
        # Pattern for method-specific routes: app.get('/path', handler)
        self.method_pattern = re.compile(
            r"(?:app|router)\.(get|post|put|delete|patch|options|head)"
            r'\s*\(\s*[\'"]([^\'"]+)[\'"]'
        )

        # Pattern for app.use('/path', router)
        self.use_pattern = re.compile(r'(?:app|router)\.use\s*\(\s*[\'"]([^\'"]+)[\'"]')

        # Pattern for app.route('/path').get().post()
        self.route_chain_pattern = re.compile(
            r'(?:app|router)\.route\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
            r"((?:\s*\.\s*(?:get|post|put|delete|patch|options|head)\s*\([^)]*\))+)"
        )

        # Pattern for chained methods
        self.chain_method_pattern = re.compile(
            r"\.\s*(get|post|put|delete|patch|options|head)\s*\("
        )

        # Pattern for handler function names
        self.handler_pattern = re.compile(
            r"(?:function\s+(\w+)|(\w+)\s*(?:=|:)\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>))"
        )

    def can_parse(self, filename: str) -> bool:
        """
        Check if this parser can handle the given file.

        Args:
            filename: Name of the file to check

        Returns:
            True if file is JavaScript/TypeScript
        """
        return filename.endswith((".js", ".ts", ".mjs", ".tsx", ".jsx"))

    def parse(self, content: str, filename: str) -> List[Dict]:
        """
        Parse Express.js routes from source code.

        Args:
            content: File content to parse
            filename: Name of the source file

        Returns:
            List of endpoint dictionaries
        """
        endpoints = []
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            # Skip comments
            if line.strip().startswith("//") or line.strip().startswith("*"):
                continue

            # Parse method-specific routes
            endpoints.extend(self._parse_method_routes(line, line_num, filename))

            # Parse app.use() routes
            endpoints.extend(self._parse_use_routes(line, line_num, filename))

            # Parse chained routes
            endpoints.extend(self._parse_chained_routes(line, line_num, filename))

        return endpoints

    def _parse_method_routes(
        self, line: str, line_num: int, filename: str
    ) -> List[Dict]:
        """Parse method-specific routes like app.get('/path', handler)."""
        endpoints = []

        for match in self.method_pattern.finditer(line):
            method = match.group(1).upper()
            path = match.group(2)

            # Convert Express path params to OpenAPI format
            path = self._convert_path_params(path)

            # Check for middleware
            has_middleware = self._detect_middleware(line, match.end())

            # Try to find handler name
            handler_name = self._find_handler_name(line, match.end())

            endpoint = {
                "path": path,
                "methods": [method],
                "handler_name": handler_name,
                "line_number": line_num,
                "framework": "express",
                "source_file": filename,
                "has_middleware": has_middleware,
            }
            endpoints.append(endpoint)

        return endpoints

    def _parse_use_routes(self, line: str, line_num: int, filename: str) -> List[Dict]:
        """Parse app.use('/path', router) routes."""
        endpoints = []

        for match in self.use_pattern.finditer(line):
            path = match.group(1)
            path = self._convert_path_params(path)

            # app.use() can handle all methods
            endpoint = {
                "path": path,
                "methods": ["ALL"],
                "handler_name": "middleware",
                "line_number": line_num,
                "framework": "express",
                "source_file": filename,
                "has_middleware": True,
            }
            endpoints.append(endpoint)

        return endpoints

    def _parse_chained_routes(
        self, line: str, line_num: int, filename: str
    ) -> List[Dict]:
        """Parse chained routes like app.route('/path').get().post()."""
        endpoints = []

        for match in self.route_chain_pattern.finditer(line):
            path = match.group(1)
            chain = match.group(2)

            path = self._convert_path_params(path)

            # Extract all methods from the chain
            methods = []
            for method_match in self.chain_method_pattern.finditer(chain):
                methods.append(method_match.group(1).upper())

            if methods:
                endpoint = {
                    "path": path,
                    "methods": methods,
                    "handler_name": "chained_handlers",
                    "line_number": line_num,
                    "framework": "express",
                    "source_file": filename,
                    "has_middleware": False,
                }
                endpoints.append(endpoint)

        return endpoints

    def _convert_path_params(self, path: str) -> str:
        """
        Convert Express path parameters to OpenAPI format.

        Args:
            path: Express path with :param syntax

        Returns:
            Path with {param} syntax
        """
        # Convert :param to {param}
        return re.sub(r":(\w+)", r"{\1}", path)

    def _detect_middleware(self, line: str, start_pos: int) -> bool:
        """
        Detect if middleware functions are present.

        Args:
            line: Line to check
            start_pos: Position to start checking from

        Returns:
            True if middleware detected
        """
        # Look for comma-separated functions before the final handler
        remainder = line[start_pos:]
        # Count commas (if > 1, there are middleware functions)
        return remainder.count(",") > 1

    def _find_handler_name(self, line: str, start_pos: int) -> Optional[str]:
        """
        Try to find the handler function name.

        Args:
            line: Line to search
            start_pos: Position to start searching from

        Returns:
            Handler name if found, None otherwise
        """
        remainder = line[start_pos:]

        # Look for simple function references
        simple_ref = re.search(r",\s*(\w+)\s*[,)]", remainder)
        if simple_ref:
            return simple_ref.group(1)

        # Look for inline function definitions
        inline_func = re.search(
            r"(?:function\s+(\w+)|async\s+(?:function\s+)?(\w+))", remainder
        )
        if inline_func:
            return inline_func.group(1) or inline_func.group(2)

        # Look for arrow functions with names
        arrow_func = re.search(r"(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>", remainder)
        if arrow_func:
            return arrow_func.group(1)

        return None
