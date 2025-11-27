-- v3.0.0: Data Stores and Group Membership Management Migration
-- Run this migration for upgrades from v2.x to v3.0.0

-- ============================================
-- Part 1: Data Stores (Community Feature)
-- ============================================

-- Create data_stores table
CREATE TABLE IF NOT EXISTS data_stores (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    village_id VARCHAR(32) UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    storage_type VARCHAR(50) DEFAULT 'other',
    storage_provider VARCHAR(100),
    location_region VARCHAR(50),
    location_physical VARCHAR(255),
    data_classification VARCHAR(20) DEFAULT 'internal',
    encryption_at_rest BOOLEAN DEFAULT FALSE,
    encryption_in_transit BOOLEAN DEFAULT FALSE,
    encryption_key_id INTEGER REFERENCES crypto_keys(id) ON DELETE SET NULL,
    retention_days INTEGER,
    backup_enabled BOOLEAN DEFAULT FALSE,
    backup_frequency VARCHAR(50),
    access_control_type VARCHAR(20) DEFAULT 'private',
    poc_identity_id INTEGER REFERENCES identities(id) ON DELETE SET NULL,
    compliance_frameworks JSONB,
    contains_pii BOOLEAN DEFAULT FALSE,
    contains_phi BOOLEAN DEFAULT FALSE,
    contains_pci BOOLEAN DEFAULT FALSE,
    size_bytes BIGINT,
    last_access_audit TIMESTAMP,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    created_by INTEGER REFERENCES portal_users(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create data_store_labels junction table
CREATE TABLE IF NOT EXISTS data_store_labels (
    id SERIAL PRIMARY KEY,
    data_store_id INTEGER NOT NULL REFERENCES data_stores(id) ON DELETE CASCADE,
    label_id INTEGER NOT NULL REFERENCES issue_labels(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(data_store_id, label_id)
);

-- Create indexes for data_stores
CREATE INDEX IF NOT EXISTS idx_data_stores_tenant ON data_stores(tenant_id);
CREATE INDEX IF NOT EXISTS idx_data_stores_org ON data_stores(organization_id);
CREATE INDEX IF NOT EXISTS idx_data_stores_classification ON data_stores(data_classification);
CREATE INDEX IF NOT EXISTS idx_data_stores_active ON data_stores(is_active);
CREATE INDEX IF NOT EXISTS idx_data_stores_pii ON data_stores(contains_pii) WHERE contains_pii = TRUE;
CREATE INDEX IF NOT EXISTS idx_data_stores_phi ON data_stores(contains_phi) WHERE contains_phi = TRUE;
CREATE INDEX IF NOT EXISTS idx_data_stores_pci ON data_stores(contains_pci) WHERE contains_pci = TRUE;

-- ============================================
-- Part 2: Group Membership Management (Enterprise)
-- ============================================

-- Add columns to identity_groups for ownership and approval workflow
ALTER TABLE identity_groups ADD COLUMN IF NOT EXISTS owner_identity_id INTEGER REFERENCES identities(id) ON DELETE SET NULL;
ALTER TABLE identity_groups ADD COLUMN IF NOT EXISTS owner_group_id INTEGER REFERENCES identity_groups(id) ON DELETE SET NULL;
ALTER TABLE identity_groups ADD COLUMN IF NOT EXISTS approval_mode VARCHAR(20) DEFAULT 'any';
ALTER TABLE identity_groups ADD COLUMN IF NOT EXISTS approval_threshold INTEGER DEFAULT 1;
ALTER TABLE identity_groups ADD COLUMN IF NOT EXISTS sync_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE identity_groups ADD COLUMN IF NOT EXISTS provider VARCHAR(50) DEFAULT 'internal';
ALTER TABLE identity_groups ADD COLUMN IF NOT EXISTS provider_group_id VARCHAR(512);

-- Add columns to identity_group_memberships for expiration and tracking
ALTER TABLE identity_group_memberships ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP;
ALTER TABLE identity_group_memberships ADD COLUMN IF NOT EXISTS granted_via_request_id INTEGER;
ALTER TABLE identity_group_memberships ADD COLUMN IF NOT EXISTS provider_synced BOOLEAN DEFAULT FALSE;
ALTER TABLE identity_group_memberships ADD COLUMN IF NOT EXISTS provider_synced_at TIMESTAMP;
ALTER TABLE identity_group_memberships ADD COLUMN IF NOT EXISTS provider_member_id VARCHAR(512);

-- Create group_access_requests table
CREATE TABLE IF NOT EXISTS group_access_requests (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    group_id INTEGER NOT NULL REFERENCES identity_groups(id) ON DELETE CASCADE,
    requester_id INTEGER NOT NULL REFERENCES identities(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'pending',
    justification TEXT,
    requested_expires_at TIMESTAMP,
    decided_at TIMESTAMP,
    decided_by INTEGER REFERENCES identities(id) ON DELETE SET NULL,
    decision_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    village_id VARCHAR(32) UNIQUE
);

-- Create group_access_approvals table for multi-approval workflows
CREATE TABLE IF NOT EXISTS group_access_approvals (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    request_id INTEGER NOT NULL REFERENCES group_access_requests(id) ON DELETE CASCADE,
    approver_id INTEGER NOT NULL REFERENCES identities(id) ON DELETE CASCADE,
    decision VARCHAR(20) NOT NULL,
    comment TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for group membership tables
CREATE INDEX IF NOT EXISTS idx_group_requests_status ON group_access_requests(status);
CREATE INDEX IF NOT EXISTS idx_group_requests_group ON group_access_requests(group_id);
CREATE INDEX IF NOT EXISTS idx_group_requests_requester ON group_access_requests(requester_id);
CREATE INDEX IF NOT EXISTS idx_group_memberships_expires ON identity_group_memberships(expires_at) WHERE expires_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_groups_provider ON identity_groups(provider);
CREATE INDEX IF NOT EXISTS idx_groups_sync_enabled ON identity_groups(sync_enabled) WHERE sync_enabled = TRUE;

-- ============================================
-- Part 3: OIDC SSO Support (Enterprise)
-- ============================================

-- Add OIDC columns to idp_configurations table
ALTER TABLE idp_configurations ADD COLUMN IF NOT EXISTS oidc_client_id VARCHAR(255);
ALTER TABLE idp_configurations ADD COLUMN IF NOT EXISTS oidc_client_secret VARCHAR(512);
ALTER TABLE idp_configurations ADD COLUMN IF NOT EXISTS oidc_issuer_url VARCHAR(512);
ALTER TABLE idp_configurations ADD COLUMN IF NOT EXISTS oidc_scopes VARCHAR(255) DEFAULT 'openid profile email';
ALTER TABLE idp_configurations ADD COLUMN IF NOT EXISTS oidc_response_type VARCHAR(50) DEFAULT 'code';
ALTER TABLE idp_configurations ADD COLUMN IF NOT EXISTS oidc_token_endpoint_auth_method VARCHAR(50) DEFAULT 'client_secret_basic';
