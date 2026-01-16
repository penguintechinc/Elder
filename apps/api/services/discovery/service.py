"""Discovery service - business logic layer for cloud resource discovery."""

# flake8: noqa: E501


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
        organization_id: int = None,  # Optional - stored in config for now
        schedule_interval: Optional[int] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new discovery job."""
        # Validate provider type
        valid_providers = [
            "aws",
            "gcp",
            "azure",
            "kubernetes",
            "network",
            "http_screenshot",
            "banner",
        ]
        if provider.lower() not in valid_providers:
            raise Exception(
                f"Invalid provider: {provider}. Must be one of {valid_providers}"
            )

        # Store organization_id and description in config for now
        # (until schema migration adds these columns)
        job_config = dict(config)
        if organization_id:
            job_config["_organization_id"] = organization_id
        if description:
            job_config["_description"] = description

        # Create job
        job_id = self.db.discovery_jobs.insert(
            name=name,
            provider=provider.lower(),
            enabled=True,
            config_json=job_config,
            schedule_interval=schedule_interval or 3600,
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
        self.db(self.db.discovery_history.job_id == job_id).delete()

        # Delete job
        self.db(self.db.discovery_jobs.id == job_id).delete()
        self.db.commit()

        return {"message": "Discovery job deleted successfully"}

    def test_job(self, job_id: int) -> Dict[str, Any]:
        """Test discovery job connectivity."""
        try:
            client = self._get_discovery_client(job_id)
            success = client.test_connection()

            result = {
                "job_id": job_id,
                "success": success,
                "tested_at": datetime.utcnow().isoformat(),
            }

            # Add auth method if available (AWS client)
            if hasattr(client, "get_auth_method"):
                result["auth_method"] = client.get_auth_method()

            # Add identity info if available (AWS client)
            if hasattr(client, "get_caller_identity") and success:
                identity = client.get_caller_identity()
                if identity:
                    result["identity"] = identity

            return result

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

            # Convert datetime to string for JSON storage
            results_for_storage = dict(results)
            if "discovery_time" in results_for_storage:
                results_for_storage["discovery_time"] = results_for_storage[
                    "discovery_time"
                ].isoformat()

            # Record discovery history
            history_id = self.db.discovery_history.insert(
                job_id=job_id,
                started_at=datetime.utcnow(),
                entities_discovered=results["resources_count"],
                status="completed",
                results_json=results_for_storage,
            )

            # Update job's last_run timestamp
            self.db(self.db.discovery_jobs.id == job_id).update(
                last_run_at=datetime.utcnow()
            )

            self.db.commit()

            # Get organization_id from config if available
            organization_id = None
            if job.config_json:
                organization_id = job.config_json.get("_organization_id")

            # Store discovered resources as entities (if organization_id available)
            if organization_id:
                self._store_discovered_resources(organization_id, results)

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
                job_id=job_id,
                started_at=datetime.utcnow(),
                entities_discovered=0,
                status="failed",
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
            query &= self.db.discovery_history.job_id == job_id

        history = self.db(query).select(
            orderby=~self.db.discovery_history.started_at, limitby=(0, limit)
        )

        return [h.as_dict() for h in history]

    # Helper Methods

    def _store_discovered_resources(
        self, organization_id: int, discovery_results: Dict[str, Any]
    ) -> None:
        """
        Store discovered resources in Elder.

        Resources are stored in their proper Resource tables first (e.g., IAM users
        go to the identities table), and fall back to the generic entities table
        for resource types that don't have dedicated tables.

        Args:
            organization_id: Organization ID for the resources
            discovery_results: Discovery results from provider
        """
        # Map discovery categories to entity types (fallback for entities table)
        type_mapping = {
            "compute": "compute",
            "storage": "storage",
            "network": "network",
            "database": "storage",  # Map databases to storage type
            "serverless": "compute",  # Map serverless to compute type
        }

        # Resource types that map to specific Resource tables
        # Format: resource_type -> (table_name, store_method)
        resource_mappings = {
            "iam_user": "identity",
            "iam_role": "identity",
        }

        for category, resources in discovery_results.items():
            if category in ["resources_count", "discovery_time", "duration_seconds"]:
                continue

            if not resources:
                continue

            for resource in resources:
                resource_type = resource.get("resource_type", "")

                # Check if this resource type maps to a specific Resource table
                if resource_type in resource_mappings:
                    resource_table = resource_mappings[resource_type]

                    if resource_table == "identity":
                        self._store_iam_as_identity(organization_id, resource)
                    # Add more resource table mappings here as needed
                    # elif resource_table == "software": ...
                    # elif resource_table == "services": ...
                else:
                    # Fall back to generic entities table
                    entity_type = type_mapping.get(category)
                    if entity_type:
                        self._store_as_entity(organization_id, resource, entity_type)

        self.db.commit()

    def _store_iam_as_identity(
        self, organization_id: int, resource: Dict[str, Any]
    ) -> None:
        """
        Store IAM user or role as an Identity resource.

        Args:
            organization_id: Organization ID
            resource: Discovered IAM resource data
        """
        resource_type = resource.get("resource_type", "")
        name = resource.get("name", "Unnamed")
        metadata = resource.get("metadata", {})
        arn = metadata.get("arn", resource.get("resource_id", ""))

        # Determine identity type based on IAM resource type
        if resource_type == "iam_user":
            identity_type = "integration"  # AWS IAM users are integrations
        elif resource_type == "iam_role":
            identity_type = "serviceAccount"  # IAM roles are service accounts
        else:
            identity_type = "other"

        # Generate a unique username for AWS resources
        # Format: aws:<account_id>:<user_or_role_name>
        # Extract account ID from ARN: arn:aws:iam::123456789012:user/username
        account_id = ""
        if arn and "::" in arn:
            parts = arn.split(":")
            if len(parts) >= 5:
                account_id = parts[4]

        aws_username = f"aws:{account_id}:{name}" if account_id else f"aws:{name}"

        # Check if identity already exists
        existing = (
            self.db(
                (self.db.identities.username == aws_username)
                | (
                    (self.db.identities.auth_provider == "aws")
                    & (self.db.identities.auth_provider_id == arn)
                )
            )
            .select()
            .first()
        )

        if existing:
            # Update existing identity
            self.db(self.db.identities.id == existing.id).update(
                full_name=name,
                updated_at=datetime.utcnow(),
            )
        else:
            # Create new identity
            self.db.identities.insert(
                tenant_id=1,  # Default tenant
                identity_type=identity_type,
                username=aws_username,
                full_name=name,
                organization_id=organization_id,
                auth_provider="aws",
                auth_provider_id=arn,
                portal_role="observer",  # AWS identities get observer role by default
                is_active=True,
                is_superuser=False,
                mfa_enabled=False,
                created_at=datetime.utcnow(),
            )

    def _store_as_entity(
        self,
        organization_id: int,
        resource: Dict[str, Any],
        entity_type: str,
    ) -> None:
        """
        Store a discovered resource in the generic entities table.

        Args:
            organization_id: Organization ID
            resource: Discovered resource data
            entity_type: Entity type (compute, storage, network, etc.)
        """
        name = resource.get("name", "Unnamed")
        resource_type = resource.get("resource_type", "")

        # Check if entity already exists
        existing = (
            self.db(
                (self.db.entities.organization_id == organization_id)
                & (self.db.entities.sub_type == resource_type)
                & (self.db.entities.name == name)
            )
            .select()
            .first()
        )

        # Prepare attributes JSON
        resource_attrs = {
            "resource_id": resource.get("resource_id"),
            "resource_type": resource_type,
            "region": resource.get("region"),
            "tags": resource.get("tags", {}),
            "metadata": resource.get("metadata", {}),
            "discovered_at": datetime.utcnow().isoformat(),
        }

        if existing:
            # Update existing entity
            self.db(self.db.entities.id == existing.id).update(
                name=name,
                attributes=resource_attrs,
                updated_at=datetime.utcnow(),
            )
        else:
            # Create new entity
            self.db.entities.insert(
                name=name,
                entity_type=entity_type,
                sub_type=resource_type,
                organization_id=organization_id,
                attributes=resource_attrs,
                created_at=datetime.utcnow(),
            )

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

    # Scanner service methods

    def get_pending_jobs(self) -> List[Dict[str, Any]]:
        """
        Get jobs that are ready to be picked up by the scanner.

        A job is pending if:
        - It's enabled
        - It's a local scan type (network, http_screenshot, banner)
        - Either: schedule_interval=0 (one-time) and never run, or scheduled and due

        Returns:
            List of pending job dictionaries
        """
        # Get local scan providers
        local_providers = ["network", "http_screenshot", "banner"]

        # Find pending one-time jobs (never run)
        pending_jobs = self.db(
            (self.db.discovery_jobs.enabled == True)  # noqa: E712
            & (self.db.discovery_jobs.provider.belongs(local_providers))
            & (self.db.discovery_jobs.schedule_interval == 0)
            & (self.db.discovery_jobs.last_run_at == None)  # noqa: E711
        ).select()

        # Also get scheduled jobs that are due
        now = datetime.utcnow()
        scheduled_jobs = self.db(
            (self.db.discovery_jobs.enabled == True)  # noqa: E712
            & (self.db.discovery_jobs.provider.belongs(local_providers))
            & (self.db.discovery_jobs.schedule_interval > 0)
            & (
                (self.db.discovery_jobs.next_run_at == None)  # noqa: E711
                | (self.db.discovery_jobs.next_run_at <= now)
            )
        ).select()

        all_jobs = list(pending_jobs) + list(scheduled_jobs)

        return [self._sanitize_job(job.as_dict()) for job in all_jobs]

    def mark_job_running(self, job_id: int) -> Dict[str, Any]:
        """
        Mark a job as currently running.

        Args:
            job_id: Job ID

        Returns:
            Updated job info

        Raises:
            Exception: If job not found
        """
        job = self.db.discovery_jobs[job_id]
        if not job:
            raise Exception(f"Job not found: {job_id}")

        # Update job status
        self.db(self.db.discovery_jobs.id == job_id).update(
            last_run_at=datetime.utcnow(),
        )

        # Create history entry
        self.db.discovery_history.insert(
            job_id=job_id,
            started_at=datetime.utcnow(),
            status="running",
            entities_discovered=0,
            entities_updated=0,
            entities_created=0,
        )

        self.db.commit()

        return {"success": True, "message": "Job marked as running", "job_id": job_id}

    def complete_job(
        self,
        job_id: int,
        success: bool,
        results: Dict[str, Any],
        error_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Complete a job and record results.

        Args:
            job_id: Job ID
            success: Whether the scan succeeded
            results: Scan results
            error_message: Error message if failed

        Returns:
            Completion status

        Raises:
            Exception: If job not found
        """
        job = self.db.discovery_jobs[job_id]
        if not job:
            raise Exception(f"Job not found: {job_id}")

        # Find the running history entry
        history_entry = (
            self.db(
                (self.db.discovery_history.job_id == job_id)
                & (self.db.discovery_history.status == "running")
            )
            .select(orderby=~self.db.discovery_history.started_at)
            .first()
        )

        if history_entry:
            # Update history entry
            status = "completed" if success else "failed"
            self.db(self.db.discovery_history.id == history_entry.id).update(
                completed_at=datetime.utcnow(),
                status=status,
                error_message=error_message,
                results_json=results,
            )

        # Update next_run_at for scheduled jobs
        if job.schedule_interval and job.schedule_interval > 0:
            from datetime import timedelta

            next_run = datetime.utcnow() + timedelta(seconds=job.schedule_interval)
            self.db(self.db.discovery_jobs.id == job_id).update(next_run_at=next_run)

        self.db.commit()

        return {
            "success": True,
            "message": "Job completed",
            "job_id": job_id,
            "status": "completed" if success else "failed",
        }
