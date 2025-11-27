-- Migration: Add certificates table for SSL/TLS certificate tracking
-- Version: 006
-- Description: Comprehensive certificate management with creator, type, dates, and metadata

-- ============================================
-- Certificates Table
-- ============================================

CREATE TABLE IF NOT EXISTS certificates (
    id SERIAL PRIMARY KEY,

    -- Multi-tenancy
    tenant_id INTEGER NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,

    -- Basic information
    name VARCHAR(255) NOT NULL,
    description TEXT,
    organization_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,

    -- Certificate details
    creator VARCHAR(100) NOT NULL,  -- digicert, letsencrypt, self_signed, sectigo, globalsign, godaddy, entrust, etc.
    cert_type VARCHAR(50) NOT NULL,  -- ca_root, ca_intermediate, server_cert, client_cert, code_signing, wildcard, san, ecc, rsa

    -- Subject information (from certificate)
    common_name VARCHAR(255),  -- CN (e.g., *.example.com, www.example.com)
    subject_alternative_names TEXT[],  -- SAN entries (array of domain names)
    organization_unit VARCHAR(255),  -- OU
    locality VARCHAR(100),  -- L (city)
    state_province VARCHAR(100),  -- ST (state)
    country VARCHAR(2),  -- C (ISO 3166-1 alpha-2 code)

    -- Issuer information
    issuer_common_name VARCHAR(255),  -- Issuer CN
    issuer_organization VARCHAR(255),  -- Issuer O

    -- Key information
    key_algorithm VARCHAR(50),  -- RSA, ECDSA, DSA, Ed25519
    key_size INTEGER,  -- 2048, 4096, 256, 384, 521 (bits)
    signature_algorithm VARCHAR(100),  -- SHA256withRSA, SHA384withRSA, ECDSAwithSHA256, etc.

    -- Dates
    issue_date DATE NOT NULL,
    expiration_date DATE NOT NULL,
    not_before TIMESTAMP,  -- Full timestamp from cert
    not_after TIMESTAMP,  -- Full timestamp from cert

    -- Certificate content (optional, for storage)
    certificate_pem TEXT,  -- PEM-encoded certificate
    certificate_fingerprint_sha1 VARCHAR(64),  -- SHA-1 fingerprint (legacy compatibility)
    certificate_fingerprint_sha256 VARCHAR(64),  -- SHA-256 fingerprint
    serial_number VARCHAR(255),  -- Certificate serial number (hex)

    -- Key storage reference (if separate from cert)
    private_key_secret_id INTEGER REFERENCES builtin_secrets(id) ON DELETE SET NULL,  -- Reference to secrets table

    -- Usage tracking
    entities_using JSONB,  -- Array of {entity_id, entity_name, usage_type} for servers/services using this cert
    services_using INTEGER[],  -- Array of service IDs using this certificate

    -- File/location tracking
    file_path VARCHAR(1024),  -- Path to certificate file if stored on filesystem
    vault_path VARCHAR(512),  -- Path in secrets vault (HashiCorp Vault, etc.)

    -- Renewal information
    auto_renew BOOLEAN DEFAULT FALSE NOT NULL,
    renewal_days_before INTEGER DEFAULT 30,  -- Days before expiration to trigger renewal
    last_renewed_at TIMESTAMP,
    renewal_method VARCHAR(50),  -- acme_http, acme_dns, manual, api

    -- ACME/Let's Encrypt specific
    acme_account_url VARCHAR(512),
    acme_order_url VARCHAR(512),
    acme_challenge_type VARCHAR(50),  -- http-01, dns-01, tls-alpn-01

    -- Revocation information
    is_revoked BOOLEAN DEFAULT FALSE NOT NULL,
    revoked_at TIMESTAMP,
    revocation_reason VARCHAR(100),  -- keyCompromise, caCompromise, affiliationChanged, superseded, cessationOfOperation, certificateHold, removeFromCRL, privilegeWithdrawn, aaCompromise

    -- Validation and compliance
    validation_type VARCHAR(50),  -- DV (Domain Validation), OV (Organization Validation), EV (Extended Validation)
    ct_log_status VARCHAR(50),  -- Certificate Transparency status: logged, pending, not_required
    ocsp_must_staple BOOLEAN DEFAULT FALSE,

    -- Cost tracking
    cost_annual DECIMAL(10,2),  -- Annual cost
    purchase_date DATE,
    vendor VARCHAR(255),  -- Vendor/reseller

    -- Metadata and tags
    notes TEXT,
    tags VARCHAR(100)[],
    custom_metadata JSONB,  -- Additional custom fields

    -- Status
    status VARCHAR(50) DEFAULT 'active' NOT NULL,  -- active, expiring_soon, expired, revoked, pending, archived
    is_active BOOLEAN DEFAULT TRUE NOT NULL,

    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_by_id INTEGER REFERENCES identities(id) ON DELETE SET NULL,
    updated_by_id INTEGER REFERENCES identities(id) ON DELETE SET NULL,

    -- Village ID for universal referencing
    village_id VARCHAR(32) UNIQUE,

    -- Constraints
    CONSTRAINT valid_dates CHECK (expiration_date >= issue_date),
    CONSTRAINT valid_key_size CHECK (key_size > 0 OR key_size IS NULL),
    CONSTRAINT valid_renewal_days CHECK (renewal_days_before >= 0 OR renewal_days_before IS NULL),
    CONSTRAINT valid_country_code CHECK (country IS NULL OR LENGTH(country) = 2)
);

-- Indexes for performance
CREATE INDEX idx_certificates_tenant_id ON certificates(tenant_id);
CREATE INDEX idx_certificates_organization_id ON certificates(organization_id);
CREATE INDEX idx_certificates_creator ON certificates(creator);
CREATE INDEX idx_certificates_cert_type ON certificates(cert_type);
CREATE INDEX idx_certificates_common_name ON certificates(common_name);
CREATE INDEX idx_certificates_expiration_date ON certificates(expiration_date);
CREATE INDEX idx_certificates_status ON certificates(status);
CREATE INDEX idx_certificates_is_active ON certificates(is_active);
CREATE INDEX idx_certificates_village_id ON certificates(village_id);
CREATE INDEX idx_certificates_fingerprint_sha256 ON certificates(certificate_fingerprint_sha256);
CREATE INDEX idx_certificates_serial_number ON certificates(serial_number);

-- Index for expiring certificates (for renewal automation)
CREATE INDEX idx_certificates_expiring ON certificates(expiration_date) WHERE is_active = TRUE AND is_revoked = FALSE;

-- GIN index for JSONB fields
CREATE INDEX idx_certificates_entities_using ON certificates USING gin(entities_using);
CREATE INDEX idx_certificates_custom_metadata ON certificates USING gin(custom_metadata);

-- GIN index for array fields
CREATE INDEX idx_certificates_san ON certificates USING gin(subject_alternative_names);
CREATE INDEX idx_certificates_tags ON certificates USING gin(tags);

-- Comments for documentation
COMMENT ON TABLE certificates IS 'SSL/TLS certificate tracking and management';
COMMENT ON COLUMN certificates.creator IS 'Certificate authority or issuer (digicert, letsencrypt, self_signed, etc.)';
COMMENT ON COLUMN certificates.cert_type IS 'Type of certificate (ca_root, ca_intermediate, server_cert, client_cert, wildcard, san, etc.)';
COMMENT ON COLUMN certificates.subject_alternative_names IS 'Array of SAN entries from the certificate';
COMMENT ON COLUMN certificates.validation_type IS 'DV (Domain Validation), OV (Organization Validation), or EV (Extended Validation)';
COMMENT ON COLUMN certificates.ct_log_status IS 'Certificate Transparency log status';
COMMENT ON COLUMN certificates.entities_using IS 'JSONB array of entities using this certificate';
COMMENT ON COLUMN certificates.auto_renew IS 'Enable automatic renewal before expiration';
COMMENT ON COLUMN certificates.renewal_days_before IS 'Days before expiration to trigger renewal (default 30)';
COMMENT ON COLUMN certificates.acme_challenge_type IS 'ACME challenge type for Let''s Encrypt/ACME protocol';
