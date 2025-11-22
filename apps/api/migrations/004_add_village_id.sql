-- Migration: Add hierarchical village_id to trackable resources
-- Version: 004
-- Description: Adds unique hierarchical 64-bit hexadecimal identifier (village_id)
-- Format: TTTT-OOOO-IIIIIIII (tenant-org-item, 18 chars with dashes)

-- ============================================
-- Step 1: Add village_segment to tenants and organizations
-- ============================================

-- Add village_segment to tenants (stores their 4-char random segment)
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS village_segment VARCHAR(4);
UPDATE tenants SET village_segment = encode(gen_random_bytes(2), 'hex') WHERE village_segment IS NULL;

-- Add village_segment to organizations (stores their 4-char random segment)
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS village_segment VARCHAR(4);
UPDATE organizations SET village_segment = encode(gen_random_bytes(2), 'hex') WHERE village_segment IS NULL;

-- ============================================
-- Step 2: Add village_id columns with VARCHAR(18) for hierarchical format
-- ============================================

-- tenants: TTTT-0000-00000000
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS village_id VARCHAR(18) UNIQUE;
CREATE INDEX IF NOT EXISTS idx_tenants_village_id ON tenants(village_id);
UPDATE tenants SET village_id = village_segment || '-0000-00000000' WHERE village_id IS NULL;

-- organizations: TTTT-OOOO-00000000 (inherits tenant segment)
ALTER TABLE organizations ADD COLUMN IF NOT EXISTS village_id VARCHAR(18) UNIQUE;
CREATE INDEX IF NOT EXISTS idx_organizations_village_id ON organizations(village_id);
UPDATE organizations o SET village_id = (
    SELECT t.village_segment || '-' || o.village_segment || '-00000000'
    FROM tenants t WHERE t.id = o.tenant_id
) WHERE o.village_id IS NULL;

-- entities: TTTT-OOOO-IIIIIIII
ALTER TABLE entities ADD COLUMN IF NOT EXISTS village_id VARCHAR(18) UNIQUE;
CREATE INDEX IF NOT EXISTS idx_entities_village_id ON entities(village_id);
UPDATE entities e SET village_id = (
    SELECT t.village_segment || '-' || org.village_segment || '-' || encode(gen_random_bytes(4), 'hex')
    FROM organizations org
    JOIN tenants t ON t.id = org.tenant_id
    WHERE org.id = e.organization_id
) WHERE e.village_id IS NULL;

-- identities: TTTT-OOOO-IIIIIIII
ALTER TABLE identities ADD COLUMN IF NOT EXISTS village_id VARCHAR(18) UNIQUE;
CREATE INDEX IF NOT EXISTS idx_identities_village_id ON identities(village_id);
UPDATE identities i SET village_id = (
    SELECT t.village_segment || '-' || org.village_segment || '-' || encode(gen_random_bytes(4), 'hex')
    FROM organizations org
    JOIN tenants t ON t.id = org.tenant_id
    WHERE org.id = i.organization_id
) WHERE i.village_id IS NULL;

-- software: TTTT-OOOO-IIIIIIII
ALTER TABLE software ADD COLUMN IF NOT EXISTS village_id VARCHAR(18) UNIQUE;
CREATE INDEX IF NOT EXISTS idx_software_village_id ON software(village_id);
UPDATE software s SET village_id = (
    SELECT t.village_segment || '-' || org.village_segment || '-' || encode(gen_random_bytes(4), 'hex')
    FROM organizations org
    JOIN tenants t ON t.id = org.tenant_id
    WHERE org.id = s.organization_id
) WHERE s.village_id IS NULL;

-- services: TTTT-OOOO-IIIIIIII
ALTER TABLE services ADD COLUMN IF NOT EXISTS village_id VARCHAR(18) UNIQUE;
CREATE INDEX IF NOT EXISTS idx_services_village_id ON services(village_id);
UPDATE services sv SET village_id = (
    SELECT t.village_segment || '-' || org.village_segment || '-' || encode(gen_random_bytes(4), 'hex')
    FROM organizations org
    JOIN tenants t ON t.id = org.tenant_id
    WHERE org.id = sv.organization_id
) WHERE sv.village_id IS NULL;

-- ipam_prefixes: TTTT-OOOO-IIIIIIII
ALTER TABLE ipam_prefixes ADD COLUMN IF NOT EXISTS village_id VARCHAR(18) UNIQUE;
CREATE INDEX IF NOT EXISTS idx_ipam_prefixes_village_id ON ipam_prefixes(village_id);
UPDATE ipam_prefixes ip SET village_id = (
    SELECT t.village_segment || '-' || org.village_segment || '-' || encode(gen_random_bytes(4), 'hex')
    FROM organizations org
    JOIN tenants t ON t.id = org.tenant_id
    WHERE org.id = ip.organization_id
) WHERE ip.village_id IS NULL;

-- ipam_addresses: Uses tenant from prefix
ALTER TABLE ipam_addresses ADD COLUMN IF NOT EXISTS village_id VARCHAR(18) UNIQUE;
CREATE INDEX IF NOT EXISTS idx_ipam_addresses_village_id ON ipam_addresses(village_id);
UPDATE ipam_addresses ia SET village_id = (
    SELECT t.village_segment || '-' || org.village_segment || '-' || encode(gen_random_bytes(4), 'hex')
    FROM ipam_prefixes ip
    JOIN organizations org ON org.id = ip.organization_id
    JOIN tenants t ON t.id = org.tenant_id
    WHERE ip.id = ia.prefix_id
) WHERE ia.village_id IS NULL;

-- ipam_vlans: TTTT-OOOO-IIIIIIII
ALTER TABLE ipam_vlans ADD COLUMN IF NOT EXISTS village_id VARCHAR(18) UNIQUE;
CREATE INDEX IF NOT EXISTS idx_ipam_vlans_village_id ON ipam_vlans(village_id);
UPDATE ipam_vlans iv SET village_id = (
    SELECT t.village_segment || '-' || org.village_segment || '-' || encode(gen_random_bytes(4), 'hex')
    FROM organizations org
    JOIN tenants t ON t.id = org.tenant_id
    WHERE org.id = iv.organization_id
) WHERE iv.village_id IS NULL;

-- issues: TTTT-OOOO-IIIIIIII
ALTER TABLE issues ADD COLUMN IF NOT EXISTS village_id VARCHAR(18) UNIQUE;
CREATE INDEX IF NOT EXISTS idx_issues_village_id ON issues(village_id);
UPDATE issues i SET village_id = (
    SELECT t.village_segment || '-' || org.village_segment || '-' || encode(gen_random_bytes(4), 'hex')
    FROM organizations org
    JOIN tenants t ON t.id = org.tenant_id
    WHERE org.id = i.organization_id
) WHERE i.village_id IS NULL;

-- projects: TTTT-OOOO-IIIIIIII
ALTER TABLE projects ADD COLUMN IF NOT EXISTS village_id VARCHAR(18) UNIQUE;
CREATE INDEX IF NOT EXISTS idx_projects_village_id ON projects(village_id);
UPDATE projects p SET village_id = (
    SELECT t.village_segment || '-' || org.village_segment || '-' || encode(gen_random_bytes(4), 'hex')
    FROM organizations org
    JOIN tenants t ON t.id = org.tenant_id
    WHERE org.id = p.organization_id
) WHERE p.village_id IS NULL;

-- milestones: TTTT-OOOO-IIIIIIII (via project)
ALTER TABLE milestones ADD COLUMN IF NOT EXISTS village_id VARCHAR(18) UNIQUE;
CREATE INDEX IF NOT EXISTS idx_milestones_village_id ON milestones(village_id);
UPDATE milestones m SET village_id = (
    SELECT t.village_segment || '-' || org.village_segment || '-' || encode(gen_random_bytes(4), 'hex')
    FROM projects p
    JOIN organizations org ON org.id = p.organization_id
    JOIN tenants t ON t.id = org.tenant_id
    WHERE p.id = m.project_id
) WHERE m.village_id IS NULL;

-- metadata_fields: TTTT-0000-IIIIIIII (tenant-level, no org)
ALTER TABLE metadata_fields ADD COLUMN IF NOT EXISTS village_id VARCHAR(18) UNIQUE;
CREATE INDEX IF NOT EXISTS idx_metadata_fields_village_id ON metadata_fields(village_id);
UPDATE metadata_fields mf SET village_id = (
    SELECT t.village_segment || '-0000-' || encode(gen_random_bytes(4), 'hex')
    FROM tenants t WHERE t.id = mf.tenant_id
) WHERE mf.village_id IS NULL;

-- resource_roles: TTTT-0000-IIIIIIII (tenant-level)
ALTER TABLE resource_roles ADD COLUMN IF NOT EXISTS village_id VARCHAR(18) UNIQUE;
CREATE INDEX IF NOT EXISTS idx_resource_roles_village_id ON resource_roles(village_id);
UPDATE resource_roles rr SET village_id = (
    SELECT t.village_segment || '-0000-' || encode(gen_random_bytes(4), 'hex')
    FROM tenants t WHERE t.id = rr.tenant_id
) WHERE rr.village_id IS NULL;

-- dependencies: TTTT-0000-IIIIIIII (tenant-level)
ALTER TABLE dependencies ADD COLUMN IF NOT EXISTS village_id VARCHAR(18) UNIQUE;
CREATE INDEX IF NOT EXISTS idx_dependencies_village_id ON dependencies(village_id);
UPDATE dependencies d SET village_id = (
    SELECT t.village_segment || '-0000-' || encode(gen_random_bytes(4), 'hex')
    FROM tenants t WHERE t.id = d.tenant_id
) WHERE d.village_id IS NULL;
