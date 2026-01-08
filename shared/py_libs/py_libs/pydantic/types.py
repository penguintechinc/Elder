"""
Custom Pydantic 2 Annotated types for string validation.

Provides a collection of pre-built Annotated types and factory functions
that integrate with the py_libs.validation module's IS_* validators.

These types work alongside (not replace) the existing IS_* validators and
use Pydantic's Annotated pattern with AfterValidator for seamless integration.

Usage:
    from pydantic import BaseModel
    from py_libs.pydantic.types import EmailStr, StrongPassword, Name255

    class User(BaseModel):
        email: EmailStr
        password: StrongPassword
        name: Name255

    # Pydantic will automatically validate using the IS_* validators
    user = User(email="user@example.com", password="SecureP@ss123", name="John Doe")
"""
# flake8: noqa: E501


from __future__ import annotations

from typing import Annotated

from py_libs.validation import (IsEmail, IsHostname, IsIPAddress, IsLength,
                                IsNotEmpty, IsSlug, IsStrongPassword, IsURL,
                                PasswordOptions)
from pydantic import AfterValidator


def _validate_with_is_validator(validator_instance) -> callable:
    """
    Create a Pydantic validator function from an IS_* validator.

    Args:
        validator_instance: An instance of an IS_* validator class

    Returns:
        A validator function compatible with Pydantic's AfterValidator
    """

    def validate(value: str) -> str:
        result = validator_instance(value)
        if not result.is_valid:
            raise ValueError(result.error or "Validation failed")
        return result.value

    return validate


# Basic string types

EmailStr = Annotated[str, AfterValidator(_validate_with_is_validator(IsEmail()))]
"""
Email address string type.

Validates RFC 5322 compliant email addresses and normalizes to lowercase.
Enforces max length of 254 characters per RFC specification.

Example:
    user: EmailStr = "user@example.com"  # Valid
    user: EmailStr = "invalid-email"     # Raises ValidationError
"""

URLStr = Annotated[str, AfterValidator(_validate_with_is_validator(IsURL()))]
"""
URL string type.

Validates URLs with http/https schemes and requires TLD by default.
Enforces proper URL structure with scheme, netloc, and optional path/query.

Example:
    url: URLStr = "https://example.com/path"  # Valid
    url: URLStr = "not-a-url"                 # Raises ValidationError
"""

IPAddressStr = Annotated[
    str, AfterValidator(_validate_with_is_validator(IsIPAddress()))
]
"""
IP address string type (IPv4 or IPv6).

Validates both IPv4 and IPv6 addresses using Python's ipaddress module.

Example:
    ip: IPAddressStr = "192.168.1.1"   # Valid (IPv4)
    ip: IPAddressStr = "::1"            # Valid (IPv6)
    ip: IPAddressStr = "not-an-ip"      # Raises ValidationError
"""

IPv4Str = Annotated[
    str, AfterValidator(_validate_with_is_validator(IsIPAddress(version=4)))
]
"""
IPv4 address string type.

Validates only IPv4 addresses. IPv6 addresses will be rejected.

Example:
    ip: IPv4Str = "192.168.1.1"   # Valid
    ip: IPv4Str = "::1"            # Raises ValidationError
"""

IPv6Str = Annotated[
    str, AfterValidator(_validate_with_is_validator(IsIPAddress(version=6)))
]
"""
IPv6 address string type.

Validates only IPv6 addresses. IPv4 addresses will be rejected.

Example:
    ip: IPv6Str = "::1"              # Valid
    ip: IPv6Str = "192.168.1.1"      # Raises ValidationError
"""

HostnameStr = Annotated[str, AfterValidator(_validate_with_is_validator(IsHostname()))]
"""
Hostname string type.

Validates RFC 1123 hostname format. Allows single labels and FQDNs.
Maximum length of 253 characters per DNS specification.

Example:
    host: HostnameStr = "example.com"   # Valid
    host: HostnameStr = "my-server"     # Valid
    host: HostnameStr = "--invalid"     # Raises ValidationError
"""

NonEmptyStr = Annotated[str, AfterValidator(_validate_with_is_validator(IsNotEmpty()))]
"""
Non-empty string type.

Validates that a string is not empty or whitespace-only.
Automatically strips leading/trailing whitespace.

Example:
    value: NonEmptyStr = "hello"   # Valid
    value: NonEmptyStr = ""        # Raises ValidationError
    value: NonEmptyStr = "   "     # Raises ValidationError (all whitespace)
"""

SlugStr = Annotated[str, AfterValidator(_validate_with_is_validator(IsSlug()))]
"""
URL slug string type.

Validates that a string is a valid URL slug:
- Contains only lowercase letters, numbers, and hyphens
- Starts and ends with alphanumeric characters
- No consecutive hyphens

Example:
    slug: SlugStr = "my-blog-post"    # Valid
    slug: SlugStr = "My Blog Post"    # Raises ValidationError
    slug: SlugStr = "--invalid--"     # Raises ValidationError
"""


# Factory functions for customizable types


def strong_password(
    min_length: int = 8,
    max_length: int = 128,
    require_special: bool = True,
    require_uppercase: bool = True,
    require_lowercase: bool = True,
    require_digit: bool = True,
    special_chars: str | None = None,
    disallow_spaces: bool = True,
) -> type:
    """
    Create a custom strong password Annotated type.

    All parameters correspond to PasswordOptions configuration.

    Args:
        min_length: Minimum password length (default: 8)
        max_length: Maximum password length (default: 128)
        require_special: Require at least one special character (default: True)
        require_uppercase: Require at least one uppercase letter (default: True)
        require_lowercase: Require at least one lowercase letter (default: True)
        require_digit: Require at least one digit (default: True)
        special_chars: Allowed special characters (default: "!@#$%^&*()_+-=[]{}|;:,.<>?~`")
        disallow_spaces: Disallow spaces in password (default: True)

    Returns:
        An Annotated type for use in Pydantic models

    Example:
        CustomPassword = strong_password(min_length=12, require_special=True)

        class User(BaseModel):
            password: CustomPassword
    """
    if special_chars is None:
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?~`"

    options = PasswordOptions(
        min_length=min_length,
        max_length=max_length,
        require_special=require_special,
        require_uppercase=require_uppercase,
        require_lowercase=require_lowercase,
        require_digit=require_digit,
        special_chars=special_chars,
        disallow_spaces=disallow_spaces,
    )

    validator = IsStrongPassword(options=options)
    return Annotated[str, AfterValidator(_validate_with_is_validator(validator))]


def bounded_str(
    min_length: int = 0,
    max_length: int | None = None,
) -> type:
    """
    Create a custom bounded string Annotated type.

    Args:
        min_length: Minimum string length (default: 0)
        max_length: Maximum string length (default: None = unlimited)

    Returns:
        An Annotated type for use in Pydantic models

    Example:
        ShortDescription = bounded_str(0, 500)

        class Product(BaseModel):
            description: ShortDescription
    """
    validator = IsLength(min_length=min_length, max_length=max_length)
    return Annotated[str, AfterValidator(_validate_with_is_validator(validator))]


# Pre-built password types

StrongPassword = strong_password(
    min_length=8,
    require_special=True,
    require_uppercase=True,
    require_lowercase=True,
    require_digit=True,
)
"""
Strong password type (default configuration).

Requirements:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character
- No spaces allowed

Example:
    password: StrongPassword = "SecureP@ss123"  # Valid
    password: StrongPassword = "weak"            # Raises ValidationError
"""

ModeratePassword = strong_password(
    min_length=8,
    require_special=False,
    require_uppercase=True,
    require_lowercase=True,
    require_digit=True,
)
"""
Moderate password type (no special character requirement).

Requirements:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- Special characters not required
- No spaces allowed

Example:
    password: ModeratePassword = "SecurePass123"  # Valid
"""


# Pre-built text length types


def _name255_validator():
    """Create Name255 type with custom error message."""
    validator = IsLength(
        min_length=1,
        max_length=255,
        error_message="name cannot be empty or whitespace-only",
    )
    return Annotated[str, AfterValidator(_validate_with_is_validator(validator))]


Name255 = _name255_validator()
"""
Name string type (1-255 characters).

Suitable for user names, display names, or other name fields.

Example:
    name: Name255 = "John Doe"  # Valid
    name: Name255 = ""          # Raises ValidationError (too short)
"""

Description1000 = bounded_str(min_length=0, max_length=1000)
"""
Description string type (0-1000 characters).

Suitable for user-provided descriptions, notes, or short text content.
Allows empty strings.

Example:
    description: Description1000 = "A detailed product description"  # Valid
    description: Description1000 = ""                                # Valid
"""

ShortText100 = bounded_str(min_length=0, max_length=100)
"""
Short text string type (0-100 characters).

Suitable for short text fields like titles, labels, or summaries.
Allows empty strings.

Example:
    title: ShortText100 = "Product Title"  # Valid
    title: ShortText100 = ""               # Valid
"""


__all__ = [
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
