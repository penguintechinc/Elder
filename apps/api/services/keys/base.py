"""Base abstract class for key management providers."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime


class BaseKeyProvider(ABC):
    """Abstract base class for key management providers (AWS KMS, GCP KMS, Infisical)."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the key provider.

        Args:
            config: Provider-specific configuration dictionary
        """
        self.config = config
        self.provider_type = config.get("provider_type")

    @abstractmethod
    def create_key(
        self,
        key_name: str,
        key_type: str = "symmetric",
        key_spec: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new encryption key.

        Args:
            key_name: Name/identifier for the key
            key_type: Type of key (symmetric, asymmetric, hmac)
            key_spec: Key specification (algorithm, key size)
            description: Optional description
            tags: Optional tags/labels

        Returns:
            Dictionary with key details:
            {
                "key_id": "provider-specific-key-id",
                "key_arn": "full-arn-or-resource-name",
                "key_type": "symmetric",
                "state": "enabled",
                "created_at": "ISO8601 timestamp",
            }
        """
        pass

    @abstractmethod
    def get_key(self, key_id: str) -> Dict[str, Any]:
        """
        Get key metadata.

        Args:
            key_id: Provider-specific key identifier

        Returns:
            Dictionary with key metadata
        """
        pass

    @abstractmethod
    def list_keys(
        self, limit: Optional[int] = None, next_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List all keys.

        Args:
            limit: Maximum number of keys to return
            next_token: Pagination token

        Returns:
            Dictionary with:
            {
                "keys": [list of key metadata dicts],
                "next_token": "pagination-token" or None
            }
        """
        pass

    @abstractmethod
    def enable_key(self, key_id: str) -> Dict[str, Any]:
        """
        Enable a disabled key.

        Args:
            key_id: Provider-specific key identifier

        Returns:
            Dictionary with updated key state
        """
        pass

    @abstractmethod
    def disable_key(self, key_id: str) -> Dict[str, Any]:
        """
        Disable a key (soft delete).

        Args:
            key_id: Provider-specific key identifier

        Returns:
            Dictionary with updated key state
        """
        pass

    @abstractmethod
    def schedule_key_deletion(
        self, key_id: str, pending_days: int = 30
    ) -> Dict[str, Any]:
        """
        Schedule key deletion.

        Args:
            key_id: Provider-specific key identifier
            pending_days: Number of days before permanent deletion

        Returns:
            Dictionary with deletion details
        """
        pass

    @abstractmethod
    def cancel_key_deletion(self, key_id: str) -> Dict[str, Any]:
        """
        Cancel scheduled key deletion.

        Args:
            key_id: Provider-specific key identifier

        Returns:
            Dictionary with updated key state
        """
        pass

    @abstractmethod
    def encrypt(
        self, key_id: str, plaintext: str, context: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Encrypt data using a key.

        Args:
            key_id: Provider-specific key identifier
            plaintext: Data to encrypt (string or bytes)
            context: Optional encryption context (additional authenticated data)

        Returns:
            Dictionary with:
            {
                "ciphertext": "base64-encoded-ciphertext",
                "key_id": "key-used-for-encryption",
            }
        """
        pass

    @abstractmethod
    def decrypt(
        self, ciphertext: str, context: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Decrypt data.

        Args:
            ciphertext: Base64-encoded ciphertext
            context: Optional encryption context (must match encryption context)

        Returns:
            Dictionary with:
            {
                "plaintext": "decrypted-data",
                "key_id": "key-used-for-decryption",
            }
        """
        pass

    @abstractmethod
    def generate_data_key(
        self,
        key_id: str,
        key_spec: str = "AES_256",
        context: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a data encryption key.

        Args:
            key_id: Provider-specific key identifier (master key)
            key_spec: Data key specification (AES_256, AES_128)
            context: Optional encryption context

        Returns:
            Dictionary with:
            {
                "plaintext_key": "base64-plaintext-key",
                "ciphertext_key": "base64-encrypted-key",
                "key_id": "master-key-id",
            }
        """
        pass

    @abstractmethod
    def sign(
        self,
        key_id: str,
        message: str,
        signing_algorithm: str = "RSASSA_PSS_SHA_256",
    ) -> Dict[str, Any]:
        """
        Sign a message using an asymmetric key.

        Args:
            key_id: Provider-specific key identifier
            message: Message to sign
            signing_algorithm: Signing algorithm

        Returns:
            Dictionary with:
            {
                "signature": "base64-encoded-signature",
                "key_id": "key-used-for-signing",
                "algorithm": "signing-algorithm-used",
            }
        """
        pass

    @abstractmethod
    def verify(
        self, key_id: str, message: str, signature: str, signing_algorithm: str
    ) -> Dict[str, Any]:
        """
        Verify a message signature.

        Args:
            key_id: Provider-specific key identifier
            message: Original message
            signature: Base64-encoded signature
            signing_algorithm: Signing algorithm used

        Returns:
            Dictionary with:
            {
                "valid": true/false,
                "key_id": "key-used-for-verification",
            }
        """
        pass

    @abstractmethod
    def rotate_key(self, key_id: str) -> Dict[str, Any]:
        """
        Rotate a key (create new version or rotate key material).

        Args:
            key_id: Provider-specific key identifier

        Returns:
            Dictionary with rotation details
        """
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test connectivity to the key provider.

        Returns:
            True if connection successful, False otherwise
        """
        pass

    def _normalize_key_metadata(self, raw_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize provider-specific key metadata to common format.

        Args:
            raw_metadata: Provider-specific metadata

        Returns:
            Normalized metadata dictionary
        """
        return {
            "key_id": raw_metadata.get("key_id") or raw_metadata.get("KeyId"),
            "key_arn": raw_metadata.get("key_arn")
            or raw_metadata.get("KeyMetadata", {}).get("Arn"),
            "state": raw_metadata.get("state") or raw_metadata.get("KeyState"),
            "created_at": raw_metadata.get("created_at")
            or raw_metadata.get("CreationDate"),
            "description": raw_metadata.get("description")
            or raw_metadata.get("Description"),
            "enabled": raw_metadata.get("enabled")
            or raw_metadata.get("Enabled", True),
        }
