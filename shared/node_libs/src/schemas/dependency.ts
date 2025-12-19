import { z } from 'zod';

/**
 * Dependency type enumeration
 */
export const DependencyTypeSchema = z.enum([
  'depends_on',
  'required_by',
  'blocks',
  'blocked_by',
  'related_to',
  'parent_of',
  'child_of',
  'conflicts_with',
  'references',
  'referenced_by',
]);

/**
 * Schema for creating a new dependency
 */
export const CreateDependencySchema = z.object({
  source_id: z.string().min(1, 'Source ID is required'),
  target_id: z.string().min(1, 'Target ID is required'),
  dependency_type: DependencyTypeSchema,
});

/**
 * Schema for updating a dependency
 */
export const UpdateDependencySchema = CreateDependencySchema.partial();

/**
 * Full dependency data transfer object schema
 */
export const DependencySchema = z.object({
  id: z.number().int().positive(),
  source_id: z.string(),
  target_id: z.string(),
  dependency_type: DependencyTypeSchema,
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

/**
 * Inferred TypeScript types from schemas
 */
export type DependencyType = z.infer<typeof DependencyTypeSchema>;
export type CreateDependencyRequest = z.infer<typeof CreateDependencySchema>;
export type UpdateDependencyRequest = z.infer<typeof UpdateDependencySchema>;
export type Dependency = z.infer<typeof DependencySchema>;
