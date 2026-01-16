"""
Structured logging package for Elder application.
"""

# flake8: noqa: E501


from .logger import StructuredLogger, configure_logging_from_env

__all__ = ["StructuredLogger", "configure_logging_from_env"]
