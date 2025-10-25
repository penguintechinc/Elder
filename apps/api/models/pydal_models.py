"""PyDAL table definitions for Elder application."""

import datetime
from pydal import Field
from pydal.validators import *


def define_all_tables(db):
    """Define all database tables using PyDAL.

    Tables are defined in dependency order to satisfy foreign key references.
    """

    # ==========================================
    # LEVEL 1: Base tables with no dependencies
    # ==========================================

    # Identities table - must be first (referenced by many tables)
    db.define_table(
        'identities',
        Field('identity_type', 'string', length=50, notnull=True),
        Field('username', 'string', length=255, notnull=True, unique=True, requires=IS_NOT_EMPTY()),
        Field('email', 'string', length=255, requires=IS_EMAIL()),
        Field('full_name', 'string', length=255),
        Field('organization_id', 'integer'),  # Integer field to avoid circular FK reference
        Field('portal_role', 'string', length=20, default='observer', notnull=True,
              requires=IS_IN_SET(['admin', 'editor', 'observer'])),  # Portal access level
        Field('auth_provider', 'string', length=50, notnull=True),
        Field('auth_provider_id', 'string', length=255),
        Field('password_hash', 'string', length=255),
        Field('is_active', 'boolean', default=True, notnull=True),
        Field('is_superuser', 'boolean', default=False, notnull=True),
        Field('mfa_enabled', 'boolean', default=False, notnull=True),
        Field('mfa_secret', 'string', length=255),
        Field('last_login_at', 'datetime'),
        Field('created_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc)),
        Field('updated_at', 'datetime', update=lambda: datetime.datetime.now(datetime.timezone.utc)),
        migrate=True,
    )

    # Identity Groups table - must be before organizations
    db.define_table(
        'identity_groups',
        Field('name', 'string', length=255, notnull=True, requires=IS_NOT_EMPTY()),
        Field('description', 'string', length=512),
        Field('ldap_dn', 'string', length=512),
        Field('saml_group', 'string', length=255),
        Field('is_active', 'boolean', default=True, notnull=True),
        Field('created_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc)),
        Field('updated_at', 'datetime', update=lambda: datetime.datetime.now(datetime.timezone.utc)),
        migrate=True,
    )

    # Roles table - no dependencies
    db.define_table(
        'roles',
        Field('name', 'string', length=100, notnull=True, unique=True, requires=IS_NOT_EMPTY()),
        Field('description', 'string', length=512),
        Field('created_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc)),
        Field('updated_at', 'datetime', update=lambda: datetime.datetime.now(datetime.timezone.utc)),
        migrate=True,
    )

    # Permissions table - no dependencies
    db.define_table(
        'permissions',
        Field('name', 'string', length=100, notnull=True, unique=True, requires=IS_NOT_EMPTY()),
        Field('resource_type', 'string', length=50, notnull=True),
        Field('action_name', 'string', length=50, notnull=True),
        Field('description', 'string', length=512),
        Field('created_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc)),
        Field('updated_at', 'datetime', update=lambda: datetime.datetime.now(datetime.timezone.utc)),
        migrate=True,
    )

    # ==========================================
    # LEVEL 2: Tables with Level 1 dependencies
    # ==========================================

    # Identity Group Memberships table (depends on: identities, identity_groups)
    db.define_table(
        'identity_group_memberships',
        Field('identity_id', 'reference identities', notnull=True, ondelete='CASCADE'),
        Field('group_id', 'reference identity_groups', notnull=True, ondelete='CASCADE'),
        Field('created_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc)),
        migrate=True,
    )

    # Role Permissions table (depends on: roles, permissions)
    db.define_table(
        'role_permissions',
        Field('role_id', 'reference roles', notnull=True, ondelete='CASCADE'),
        Field('permission_id', 'reference permissions', notnull=True, ondelete='CASCADE'),
        Field('created_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc)),
        migrate=True,
    )

    # User Roles table (depends on: identities, roles)
    db.define_table(
        'user_roles',
        Field('identity_id', 'reference identities', notnull=True, ondelete='CASCADE'),
        Field('role_id', 'reference roles', notnull=True, ondelete='CASCADE'),
        Field('scope', 'string', length=50, notnull=True),
        Field('scope_id', 'integer'),
        Field('created_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc)),
        migrate=True,
    )

    # API Keys table (depends on: identities)
    db.define_table(
        'api_keys',
        Field('identity_id', 'reference identities', notnull=True, ondelete='CASCADE'),
        Field('name', 'string', length=255, notnull=True, requires=IS_NOT_EMPTY()),
        Field('key_hash', 'string', length=255, notnull=True),  # SHA256 hash of the API key
        Field('prefix', 'string', length=20, notnull=True),  # First few chars for display (e.g., "elder_123...")
        Field('last_used_at', 'datetime'),
        Field('expires_at', 'datetime'),
        Field('is_active', 'boolean', default=True, notnull=True),
        Field('created_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc)),
        Field('updated_at', 'datetime', update=lambda: datetime.datetime.now(datetime.timezone.utc)),
        migrate=True,
    )

    # Organizations table (depends on: identities, identity_groups)
    db.define_table(
        'organizations',
        Field('name', 'string', length=255, notnull=True, requires=IS_NOT_EMPTY()),
        Field('description', 'text'),
        Field('organization_type', 'string', length=50, notnull=True, default='organization',
              requires=IS_IN_SET(['department', 'organization', 'team', 'collection', 'other'])),
        Field('parent_id', 'reference organizations', ondelete='CASCADE'),
        Field('ldap_dn', 'string', length=512),
        Field('saml_group', 'string', length=255),
        Field('owner_identity_id', 'reference identities', ondelete='SET NULL'),
        Field('owner_group_id', 'reference identity_groups', ondelete='SET NULL'),
        Field('created_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc)),
        Field('updated_at', 'datetime', update=lambda: datetime.datetime.now(datetime.timezone.utc)),
        migrate=True,
    )

    # Resource Roles table (depends on: identities, identity_groups)
    db.define_table(
        'resource_roles',
        Field('identity_id', 'reference identities', ondelete='CASCADE'),
        Field('group_id', 'reference identity_groups', ondelete='CASCADE'),
        Field('role', 'string', length=50, notnull=True),
        Field('resource_type', 'string', length=50, notnull=True),
        Field('resource_id', 'integer'),
        Field('created_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc)),
        Field('updated_at', 'datetime', update=lambda: datetime.datetime.now(datetime.timezone.utc)),
        migrate=True,
    )

    # Audit Logs table (depends on: identities)
    db.define_table(
        'audit_logs',
        Field('identity_id', 'reference identities', ondelete='SET NULL'),
        Field('action_name', 'string', length=50, notnull=True),
        Field('resource_type', 'string', length=50, notnull=True),
        Field('resource_id', 'integer'),
        Field('details', 'json'),
        Field('success', 'boolean', default=True, notnull=True),
        Field('ip_address', 'string', length=45),
        Field('user_agent', 'string', length=512),
        Field('created_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc)),
        migrate=True,
    )

    # ==========================================
    # LEVEL 3: Tables with Level 2 dependencies
    # ==========================================

    # Entities table (depends on: organizations)
    db.define_table(
        'entities',
        Field('name', 'string', length=255, notnull=True, requires=IS_NOT_EMPTY()),
        Field('description', 'text'),
        Field('entity_type', 'string', length=50, notnull=True),
        Field('organization_id', 'reference organizations', notnull=True, ondelete='CASCADE'),
        Field('parent_id', 'reference entities', ondelete='CASCADE'),
        Field('attributes', 'json'),
        Field('tags', 'list:string'),
        Field('is_active', 'boolean', default=True),
        Field('created_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc)),
        Field('updated_at', 'datetime', update=lambda: datetime.datetime.now(datetime.timezone.utc)),
        migrate=True,
    )

    # Issues table (depends on: identities, organizations)
    db.define_table(
        'issues',
        Field('title', 'string', length=255, notnull=True, requires=IS_NOT_EMPTY()),
        Field('description', 'text'),
        Field('status', 'string', length=50, notnull=True, default='open'),
        Field('priority', 'string', length=50, default='medium'),
        Field('issue_type', 'string', length=50, default='other'),
        Field('reporter_id', 'reference identities', notnull=True, ondelete='CASCADE'),
        Field('assignee_id', 'reference identities', ondelete='SET NULL'),
        Field('organization_id', 'reference organizations', ondelete='CASCADE'),
        Field('closed_at', 'datetime'),
        Field('created_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc)),
        Field('updated_at', 'datetime', update=lambda: datetime.datetime.now(datetime.timezone.utc)),
        migrate=True,
    )

    # Issue Labels table - no dependencies
    db.define_table(
        'issue_labels',
        Field('name', 'string', length=100, notnull=True, unique=True, requires=IS_NOT_EMPTY()),
        Field('color', 'string', length=7, default='#cccccc'),
        Field('description', 'string', length=512),
        Field('created_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc)),
        migrate=True,
    )

    # Projects table (depends on: organizations)
    db.define_table(
        'projects',
        Field('name', 'string', length=255, notnull=True, requires=IS_NOT_EMPTY()),
        Field('description', 'text'),
        Field('status', 'string', length=50, notnull=True, default='active'),
        Field('organization_id', 'reference organizations', notnull=True, ondelete='CASCADE'),
        Field('start_date', 'date'),
        Field('end_date', 'date'),
        Field('created_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc)),
        Field('updated_at', 'datetime', update=lambda: datetime.datetime.now(datetime.timezone.utc)),
        migrate=True,
    )

    # Milestones table (depends on: organizations, projects)
    db.define_table(
        'milestones',
        Field('title', 'string', length=255, notnull=True, requires=IS_NOT_EMPTY()),
        Field('description', 'text'),
        Field('status', 'string', length=50, notnull=True, default='open'),
        Field('organization_id', 'reference organizations', notnull=True, ondelete='CASCADE'),
        Field('project_id', 'reference projects', ondelete='CASCADE'),
        Field('due_date', 'date'),
        Field('closed_at', 'datetime'),
        Field('created_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc)),
        Field('updated_at', 'datetime', update=lambda: datetime.datetime.now(datetime.timezone.utc)),
        migrate=True,
    )

    # ==========================================
    # LEVEL 4: Tables with Level 3 dependencies
    # ==========================================

    # Dependencies table (depends on: entities)
    db.define_table(
        'dependencies',
        Field('source_entity_id', 'reference entities', notnull=True, ondelete='CASCADE'),
        Field('target_entity_id', 'reference entities', notnull=True, ondelete='CASCADE'),
        Field('dependency_type', 'string', length=50, notnull=True),
        Field('metadata', 'json'),
        Field('created_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc)),
        Field('updated_at', 'datetime', update=lambda: datetime.datetime.now(datetime.timezone.utc)),
        migrate=True,
    )

    # Issue Comments table (depends on: issues, identities)
    db.define_table(
        'issue_comments',
        Field('issue_id', 'reference issues', notnull=True, ondelete='CASCADE'),
        Field('author_id', 'reference identities', notnull=True, ondelete='CASCADE'),
        Field('content', 'text', notnull=True, requires=IS_NOT_EMPTY()),
        Field('created_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc)),
        Field('updated_at', 'datetime', update=lambda: datetime.datetime.now(datetime.timezone.utc)),
        migrate=True,
    )

    # Issue Label Assignments table (depends on: issues, issue_labels)
    db.define_table(
        'issue_label_assignments',
        Field('issue_id', 'reference issues', notnull=True, ondelete='CASCADE'),
        Field('label_id', 'reference issue_labels', notnull=True, ondelete='CASCADE'),
        Field('created_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc)),
        migrate=True,
    )

    # Issue Entity Links table (depends on: issues, entities)
    db.define_table(
        'issue_entity_links',
        Field('issue_id', 'reference issues', notnull=True, ondelete='CASCADE'),
        Field('entity_id', 'reference entities', notnull=True, ondelete='CASCADE'),
        Field('created_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc)),
        migrate=True,
    )

    # Issue Milestone Links table (depends on: issues, milestones)
    db.define_table(
        'issue_milestone_links',
        Field('issue_id', 'reference issues', notnull=True, ondelete='CASCADE'),
        Field('milestone_id', 'reference milestones', notnull=True, ondelete='CASCADE'),
        Field('created_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc)),
        migrate=True,
    )

    # Issue Project Links table (depends on: issues, projects)
    db.define_table(
        'issue_project_links',
        Field('issue_id', 'reference issues', notnull=True, ondelete='CASCADE'),
        Field('project_id', 'reference projects', notnull=True, ondelete='CASCADE'),
        Field('created_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc)),
        migrate=True,
    )

    # Metadata Fields table - uses generic resource_type/resource_id pattern
    db.define_table(
        'metadata_fields',
        Field('key', 'string', length=255, notnull=True, requires=IS_NOT_EMPTY()),
        Field('value', 'text'),
        Field('field_type', 'string', length=50, notnull=True, default='string'),
        Field('is_system', 'boolean', default=False, notnull=True),
        Field('resource_type', 'string', length=50, notnull=True),
        Field('resource_id', 'integer', notnull=True),
        Field('created_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc)),
        Field('updated_at', 'datetime', update=lambda: datetime.datetime.now(datetime.timezone.utc)),
        migrate=True,
    )
