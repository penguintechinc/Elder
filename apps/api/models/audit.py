"""Audit log model for tracking all system changes."""

import enum
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import JSON, Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship

from apps.api.models.base import Base, IDMixin


class AuditAction(enum.Enum):
    """Types of actions that can be audited."""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    VIEW = "view"  # Optional: track sensitive views
    LOGIN = "login"
    LOGOUT = "logout"
    PERMISSION_CHANGE = "permission_change"
    ROLE_ASSIGNMENT = "role_assignment"


class AuditResourceType(enum.Enum):
    """Types of resources that can be audited."""

    ENTITY = "entity"
    ORGANIZATION = "organization"
    IDENTITY = "identity"
    IDENTITY_GROUP = "identity_group"
    DEPENDENCY = "dependency"
    ROLE = "role"
    PERMISSION = "permission"
    AUTH = "auth"


class AuditLog(Base, IDMixin):
    """
    Audit log for tracking all system changes and access.

    Provides comprehensive audit trail for compliance and security.
    """

    __tablename__ = "audit_logs"

    # Actor (who performed the action)
    identity_id = Column(
        Integer,
        ForeignKey("identities.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Identity that performed the action",
    )

    # Action details
    action = Column(
        Enum(AuditAction),
        nullable=False,
        index=True,
        comment="Action performed",
    )

    resource_type = Column(
        Enum(AuditResourceType),
        nullable=False,
        index=True,
        comment="Type of resource affected",
    )

    resource_id = Column(
        Integer,
        nullable=True,
        index=True,
        comment="ID of the affected resource",
    )

    # Change details
    changes = Column(
        JSON,
        nullable=True,
        comment="Details of changes made (before/after values)",
    )

    # Additional metadata
    audit_metadata = Column(
        "metadata",  # Column name in database
        JSON,
        nullable=True,
        comment="Additional context (e.g., reason, ticket number)",
    )

    # Request context
    ip_address = Column(
        String(45),
        nullable=True,
        index=True,
        comment="IP address of requester (IPv4 or IPv6)",
    )

    user_agent = Column(
        String(512),
        nullable=True,
        comment="User agent string",
    )

    # Result
    success = Column(
        String(10),
        nullable=False,
        default="true",
        comment="Whether action succeeded (true/false)",
    )

    error_message = Column(
        String(1024),
        nullable=True,
        comment="Error message if action failed",
    )

    # Timestamp
    timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    # Relationships
    identity: Mapped[Optional["Identity"]] = relationship(
        "Identity",
        backref="audit_logs",
    )

    def __repr__(self) -> str:
        """String representation of audit log entry."""
        return (
            f"<AuditLog(id={self.id}, "
            f"action={self.action.value}, "
            f"resource_type={self.resource_type.value}, "
            f"resource_id={self.resource_id}, "
            f"timestamp={self.timestamp})>"
        )

    @property
    def action_display(self) -> str:
        """Get human-readable action."""
        action_names = {
            AuditAction.CREATE: "Created",
            AuditAction.UPDATE: "Updated",
            AuditAction.DELETE: "Deleted",
            AuditAction.VIEW: "Viewed",
            AuditAction.LOGIN: "Logged In",
            AuditAction.LOGOUT: "Logged Out",
            AuditAction.PERMISSION_CHANGE: "Permission Changed",
            AuditAction.ROLE_ASSIGNMENT: "Role Assigned",
        }
        return action_names.get(self.action, self.action.value)

    @property
    def resource_type_display(self) -> str:
        """Get human-readable resource type."""
        type_names = {
            AuditResourceType.ENTITY: "Entity",
            AuditResourceType.ORGANIZATION: "Organization",
            AuditResourceType.IDENTITY: "Identity",
            AuditResourceType.IDENTITY_GROUP: "Identity Group",
            AuditResourceType.DEPENDENCY: "Dependency",
            AuditResourceType.ROLE: "Role",
            AuditResourceType.PERMISSION: "Permission",
            AuditResourceType.AUTH: "Authentication",
        }
        return type_names.get(self.resource_type, self.resource_type.value)

    def get_summary(self) -> str:
        """
        Get a human-readable summary of the audit log entry.

        Returns:
            Summary string
        """
        actor = f"User {self.identity_id}" if self.identity_id else "System"
        action = self.action_display
        resource = f"{self.resource_type_display}"

        if self.resource_id:
            resource += f" #{self.resource_id}"

        return f"{actor} {action} {resource}"
