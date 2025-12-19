import { z } from 'zod';

// Enums
export const IssueStatusSchema = z.enum([
  'open',
  'in_progress',
  'resolved',
  'closed',
  'reopened',
]);

export const IssuePrioritySchema = z.enum([
  'low',
  'medium',
  'high',
  'critical',
]);

export const IssueSeveritySchema = z.enum([
  'info',
  'warning',
  'error',
  'critical',
]);

// Create Schema
export const CreateIssueSchema = z.object({
  title: z.string().min(1).max(255),
  description: z.string().optional(),
  status: IssueStatusSchema.default('open'),
  priority: IssuePrioritySchema.default('medium'),
  severity: IssueSeveritySchema.default('warning'),
  assignedTo: z.string().optional(),
  resourceId: z.string().optional(),
  tags: z.array(z.string()).optional(),
  dueDate: z.string().datetime().optional(),
});

// Update Schema
export const UpdateIssueSchema = CreateIssueSchema.partial();

// DTO Schema
export const IssueSchema = z.object({
  id: z.string(),
  villageId: z.string(),
  title: z.string(),
  description: z.string().nullable(),
  status: IssueStatusSchema,
  priority: IssuePrioritySchema,
  severity: IssueSeveritySchema,
  assignedTo: z.string().nullable(),
  resourceId: z.string().nullable(),
  tags: z.array(z.string()),
  dueDate: z.string().datetime().nullable(),
  createdAt: z.string().datetime(),
  updatedAt: z.string().datetime(),
});

// Inferred Types
export type IssueStatus = z.infer<typeof IssueStatusSchema>;
export type IssuePriority = z.infer<typeof IssuePrioritySchema>;
export type IssueSeverity = z.infer<typeof IssueSeveritySchema>;
export type CreateIssue = z.infer<typeof CreateIssueSchema>;
export type UpdateIssue = z.infer<typeof UpdateIssueSchema>;
export type Issue = z.infer<typeof IssueSchema>;
