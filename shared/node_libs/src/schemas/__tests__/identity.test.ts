import { describe, it, expect } from 'vitest';
import {
  IdentityTypeSchema,
  AuthProviderSchema,
  PortalRoleSchema,
  CreateIdentitySchema,
  UpdateIdentitySchema,
  IdentitySchema,
  type IdentityType,
  type AuthProvider,
  type PortalRole,
  type CreateIdentityRequest,
  type UpdateIdentityRequest,
  type Identity,
} from '../identity';

describe('Identity Schemas', () => {
  describe('IdentityTypeSchema', () => {
    it('should accept valid identity types', () => {
      expect(IdentityTypeSchema.parse('human')).toBe('human');
      expect(IdentityTypeSchema.parse('service_account')).toBe('service_account');
    });

    it('should reject invalid identity types', () => {
      expect(() => IdentityTypeSchema.parse('invalid')).toThrow();
      expect(() => IdentityTypeSchema.parse('user')).toThrow();
      expect(() => IdentityTypeSchema.parse('admin')).toThrow();
    });
  });

  describe('AuthProviderSchema', () => {
    it('should accept valid auth providers', () => {
      expect(AuthProviderSchema.parse('local')).toBe('local');
      expect(AuthProviderSchema.parse('oauth2')).toBe('oauth2');
      expect(AuthProviderSchema.parse('saml')).toBe('saml');
      expect(AuthProviderSchema.parse('mfa')).toBe('mfa');
      expect(AuthProviderSchema.parse('ldap')).toBe('ldap');
    });

    it('should reject invalid auth providers', () => {
      expect(() => AuthProviderSchema.parse('github')).toThrow();
      expect(() => AuthProviderSchema.parse('jwt')).toThrow();
      expect(() => AuthProviderSchema.parse('')).toThrow();
    });
  });

  describe('PortalRoleSchema', () => {
    it('should accept valid portal roles', () => {
      expect(PortalRoleSchema.parse('viewer')).toBe('viewer');
      expect(PortalRoleSchema.parse('editor')).toBe('editor');
      expect(PortalRoleSchema.parse('admin')).toBe('admin');
      expect(PortalRoleSchema.parse('super_admin')).toBe('super_admin');
    });

    it('should reject invalid portal roles', () => {
      expect(() => PortalRoleSchema.parse('superadmin')).toThrow();
      expect(() => PortalRoleSchema.parse('moderator')).toThrow();
      expect(() => PortalRoleSchema.parse('user')).toThrow();
    });
  });

  describe('CreateIdentitySchema', () => {
    const validData = {
      username: 'john_doe',
      email: 'john@example.com',
      password: 'SecurePass123!',
      display_name: 'John Doe',
    };

    it('should accept valid identity creation data', () => {
      const result = CreateIdentitySchema.parse(validData);
      expect(result.username).toBe('john_doe');
      expect(result.email).toBe('john@example.com');
      expect(result.password).toBe('SecurePass123!');
      expect(result.display_name).toBe('John Doe');
      expect(result.identity_type).toBe('human');
      expect(result.portal_role).toBe('viewer');
      expect(result.auth_provider).toBe('local');
      expect(result.is_active).toBe(true);
      expect(result.mfa_enabled).toBe(false);
    });

    it('should apply default values', () => {
      const result = CreateIdentitySchema.parse(validData);
      expect(result.identity_type).toBe('human');
      expect(result.portal_role).toBe('viewer');
      expect(result.auth_provider).toBe('local');
      expect(result.is_active).toBe(true);
      expect(result.mfa_enabled).toBe(false);
    });

    it('should accept optional description', () => {
      const data = {
        ...validData,
        description: 'Senior Engineer',
      };
      const result = CreateIdentitySchema.parse(data);
      expect(result.description).toBe('Senior Engineer');
    });

    it('should reject username shorter than 3 characters', () => {
      expect(() => CreateIdentitySchema.parse({
        ...validData,
        username: 'ab',
      })).toThrow('Username must be at least 3 characters');
    });

    it('should reject username longer than 255 characters', () => {
      expect(() => CreateIdentitySchema.parse({
        ...validData,
        username: 'a'.repeat(256),
      })).toThrow('Username must be at most 255 characters');
    });

    it('should reject username with invalid characters', () => {
      expect(() => CreateIdentitySchema.parse({
        ...validData,
        username: 'john@doe',
      })).toThrow('Username can only contain letters, numbers, underscores, and hyphens');

      expect(() => CreateIdentitySchema.parse({
        ...validData,
        username: 'john doe',
      })).toThrow('Username can only contain letters, numbers, underscores, and hyphens');
    });

    it('should accept valid usernames', () => {
      expect(CreateIdentitySchema.parse({
        ...validData,
        username: 'user_name-123',
      }).username).toBe('user_name-123');

      expect(CreateIdentitySchema.parse({
        ...validData,
        username: 'User123',
      }).username).toBe('User123');
    });

    it('should reject invalid email addresses', () => {
      expect(() => CreateIdentitySchema.parse({
        ...validData,
        email: 'invalid-email',
      })).toThrow('Invalid email address');

      expect(() => CreateIdentitySchema.parse({
        ...validData,
        email: 'test@',
      })).toThrow('Invalid email address');
    });

    it('should reject email longer than 255 characters', () => {
      expect(() => CreateIdentitySchema.parse({
        ...validData,
        email: `${'a'.repeat(250)}@example.com`,
      })).toThrow('Email must be at most 255 characters');
    });

    it('should reject password shorter than 12 characters', () => {
      expect(() => CreateIdentitySchema.parse({
        ...validData,
        password: 'Short123!',
      })).toThrow('Password must be at least 12 characters');
    });

    it('should reject password without uppercase letter', () => {
      expect(() => CreateIdentitySchema.parse({
        ...validData,
        password: 'lowercase123!',
      })).toThrow('Password must contain at least one uppercase letter');
    });

    it('should reject password without lowercase letter', () => {
      expect(() => CreateIdentitySchema.parse({
        ...validData,
        password: 'UPPERCASE123!',
      })).toThrow('Password must contain at least one lowercase letter');
    });

    it('should reject password without digit', () => {
      expect(() => CreateIdentitySchema.parse({
        ...validData,
        password: 'NoDigitsHere!',
      })).toThrow('Password must contain at least one digit');
    });

    it('should reject password without special character', () => {
      expect(() => CreateIdentitySchema.parse({
        ...validData,
        password: 'NoSpecial123',
      })).toThrow('Password must contain at least one special character (!@#$%^&*)');
    });

    it('should accept valid passwords', () => {
      const validPasswords = [
        'SecurePass123!',
        'MyPass@2024Xyz',
        'Strong#Pass99abc',
        'Complex$Password123',
      ];

      validPasswords.forEach((pwd) => {
        expect(CreateIdentitySchema.parse({
          ...validData,
          password: pwd,
        }).password).toBe(pwd);
      });
    });

    it('should reject empty display name', () => {
      expect(() => CreateIdentitySchema.parse({
        ...validData,
        display_name: '',
      })).toThrow('Display name is required');
    });

    it('should reject display name longer than 255 characters', () => {
      expect(() => CreateIdentitySchema.parse({
        ...validData,
        display_name: 'a'.repeat(256),
      })).toThrow('Display name must be at most 255 characters');
    });

    it('should reject description longer than 1000 characters', () => {
      expect(() => CreateIdentitySchema.parse({
        ...validData,
        description: 'a'.repeat(1001),
      })).toThrow('Description must be at most 1000 characters');
    });

    it('should accept custom enum values', () => {
      const data = {
        ...validData,
        identity_type: 'service_account' as const,
        portal_role: 'admin' as const,
        auth_provider: 'oauth2' as const,
      };
      const result = CreateIdentitySchema.parse(data);
      expect(result.identity_type).toBe('service_account');
      expect(result.portal_role).toBe('admin');
      expect(result.auth_provider).toBe('oauth2');
    });

    it('should accept is_active and mfa_enabled booleans', () => {
      const data = {
        ...validData,
        is_active: false,
        mfa_enabled: true,
      };
      const result = CreateIdentitySchema.parse(data);
      expect(result.is_active).toBe(false);
      expect(result.mfa_enabled).toBe(true);
    });

    it('should reject missing required fields', () => {
      expect(() => CreateIdentitySchema.parse({
        username: 'john_doe',
      })).toThrow();

      expect(() => CreateIdentitySchema.parse({
        email: 'john@example.com',
        password: 'SecurePass123!',
      })).toThrow();

      expect(() => CreateIdentitySchema.parse({
        username: 'john_doe',
        email: 'john@example.com',
        password: 'SecurePass123!',
      })).toThrow();
    });
  });

  describe('UpdateIdentitySchema', () => {
    const partialData = {
      email: 'newemail@example.com',
      display_name: 'Jane Doe',
    };

    it('should accept partial updates', () => {
      const result = UpdateIdentitySchema.parse(partialData);
      expect(result.email).toBe('newemail@example.com');
      expect(result.display_name).toBe('Jane Doe');
      expect(result.username).toBeUndefined();
    });

    it('should allow optional password update', () => {
      const data = {
        ...partialData,
        password: 'NewSecurePass123!',
      };
      const result = UpdateIdentitySchema.parse(data);
      expect(result.password).toBe('NewSecurePass123!');
    });

    it('should enforce password strength rules when provided', () => {
      expect(() => UpdateIdentitySchema.parse({
        password: 'weak',
      })).toThrow('Password must be at least 12 characters');
    });

    it('should allow updates without password', () => {
      const result = UpdateIdentitySchema.parse(partialData);
      expect(result.password).toBeUndefined();
    });

    it('should validate provided fields', () => {
      expect(() => UpdateIdentitySchema.parse({
        email: 'invalid-email',
      })).toThrow('Invalid email address');
    });

    it('should allow all optional fields to be undefined', () => {
      const result = UpdateIdentitySchema.parse({});
      expect(Object.keys(result).length).toBe(0);
    });
  });

  describe('IdentitySchema', () => {
    const validIdentity = {
      id: 1,
      village_id: 'a1b2-c3d4-e5f67890',
      username: 'john_doe',
      email: 'john@example.com',
      display_name: 'John Doe',
      identity_type: 'human' as const,
      portal_role: 'viewer' as const,
      auth_provider: 'local' as const,
      is_active: true,
      mfa_enabled: false,
      description: null,
      last_login: null,
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
    };

    it('should accept valid identity data', () => {
      const result = IdentitySchema.parse(validIdentity);
      expect(result.id).toBe(1);
      expect(result.username).toBe('john_doe');
      expect(result.email).toBe('john@example.com');
    });

    it('should accept nullable description and last_login', () => {
      const result = IdentitySchema.parse(validIdentity);
      expect(result.description).toBeNull();
      expect(result.last_login).toBeNull();
    });

    it('should validate datetime fields', () => {
      const result = IdentitySchema.parse({
        ...validIdentity,
        last_login: '2024-01-15T12:30:00Z',
      });
      expect(result.last_login).toBe('2024-01-15T12:30:00Z');
    });

    it('should reject invalid datetime format', () => {
      expect(() => IdentitySchema.parse({
        ...validIdentity,
        created_at: 'not-a-date',
      })).toThrow();
    });

    it('should reject non-positive id', () => {
      expect(() => IdentitySchema.parse({
        ...validIdentity,
        id: 0,
      })).toThrow();

      expect(() => IdentitySchema.parse({
        ...validIdentity,
        id: -1,
      })).toThrow();
    });

    it('should reject missing required fields', () => {
      expect(() => IdentitySchema.parse({
        id: 1,
        username: 'john_doe',
      })).toThrow();
    });

    it('should validate enum fields', () => {
      expect(() => IdentitySchema.parse({
        ...validIdentity,
        identity_type: 'invalid',
      })).toThrow();

      expect(() => IdentitySchema.parse({
        ...validIdentity,
        auth_provider: 'unknown',
      })).toThrow();
    });
  });

  describe('Type Inference', () => {
    it('should correctly infer IdentityType', () => {
      const type: IdentityType = 'human';
      expect(type).toBe('human');
    });

    it('should correctly infer AuthProvider', () => {
      const provider: AuthProvider = 'oauth2';
      expect(provider).toBe('oauth2');
    });

    it('should correctly infer PortalRole', () => {
      const role: PortalRole = 'admin';
      expect(role).toBe('admin');
    });

    it('should correctly infer CreateIdentityRequest', () => {
      const request: CreateIdentityRequest = {
        username: 'test_user',
        email: 'test@example.com',
        password: 'SecurePass123!',
        display_name: 'Test User',
      };
      expect(request.username).toBe('test_user');
    });

    it('should correctly infer UpdateIdentityRequest', () => {
      const request: UpdateIdentityRequest = {
        email: 'new@example.com',
      };
      expect(request.email).toBe('new@example.com');
    });

    it('should correctly infer Identity', () => {
      const identity: Identity = {
        id: 1,
        village_id: 'a1b2-c3d4-e5f67890',
        username: 'john_doe',
        email: 'john@example.com',
        display_name: 'John Doe',
        identity_type: 'human',
        portal_role: 'viewer',
        auth_provider: 'local',
        is_active: true,
        mfa_enabled: false,
        description: null,
        last_login: null,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      };
      expect(identity.id).toBe(1);
    });
  });

  describe('Integration Tests', () => {
    it('should validate a complete user registration flow', () => {
      const createRequest: CreateIdentityRequest = {
        username: 'new_user',
        email: 'newuser@example.com',
        password: 'StrongPass123!',
        display_name: 'New User',
      };

      const parsed = CreateIdentitySchema.parse(createRequest);
      expect(parsed).toMatchObject({
        username: 'new_user',
        email: 'newuser@example.com',
        identity_type: 'human',
        portal_role: 'viewer',
      });
    });

    it('should validate a user update flow', () => {
      const updateRequest: UpdateIdentityRequest = {
        display_name: 'Updated Name',
        mfa_enabled: true,
      };

      const parsed = UpdateIdentitySchema.parse(updateRequest);
      expect(parsed.display_name).toBe('Updated Name');
      expect(parsed.mfa_enabled).toBe(true);
    });

    it('should validate service account creation', () => {
      const serviceAccount = CreateIdentitySchema.parse({
        username: 'api_service',
        email: 'api@example.com',
        password: 'SecureServicePass123!',
        display_name: 'API Service Account',
        identity_type: 'service_account',
        auth_provider: 'oauth2',
      });

      expect(serviceAccount.identity_type).toBe('service_account');
      expect(serviceAccount.auth_provider).toBe('oauth2');
    });
  });
});
