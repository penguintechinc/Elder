"""Converters between database models and protobuf messages."""

from datetime import datetime
from typing import List, Optional

from apps.api.grpc.generated import (
    common_pb2,
    organization_pb2,
    entity_pb2,
    dependency_pb2,
    auth_pb2,
)
from apps.api.models import (
    Organization,
    Entity,
    Dependency,
    Identity,
)


def datetime_to_timestamp(dt: Optional[datetime]) -> common_pb2.Timestamp:
    """Convert datetime to protobuf Timestamp."""
    if dt is None:
        return common_pb2.Timestamp(seconds=0, nanos=0)

    timestamp = int(dt.timestamp())
    nanos = dt.microsecond * 1000
    return common_pb2.Timestamp(seconds=timestamp, nanos=nanos)


def dict_to_metadata_fields(data: dict) -> List[common_pb2.MetadataField]:
    """Convert dict to list of MetadataField."""
    if not data:
        return []

    fields = []
    for key, value in data.items():
        # Determine type
        if isinstance(value, bool):
            field_type = "boolean"
            value_str = str(value).lower()
        elif isinstance(value, (int, float)):
            field_type = "number"
            value_str = str(value)
        elif isinstance(value, dict) or isinstance(value, list):
            field_type = "json"
            import json
            value_str = json.dumps(value)
        else:
            field_type = "string"
            value_str = str(value)

        fields.append(
            common_pb2.MetadataField(
                key=key,
                value=value_str,
                type=field_type,
            )
        )
    return fields


def organization_to_proto(org: Organization) -> organization_pb2.Organization:
    """Convert Organization model to protobuf message."""
    return organization_pb2.Organization(
        id=org.id,
        parent_id=org.parent_id or 0,
        name=org.name,
        description=org.description or "",
        ldap_dn=org.ldap_dn or "",
        saml_group=org.saml_group or "",
        owner_identity_id=org.owner_identity_id or 0,
        owner_group_id=org.owner_group_id or 0,
        metadata=dict_to_metadata_fields(org.metadata or {}),
        created_at=datetime_to_timestamp(org.created_at),
        updated_at=datetime_to_timestamp(org.updated_at),
    )


def entity_type_to_proto(entity_type: str) -> entity_pb2.EntityType:
    """Convert entity type string to protobuf enum."""
    mapping = {
        "datacenter": entity_pb2.EntityType.DATACENTER,
        "vpc": entity_pb2.EntityType.VPC,
        "subnet": entity_pb2.EntityType.SUBNET,
        "compute": entity_pb2.EntityType.COMPUTE,
        "network": entity_pb2.EntityType.NETWORK,
        "user": entity_pb2.EntityType.USER,
        "security_issue": entity_pb2.EntityType.SECURITY_ISSUE,
    }
    return mapping.get(entity_type, entity_pb2.EntityType.ENTITY_TYPE_UNSPECIFIED)


def entity_type_from_proto(entity_type: entity_pb2.EntityType) -> str:
    """Convert protobuf entity type enum to string."""
    mapping = {
        entity_pb2.EntityType.DATACENTER: "datacenter",
        entity_pb2.EntityType.VPC: "vpc",
        entity_pb2.EntityType.SUBNET: "subnet",
        entity_pb2.EntityType.COMPUTE: "compute",
        entity_pb2.EntityType.NETWORK: "network",
        entity_pb2.EntityType.USER: "user",
        entity_pb2.EntityType.SECURITY_ISSUE: "security_issue",
    }
    return mapping.get(entity_type, "datacenter")


def entity_to_proto(entity: Entity) -> entity_pb2.Entity:
    """Convert Entity model to protobuf message."""
    return entity_pb2.Entity(
        id=entity.id,
        unique_id=entity.unique_id or "",
        organization_id=entity.organization_id,
        entity_type=entity_type_to_proto(entity.entity_type),
        name=entity.name,
        description=entity.description or "",
        metadata=dict_to_metadata_fields(entity.metadata or {}),
        owner_identity_id=entity.owner_identity_id or 0,
        created_at=datetime_to_timestamp(entity.created_at),
        updated_at=datetime_to_timestamp(entity.updated_at),
        organization_name=entity.organization.name if entity.organization else "",
    )


def dependency_type_to_proto(dep_type: str) -> entity_pb2.DependencyType:
    """Convert dependency type string to protobuf enum."""
    mapping = {
        "depends_on": entity_pb2.DependencyType.DEPENDS_ON,
        "related_to": entity_pb2.DependencyType.RELATED_TO,
        "part_of": entity_pb2.DependencyType.PART_OF,
    }
    return mapping.get(dep_type, entity_pb2.DependencyType.DEPENDENCY_TYPE_UNSPECIFIED)


def dependency_type_from_proto(dep_type: entity_pb2.DependencyType) -> str:
    """Convert protobuf dependency type enum to string."""
    mapping = {
        entity_pb2.DependencyType.DEPENDS_ON: "depends_on",
        entity_pb2.DependencyType.RELATED_TO: "related_to",
        entity_pb2.DependencyType.PART_OF: "part_of",
    }
    return mapping.get(dep_type, "depends_on")


def dependency_to_proto(dep: Dependency) -> entity_pb2.Dependency:
    """Convert Dependency model to protobuf message."""
    proto = entity_pb2.Dependency(
        id=dep.id,
        source_entity_id=dep.source_entity_id,
        target_entity_id=dep.target_entity_id,
        dependency_type=dependency_type_to_proto(dep.dependency_type),
        metadata=dict_to_metadata_fields(dep.metadata or {}),
        created_at=datetime_to_timestamp(dep.created_at),
    )

    # Optionally include entity details
    if dep.source_entity:
        proto.source_entity.CopyFrom(entity_to_proto(dep.source_entity))
    if dep.target_entity:
        proto.target_entity.CopyFrom(entity_to_proto(dep.target_entity))

    return proto


def identity_type_to_proto(identity_type: str) -> auth_pb2.IdentityType:
    """Convert identity type string to protobuf enum."""
    mapping = {
        "human": auth_pb2.IdentityType.HUMAN,
        "service_account": auth_pb2.IdentityType.SERVICE_ACCOUNT,
    }
    return mapping.get(identity_type, auth_pb2.IdentityType.IDENTITY_TYPE_UNSPECIFIED)


def auth_provider_to_proto(auth_provider: str) -> auth_pb2.AuthProvider:
    """Convert auth provider string to protobuf enum."""
    mapping = {
        "local": auth_pb2.AuthProvider.LOCAL,
        "saml": auth_pb2.AuthProvider.SAML,
        "oauth2": auth_pb2.AuthProvider.OAUTH2,
        "ldap": auth_pb2.AuthProvider.LDAP,
    }
    return mapping.get(auth_provider, auth_pb2.AuthProvider.AUTH_PROVIDER_UNSPECIFIED)


def identity_to_proto(identity: Identity) -> auth_pb2.Identity:
    """Convert Identity model to protobuf message."""
    return auth_pb2.Identity(
        id=identity.id,
        identity_type=identity_type_to_proto(identity.identity_type),
        username=identity.username,
        email=identity.email or "",
        display_name=identity.display_name or "",
        auth_provider=auth_provider_to_proto(identity.auth_provider),
        auth_provider_id=identity.auth_provider_id or "",
        is_active=identity.is_active,
        is_superuser=identity.is_superuser,
        last_login=datetime_to_timestamp(identity.last_login),
        created_at=datetime_to_timestamp(identity.created_at),
        updated_at=datetime_to_timestamp(identity.updated_at),
    )
