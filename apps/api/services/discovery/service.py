"""Discovery service - business logic layer for cloud resource discovery."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from apps.api.services.discovery.aws_discovery import AWSDiscoveryClient
from apps.api.services.discovery.azure_discovery import AzureDiscoveryClient
from apps.api.services.discovery.base import BaseDiscoveryProvider
from apps.api.services.discovery.gcp_discovery import GCPDiscoveryClient
from apps.api.services.discovery.k8s_discovery import KubernetesDiscoveryClient


class DiscoveryService:
    """Service layer for cloud discovery operations."""

    def __init__(self, db):
        """
        Initialize DiscoveryService.

        Args:
            db: PyDAL database instance
        """
        self.db = db

    def _get_discovery_client(self, job_id: int) -> BaseDiscoveryProvider:
        """
        Get configured discovery client for a job.

        Args:
            job_id: Discovery job ID

        Returns:
            Configured discovery client instance

        Raises:
            Exception: If job not found or invalid provider type
        """
        job = self.db.discovery_jobs[job_id]

        if not job:
            raise Exception(f"Discovery job not found: {job_id}")

        config = job.as_dict()
        config["provider_type"] = job.provider

        # Add config_json fields to config
        if job.config_json:
            config.update(job.config_json)

        # Create appropriate client based on provider
        provider_type = job.provider.lower()

        if provider_type == "aws":
            return AWSDiscoveryClient(config)
        elif provider_type == "gcp":
            return GCPDiscoveryClient(config)
        elif provider_type == "azure":
            return AzureDiscoveryClient(config)
        elif provider_type == "kubernetes":
            return KubernetesDiscoveryClient(config)
        else:
            raise Exception(f"Unsupported provider type: {provider_type}")

    # Discovery Job Management

    def list_jobs(
        self,
        provider: Optional[str] = None,
        enabled: Optional[bool] = None,
        organization_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """List all discovery jobs with optional filters."""
        query = self.db.discovery_jobs.id > 0

        if provider:
            query &= self.db.discovery_jobs.provider == provider

        if enabled is not None:
            query &= self.db.discovery_jobs.enabled == enabled

        if organization_id:
            query &= self.db.discovery_jobs.organization_id == organization_id

        jobs = self.db(query).select(orderby=self.db.discovery_jobs.name)

        return [self._sanitize_job(j.as_dict()) for j in jobs]

    def get_job(self, job_id: int) -> Dict[str, Any]:
        """Get discovery job details."""
        job = self.db.discovery_jobs[job_id]

        if not job:
            raise Exception(f"Discovery job not found: {job_id}")

        return self._sanitize_job(job.as_dict())

    def create_job(
        self,
        name: str,
        provider: str,
        config: Dict[str, Any],
        organization_id: int,
        schedule_interval: Optional[int] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new discovery job."""
        # Validate provider type
        valid_providers = ["aws", "gcp", "azure", "kubernetes"]
        if provider.lower() not in valid_providers:
            raise Exception(
                f"Invalid provider: {provider}. Must be one of {valid_providers}"
            )

        # Create job
        job_id = self.db.discovery_jobs.insert(
            name=name,
            provider=provider.lower(),
            enabled=True,
            config_json=config,
            organization_id=organization_id,
            schedule_interval=schedule_interval,
            description=description,
            created_at=datetime.utcnow(),
        )

        self.db.commit()

        return self.get_job(job_id)

    def update_job(
        self,
        job_id: int,
        name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        schedule_interval: Optional[int] = None,
        description: Optional[str] = None,
        enabled: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Update discovery job configuration."""
        job = self.db.discovery_jobs[job_id]

        if not job:
            raise Exception(f"Discovery job not found: {job_id}")

        update_data = {}
        if name is not None:
            update_data["name"] = name
        if config is not None:
            update_data["config_json"] = config
        if schedule_interval is not None:
            update_data["schedule_interval"] = schedule_interval
        if description is not None:
            update_data["description"] = description
        if enabled is not None:
            update_data["enabled"] = enabled

        if update_data:
            self.db(self.db.discovery_jobs.id == job_id).update(**update_data)
            self.db.commit()

        return self.get_job(job_id)

    def delete_job(self, job_id: int) -> Dict[str, Any]:
        """Delete a discovery job."""
        job = self.db.discovery_jobs[job_id]

        if not job:
            raise Exception(f"Discovery job not found: {job_id}")

        # Delete associated history records
        self.db(self.db.discovery_history.discovery_job_id == job_id).delete()

        # Delete job
        self.db(self.db.discovery_jobs.id == job_id).delete()
        self.db.commit()

        return {"message": "Discovery job deleted successfully"}

    def test_job(self, job_id: int) -> Dict[str, Any]:
        """Test discovery job connectivity."""
        try:
            client = self._get_discovery_client(job_id)
            success = client.test_connection()

            return {
                "job_id": job_id,
                "success": success,
                "tested_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {
                "job_id": job_id,
                "success": False,
                "error": str(e),
                "tested_at": datetime.utcnow().isoformat(),
            }

    # Discovery Execution

    def run_discovery(self, job_id: int) -> Dict[str, Any]:
        """Execute discovery for a job."""
        job = self.db.discovery_jobs[job_id]

        if not job:
            raise Exception(f"Discovery job not found: {job_id}")

        try:
            client = self._get_discovery_client(job_id)
            results = client.discover_all()

            # Record discovery history
            history_id = self.db.discovery_history.insert(
                discovery_job_id=job_id,
                discovered_at=datetime.utcnow(),
                resources_discovered=results["resources_count"],
                success=True,
                details_json=results,
            )

            # Update job's last_run timestamp
            self.db(self.db.discovery_jobs.id == job_id).update(
                last_run=datetime.utcnow()
            )

            self.db.commit()

            # Store discovered resources as entities
            self._store_discovered_resources(job.organization_id, results)

            return {
                "job_id": job_id,
                "history_id": history_id,
                "resources_discovered": results["resources_count"],
                "success": True,
                "discovery_time": results["discovery_time"].isoformat(),
            }

        except Exception as e:
            # Record failed discovery
            self.db.discovery_history.insert(
                discovery_job_id=job_id,
                discovered_at=datetime.utcnow(),
                resources_discovered=0,
                success=False,
                error_message=str(e),
            )
            self.db.commit()

            return {
                "job_id": job_id,
                "resources_discovered": 0,
                "success": False,
                "error": str(e),
            }

    def get_discovery_history(
        self, job_id: Optional[int] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get discovery execution history."""
        query = self.db.discovery_history.id > 0

        if job_id:
            query &= self.db.discovery_history.discovery_job_id == job_id

        history = self.db(query).select(
            orderby=~self.db.discovery_history.discovered_at, limitby=(0, limit)
        )

        return [h.as_dict() for h in history]

    # Helper Methods

    def _store_discovered_resources(
        self, organization_id: int, discovery_results: Dict[str, Any]
    ) -> None:
        """
        Store discovered resources as entities in Elder.

        Args:
            organization_id: Organization ID for the resources
            discovery_results: Discovery results from provider
        """
        # Map discovery categories to entity types
        type_mapping = {
            "compute": "compute",
            "storage": "storage",
            "network": "network",
            "database": "storage",  # Map databases to storage type
            "serverless": "compute",  # Map serverless to compute type
        }

        for category, resources in discovery_results.items():
            if category in ["resources_count", "discovery_time", "duration_seconds"]:
                continue

            entity_type = type_mapping.get(category)
            if not entity_type or not resources:
                continue

            for resource in resources:
                # Check if entity already exists by resource_id in metadata
                existing = (
                    self.db(
                        (self.db.entities.organization_id == organization_id)
                        & (
                            self.db.entities.metadata.like(
                                f'%{resource["resource_id"]}%'
                            )
                        )
                    )
                    .select()
                    .first()
                )

                if existing:
                    # Update existing entity
                    self.db(self.db.entities.id == existing.id).update(
                        name=resource["name"],
                        metadata=resource["metadata"],
                        updated_at=datetime.utcnow(),
                    )
                else:
                    # Create new entity
                    self.db.entities.insert(
                        name=resource["name"],
                        entity_type=entity_type,
                        sub_type=resource["resource_type"],
                        organization_id=organization_id,
                        metadata=resource,
                        created_at=datetime.utcnow(),
                    )

        self.db.commit()

    def _sanitize_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive fields from job data."""
        sanitized = dict(job)

        # Mask sensitive config fields
        if "config_json" in sanitized and sanitized["config_json"]:
            config = dict(sanitized["config_json"])

            sensitive_fields = [
                "access_key_id",
                "secret_access_key",
                "credentials_json",
                "token",
                "client_secret",
                "kubeconfig",
            ]

            for field in sensitive_fields:
                if field in config:
                    config[field] = "***REDACTED***"

            sanitized["config_json"] = config

        return sanitized
