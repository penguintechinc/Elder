import { z } from 'zod';

export const PaginationParamsSchema = z.object({
  page: z.coerce
    .number()
    .int('Page must be an integer')
    .positive('Page must be positive')
    .default(1),
  per_page: z.coerce
    .number()
    .int('Per page must be an integer')
    .min(1, 'Per page must be at least 1')
    .max(1000, 'Per page must not exceed 1000')
    .default(50),
  sort_by: z.string().optional(),
  sort_order: z.enum(['asc', 'desc']).optional(),
});

export const PaginatedResponseSchema = <T extends z.ZodTypeAny>(
  itemSchema: T
) => {
  return z.object({
    items: z.array(itemSchema),
    total: z.number().int().nonnegative('Total must be non-negative'),
    page: z.number().int().positive('Page must be positive'),
    per_page: z.number().int().positive('Per page must be positive'),
    pages: z.number().int().nonnegative('Pages must be non-negative'),
  });
};

export const ErrorResponseSchema = z.object({
  error: z.string('Error code is required'),
  message: z.string('Error message is required'),
  details: z.record(z.unknown()).optional(),
});

export const BulkOperationResultSchema = z.object({
  succeeded: z.array(z.object({
    id: z.string(),
    data: z.unknown(),
  })),
  failed: z.array(z.object({
    id: z.string().optional(),
    error: z.string(),
    message: z.string(),
  })),
  errors: z.array(z.string()).optional(),
});

export type PaginationParams = z.infer<typeof PaginationParamsSchema>;
export type ErrorResponse = z.infer<typeof ErrorResponseSchema>;
export type BulkOperationResult = z.infer<typeof BulkOperationResultSchema>;
export type PaginatedResponse<T> = z.infer<ReturnType<typeof PaginatedResponseSchema<z.ZodType<T>>>>;
