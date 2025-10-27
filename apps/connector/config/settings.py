"""Configuration settings for Elder Connector Service."""

import os
from typing import Optional, Dict, Any
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Main configuration for the connector service."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )

    # Elder API Configuration
    elder_api_url: str = Field(
        default="http://api:5000",
        description="Elder API base URL",
    )
    elder_api_key: Optional[str] = Field(
        default=None,
        description="Elder API authentication key (if required)",
    )

    # AWS Configuration
    aws_enabled: bool = Field(default=False, description="Enable AWS connector")
    aws_access_key_id: Optional[str] = Field(default=None, description="AWS Access Key ID")
    aws_secret_access_key: Optional[str] = Field(default=None, description="AWS Secret Access Key")
    aws_default_region: str = Field(default="us-east-1", description="Default AWS region")
    aws_regions: str = Field(
        default="us-east-1,us-west-2",
        description="Comma-separated list of AWS regions to scan",
    )
    aws_sync_interval: int = Field(
        default=3600,
        description="AWS sync interval in seconds (default: 1 hour)",
    )

    # GCP Configuration
    gcp_enabled: bool = Field(default=False, description="Enable GCP connector")
    gcp_project_id: Optional[str] = Field(default=None, description="GCP Project ID")
    gcp_credentials_path: Optional[str] = Field(
        default=None,
        description="Path to GCP service account credentials JSON",
    )
    gcp_sync_interval: int = Field(
        default=3600,
        description="GCP sync interval in seconds (default: 1 hour)",
    )

    # Google Workspace Configuration
    google_workspace_enabled: bool = Field(
        default=False,
        description="Enable Google Workspace connector",
    )
    google_workspace_credentials_path: Optional[str] = Field(
        default=None,
        description="Path to Google Workspace service account credentials JSON",
    )
    google_workspace_admin_email: Optional[str] = Field(
        default=None,
        description="Google Workspace admin email for impersonation",
    )
    google_workspace_customer_id: str = Field(
        default="my_customer",
        description="Google Workspace customer ID",
    )
    google_workspace_sync_interval: int = Field(
        default=3600,
        description="Google Workspace sync interval in seconds (default: 1 hour)",
    )

    # LDAP/LDAPS Configuration
    ldap_enabled: bool = Field(default=False, description="Enable LDAP connector")
    ldap_server: Optional[str] = Field(
        default=None,
        description="LDAP server hostname or IP",
    )
    ldap_port: int = Field(
        default=389,
        description="LDAP server port (389 for LDAP, 636 for LDAPS)",
    )
    ldap_use_ssl: bool = Field(
        default=False,
        description="Use LDAPS (SSL/TLS) connection",
    )
    ldap_verify_cert: bool = Field(
        default=True,
        description="Verify SSL certificate for LDAPS",
    )
    ldap_bind_dn: Optional[str] = Field(
        default=None,
        description="LDAP bind DN for authentication",
    )
    ldap_bind_password: Optional[str] = Field(
        default=None,
        description="LDAP bind password",
    )
    ldap_base_dn: Optional[str] = Field(
        default=None,
        description="LDAP base DN for searches",
    )
    ldap_user_filter: str = Field(
        default="(objectClass=person)",
        description="LDAP filter for user searches",
    )
    ldap_group_filter: str = Field(
        default="(objectClass=group)",
        description="LDAP filter for group searches",
    )
    ldap_sync_interval: int = Field(
        default=3600,
        description="LDAP sync interval in seconds (default: 1 hour)",
    )

    # Elder Organization Mapping
    default_organization_id: Optional[int] = Field(
        default=None,
        description="Default Elder organization ID for entities without mapping",
    )
    create_missing_organizations: bool = Field(
        default=True,
        description="Auto-create organizations in Elder if they don't exist",
    )

    # Sync Configuration
    sync_on_startup: bool = Field(
        default=True,
        description="Run initial sync on connector startup",
    )
    sync_batch_size: int = Field(
        default=100,
        description="Number of entities to create/update per batch",
    )
    sync_max_retries: int = Field(
        default=3,
        description="Maximum number of retries for failed sync operations",
    )

    # Sync Batch Fallback Configuration (v1.1.0)
    sync_batch_fallback_enabled: bool = Field(
        default=True,
        description="Enable batch sync fallback when webhooks fail or timeout",
    )
    sync_batch_interval: int = Field(
        default=3600,
        description="Interval in seconds for batch sync fallback (default: 1 hour)",
    )
    sync_batch_fallback_size: int = Field(
        default=100,
        description="Number of items to sync per batch in fallback mode",
    )

    # Syslog Configuration
    syslog_enabled: bool = Field(
        default=False,
        description="Enable UDP syslog logging",
    )
    syslog_host: str = Field(
        default="localhost",
        description="Syslog server hostname or IP",
    )
    syslog_port: int = Field(
        default=514,
        description="Syslog server UDP port",
    )

    # KillKrill Configuration (HTTP3/QUIC Logging)
    killkrill_enabled: bool = Field(
        default=False,
        description="Enable KillKrill HTTP3/QUIC logging",
    )
    killkrill_url: str = Field(
        default="https://killkrill.penguintech.io",
        description="KillKrill server URL",
    )
    killkrill_api_key: Optional[str] = Field(
        default=None,
        description="KillKrill API authentication key",
    )
    killkrill_use_http3: bool = Field(
        default=True,
        description="Use HTTP3/QUIC for KillKrill (fallback to HTTP/2 if False)",
    )

    # Health Check & Monitoring
    health_check_port: int = Field(
        default=8000,
        description="Port for health check HTTP server",
    )
    metrics_enabled: bool = Field(
        default=True,
        description="Enable Prometheus metrics",
    )

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )
    log_format: str = Field(
        default="json",
        description="Log format (json or text)",
    )

    @property
    def aws_regions_list(self) -> list[str]:
        """Get AWS regions as a list."""
        return [r.strip() for r in self.aws_regions.split(",") if r.strip()]


# Global settings instance
settings = Settings()
