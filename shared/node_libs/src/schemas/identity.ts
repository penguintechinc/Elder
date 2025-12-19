import { z } from 'zod';

/**
 * Identity type enumeration
 */
export const IdentityTypeSchema = z.enum([
  'human',
  'service_account',
]);

/**
 * Authentication provider enumeration
 */
export const AuthProviderSchema = z.enum([
  'local',
  'oauth2',
  'saml',
  'mfa',
  'ldap',
]);

/**
 * Portal role enumeration
 */
export const PortalRoleSchema = z.enum([
  'viewer',
  'editor',
  'admin',
  'super_admin',
]);

/**
 * Schema for creating a new identity
 */
export const CreateIdentitySchema = z.object({
  username: z.string()
    .min(3, 'Username must be at least 3 characters')
    .max(255, 'Username must be at most 255 characters')
    .regex(/^[a-zA-Z0-9_-]+$/, 'Username can only contain letters, numbers, underscores, and hyphens'),
  email: z.string()
    .email('Invalid email address')
    .max(255, 'Email must be at most 255 characters'),
  password: z.string()
    .min(12, 'Password must be at least 12 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one digit')
    .regex(/[!@#$%^&*]/, 'Password must contain at least one special character (!@#$%^&*)'),
  identity_type: IdentityTypeSchema.default('human'),
  display_name: z.string()
    .min(1, 'Display name is required')
    .max(255, 'Display name must be at most 255 characters'),
  portal_role: PortalRoleSchema.default('viewer'),
  auth_provider: AuthProviderSchema.default('local'),
  is_active: z.boolean().default(true),
  mfa_enabled: z.boolean().default(false),
  description: z.string()
    .max(1000, 'Description must be at most 1000 characters')
    .optional(),
});

/**
 * Schema for updating an identity
 */
export const UpdateIdentitySchema = CreateIdentitySchema.partial().omit({
  password: true,
}).extend({
  password: z.string()
    .min(12, 'Password must be at least 12 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one digit')
    .regex(/[!@#$%^&*]/, 'Password must contain at least one special character (!@#$%^&*)')
    .optional(),
});

/**
 * Full identity data transfer object schema (excludes password)
 */
export const IdentitySchema = z.object({
  id: z.number().int().positive(),
  village_id: z.string(),
  username: z.string(),
  email: z.string(),
  display_name: z.string(),
  identity_type: IdentityTypeSchema,
  portal_role: PortalRoleSchema,
  auth_provider: AuthProviderSchema,
  is_active: z.boolean(),
  mfa_enabled: z.boolean(),
  description: z.string().nullable(),
  last_login: z.string().datetime().nullable(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

/**
 * Inferred TypeScript types from schemas
 */
export type IdentityType = z.infer<typeof IdentityTypeSchema>;
export type AuthProvider = z.infer<typeof AuthProviderSchema>;
export type PortalRole = z.infer<typeof PortalRoleSchema>;
export type CreateIdentityRequest = z.infer<typeof CreateIdentitySchema>;
export type UpdateIdentityRequest = z.infer<typeof UpdateIdentitySchema>;
export type Identity = z.infer<typeof IdentitySchema>;
