"""Secrets Management service layer for Elder v2.0.0."""

from .base import SecretProviderClient, SecretValue
from .aws_client import AWSSecretsManagerClient
from .gcp_client import GCPSecretManagerClient
from .infisical_client import InfisicalClient
from .builtin_client import BuiltinSecretsClient
from .vault_client import HashicorpVaultClient
from .service import SecretsService

__all__ = [
    'SecretProviderClient',
    'SecretValue',
    'AWSSecretsManagerClient',
    'GCPSecretManagerClient',
    'InfisicalClient',
    'BuiltinSecretsClient',
    'HashicorpVaultClient',
    'SecretsService',
]
