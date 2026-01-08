"""PenguinTech License Server client for Elder."""

# flake8: noqa: E501


import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

import requests
import structlog

logger = structlog.get_logger()


@dataclass
class Feature:
    """License feature with entitlement details."""

    name: str
    entitled: bool
    units: int  # 0 = unlimited, -1 = not applicable
    description: str
    metadata: Dict


@dataclass
class LicenseInfo:
    """License information from server."""

    valid: bool
    customer: str
    product: str
    license_version: str
    license_key: str
    expires_at: datetime
    issued_at: datetime
    tier: str  # community, professional, enterprise
    features: List[Feature]
    limits: Dict
    metadata: Dict
    server_id: Optional[str] = None
    message: Optional[str] = None


class LicenseClient:
    """
    Client for PenguinTech License Server integration.

    Provides license validation, feature checking, and keepalive reporting.
    Caches validation results in memory for performance.
    """

    def __init__(
        self,
        license_key: Optional[str] = None,
        product: str = "elder",
        base_url: str = "https://license.penguintech.io",
    ):
        """
        Initialize license client.

        Args:
            license_key: PenguinTech license key (PENG-XXXX-...)
            product: Product identifier
            base_url: License server base URL
        """
        self.license_key = license_key or os.getenv("LICENSE_KEY", "")
        self.product = product
        self.base_url = base_url or os.getenv(
            "LICENSE_SERVER_URL", "https://license.penguintech.io"
        )
        self.server_id: Optional[str] = None

        # Cache validation results (5 minute TTL)
        self._cached_validation: Optional[LicenseInfo] = None
        self._cache_expiry: Optional[datetime] = None

        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "User-Agent": f"Elder/{os.getenv('APP_VERSION', '0.1.0')}",
            }
        )

        if self.license_key:
            self.session.headers["Authorization"] = f"Bearer {self.license_key}"

    def validate(self, force_refresh: bool = False) -> LicenseInfo:
        """
        Validate license and get server ID for keepalives.

        Args:
            force_refresh: Force refresh from server (ignore cache)

        Returns:
            LicenseInfo with validation results
        """
        # Check cache first
        if not force_refresh and self._cached_validation and self._cache_expiry:
            if datetime.now(timezone.utc) < self._cache_expiry:
                logger.debug("license_validation_cache_hit")
                return self._cached_validation

        # No license key = community tier with basic features
        if not self.license_key:
            logger.warning("no_license_key_configured", tier="community")
            return self._get_community_tier_info()

        try:
            response = self.session.post(
                f"{self.base_url}/api/v2/validate",
                json={"product": self.product},
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()

                # Parse features
                features = [
                    Feature(
                        name=f["name"],
                        entitled=f["entitled"],
                        units=f.get("units", -1),
                        description=f.get("description", ""),
                        metadata=f.get("metadata", {}),
                    )
                    for f in data.get("features", [])
                ]

                # Parse timestamps
                expires_at = datetime.fromisoformat(
                    data["expires_at"].replace("Z", "+00:00")
                )
                issued_at = datetime.fromisoformat(
                    data["issued_at"].replace("Z", "+00:00")
                )

                license_info = LicenseInfo(
                    valid=True,
                    customer=data["customer"],
                    product=data["product"],
                    license_version=data["license_version"],
                    license_key=data["license_key"],
                    expires_at=expires_at,
                    issued_at=issued_at,
                    tier=data["tier"],
                    features=features,
                    limits=data.get("limits", {}),
                    metadata=data.get("metadata", {}),
                    server_id=data.get("metadata", {}).get("server_id"),
                )

                # Store server ID for keepalives
                if license_info.server_id:
                    self.server_id = license_info.server_id

                # Cache validation result
                self._cached_validation = license_info
                self._cache_expiry = datetime.now(timezone.utc) + timedelta(minutes=5)

                logger.info(
                    "license_validation_success",
                    customer=license_info.customer,
                    tier=license_info.tier,
                    expires_at=license_info.expires_at.isoformat(),
                )

                return license_info

            else:
                logger.error(
                    "license_validation_failed",
                    status_code=response.status_code,
                    response=response.text,
                )
                return LicenseInfo(
                    valid=False,
                    customer="",
                    product=self.product,
                    license_version="2.0",
                    license_key=self.license_key,
                    expires_at=datetime.now(timezone.utc),
                    issued_at=datetime.now(timezone.utc),
                    tier="community",
                    features=[],
                    limits={},
                    metadata={},
                    message=f"Validation failed: {response.status_code}",
                )

        except Exception as e:
            logger.error("license_validation_exception", error=str(e), exc_info=True)
            # Fall back to community tier on error
            return self._get_community_tier_info(message=f"Validation error: {str(e)}")

    def check_feature(self, feature_name: str) -> bool:
        """
        Check if specific feature is enabled.

        Args:
            feature_name: Feature identifier to check

        Returns:
            True if feature is entitled, False otherwise
        """
        validation = self.validate()

        if not validation.valid:
            return False

        for feature in validation.features:
            if feature.name == feature_name and feature.entitled:
                return True

        return False

    def check_tier(self, required_tier: str) -> bool:
        """
        Check if license meets minimum tier requirement.

        Tier hierarchy: community < professional < enterprise

        Args:
            required_tier: Minimum tier required (community, professional, enterprise)

        Returns:
            True if license tier meets or exceeds requirement
        """
        tier_levels = {"community": 1, "professional": 2, "enterprise": 3}

        validation = self.validate()
        current_level = tier_levels.get(validation.tier, 0)
        required_level = tier_levels.get(required_tier, 99)

        return current_level >= required_level

    def keepalive(self, usage_data: Optional[Dict] = None) -> Dict:
        """
        Send keepalive with optional usage statistics.

        Args:
            usage_data: Optional usage statistics to report

        Returns:
            Keepalive response data
        """
        if not self.license_key:
            logger.debug("keepalive_skipped_no_license")
            return {"success": False, "message": "No license key configured"}

        # Ensure we have server_id
        if not self.server_id:
            validation = self.validate(force_refresh=True)
            if not validation.valid or not validation.server_id:
                return {"success": False, "message": "No server ID available"}

        payload = {
            "product": self.product,
            "server_id": self.server_id,
        }

        if usage_data:
            payload.update(usage_data)

        try:
            response = self.session.post(
                f"{self.base_url}/api/v2/keepalive",
                json=payload,
                timeout=10,
            )

            if response.status_code == 200:
                logger.info("keepalive_success", server_id=self.server_id)
                return response.json()
            else:
                logger.error(
                    "keepalive_failed",
                    status_code=response.status_code,
                    response=response.text,
                )
                return {
                    "success": False,
                    "message": f"Keepalive failed: {response.status_code}",
                }

        except Exception as e:
            logger.error("keepalive_exception", error=str(e))
            return {"success": False, "message": f"Keepalive error: {str(e)}"}

    def _get_community_tier_info(self, message: Optional[str] = None) -> LicenseInfo:
        """Get default community tier license info."""
        return LicenseInfo(
            valid=True,  # Community tier is always valid
            customer="Community User",
            product=self.product,
            license_version="2.0",
            license_key="",
            expires_at=datetime.max.replace(tzinfo=timezone.utc),
            issued_at=datetime.now(timezone.utc),
            tier="community",
            features=[
                Feature(
                    name="basic_features",
                    entitled=True,
                    units=-1,
                    description="Basic Elder features",
                    metadata={},
                ),
            ],
            limits={"max_entities": 100},
            metadata={},
            message=message or "Community tier (no license key)",
        )


# Global license client instance
_license_client: Optional[LicenseClient] = None


def get_license_client() -> LicenseClient:
    """
    Get global license client instance.

    Returns:
        Shared LicenseClient instance
    """
    global _license_client

    if _license_client is None:
        _license_client = LicenseClient()

    return _license_client


def init_license_client(app) -> LicenseClient:
    """
    Initialize license client from Flask app config.

    Args:
        app: Flask application instance

    Returns:
        Configured LicenseClient
    """
    global _license_client

    license_key = app.config.get("LICENSE_KEY") or os.getenv("LICENSE_KEY")
    base_url = app.config.get("LICENSE_SERVER_URL") or os.getenv(
        "LICENSE_SERVER_URL", "https://license.penguintech.io"
    )

    _license_client = LicenseClient(
        license_key=license_key,
        product="elder",
        base_url=base_url,
    )

    # Validate on startup
    validation = _license_client.validate()

    logger.info(
        "license_client_initialized",
        tier=validation.tier,
        valid=validation.valid,
        customer=validation.customer,
    )

    return _license_client
