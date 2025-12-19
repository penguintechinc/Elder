"""
Pydantic 2 integration module for py_libs.

Provides custom base models for Elder applications and custom Annotated types that
integrate with py_libs.validation validators for seamless Pydantic model validation.

Features:
- Base models with Elder-specific configuration (ElderBaseModel, ImmutableModel, RequestModel, ConfigurableModel)
- Pre-built Annotated types for common use cases (email, URL, IP, hostname)
- Factory functions for customizable types (strong_password, bounded_str)
- Full integration with py_libs.validation IS_* validators
- No breaking changes to existing validation code

Usage:
    from pydantic import BaseModel
    from py_libs.pydantic import (
        ElderBaseModel,
        RequestModel,
        EmailStr,
        StrongPassword,
        Name255,
    )

    class UserRequest(RequestModel):
        email: EmailStr
        password: StrongPassword
        name: Name255

    user = UserRequest(
        email="user@example.com",
        password="SecureP@ss123",
        name="John Doe"
    )
"""

# Base Models
from py_libs.pydantic.base import (
    ConfigurableModel,
    ElderBaseModel,
    ImmutableModel,
    RequestModel,
)

# Type Aliases
from py_libs.pydantic.types import (
    Description1000,
    EmailStr,
    HostnameStr,
    IPAddressStr,
    IPv4Str,
    IPv6Str,
    ModeratePassword,
    Name255,
    NonEmptyStr,
    ShortText100,
    SlugStr,
    StrongPassword,
    URLStr,
    bounded_str,
    strong_password,
)

__all__ = [
    # Base Models
    "ElderBaseModel",
    "ImmutableModel",
    "RequestModel",
    "ConfigurableModel",
    # Basic types
    "EmailStr",
    "URLStr",
    "IPAddressStr",
    "IPv4Str",
    "IPv6Str",
    "HostnameStr",
    "NonEmptyStr",
    "SlugStr",
    # Factory functions
    "strong_password",
    "bounded_str",
    # Pre-built password types
    "StrongPassword",
    "ModeratePassword",
    # Pre-built text length types
    "Name255",
    "Description1000",
    "ShortText100",
]
