"""Identity models for users, service accounts, and groups."""

import enum
from typing import List

from sqlalchemy import Column, Enum, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship, Mapped

from apps.api.models.base import Base, IDMixin, TimestampMixin


class IdentityType(enum.Enum):
    """Types of identities."""

    HUMAN = "human"  # Human user
    SERVICE_ACCOUNT = "service_account"  # Non-human service account


class AuthProvider(enum.Enum):
    """Authentication providers."""

    LOCAL = "local"  # Local username/password
    SAML = "saml"  # SAML SSO
    OAUTH2 = "oauth2"  # OAuth2
    LDAP = "ldap"  # LDAP


class Identity(Base, IDMixin, TimestampMixin):
    """
    Identity model for users and service accounts.

    Supports multiple authentication providers (local, SAML, OAuth2, LDAP).
    """

    __tablename__ = "identities"

    # Identity type
    identity_type = Column(
        Enum(IdentityType),
        nullable=False,
        default=IdentityType.HUMAN,
        index=True,
    )

    # Core identity fields
    username = Column(String(255), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=True, index=True)
    full_name = Column(String(255), nullable=True)

    # Authentication
    auth_provider = Column(
        Enum(AuthProvider),
        nullable=False,
        default=AuthProvider.LOCAL,
        index=True,
    )
    auth_provider_id = Column(
        String(255),
        nullable=True,
        index=True,
        comment="Unique identifier from auth provider (SAML NameID, OAuth2 sub, etc.)",
    )
    password_hash = Column(String(255), nullable=True, comment="For local auth only")

    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_superuser = Column(Boolean, default=False, nullable=False)

    # Multi-factor authentication
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    mfa_secret = Column(String(255), nullable=True, comment="TOTP secret for MFA")

    # Last activity
    last_login_at = Column(
        String(255),  # Using String for ISO format datetime
        nullable=True,
        comment="Last login timestamp (ISO format)",
    )

    # Relationships
    group_memberships: Mapped[List["IdentityGroupMembership"]] = relationship(
        "IdentityGroupMembership",
        back_populates="identity",
        cascade="all, delete-orphan",
    )

    roles: Mapped[List["UserRole"]] = relationship(
        "UserRole",
        back_populates="identity",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """String representation of identity."""
        return f"<Identity(id={self.id}, username='{self.username}', type={self.identity_type.value})>"

    @property
    def display_name(self) -> str:
        """Get display name (full name or username)."""
        return self.full_name or self.username

    def get_groups(self) -> List["IdentityGroup"]:
        """
        Get all identity groups this identity belongs to.

        Returns:
            List of IdentityGroup objects
        """
        return [membership.group for membership in self.group_memberships]

    def is_member_of(self, group: "IdentityGroup") -> bool:
        """
        Check if identity is a member of a specific group.

        Args:
            group: IdentityGroup to check membership

        Returns:
            True if member, False otherwise
        """
        return any(membership.group_id == group.id for membership in self.group_memberships)


class IdentityGroup(Base, IDMixin, TimestampMixin):
    """
    Identity group model for teams and organizational groups.

    Can be mapped to LDAP or SAML groups for synchronization.
    """

    __tablename__ = "identity_groups"

    # Core fields
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(String(512), nullable=True)

    # LDAP/SAML integration
    ldap_dn = Column(
        String(512),
        nullable=True,
        index=True,
        comment="LDAP Distinguished Name for group sync",
    )
    saml_group = Column(
        String(255),
        nullable=True,
        index=True,
        comment="SAML group identifier for group sync",
    )

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    memberships: Mapped[List["IdentityGroupMembership"]] = relationship(
        "IdentityGroupMembership",
        back_populates="group",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """String representation of identity group."""
        return f"<IdentityGroup(id={self.id}, name='{self.name}')>"

    def get_members(self) -> List["Identity"]:
        """
        Get all identities that are members of this group.

        Returns:
            List of Identity objects
        """
        return [membership.identity for membership in self.memberships]

    def add_member(self, identity: "Identity") -> "IdentityGroupMembership":
        """
        Add an identity to this group.

        Args:
            identity: Identity to add

        Returns:
            Created IdentityGroupMembership
        """
        from apps.api.models.identity import IdentityGroupMembership

        membership = IdentityGroupMembership(identity=identity, group=self)
        return membership

    def remove_member(self, identity: "Identity") -> bool:
        """
        Remove an identity from this group.

        Args:
            identity: Identity to remove

        Returns:
            True if removed, False if not a member
        """
        membership = next(
            (m for m in self.memberships if m.identity_id == identity.id),
            None,
        )
        if membership:
            self.memberships.remove(membership)
            return True
        return False


class IdentityGroupMembership(Base, IDMixin, TimestampMixin):
    """
    Many-to-many relationship between identities and groups.
    """

    __tablename__ = "identity_group_memberships"

    identity_id = Column(
        Integer,
        ForeignKey("identities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    group_id = Column(
        Integer,
        ForeignKey("identity_groups.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    identity: Mapped["Identity"] = relationship(
        "Identity",
        back_populates="group_memberships",
    )

    group: Mapped["IdentityGroup"] = relationship(
        "IdentityGroup",
        back_populates="memberships",
    )

    def __repr__(self) -> str:
        """String representation of membership."""
        return f"<IdentityGroupMembership(identity_id={self.identity_id}, group_id={self.group_id})>"
