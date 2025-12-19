import { describe, it, expect } from 'vitest';
import { PaginationParamsSchema, ErrorResponseSchema } from '../common';

describe('PaginationParamsSchema', () => {
  it('should parse valid pagination params with defaults', () => {
    const result = PaginationParamsSchema.parse({});
    expect(result).toEqual({
      page: 1,
      per_page: 50,
      sort_by: undefined,
      sort_order: undefined,
    });
  });

  it('should parse valid pagination params with custom values', () => {
    const result = PaginationParamsSchema.parse({
      page: 2,
      per_page: 100,
      sort_by: 'name',
      sort_order: 'asc',
    });
    expect(result).toEqual({
      page: 2,
      per_page: 100,
      sort_by: 'name',
      sort_order: 'asc',
    });
  });

  it('should coerce string page to number', () => {
    const result = PaginationParamsSchema.parse({ page: '3' });
    expect(result.page).toBe(3);
    expect(typeof result.page).toBe('number');
  });

  it('should coerce string per_page to number', () => {
    const result = PaginationParamsSchema.parse({ per_page: '25' });
    expect(result.per_page).toBe(25);
    expect(typeof result.per_page).toBe('number');
  });

  it('should reject non-positive page values', () => {
    expect(() => PaginationParamsSchema.parse({ page: 0 })).toThrow();
    expect(() => PaginationParamsSchema.parse({ page: -1 })).toThrow();
  });

  it('should reject non-integer page values', () => {
    expect(() => PaginationParamsSchema.parse({ page: 1.5 })).toThrow();
  });

  it('should reject per_page less than 1', () => {
    expect(() => PaginationParamsSchema.parse({ per_page: 0 })).toThrow();
    expect(() => PaginationParamsSchema.parse({ per_page: -10 })).toThrow();
  });

  it('should reject per_page greater than 1000', () => {
    expect(() => PaginationParamsSchema.parse({ per_page: 1001 })).toThrow();
  });

  it('should reject non-integer per_page values', () => {
    expect(() => PaginationParamsSchema.parse({ per_page: 50.5 })).toThrow();
  });

  it('should reject invalid sort_order values', () => {
    expect(() => PaginationParamsSchema.parse({ sort_order: 'invalid' })).toThrow();
  });

  it('should accept asc and desc for sort_order', () => {
    const ascResult = PaginationParamsSchema.parse({ sort_order: 'asc' });
    expect(ascResult.sort_order).toBe('asc');

    const descResult = PaginationParamsSchema.parse({ sort_order: 'desc' });
    expect(descResult.sort_order).toBe('desc');
  });

  it('should allow page at boundary values', () => {
    const result = PaginationParamsSchema.parse({ page: 1 });
    expect(result.page).toBe(1);
  });

  it('should allow per_page at min boundary', () => {
    const result = PaginationParamsSchema.parse({ per_page: 1 });
    expect(result.per_page).toBe(1);
  });

  it('should allow per_page at max boundary', () => {
    const result = PaginationParamsSchema.parse({ per_page: 1000 });
    expect(result.per_page).toBe(1000);
  });
});

describe('ErrorResponseSchema', () => {
  it('should parse valid error response with required fields', () => {
    const result = ErrorResponseSchema.parse({
      error: 'NOT_FOUND',
      message: 'Resource not found',
    });
    expect(result).toEqual({
      error: 'NOT_FOUND',
      message: 'Resource not found',
      details: undefined,
    });
  });

  it('should parse error response with details', () => {
    const detailsObj = { field: 'email', code: 'INVALID_FORMAT' };
    const result = ErrorResponseSchema.parse({
      error: 'VALIDATION_ERROR',
      message: 'Validation failed',
      details: detailsObj,
    });
    expect(result).toEqual({
      error: 'VALIDATION_ERROR',
      message: 'Validation failed',
      details: detailsObj,
    });
  });

  it('should allow arbitrary keys in details object', () => {
    const details = {
      field1: 'value1',
      nested: { key: 'value' },
      count: 42,
      flag: true,
    };
    const result = ErrorResponseSchema.parse({
      error: 'COMPLEX_ERROR',
      message: 'Error with complex details',
      details,
    });
    expect(result.details).toEqual(details);
  });

  it('should reject missing error field', () => {
    expect(() => ErrorResponseSchema.parse({
      message: 'Resource not found',
    })).toThrow();
  });

  it('should reject missing message field', () => {
    expect(() => ErrorResponseSchema.parse({
      error: 'NOT_FOUND',
    })).toThrow();
  });

  it('should reject non-string error field', () => {
    expect(() => ErrorResponseSchema.parse({
      error: 123,
      message: 'Error message',
    })).toThrow();
  });

  it('should reject non-string message field', () => {
    expect(() => ErrorResponseSchema.parse({
      error: 'ERROR_CODE',
      message: 456,
    })).toThrow();
  });

  it('should allow empty strings for error and message', () => {
    const result = ErrorResponseSchema.parse({
      error: '',
      message: '',
    });
    expect(result.error).toBe('');
    expect(result.message).toBe('');
  });

  it('should ignore extra fields', () => {
    const result = ErrorResponseSchema.parse({
      error: 'ERROR',
      message: 'Message',
      extraField: 'should be ignored',
      timestamp: 12345,
    });
    expect(result).toEqual({
      error: 'ERROR',
      message: 'Message',
      details: undefined,
    });
  });

  it('should handle details with nested objects', () => {
    const details = {
      validation: {
        fields: ['email', 'password'],
        reasons: {
          email: 'invalid format',
          password: 'too short',
        },
      },
    };
    const result = ErrorResponseSchema.parse({
      error: 'VALIDATION_ERROR',
      message: 'Multiple validation errors',
      details,
    });
    expect(result.details).toEqual(details);
  });

  it('should handle details with mixed types', () => {
    const details = {
      string: 'value',
      number: 42,
      boolean: true,
      null: null,
      array: [1, 'two', true],
      object: { nested: 'value' },
    };
    const result = ErrorResponseSchema.parse({
      error: 'MIXED_ERROR',
      message: 'Error with mixed types',
      details,
    });
    expect(result.details).toEqual(details);
  });
});
