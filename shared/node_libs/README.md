# @penguin/node_libs - Node.js/TypeScript Shared Library

See [docs/shared-libraries/node-libs.md](../../docs/shared-libraries/node-libs.md) for complete documentation.

## Zod Schemas

Zod provides TypeScript-first schema validation with static type inference and runtime validation.

### Basic Schema Definition

```typescript
import { z } from 'zod';

const userSchema = z.object({
  id: z.number().int().positive(),
  name: z.string().min(2).max(100),
  email: z.string().email(),
  age: z.number().int().min(0).max(150),
});

type User = z.infer<typeof userSchema>;

const validUser = userSchema.parse({
  id: 1,
  name: 'John Doe',
  email: 'john@example.com',
  age: 30,
});
```

### Nested Schemas

```typescript
import { z } from 'zod';

const addressSchema = z.object({
  street: z.string(),
  city: z.string(),
  zipCode: z.string().length(5),
});

const personSchema = z.object({
  name: z.string(),
  addresses: z.array(addressSchema),
});

type Person = z.infer<typeof personSchema>;

const person = personSchema.parse({
  name: 'Jane',
  addresses: [
    { street: '123 Main St', city: 'NYC', zipCode: '10001' },
    { street: '456 Oak Ave', city: 'LA', zipCode: '90001' },
  ],
});
```

### Custom Validation

```typescript
import { z } from 'zod';

const productSchema = z.object({
  name: z.string(),
  price: z.number().positive(),
  stock: z.number().int().nonnegative(),
  sku: z.string().regex(/^[A-Z0-9-]+$/),
}).refine(
  (data) => data.price * data.stock > 0,
  { message: "Inventory value must be positive" }
);

const product = productSchema.parse({
  name: 'Widget',
  price: 9.99,
  stock: 100,
  sku: 'WID-001',
});
```

### Conditional Validation

```typescript
import { z } from 'zod';

const accountSchema = z.discriminatedUnion('type', [
  z.object({
    type: z.literal('personal'),
    ssn: z.string().regex(/^\d{3}-\d{2}-\d{4}$/),
  }),
  z.object({
    type: z.literal('business'),
    taxId: z.string().regex(/^\d{2}-\d{7}$/),
    companyName: z.string(),
  }),
]);

type Account = z.infer<typeof accountSchema>;

const businessAccount = accountSchema.parse({
  type: 'business',
  taxId: '12-3456789',
  companyName: 'Acme Corp',
});
```

### Safe Parsing with Error Handling

```typescript
import { z } from 'zod';

const schema = z.object({
  email: z.string().email(),
  age: z.number().int().min(0),
});

const result = schema.safeParse({
  email: 'invalid-email',
  age: -5,
});

if (!result.success) {
  console.error('Validation errors:', result.error.errors);
} else {
  console.log('Valid data:', result.data);
}
```
