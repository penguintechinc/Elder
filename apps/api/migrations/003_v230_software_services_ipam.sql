-- Migration: v2.3.0 - Add Software, Services, and IPAM tables
-- This adds Software tracking, Microservice tracking, and IP Address Management

-- ==========================================
-- Software table - Track software licenses and purchases
-- ==========================================
CREATE TABLE IF NOT EXISTS software (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    purchasing_poc_id INTEGER REFERENCES identities(id) ON DELETE SET NULL,
    license_url VARCHAR(1024) DEFAULT 'https://www.gnu.org/licenses/agpl-3.0.html',
    version VARCHAR(100),
    business_purpose TEXT,
    software_type VARCHAR(50) NOT NULL,
    seats INTEGER,
    cost_monthly DECIMAL(10,2),
    renewal_date DATE,
    vendor VARCHAR(255),
    support_contact VARCHAR(255),
    notes TEXT,
    tags TEXT[],
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_software_tenant ON software(tenant_id);
CREATE INDEX IF NOT EXISTS idx_software_organization ON software(organization_id);
CREATE INDEX IF NOT EXISTS idx_software_type ON software(software_type);

-- ==========================================
-- Services table - Track microservices and applications
-- ==========================================
CREATE TABLE IF NOT EXISTS services (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    domains TEXT[],
    paths TEXT[],
    poc_identity_id INTEGER REFERENCES identities(id) ON DELETE SET NULL,
    language VARCHAR(50),
    deployment_method VARCHAR(50),
    deployment_type VARCHAR(100),
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    port INTEGER,
    health_endpoint VARCHAR(255),
    repository_url VARCHAR(1024),
    documentation_url VARCHAR(1024),
    sla_uptime DECIMAL(5,2),
    sla_response_time_ms INTEGER,
    notes TEXT,
    tags TEXT[],
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_services_tenant ON services(tenant_id);
CREATE INDEX IF NOT EXISTS idx_services_organization ON services(organization_id);
CREATE INDEX IF NOT EXISTS idx_services_status ON services(status);
CREATE INDEX IF NOT EXISTS idx_services_language ON services(language);

-- ==========================================
-- IPAM Prefixes table - IP address prefixes/subnets
-- ==========================================
CREATE TABLE IF NOT EXISTS ipam_prefixes (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    prefix VARCHAR(50) NOT NULL,
    description TEXT,
    organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    parent_id INTEGER REFERENCES ipam_prefixes(id) ON DELETE CASCADE,
    vlan_id INTEGER,
    vrf VARCHAR(100),
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    role VARCHAR(100),
    is_pool BOOLEAN NOT NULL DEFAULT FALSE,
    site VARCHAR(255),
    region VARCHAR(100),
    tags TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ipam_prefixes_tenant ON ipam_prefixes(tenant_id);
CREATE INDEX IF NOT EXISTS idx_ipam_prefixes_organization ON ipam_prefixes(organization_id);
CREATE INDEX IF NOT EXISTS idx_ipam_prefixes_prefix ON ipam_prefixes(prefix);
CREATE INDEX IF NOT EXISTS idx_ipam_prefixes_parent ON ipam_prefixes(parent_id);
CREATE INDEX IF NOT EXISTS idx_ipam_prefixes_status ON ipam_prefixes(status);

-- ==========================================
-- IPAM Addresses table - Individual IP addresses
-- ==========================================
CREATE TABLE IF NOT EXISTS ipam_addresses (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    address VARCHAR(50) NOT NULL,
    prefix_id INTEGER NOT NULL REFERENCES ipam_prefixes(id) ON DELETE CASCADE,
    dns_name VARCHAR(255),
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    assigned_object_type VARCHAR(50),
    assigned_object_id INTEGER,
    nat_inside_id INTEGER REFERENCES ipam_addresses(id) ON DELETE SET NULL,
    tags TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ipam_addresses_tenant ON ipam_addresses(tenant_id);
CREATE INDEX IF NOT EXISTS idx_ipam_addresses_prefix ON ipam_addresses(prefix_id);
CREATE INDEX IF NOT EXISTS idx_ipam_addresses_address ON ipam_addresses(address);
CREATE INDEX IF NOT EXISTS idx_ipam_addresses_status ON ipam_addresses(status);
CREATE INDEX IF NOT EXISTS idx_ipam_addresses_assigned ON ipam_addresses(assigned_object_type, assigned_object_id);

-- ==========================================
-- IPAM VLANs table - VLAN management
-- ==========================================
CREATE TABLE IF NOT EXISTS ipam_vlans (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL DEFAULT 1 REFERENCES tenants(id) ON DELETE CASCADE,
    vid INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    role VARCHAR(100),
    site VARCHAR(255),
    tags TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ipam_vlans_tenant ON ipam_vlans(tenant_id);
CREATE INDEX IF NOT EXISTS idx_ipam_vlans_organization ON ipam_vlans(organization_id);
CREATE INDEX IF NOT EXISTS idx_ipam_vlans_vid ON ipam_vlans(vid);
CREATE INDEX IF NOT EXISTS idx_ipam_vlans_status ON ipam_vlans(status);
