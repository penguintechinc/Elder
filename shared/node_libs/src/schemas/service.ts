import { z } from 'zod';

export const CreateServiceSchema = z.object({
  name: z.string().min(1, 'Service name is required').max(255),
  service_type: z.string().min(1, 'Service type is required').max(100),
  url: z.string().url('Invalid URL format').optional(),
  port: z.number().int().min(1).max(65535).optional(),
  organization_id: z.string().min(1, 'Organization ID is required'),
});

export const UpdateServiceSchema = CreateServiceSchema.partial();

export const ServiceSchema = CreateServiceSchema.extend({
  id: z.string(),
  village_id: z.string(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
});

export type CreateService = z.infer<typeof CreateServiceSchema>;
export type UpdateService = z.infer<typeof UpdateServiceSchema>;
export type Service = z.infer<typeof ServiceSchema>;
