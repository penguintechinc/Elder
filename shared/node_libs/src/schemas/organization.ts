import { z } from 'zod';

/**
 * Organization type enumeration
 */
export const OrganizationTypeSchema = z.enum([
  'department',
  'organization',
  'team',
  'collection',
  'other',
]);

/**
 * Schema for creating a new organization
 */
export const CreateOrganizationSchema = z.object({
  name: z.string().min(1, 'Name is required').max(255, 'Name must be at most 255 characters'),
  description: z.string().max(1000, 'Description must be at most 1000 characters').optional(),
  organization_type: OrganizationTypeSchema.default('organization'),
  parent_id: z.number().int().positive('Parent ID must be a positive integer').optional(),
});

/**
 * Schema for updating an organization
 */
export const UpdateOrganizationSchema = CreateOrganizationSchema.partial();

/**
 * Full organization data transfer object schema
 */
export const OrganizationSchema = z.object({
  id: z.number().int().positive(),
  village_id: z.string(),
  name: z.string(),
  description: z.string().nullable(),
  organization_type: OrganizationTypeSchema,
  parent_id: z.number().int().positive().nullable(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

/**
 * Inferred TypeScript types from schemas
 */
export type OrganizationType = z.infer<typeof OrganizationTypeSchema>;
export type CreateOrganizationRequest = z.infer<typeof CreateOrganizationSchema>;
export type UpdateOrganizationRequest = z.infer<typeof UpdateOrganizationSchema>;
export type Organization = z.infer<typeof OrganizationSchema>;
