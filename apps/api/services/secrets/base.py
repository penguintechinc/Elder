"""Base client interface for secret providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class SecretValue:
    """Represents a secret value retrieved from a provider."""

    name: str
    value: Optional[str] = None  # None if masked
    is_masked: bool = True
    is_kv: bool = False
    kv_pairs: Optional[Dict[str, str]] = None
    version: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    def mask(self) -> 'SecretValue':
        """Return a masked version of this secret."""
        return SecretValue(
            name=self.name,
            value='***MASKED***' if self.value else None,
            is_masked=True,
            is_kv=self.is_kv,
            kv_pairs={k: '***MASKED***' for k in self.kv_pairs.keys()} if self.kv_pairs else None,
            version=self.version,
            created_at=self.created_at,
            updated_at=self.updated_at,
            metadata=self.metadata,
        )


@dataclass
class SecretMetadata:
    """Metadata about a secret without the actual value."""

    name: str
    path: str
    is_kv: bool
    version: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class SecretProviderClient(ABC):
    """Abstract base class for secret provider clients."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the secret provider client.

        Args:
            config: Provider-specific configuration dictionary
        """
        self.config = config
        self._validate_config()

    @abstractmethod
    def _validate_config(self) -> None:
        """
        Validate the provider configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test the connection to the secret provider.

        Returns:
            True if connection is successful, False otherwise
        """
        pass

    @abstractmethod
    def get_secret(self, path: str, version: Optional[str] = None) -> SecretValue:
        """
        Retrieve a secret from the provider.

        Args:
            path: Path or identifier of the secret
            version: Optional specific version to retrieve

        Returns:
            SecretValue object with the secret data

        Raises:
            SecretNotFoundException: If secret doesn't exist
            SecretAccessDeniedException: If access is denied
            SecretProviderException: For other provider errors
        """
        pass

    @abstractmethod
    def list_secrets(self, prefix: Optional[str] = None) -> List[SecretMetadata]:
        """
        List secrets available in the provider.

        Args:
            prefix: Optional prefix to filter secrets

        Returns:
            List of SecretMetadata objects

        Raises:
            SecretProviderException: For provider errors
        """
        pass

    @abstractmethod
    def create_secret(self, path: str, value: str, metadata: Optional[Dict[str, Any]] = None) -> SecretMetadata:
        """
        Create a new secret in the provider.

        Args:
            path: Path or identifier for the secret
            value: Secret value to store
            metadata: Optional metadata to attach

        Returns:
            SecretMetadata of the created secret

        Raises:
            SecretAlreadyExistsException: If secret already exists
            SecretProviderException: For other provider errors
        """
        pass

    @abstractmethod
    def update_secret(self, path: str, value: str) -> SecretMetadata:
        """
        Update an existing secret in the provider.

        Args:
            path: Path or identifier of the secret
            value: New secret value

        Returns:
            SecretMetadata of the updated secret

        Raises:
            SecretNotFoundException: If secret doesn't exist
            SecretProviderException: For provider errors
        """
        pass

    @abstractmethod
    def delete_secret(self, path: str, force: bool = False) -> bool:
        """
        Delete a secret from the provider.

        Args:
            path: Path or identifier of the secret
            force: Force immediate deletion (skip recovery window if available)

        Returns:
            True if deletion was successful

        Raises:
            SecretNotFoundException: If secret doesn't exist
            SecretProviderException: For provider errors
        """
        pass

    @abstractmethod
    def get_secret_versions(self, path: str) -> List[str]:
        """
        Get all versions of a secret.

        Args:
            path: Path or identifier of the secret

        Returns:
            List of version identifiers

        Raises:
            SecretNotFoundException: If secret doesn't exist
            SecretProviderException: For provider errors
        """
        pass


class SecretProviderException(Exception):
    """Base exception for secret provider errors."""
    pass


class SecretNotFoundException(SecretProviderException):
    """Exception raised when a secret is not found."""
    pass


class SecretAccessDeniedException(SecretProviderException):
    """Exception raised when access to a secret is denied."""
    pass


class SecretAlreadyExistsException(SecretProviderException):
    """Exception raised when trying to create a secret that already exists."""
    pass


class InvalidSecretConfigException(SecretProviderException):
    """Exception raised when secret provider configuration is invalid."""
    pass
