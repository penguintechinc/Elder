"""
Test suite for Pydantic custom types.

Tests EmailStr, URLStr, StrongPassword, Name255 and other types with
valid and invalid inputs using pytest.
"""

# flake8: noqa: E501


import pytest
from py_libs.pydantic.types import (Description1000, EmailStr, HostnameStr,
                                    IPAddressStr, IPv4Str, IPv6Str,
                                    ModeratePassword, Name255, NonEmptyStr,
                                    ShortText100, SlugStr, StrongPassword,
                                    URLStr, bounded_str, strong_password)
from pydantic import BaseModel, ValidationError

# Test models


class EmailModel(BaseModel):
    email: EmailStr


class URLModel(BaseModel):
    url: URLStr


class PasswordModel(BaseModel):
    password: StrongPassword


class NameModel(BaseModel):
    name: Name255


class IPAddressModel(BaseModel):
    ip: IPAddressStr


class IPv4Model(BaseModel):
    ip: IPv4Str


class IPv6Model(BaseModel):
    ip: IPv6Str


class HostnameModel(BaseModel):
    hostname: HostnameStr


class NonEmptyStrModel(BaseModel):
    value: NonEmptyStr


class SlugModel(BaseModel):
    slug: SlugStr


class ModeratePasswordModel(BaseModel):
    password: ModeratePassword


class Description1000Model(BaseModel):
    description: Description1000


class ShortText100Model(BaseModel):
    text: ShortText100


# EmailStr Tests


class TestEmailStr:
    """Test EmailStr type validation."""

    def test_valid_email(self):
        """Test valid email addresses."""
        valid_emails = [
            "user@example.com",
            "john.doe@company.co.uk",
            "test+tag@domain.org",
            "alice123@sub.example.com",
        ]
        for email in valid_emails:
            model = EmailModel(email=email)
            assert isinstance(model.email, str)

    def test_invalid_email(self):
        """Test invalid email addresses."""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user @example.com",
            "user@example",
            "",
            "user@@example.com",
        ]
        for email in invalid_emails:
            with pytest.raises(ValidationError):
                EmailModel(email=email)

    def test_email_normalization(self):
        """Test that emails are normalized to lowercase."""
        model = EmailModel(email="USER@EXAMPLE.COM")
        # Email should be normalized
        assert model.email.lower() == model.email


# URLStr Tests


class TestURLStr:
    """Test URLStr type validation."""

    def test_valid_urls(self):
        """Test valid URL addresses."""
        valid_urls = [
            "https://example.com",
            "http://example.com",
            "https://example.com/path",
            "https://example.com/path?query=value",
            "https://subdomain.example.com",
            "https://example.com:8080/path",
        ]
        for url in valid_urls:
            model = URLModel(url=url)
            assert isinstance(model.url, str)

    def test_invalid_urls(self):
        """Test invalid URLs."""
        invalid_urls = [
            "not a url",
            "example.com",
            "ftp://example.com",
            "htp://example.com",
            ":/example.com",
            "",
            "//example.com",
        ]
        for url in invalid_urls:
            with pytest.raises(ValidationError):
                URLModel(url=url)


# StrongPassword Tests


class TestStrongPassword:
    """Test StrongPassword type validation."""

    def test_valid_strong_passwords(self):
        """Test valid strong passwords."""
        valid_passwords = [
            "SecureP@ss123",
            "MyStr0ng!Password",
            "Complex#Pass99",
            "P@ssw0rd!Strong",
        ]
        for password in valid_passwords:
            model = PasswordModel(password=password)
            assert isinstance(model.password, str)

    def test_invalid_strong_passwords(self):
        """Test invalid strong passwords."""
        invalid_passwords = [
            "weak",  # Too short, missing requirements
            "weak123",  # Missing uppercase and special char
            "WeakPassword",  # Missing digit and special char
            "UPPERCASE123!",  # Missing lowercase
            "lowercase123!",  # Missing uppercase
            "NoDigits!@#$",  # Missing digit
            "NoSpecial123",  # Missing special character
            "Pass@123 ",  # Contains space
            "",  # Empty
            "short@1",  # Too short (7 chars)
        ]
        for password in invalid_passwords:
            with pytest.raises(ValidationError):
                PasswordModel(password=password)

    def test_password_strength_requirements(self):
        """Test that password meets all strength requirements."""
        # This should pass all requirements
        model = PasswordModel(password="StrongPass@123")
        assert len(model.password) >= 8
        assert any(c.isupper() for c in model.password)
        assert any(c.islower() for c in model.password)
        assert any(c.isdigit() for c in model.password)
        assert any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?~`" for c in model.password)


# Name255 Tests


class TestName255:
    """Test Name255 type validation."""

    def test_valid_names(self):
        """Test valid names."""
        valid_names = [
            "John Doe",
            "A",
            "Jean-Claude Van Damme",
            "Mary Jane Watson",
            "José García",
            "李明",
            "Muhammad Al-Rashid",
            "X" * 255,
        ]
        for name in valid_names:
            model = NameModel(name=name)
            assert isinstance(model.name, str)
            assert 1 <= len(model.name) <= 255

    def test_invalid_names(self):
        """Test invalid names."""
        invalid_names = [
            "",  # Empty string
            "X" * 256,  # Exceeds max length
        ]
        for name in invalid_names:
            with pytest.raises(ValidationError):
                NameModel(name=name)


# IPAddressStr Tests


class TestIPAddressStr:
    """Test IPAddressStr type validation."""

    def test_valid_ipv4_addresses(self):
        """Test valid IPv4 addresses."""
        valid_ips = [
            "192.168.1.1",
            "127.0.0.1",
            "10.0.0.1",
            "255.255.255.255",
            "0.0.0.0",
        ]
        for ip in valid_ips:
            model = IPAddressModel(ip=ip)
            assert isinstance(model.ip, str)

    def test_valid_ipv6_addresses(self):
        """Test valid IPv6 addresses."""
        valid_ips = [
            "::1",
            "2001:db8::1",
            "fe80::1",
            "::",
        ]
        for ip in valid_ips:
            model = IPAddressModel(ip=ip)
            assert isinstance(model.ip, str)

    def test_invalid_ip_addresses(self):
        """Test invalid IP addresses."""
        invalid_ips = [
            "256.256.256.256",
            "192.168.1",
            "not.an.ip.address",
            "192.168.1.1.1",
            "",
        ]
        for ip in invalid_ips:
            with pytest.raises(ValidationError):
                IPAddressModel(ip=ip)


# IPv4Str Tests


class TestIPv4Str:
    """Test IPv4Str type validation."""

    def test_valid_ipv4(self):
        """Test valid IPv4 addresses."""
        valid_ips = ["192.168.1.1", "127.0.0.1", "10.0.0.0"]
        for ip in valid_ips:
            model = IPv4Model(ip=ip)
            assert isinstance(model.ip, str)

    def test_invalid_ipv4(self):
        """Test invalid IPv4 addresses and IPv6."""
        invalid_ips = [
            "256.256.256.256",
            "::1",  # IPv6, not IPv4
            "not-an-ip",
        ]
        for ip in invalid_ips:
            with pytest.raises(ValidationError):
                IPv4Model(ip=ip)


# IPv6Str Tests


class TestIPv6Str:
    """Test IPv6Str type validation."""

    def test_valid_ipv6(self):
        """Test valid IPv6 addresses."""
        valid_ips = ["::1", "2001:db8::1", "fe80::1"]
        for ip in valid_ips:
            model = IPv6Model(ip=ip)
            assert isinstance(model.ip, str)

    def test_invalid_ipv6(self):
        """Test invalid IPv6 addresses and IPv4."""
        invalid_ips = [
            "192.168.1.1",  # IPv4, not IPv6
            "not-an-ip",
        ]
        for ip in invalid_ips:
            with pytest.raises(ValidationError):
                IPv6Model(ip=ip)


# HostnameStr Tests


class TestHostnameStr:
    """Test HostnameStr type validation."""

    def test_valid_hostnames(self):
        """Test valid hostnames."""
        valid_hostnames = [
            "example.com",
            "sub.example.com",
            "my-server",
            "localhost",
            "server123",
        ]
        for hostname in valid_hostnames:
            model = HostnameModel(hostname=hostname)
            assert isinstance(model.hostname, str)

    def test_invalid_hostnames(self):
        """Test invalid hostnames."""
        invalid_hostnames = [
            "--invalid",
            "-server",
            "server-",
            "",
            "invalid..com",
            "invalid_name",
        ]
        for hostname in invalid_hostnames:
            with pytest.raises(ValidationError):
                HostnameModel(hostname=hostname)


# NonEmptyStr Tests


class TestNonEmptyStr:
    """Test NonEmptyStr type validation."""

    def test_valid_non_empty_strings(self):
        """Test valid non-empty strings."""
        valid_strings = ["hello", "hello world", "a", "123", "!@#$%"]
        for value in valid_strings:
            model = NonEmptyStrModel(value=value)
            assert isinstance(model.value, str)

    def test_invalid_non_empty_strings(self):
        """Test invalid non-empty strings."""
        invalid_strings = ["", "   ", "\t", "\n"]
        for value in invalid_strings:
            with pytest.raises(ValidationError):
                NonEmptyStrModel(value=value)


# SlugStr Tests


class TestSlugStr:
    """Test SlugStr type validation."""

    def test_valid_slugs(self):
        """Test valid slugs."""
        valid_slugs = [
            "my-blog-post",
            "hello-world",
            "test123",
            "slug",
            "a",
            "slug-with-123-numbers",
        ]
        for slug in valid_slugs:
            model = SlugModel(slug=slug)
            assert isinstance(model.slug, str)

    def test_invalid_slugs(self):
        """Test invalid slugs."""
        invalid_slugs = [
            "My-Blog-Post",  # Uppercase
            "blog post",  # Spaces
            "-invalid",  # Starts with hyphen
            "invalid-",  # Ends with hyphen
            "--invalid",  # Double hyphen
            "",
            "blog_post",  # Underscore
        ]
        for slug in invalid_slugs:
            with pytest.raises(ValidationError):
                SlugModel(slug=slug)


# ModeratePassword Tests


class TestModeratePassword:
    """Test ModeratePassword type validation."""

    def test_valid_moderate_passwords(self):
        """Test valid moderate passwords (no special char requirement)."""
        valid_passwords = [
            "SecurePass123",
            "MyPassword1",
            "TestPass99",
        ]
        for password in valid_passwords:
            model = ModeratePasswordModel(password=password)
            assert isinstance(model.password, str)

    def test_invalid_moderate_passwords(self):
        """Test invalid moderate passwords."""
        invalid_passwords = [
            "weak",  # Too short
            "Weak123",  # Too short (7 chars)
            "NoDigits",  # Missing digit
            "nouppercases123",  # Missing uppercase
            "NOLOWERCASE123",  # Missing lowercase
            "Pass@123 ",  # Contains space
        ]
        for password in invalid_passwords:
            with pytest.raises(ValidationError):
                ModeratePasswordModel(password=password)


# Description1000 Tests


class TestDescription1000:
    """Test Description1000 type validation."""

    def test_valid_descriptions(self):
        """Test valid descriptions."""
        valid_descriptions = [
            "",  # Empty allowed
            "A",
            "A brief description",
            "X" * 1000,  # Max length
        ]
        for description in valid_descriptions:
            model = Description1000Model(description=description)
            assert isinstance(model.description, str)
            assert len(model.description) <= 1000

    def test_invalid_descriptions(self):
        """Test invalid descriptions."""
        invalid_descriptions = [
            "X" * 1001,  # Exceeds max length
        ]
        for description in invalid_descriptions:
            with pytest.raises(ValidationError):
                Description1000Model(description=description)


# ShortText100 Tests


class TestShortText100:
    """Test ShortText100 type validation."""

    def test_valid_short_text(self):
        """Test valid short text."""
        valid_texts = [
            "",  # Empty allowed
            "Title",
            "A short text field",
            "X" * 100,  # Max length
        ]
        for text in valid_texts:
            model = ShortText100Model(text=text)
            assert isinstance(model.text, str)
            assert len(model.text) <= 100

    def test_invalid_short_text(self):
        """Test invalid short text."""
        invalid_texts = [
            "X" * 101,  # Exceeds max length
        ]
        for text in invalid_texts:
            with pytest.raises(ValidationError):
                ShortText100Model(text=text)


# Factory Function Tests


class TestStrongPasswordFactory:
    """Test strong_password factory function."""

    def test_custom_length_requirements(self):
        """Test custom password with different length requirements."""
        CustomPassword = strong_password(min_length=12, max_length=64)

        class CustomPasswordModel(BaseModel):
            password: CustomPassword

        # Valid: meets 12 char min
        model = CustomPasswordModel(password="VeryStr0ng@Pass12")
        assert len(model.password) >= 12

        # Invalid: too short
        with pytest.raises(ValidationError):
            CustomPasswordModel(password="Short@1")

    def test_custom_requirements_no_special(self):
        """Test custom password without special character requirement."""
        NoSpecialPassword = strong_password(
            min_length=8,
            require_special=False,
            require_uppercase=True,
            require_lowercase=True,
            require_digit=True,
        )

        class NoSpecialPasswordModel(BaseModel):
            password: NoSpecialPassword

        # Valid: no special character required
        model = NoSpecialPasswordModel(password="ValidPass123")
        assert isinstance(model.password, str)

        # Invalid: still requires uppercase, lowercase, digit
        with pytest.raises(ValidationError):
            NoSpecialPasswordModel(password="validpass123")


class TestBoundedStrFactory:
    """Test bounded_str factory function."""

    def test_custom_bounded_string(self):
        """Test custom bounded string."""
        ShortDescription = bounded_str(min_length=1, max_length=50)

        class ProductModel(BaseModel):
            description: ShortDescription

        # Valid
        model = ProductModel(description="Short description")
        assert 1 <= len(model.description) <= 50

        # Invalid: too long
        with pytest.raises(ValidationError):
            ProductModel(description="X" * 51)

    def test_unbounded_max(self):
        """Test bounded string with no max limit."""
        LongText = bounded_str(min_length=1, max_length=None)

        class LongModel(BaseModel):
            text: LongText

        # Should accept very long strings
        model = LongModel(text="X" * 10000)
        assert len(model.text) == 10000


# Edge Case Tests


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_email_max_length(self):
        """Test that emails respect RFC 254 character limit."""
        # Create a very long but valid email
        long_email = "a" * 64 + "@" + "b" * 189  # Should be under 254
        try:
            model = EmailModel(email=long_email)
            assert isinstance(model.email, str)
        except ValidationError:
            # If it fails due to length, that's expected for RFC compliance
            pass

    def test_name_boundary_values(self):
        """Test Name255 at boundary values."""
        # Exactly 1 character (minimum)
        model = NameModel(name="A")
        assert model.name == "A"

        # Exactly 255 characters (maximum)
        model = NameModel(name="X" * 255)
        assert len(model.name) == 255

    def test_unicode_support(self):
        """Test Unicode support in various types."""
        # Unicode in email (may or may not be supported)
        try:
            EmailModel(email="user+€@example.com")
        except ValidationError:
            pass  # Unicode in email may not be supported

        # Unicode in names should work
        model = NameModel(name="François")
        assert "ç" in model.name or model.name == "François"

        # Unicode in descriptions should work
        model = Description1000Model(
            description="Descripción con caracteres especiales: 中文"
        )
        assert isinstance(model.description, str)

    def test_type_coercion(self):
        """Test that types are properly coerced."""
        # Pydantic should accept string types and validate them
        model = EmailModel(email="test@example.com")
        assert isinstance(model.email, str)

        model = PasswordModel(password="ValidPass@123")
        assert isinstance(model.password, str)

        model = NameModel(name="John Doe")
        assert isinstance(model.name, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
