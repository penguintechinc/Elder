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

    # Sync Configs table - no dependencies
    db.define_table(
        'sync_configs',
        Field('name', 'string', length=255, notnull=True, unique=True, requires=IS_NOT_EMPTY()),
        Field('platform', 'string', length=50, notnull=True,
              requires=IS_IN_SET(['github', 'gitlab', 'jira', 'trello', 'openproject'])),
        Field('enabled', 'boolean', default=True, notnull=True),
        Field('sync_interval', 'integer', default=300, notnull=True),  # seconds
        Field('batch_fallback_enabled', 'boolean', default=True, notnull=True),
        Field('batch_size', 'integer', default=100, notnull=True),
        Field('two_way_create', 'boolean', default=False, notnull=True),
        Field('webhook_enabled', 'boolean', default=True, notnull=True),
        Field('webhook_secret', 'string', length=255),
        Field('last_sync_at', 'datetime'),
        Field('last_batch_sync_at', 'datetime'),
        Field('config_json', 'json'),  # Platform-specific configuration (API tokens, URLs, etc.)
        Field('created_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc)),
        Field('updated_at', 'datetime', update=lambda: datetime.datetime.now(datetime.timezone.utc)),
        migrate=True,
    )

    # Discovery Jobs table - no dependencies (Phase 5: Cloud Auto-Discovery)
    db.define_table(
        'discovery_jobs',
        Field('name', 'string', length=255, notnull=True, requires=IS_NOT_EMPTY()),
        Field('provider', 'string', length=50, notnull=True,
              requires=IS_IN_SET(['aws', 'gcp', 'azure', 'kubernetes'])),
        Field('config_json', 'json', notnull=True),  # Provider-specific configuration
        Field('schedule_interval', 'integer', default=3600, notnull=True),  # seconds
        Field('enabled', 'boolean', default=True, notnull=True),
        Field('last_run_at', 'datetime'),
        Field('next_run_at', 'datetime'),
        Field('created_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc)),
        Field('updated_at', 'datetime', update=lambda: datetime.datetime.now(datetime.timezone.utc)),
        migrate=True,
    )

    # Backup Jobs table - no dependencies (Phase 10: Advanced Search & Data Management)
    db.define_table(
        'backup_jobs',
        Field('name', 'string', length=255, notnull=True, requires=IS_NOT_EMPTY()),
        Field('schedule', 'string', length=100, notnull=True),  # Cron expression
        Field('retention_days', 'integer', default=30, notnull=True),
        Field('enabled', 'boolean', default=True, notnull=True),
        Field('last_run_at', 'datetime'),
        Field('created_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc)),
        Field('updated_at', 'datetime', update=lambda: datetime.datetime.now(datetime.timezone.utc)),
        migrate=True,
    )

    # Audit Retention Policies table - no dependencies (Phase 8: Audit System Enhancement)
    db.define_table(
        'audit_retention_policies',
        Field('resource_type', 'string', length=50, notnull=True, unique=True),
        Field('retention_days', 'integer', default=90, notnull=True),
        Field('enabled', 'boolean', default=True, notnull=True),
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

    # Sync Mappings table (depends on: sync_configs)
    db.define_table(
        'sync_mappings',
        Field('elder_type', 'string', length=50, notnull=True,
              requires=IS_IN_SET(['issue', 'project', 'milestone', 'label', 'organization'])),
        Field('elder_id', 'integer', notnull=True),
        Field('external_platform', 'string', length=50, notnull=True,
              requires=IS_IN_SET(['github', 'gitlab', 'jira', 'trello', 'openproject'])),
        Field('external_id', 'string', length=255, notnull=True),
        Field('sync_config_id', 'reference sync_configs', notnull=True, ondelete='CASCADE'),
        Field('sync_status', 'string', length=50, default='synced',
              requires=IS_IN_SET(['synced', 'conflict', 'error', 'pending'])),
        Field('sync_method', 'string', length=50, default='webhook',
              requires=IS_IN_SET(['webhook', 'poll', 'batch', 'manual'])),
        Field('last_synced_at', 'datetime'),
        Field('elder_updated_at', 'datetime'),
        Field('external_updated_at', 'datetime'),
        Field('created_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc)),
        Field('updated_at', 'datetime', update=lambda: datetime.datetime.now(datetime.timezone.utc)),
        migrate=True,
    )

    # Sync History table (depends on: sync_configs, identities)
    db.define_table(
        'sync_history',
        Field('sync_config_id', 'reference sync_configs', notnull=True, ondelete='CASCADE'),
        Field('correlation_id', 'string', length=36),  # UUID for distributed tracing
        Field('sync_type', 'string', length=50, notnull=True,
              requires=IS_IN_SET(['webhook', 'poll', 'batch', 'manual'])),
        Field('items_synced', 'integer', default=0, notnull=True),
        Field('items_failed', 'integer', default=0, notnull=True),
        Field('started_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc), notnull=True),
        Field('completed_at', 'datetime'),
        Field('success', 'boolean', default=True, notnull=True),
        Field('error_message', 'text'),
        Field('sync_metadata', 'json'),  # Additional sync details, platform-specific data
        migrate=True,
    )

    # Discovery History table (depends on: discovery_jobs) - Phase 5: Cloud Auto-Discovery
    db.define_table(
        'discovery_history',
        Field('job_id', 'reference discovery_jobs', notnull=True, ondelete='CASCADE'),
        Field('started_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc), notnull=True),
        Field('completed_at', 'datetime'),
        Field('status', 'string', length=50, notnull=True, default='running',
              requires=IS_IN_SET(['running', 'success', 'failed', 'partial'])),
        Field('entities_discovered', 'integer', default=0, notnull=True),
        Field('entities_created', 'integer', default=0, notnull=True),
        Field('entities_updated', 'integer', default=0, notnull=True),
        Field('error_message', 'text'),
        migrate=True,
    )

    # Saved Searches table (depends on: identities) - Phase 10: Advanced Search & Data Management
    db.define_table(
        'saved_searches',
        Field('name', 'string', length=255, notnull=True, requires=IS_NOT_EMPTY()),
        Field('query', 'text', notnull=True),
        Field('filters', 'json'),
        Field('identity_id', 'reference identities', notnull=True, ondelete='CASCADE'),
        Field('created_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc)),
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
        Field('entity_type', 'string', length=50, notnull=True),  # network, compute, storage, datacenter, security
        Field('sub_type', 'string', length=50),  # router, server, database, etc. (sub-type within entity_type)
        Field('organization_id', 'reference organizations', notnull=True, ondelete='CASCADE'),
        Field('parent_id', 'reference entities', ondelete='CASCADE'),
        Field('attributes', 'json'),  # Type-specific metadata
        Field('default_metadata', 'json'),  # Default metadata template for this sub_type
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

    # Secret Providers table (depends on: organizations) - Phase 2: Secrets Management
    db.define_table(
        'secret_providers',
        Field('name', 'string', length=255, notnull=True, requires=IS_NOT_EMPTY()),
        Field('provider', 'string', length=50, notnull=True,
              requires=IS_IN_SET(['aws_secrets_manager', 'gcp_secret_manager', 'infisical'])),
        Field('config_json', 'json', notnull=True),  # Provider-specific configuration
        Field('organization_id', 'reference organizations', notnull=True, ondelete='CASCADE'),
        Field('enabled', 'boolean', default=True, notnull=True),
        Field('last_sync_at', 'datetime'),
        Field('created_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc)),
        Field('updated_at', 'datetime', update=lambda: datetime.datetime.now(datetime.timezone.utc)),
        migrate=True,
    )

    # Key Providers table (depends on: organizations) - Phase 3: Keys Management
    db.define_table(
        'key_providers',
        Field('name', 'string', length=255, notnull=True, requires=IS_NOT_EMPTY()),
        Field('provider', 'string', length=50, notnull=True,
              requires=IS_IN_SET(['aws_kms', 'gcp_kms', 'infisical'])),
        Field('config_json', 'json', notnull=True),  # Provider-specific configuration
        Field('organization_id', 'reference organizations', notnull=True, ondelete='CASCADE'),
        Field('enabled', 'boolean', default=True, notnull=True),
        Field('last_sync_at', 'datetime'),
        Field('created_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc)),
        Field('updated_at', 'datetime', update=lambda: datetime.datetime.now(datetime.timezone.utc)),
        migrate=True,
    )

    # Cloud Accounts table (depends on: organizations) - Phase 5: Cloud Auto-Discovery
    db.define_table(
        'cloud_accounts',
        Field('name', 'string', length=255, notnull=True, requires=IS_NOT_EMPTY()),
        Field('provider', 'string', length=50, notnull=True,
              requires=IS_IN_SET(['aws', 'gcp', 'azure', 'kubernetes'])),
        Field('credentials_json', 'json', notnull=True),  # Encrypted credentials
        Field('organization_id', 'reference organizations', notnull=True, ondelete='CASCADE'),
        Field('enabled', 'boolean', default=True, notnull=True),
        Field('created_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc)),
        Field('updated_at', 'datetime', update=lambda: datetime.datetime.now(datetime.timezone.utc)),
        migrate=True,
    )

    # Webhooks table (depends on: organizations) - Phase 9: Webhook & Notification System
    db.define_table(
        'webhooks',
        Field('name', 'string', length=255, notnull=True, requires=IS_NOT_EMPTY()),
        Field('url', 'string', length=2048, notnull=True, requires=IS_URL()),
        Field('secret', 'string', length=255),  # HMAC secret for payload signing
        Field('events', 'list:string', notnull=True),  # List of event types to trigger on
        Field('enabled', 'boolean', default=True, notnull=True),
        Field('organization_id', 'reference organizations', notnull=True, ondelete='CASCADE'),
        Field('created_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc)),
        Field('updated_at', 'datetime', update=lambda: datetime.datetime.now(datetime.timezone.utc)),
        migrate=True,
    )

    # Notification Rules table (depends on: organizations) - Phase 9: Webhook & Notification System
    db.define_table(
        'notification_rules',
        Field('name', 'string', length=255, notnull=True, requires=IS_NOT_EMPTY()),
        Field('channel', 'string', length=50, notnull=True,
              requires=IS_IN_SET(['email', 'slack', 'teams', 'pagerduty', 'webhook'])),
        Field('events', 'list:string', notnull=True),  # List of event types to trigger on
        Field('config_json', 'json', notnull=True),  # Channel-specific configuration
        Field('enabled', 'boolean', default=True, notnull=True),
        Field('organization_id', 'reference organizations', notnull=True, ondelete='CASCADE'),
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

    # Sync Conflicts table (depends on: sync_mappings, identities)
    db.define_table(
        'sync_conflicts',
        Field('mapping_id', 'reference sync_mappings', notnull=True, ondelete='CASCADE'),
        Field('conflict_type', 'string', length=50, notnull=True,
              requires=IS_IN_SET(['timestamp', 'field_mismatch', 'deleted_external', 'deleted_local'])),
        Field('elder_data', 'json', notnull=True),  # Elder's version of the data
        Field('external_data', 'json', notnull=True),  # External platform's version of the data
        Field('resolution_strategy', 'string', length=50, default='manual',
              requires=IS_IN_SET(['manual', 'elder_wins', 'external_wins', 'merge'])),
        Field('resolved', 'boolean', default=False, notnull=True),
        Field('resolved_at', 'datetime'),
        Field('resolved_by_id', 'reference identities', ondelete='SET NULL'),
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

    # Secrets table (depends on: secret_providers, organizations) - Phase 2: Secrets Management
    db.define_table(
        'secrets',
        Field('name', 'string', length=255, notnull=True, requires=IS_NOT_EMPTY()),
        Field('provider_id', 'reference secret_providers', notnull=True, ondelete='CASCADE'),
        Field('provider_path', 'string', length=512, notnull=True),  # Path/name in provider
        Field('secret_type', 'string', length=50, notnull=True, default='generic',
              requires=IS_IN_SET(['generic', 'api_key', 'password', 'certificate', 'ssh_key'])),
        Field('is_kv', 'boolean', default=False, notnull=True),  # Key-Value store vs single value
        Field('organization_id', 'reference organizations', notnull=True, ondelete='CASCADE'),
        Field('parent_id', 'reference secrets', ondelete='CASCADE'),  # For hierarchical secrets
        Field('metadata', 'json'),  # Additional metadata about the secret
        Field('last_synced_at', 'datetime'),
        Field('created_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc)),
        Field('updated_at', 'datetime', update=lambda: datetime.datetime.now(datetime.timezone.utc)),
        migrate=True,
    )

    # Keys table (depends on: key_providers, organizations) - Phase 3: Keys Management
    db.define_table(
        'crypto_keys',
        Field('name', 'string', length=255, notnull=True, requires=IS_NOT_EMPTY()),
        Field('provider_id', 'reference key_providers', notnull=True, ondelete='CASCADE'),
        Field('provider_key_id', 'string', length=512, notnull=True),  # Key ID in provider
        Field('key_hash', 'string', length=255, notnull=True),  # Hash of key for tracking
        Field('organization_id', 'reference organizations', notnull=True, ondelete='CASCADE'),
        Field('metadata', 'json'),  # Additional metadata about the key
        Field('last_synced_at', 'datetime'),
        Field('created_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc)),
        Field('updated_at', 'datetime', update=lambda: datetime.datetime.now(datetime.timezone.utc)),
        migrate=True,
    )

    # Webhook Deliveries table (depends on: webhooks) - Phase 9: Webhook & Notification System
    db.define_table(
        'webhook_deliveries',
        Field('webhook_id', 'reference webhooks', notnull=True, ondelete='CASCADE'),
        Field('event_type', 'string', length=100, notnull=True),
        Field('payload', 'json', notnull=True),
        Field('response_status', 'integer'),  # HTTP status code
        Field('response_body', 'text'),
        Field('delivered_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc), notnull=True),
        Field('success', 'boolean', default=False, notnull=True),
        migrate=True,
    )

    # ==========================================
    # LEVEL 5: Tables with Level 4 dependencies
    # ==========================================

    # Secret Access Log table (depends on: secrets, identities) - Phase 2: Secrets Management
    db.define_table(
        'secret_access_log',
        Field('secret_id', 'reference secrets', notnull=True, ondelete='CASCADE'),
        Field('identity_id', 'reference identities', notnull=True, ondelete='CASCADE'),
        Field('action', 'string', length=50, notnull=True,
              requires=IS_IN_SET(['view_masked', 'view_unmasked', 'create', 'update', 'delete'])),
        Field('masked', 'boolean', default=True, notnull=True),  # Was secret masked when viewed?
        Field('accessed_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc), notnull=True),
        migrate=True,
    )

    # Key Access Log table (depends on: keys, identities) - Phase 3: Keys Management
    db.define_table(
        'key_access_log',
        Field('key_id', 'reference crypto_keys', notnull=True, ondelete='CASCADE'),
        Field('identity_id', 'reference identities', notnull=True, ondelete='CASCADE'),
        Field('action', 'string', length=50, notnull=True,
              requires=IS_IN_SET(['view', 'create', 'update', 'delete', 'encrypt', 'decrypt', 'sign'])),
        Field('accessed_at', 'datetime', default=lambda: datetime.datetime.now(datetime.timezone.utc), notnull=True),
        migrate=True,
    )
