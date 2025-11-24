-- Migration: Expand village_id column length for safety
-- Version: 005
-- Description: Changes village_id from VARCHAR(16) to VARCHAR(32) for all tables
-- Reason: Original schema had length=16 but village_id format is TTTT-OOOO-IIIIIIII (18 chars)
-- This migration provides extra headroom and fixes the constraint violation

-- ============================================
-- Expand all village_id columns to VARCHAR(32)
-- ============================================

-- Tenant level
ALTER TABLE tenants ALTER COLUMN village_id TYPE VARCHAR(32);
ALTER TABLE organizations ALTER COLUMN village_id TYPE VARCHAR(32);

-- Entity level
ALTER TABLE entities ALTER COLUMN village_id TYPE VARCHAR(32);
ALTER TABLE identities ALTER COLUMN village_id TYPE VARCHAR(32);

-- Software/Services/IPAM
ALTER TABLE software ALTER COLUMN village_id TYPE VARCHAR(32);
ALTER TABLE services ALTER COLUMN village_id TYPE VARCHAR(32);
ALTER TABLE ipam_prefixes ALTER COLUMN village_id TYPE VARCHAR(32);
ALTER TABLE ipam_addresses ALTER COLUMN village_id TYPE VARCHAR(32);
ALTER TABLE ipam_vlans ALTER COLUMN village_id TYPE VARCHAR(32);

-- Issues/Projects/Milestones
ALTER TABLE issues ALTER COLUMN village_id TYPE VARCHAR(32);
ALTER TABLE projects ALTER COLUMN village_id TYPE VARCHAR(32);
ALTER TABLE milestones ALTER COLUMN village_id TYPE VARCHAR(32);

-- Metadata and roles
ALTER TABLE metadata_fields ALTER COLUMN village_id TYPE VARCHAR(32);
ALTER TABLE resource_roles ALTER COLUMN village_id TYPE VARCHAR(32);
ALTER TABLE dependencies ALTER COLUMN village_id TYPE VARCHAR(32);
