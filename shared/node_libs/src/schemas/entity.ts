import { z } from 'zod';

/**
 * Schema for creating a new entity
 */
export const CreateEntitySchema = z.object({
  organization_id: z.number().int().positive('Organization ID must be a positive integer'),
  entity_type: z.string().min(1, 'Entity type is required').max(255, 'Entity type must be at most 255 characters'),
  name: z.string().min(1, 'Name is required').max(255, 'Name must be at most 255 characters'),
  description: z.string().max(1000, 'Description must be at most 1000 characters').optional(),
});

/**
 * Schema for updating an entity
 */
export const UpdateEntitySchema = CreateEntitySchema.partial();

/**
 * Full entity data transfer object schema
 */
export const EntitySchema = z.object({
  id: z.number().int().positive(),
  village_id: z.string(),
  organization_id: z.number().int().positive(),
  entity_type: z.string(),
  name: z.string(),
  description: z.string().nullable(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

/**
 * Inferred TypeScript types from schemas
 */
export type CreateEntityRequest = z.infer<typeof CreateEntitySchema>;
export type UpdateEntityRequest = z.infer<typeof UpdateEntitySchema>;
export type Entity = z.infer<typeof EntitySchema>;
