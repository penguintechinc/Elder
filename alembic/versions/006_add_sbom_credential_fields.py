"""Add credential fields to sbom_scans and sbom_scan_schedules tables.

Revision ID: 006
Revises: 005
Create Date: 2025-12-17

This migration adds support for private repository authentication in SBOM scanning.
Uses the same credential pattern as discovery_jobs (builtin_secrets reference).
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    """Add credential fields for private repo authentication."""
    # Add credential fields to sbom_scans table
    op.add_column('sbom_scans', sa.Column('credential_type', sa.String(50), nullable=True))
    op.add_column('sbom_scans', sa.Column('credential_id', sa.Integer(), nullable=True))
    op.add_column('sbom_scans', sa.Column('credential_mapping', sa.JSON(), nullable=True))

    # Add credential fields to sbom_scan_schedules table
    op.add_column('sbom_scan_schedules', sa.Column('credential_type', sa.String(50), nullable=True))
    op.add_column('sbom_scan_schedules', sa.Column('credential_id', sa.Integer(), nullable=True))
    op.add_column('sbom_scan_schedules', sa.Column('credential_mapping', sa.JSON(), nullable=True))


def downgrade():
    """Remove credential fields."""
    # Remove from sbom_scan_schedules
    op.drop_column('sbom_scan_schedules', 'credential_mapping')
    op.drop_column('sbom_scan_schedules', 'credential_id')
    op.drop_column('sbom_scan_schedules', 'credential_type')

    # Remove from sbom_scans
    op.drop_column('sbom_scans', 'credential_mapping')
    op.drop_column('sbom_scans', 'credential_id')
    op.drop_column('sbom_scans', 'credential_type')
