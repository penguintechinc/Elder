import { describe, it, expect } from 'vitest';
import {
  CreateOrganizationSchema,
  OrganizationTypeSchema,
} from '../organization';

describe('CreateOrganizationSchema', () => {
  describe('valid inputs', () => {
    it('should validate minimal required fields', () => {
      const data = { name: 'Acme Corp' };
      const result = CreateOrganizationSchema.safeParse(data);
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.name).toBe('Acme Corp');
        expect(result.data.organization_type).toBe('organization');
      }
    });

    it('should validate with all optional fields', () => {
      const data = {
        name: 'Engineering Dept',
        description: 'Main engineering department',
        organization_type: 'department' as const,
        parent_id: 42,
      };
      const result = CreateOrganizationSchema.safeParse(data);
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.name).toBe('Engineering Dept');
        expect(result.data.description).toBe('Main engineering department');
        expect(result.data.organization_type).toBe('department');
        expect(result.data.parent_id).toBe(42);
      }
    });

    it('should apply default organization_type when not provided', () => {
      const data = { name: 'Test Org' };
      const result = CreateOrganizationSchema.safeParse(data);
      expect(result.success).toBe(true);
      if (result.success) {
        expect(result.data.organization_type).toBe('organization');
      }
    });

    it('should accept all valid organization types', () => {
      const types = ['department', 'organization', 'team', 'collection', 'other'];
      types.forEach((type) => {
        const data = { name: 'Test', organization_type: type };
        const result = CreateOrganizationSchema.safeParse(data);
        expect(result.success).toBe(true);
      });
    });

    it('should allow empty description string', () => {
      const data = { name: 'Org', description: '' };
      const result = CreateOrganizationSchema.safeParse(data);
      expect(result.success).toBe(true);
    });

    it('should allow description at max length (1000 chars)', () => {
      const desc = 'a'.repeat(1000);
      const data = { name: 'Org', description: desc };
      const result = CreateOrganizationSchema.safeParse(data);
      expect(result.success).toBe(true);
    });

    it('should allow name at max length (255 chars)', () => {
      const name = 'a'.repeat(255);
      const data = { name };
      const result = CreateOrganizationSchema.safeParse(data);
      expect(result.success).toBe(true);
    });
  });

  describe('invalid inputs', () => {
    it('should reject missing name', () => {
      const data = { description: 'No name' };
      const result = CreateOrganizationSchema.safeParse(data);
      expect(result.success).toBe(false);
    });

    it('should reject empty name', () => {
      const data = { name: '' };
      const result = CreateOrganizationSchema.safeParse(data);
      expect(result.success).toBe(false);
    });

    it('should reject name exceeding 255 characters', () => {
      const name = 'a'.repeat(256);
      const data = { name };
      const result = CreateOrganizationSchema.safeParse(data);
      expect(result.success).toBe(false);
    });

    it('should reject description exceeding 1000 characters', () => {
      const desc = 'a'.repeat(1001);
      const data = { name: 'Org', description: desc };
      const result = CreateOrganizationSchema.safeParse(data);
      expect(result.success).toBe(false);
    });

    it('should reject invalid organization_type', () => {
      const data = {
        name: 'Org',
        organization_type: 'invalid_type',
      };
      const result = CreateOrganizationSchema.safeParse(data);
      expect(result.success).toBe(false);
    });

    it('should reject non-integer parent_id', () => {
      const data = { name: 'Org', parent_id: 3.14 };
      const result = CreateOrganizationSchema.safeParse(data);
      expect(result.success).toBe(false);
    });

    it('should reject non-positive parent_id', () => {
      const data = { name: 'Org', parent_id: 0 };
      const result = CreateOrganizationSchema.safeParse(data);
      expect(result.success).toBe(false);
    });

    it('should reject negative parent_id', () => {
      const data = { name: 'Org', parent_id: -1 };
      const result = CreateOrganizationSchema.safeParse(data);
      expect(result.success).toBe(false);
    });

    it('should reject non-string name', () => {
      const data = { name: 123 };
      const result = CreateOrganizationSchema.safeParse(data);
      expect(result.success).toBe(false);
    });

    it('should reject non-string description', () => {
      const data = { name: 'Org', description: 123 };
      const result = CreateOrganizationSchema.safeParse(data);
      expect(result.success).toBe(false);
    });
  });

  describe('type validation', () => {
    it('should infer correct TypeScript type', () => {
      const data = {
        name: 'Valid Org',
        description: 'Optional description',
        organization_type: 'team' as const,
        parent_id: 1,
      };
      const result = CreateOrganizationSchema.parse(data);
      expect(typeof result.name).toBe('string');
      expect(typeof result.description).toBe('string');
      expect(['department', 'organization', 'team', 'collection', 'other']).toContain(
        result.organization_type
      );
      expect(typeof result.parent_id).toBe('number');
    });
  });

  describe('edge cases', () => {
    it('should handle whitespace-only name as valid string', () => {
      const data = { name: '   ' };
      const result = CreateOrganizationSchema.safeParse(data);
      expect(result.success).toBe(true);
    });

    it('should handle special characters in name', () => {
      const data = { name: "O'Reilly & Associates, Inc." };
      const result = CreateOrganizationSchema.safeParse(data);
      expect(result.success).toBe(true);
    });

    it('should handle unicode characters in description', () => {
      const data = { name: 'Org', description: 'Здравствуй мир 世界 مرحبا' };
      const result = CreateOrganizationSchema.safeParse(data);
      expect(result.success).toBe(true);
    });

    it('should handle null parent_id explicitly', () => {
      const data = { name: 'Org', parent_id: null };
      const result = CreateOrganizationSchema.safeParse(data);
      // parent_id is optional, null is not explicitly allowed but omitting it is
      expect(result.success).toBe(false);
    });
  });
});

describe('OrganizationTypeSchema', () => {
  it('should validate all allowed types', () => {
    const types = ['department', 'organization', 'team', 'collection', 'other'];
    types.forEach((type) => {
      const result = OrganizationTypeSchema.safeParse(type);
      expect(result.success).toBe(true);
    });
  });

  it('should reject unknown types', () => {
    const result = OrganizationTypeSchema.safeParse('unknown_type');
    expect(result.success).toBe(false);
  });

  it('should be case-sensitive', () => {
    const result = OrganizationTypeSchema.safeParse('Department');
    expect(result.success).toBe(false);
  });
});
