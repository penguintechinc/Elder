"""Base abstract class for IAM providers."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime


class BaseIAMProvider(ABC):
    """Abstract base class for IAM providers (AWS IAM, GCP IAM, Kubernetes RBAC)."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the IAM provider.

        Args:
            config: Provider-specific configuration dictionary
        """
        self.config = config
        self.provider_type = config.get("provider_type")

    # User/Principal Management

    @abstractmethod
    def list_users(
        self, limit: Optional[int] = None, next_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List all users/service accounts/principals.

        Args:
            limit: Maximum number of users to return
            next_token: Pagination token

        Returns:
            Dictionary with:
            {
                "users": [list of user dicts],
                "next_token": "pagination-token" or None
            }
        """
        pass

    @abstractmethod
    def get_user(self, user_identifier: str) -> Dict[str, Any]:
        """
        Get user/service account details.

        Args:
            user_identifier: Username, email, or unique ID

        Returns:
            Dictionary with user details
        """
        pass

    @abstractmethod
    def create_user(
        self,
        username: str,
        display_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new user/service account.

        Args:
            username: Username or service account name
            display_name: Display name
            tags: Tags/labels
            **kwargs: Provider-specific options

        Returns:
            Dictionary with created user details
        """
        pass

    @abstractmethod
    def delete_user(self, user_identifier: str) -> Dict[str, Any]:
        """
        Delete a user/service account.

        Args:
            user_identifier: Username, email, or unique ID

        Returns:
            Dictionary with deletion result
        """
        pass

    @abstractmethod
    def update_user(
        self,
        user_identifier: str,
        display_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update user/service account metadata.

        Args:
            user_identifier: Username, email, or unique ID
            display_name: New display name
            tags: New tags/labels
            **kwargs: Provider-specific options

        Returns:
            Dictionary with updated user details
        """
        pass

    # Role Management

    @abstractmethod
    def list_roles(
        self, limit: Optional[int] = None, next_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List all roles.

        Args:
            limit: Maximum number of roles to return
            next_token: Pagination token

        Returns:
            Dictionary with:
            {
                "roles": [list of role dicts],
                "next_token": "pagination-token" or None
            }
        """
        pass

    @abstractmethod
    def get_role(self, role_identifier: str) -> Dict[str, Any]:
        """
        Get role details.

        Args:
            role_identifier: Role name or ARN

        Returns:
            Dictionary with role details
        """
        pass

    @abstractmethod
    def create_role(
        self,
        role_name: str,
        description: Optional[str] = None,
        trust_policy: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new role.

        Args:
            role_name: Role name
            description: Role description
            trust_policy: Trust/assume role policy
            tags: Tags/labels
            **kwargs: Provider-specific options

        Returns:
            Dictionary with created role details
        """
        pass

    @abstractmethod
    def delete_role(self, role_identifier: str) -> Dict[str, Any]:
        """
        Delete a role.

        Args:
            role_identifier: Role name or ARN

        Returns:
            Dictionary with deletion result
        """
        pass

    @abstractmethod
    def update_role(
        self,
        role_identifier: str,
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update role metadata.

        Args:
            role_identifier: Role name or ARN
            description: New description
            tags: New tags/labels
            **kwargs: Provider-specific options

        Returns:
            Dictionary with updated role details
        """
        pass

    # Policy Management

    @abstractmethod
    def list_policies(
        self, scope: Optional[str] = None, limit: Optional[int] = None, next_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List policies.

        Args:
            scope: Policy scope (e.g., "Local", "AWS", "All")
            limit: Maximum number of policies to return
            next_token: Pagination token

        Returns:
            Dictionary with:
            {
                "policies": [list of policy dicts],
                "next_token": "pagination-token" or None
            }
        """
        pass

    @abstractmethod
    def get_policy(self, policy_identifier: str) -> Dict[str, Any]:
        """
        Get policy details.

        Args:
            policy_identifier: Policy name or ARN

        Returns:
            Dictionary with policy details
        """
        pass

    @abstractmethod
    def create_policy(
        self,
        policy_name: str,
        policy_document: Dict[str, Any],
        description: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new policy.

        Args:
            policy_name: Policy name
            policy_document: Policy document/permissions
            description: Policy description
            tags: Tags/labels
            **kwargs: Provider-specific options

        Returns:
            Dictionary with created policy details
        """
        pass

    @abstractmethod
    def delete_policy(self, policy_identifier: str) -> Dict[str, Any]:
        """
        Delete a policy.

        Args:
            policy_identifier: Policy name or ARN

        Returns:
            Dictionary with deletion result
        """
        pass

    # Policy Attachments

    @abstractmethod
    def attach_policy_to_user(
        self, user_identifier: str, policy_identifier: str
    ) -> Dict[str, Any]:
        """
        Attach a policy to a user.

        Args:
            user_identifier: Username, email, or unique ID
            policy_identifier: Policy name or ARN

        Returns:
            Dictionary with attachment result
        """
        pass

    @abstractmethod
    def detach_policy_from_user(
        self, user_identifier: str, policy_identifier: str
    ) -> Dict[str, Any]:
        """
        Detach a policy from a user.

        Args:
            user_identifier: Username, email, or unique ID
            policy_identifier: Policy name or ARN

        Returns:
            Dictionary with detachment result
        """
        pass

    @abstractmethod
    def attach_policy_to_role(
        self, role_identifier: str, policy_identifier: str
    ) -> Dict[str, Any]:
        """
        Attach a policy to a role.

        Args:
            role_identifier: Role name or ARN
            policy_identifier: Policy name or ARN

        Returns:
            Dictionary with attachment result
        """
        pass

    @abstractmethod
    def detach_policy_from_role(
        self, role_identifier: str, policy_identifier: str
    ) -> Dict[str, Any]:
        """
        Detach a policy from a role.

        Args:
            role_identifier: Role name or ARN
            policy_identifier: Policy name or ARN

        Returns:
            Dictionary with detachment result
        """
        pass

    @abstractmethod
    def list_user_policies(self, user_identifier: str) -> List[Dict[str, Any]]:
        """
        List all policies attached to a user.

        Args:
            user_identifier: Username, email, or unique ID

        Returns:
            List of policy dictionaries
        """
        pass

    @abstractmethod
    def list_role_policies(self, role_identifier: str) -> List[Dict[str, Any]]:
        """
        List all policies attached to a role.

        Args:
            role_identifier: Role name or ARN

        Returns:
            List of policy dictionaries
        """
        pass

    # Access Keys / Credentials

    @abstractmethod
    def create_access_key(self, user_identifier: str) -> Dict[str, Any]:
        """
        Create access credentials for a user.

        Args:
            user_identifier: Username, email, or unique ID

        Returns:
            Dictionary with access key details
        """
        pass

    @abstractmethod
    def list_access_keys(self, user_identifier: str) -> List[Dict[str, Any]]:
        """
        List access keys for a user.

        Args:
            user_identifier: Username, email, or unique ID

        Returns:
            List of access key dictionaries
        """
        pass

    @abstractmethod
    def delete_access_key(
        self, user_identifier: str, access_key_id: str
    ) -> Dict[str, Any]:
        """
        Delete an access key.

        Args:
            user_identifier: Username, email, or unique ID
            access_key_id: Access key ID to delete

        Returns:
            Dictionary with deletion result
        """
        pass

    # Group Management (optional, not all providers support)

    def list_groups(
        self, limit: Optional[int] = None, next_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List all groups (if supported).

        Args:
            limit: Maximum number of groups to return
            next_token: Pagination token

        Returns:
            Dictionary with groups list and pagination
        """
        return {"groups": [], "next_token": None, "supported": False}

    def create_group(
        self, group_name: str, description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a group (if supported)."""
        raise NotImplementedError("Groups not supported by this provider")

    def delete_group(self, group_identifier: str) -> Dict[str, Any]:
        """Delete a group (if supported)."""
        raise NotImplementedError("Groups not supported by this provider")

    def add_user_to_group(
        self, user_identifier: str, group_identifier: str
    ) -> Dict[str, Any]:
        """Add user to group (if supported)."""
        raise NotImplementedError("Groups not supported by this provider")

    def remove_user_from_group(
        self, user_identifier: str, group_identifier: str
    ) -> Dict[str, Any]:
        """Remove user from group (if supported)."""
        raise NotImplementedError("Groups not supported by this provider")

    # Utility Methods

    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test connectivity to the IAM provider.

        Returns:
            True if connection successful, False otherwise
        """
        pass

    @abstractmethod
    def sync_from_provider(self) -> Dict[str, Any]:
        """
        Sync IAM resources from provider to Elder database.

        Returns:
            Dictionary with sync statistics:
            {
                "users_synced": int,
                "roles_synced": int,
                "policies_synced": int,
                "errors": [list of error messages]
            }
        """
        pass

    def _normalize_user(self, raw_user: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize provider-specific user data to common format.

        Args:
            raw_user: Provider-specific user data

        Returns:
            Normalized user dictionary
        """
        return {
            "id": raw_user.get("id") or raw_user.get("UserId") or raw_user.get("name"),
            "username": raw_user.get("username")
            or raw_user.get("UserName")
            or raw_user.get("email"),
            "display_name": raw_user.get("display_name") or raw_user.get("DisplayName"),
            "email": raw_user.get("email") or raw_user.get("Email"),
            "created_at": raw_user.get("created_at") or raw_user.get("CreateDate"),
            "arn": raw_user.get("arn") or raw_user.get("Arn"),
        }

    def _normalize_role(self, raw_role: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize provider-specific role data to common format.

        Args:
            raw_role: Provider-specific role data

        Returns:
            Normalized role dictionary
        """
        return {
            "id": raw_role.get("id") or raw_role.get("RoleId") or raw_role.get("name"),
            "name": raw_role.get("name") or raw_role.get("RoleName"),
            "description": raw_role.get("description") or raw_role.get("Description"),
            "created_at": raw_role.get("created_at") or raw_role.get("CreateDate"),
            "arn": raw_role.get("arn") or raw_role.get("Arn"),
        }

    def _normalize_policy(self, raw_policy: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize provider-specific policy data to common format.

        Args:
            raw_policy: Provider-specific policy data

        Returns:
            Normalized policy dictionary
        """
        return {
            "id": raw_policy.get("id")
            or raw_policy.get("PolicyId")
            or raw_policy.get("name"),
            "name": raw_policy.get("name") or raw_policy.get("PolicyName"),
            "description": raw_policy.get("description")
            or raw_policy.get("Description"),
            "created_at": raw_policy.get("created_at") or raw_policy.get("CreateDate"),
            "arn": raw_policy.get("arn") or raw_policy.get("Arn"),
        }
