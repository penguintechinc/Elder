-- Migration: Convert dependencies to polymorphic links
-- This allows linking between any resource types (entities, identities, projects, milestones, issues, organizations)

-- Step 1: Add new columns
ALTER TABLE dependencies ADD COLUMN IF NOT EXISTS tenant_id INTEGER;
ALTER TABLE dependencies ADD COLUMN IF NOT EXISTS source_type VARCHAR(50);
ALTER TABLE dependencies ADD COLUMN IF NOT EXISTS source_id INTEGER;
ALTER TABLE dependencies ADD COLUMN IF NOT EXISTS target_type VARCHAR(50);
ALTER TABLE dependencies ADD COLUMN IF NOT EXISTS target_id INTEGER;

-- Step 2: Migrate existing data (entity-to-entity links)
UPDATE dependencies
SET
    source_type = 'entity',
    source_id = source_entity_id,
    target_type = 'entity',
    target_id = target_entity_id,
    tenant_id = (SELECT tenant_id FROM entities WHERE entities.id = dependencies.source_entity_id)
WHERE source_type IS NULL;

-- Step 3: Make new columns NOT NULL after migration
ALTER TABLE dependencies ALTER COLUMN tenant_id SET NOT NULL;
ALTER TABLE dependencies ALTER COLUMN source_type SET NOT NULL;
ALTER TABLE dependencies ALTER COLUMN source_id SET NOT NULL;
ALTER TABLE dependencies ALTER COLUMN target_type SET NOT NULL;
ALTER TABLE dependencies ALTER COLUMN target_id SET NOT NULL;

-- Step 4: Drop old foreign key columns
ALTER TABLE dependencies DROP COLUMN IF EXISTS source_entity_id;
ALTER TABLE dependencies DROP COLUMN IF EXISTS target_entity_id;

-- Step 5: Add foreign key constraint for tenant
ALTER TABLE dependencies ADD CONSTRAINT fk_dependencies_tenant
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE;

-- Step 6: Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_dependencies_source ON dependencies(source_type, source_id);
CREATE INDEX IF NOT EXISTS idx_dependencies_target ON dependencies(target_type, target_id);
CREATE INDEX IF NOT EXISTS idx_dependencies_tenant ON dependencies(tenant_id);
