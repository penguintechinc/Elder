# FormBuilder System

The FormBuilder system provides standardized form rendering with automatic input sanitization based on field types. This ensures consistent space handling and data processing across all forms in Elder.

## Overview

- **Automatic space handling** - Fields are processed based on their type (strip all spaces, trim, etc.)
- **Declarative field definitions** - Define forms as configuration objects
- **Conditional visibility** - Show/hide fields based on other field values
- **Consistent styling** - All forms use the same UI components

## Core Components

### Types (`@/types/form`)

```typescript
import { FormField, FormConfig, FieldType } from '@/types/form'
```

### FormBuilder (`@/components/FormBuilder`)

Renders a form based on field definitions with automatic processing.

```typescript
import FormBuilder from '@/components/FormBuilder'
```

### ModalFormBuilder (`@/components/ModalFormBuilder`)

Wraps FormBuilder in a modal dialog.

```typescript
import ModalFormBuilder from '@/components/ModalFormBuilder'
```

## Field Types

| Type | Space Handling | Use Case |
|------|----------------|----------|
| `text` | Trim only | Names, titles |
| `email` | Strip ALL spaces | Email addresses |
| `username` | Strip ALL spaces | Usernames, identifiers |
| `password` | Trim only | Passwords (hidden) |
| `password_generate` | Trim only | Passwords with generator button (visible) |
| `url` | Strip ALL spaces | URLs |
| `domain` | Strip ALL spaces | Domain names |
| `ip` | Strip ALL spaces | IP addresses |
| `path` | Strip ALL spaces | File/URL paths |
| `slug` | Strip ALL spaces | URL slugs |
| `color` | Strip ALL spaces | Hex colors |
| `textarea` | Trim | Long text descriptions |
| `multiline` | Split by newline, strip each | Lists (one per line) |
| `number` | Strip spaces, parse | Numeric values |
| `select` | No processing | Dropdown selection |
| `checkbox` | No processing | Boolean toggle |
| `date` | No processing | Date picker |

## FormField Interface

```typescript
interface FormField {
  name: string           // Field name (used in form data)
  label: string          // Display label
  type: FieldType        // Field type (determines space handling)
  required?: boolean     // Required field
  placeholder?: string   // Input placeholder
  options?: SelectOption[] // For select fields
  rows?: number          // For textarea/multiline
  defaultValue?: any     // Default value
  hidden?: boolean       // Always hidden
  disabled?: boolean     // Disabled input
  helpText?: string      // Help text below field
  triggerField?: string  // Show when this field is truthy
  showWhen?: (values: Record<string, any>) => boolean // Complex condition
}

interface SelectOption {
  value: string | number
  label: string
}
```

## Basic Usage

### Simple Modal Form

```typescript
import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import ModalFormBuilder from '@/components/ModalFormBuilder'
import { FormConfig } from '@/types/form'
import api from '@/lib/api'

const createProjectConfig: FormConfig = {
  fields: [
    { name: 'name', label: 'Project Name', type: 'text', required: true },
    { name: 'description', label: 'Description', type: 'textarea', rows: 3 },
    { name: 'status', label: 'Status', type: 'select', required: true, options: [
      { value: 'active', label: 'Active' },
      { value: 'archived', label: 'Archived' },
    ]},
  ],
  submitLabel: 'Create Project',
}

function ProjectsPage() {
  const [showModal, setShowModal] = useState(false)

  const mutation = useMutation({
    mutationFn: (data) => api.createProject(data),
    onSuccess: () => setShowModal(false),
  })

  return (
    <>
      <button onClick={() => setShowModal(true)}>Create Project</button>

      <ModalFormBuilder
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title="Create Project"
        config={createProjectConfig}
        onSubmit={(data) => mutation.mutate(data)}
        isLoading={mutation.isPending}
      />
    </>
  )
}
```

### Inline Form

```typescript
import FormBuilder from '@/components/FormBuilder'
import { FormConfig } from '@/types/form'

const settingsConfig: FormConfig = {
  fields: [
    { name: 'email', label: 'Email', type: 'email', required: true },
    { name: 'full_name', label: 'Full Name', type: 'text', required: true },
  ],
  submitLabel: 'Save Settings',
}

function SettingsForm({ user }) {
  return (
    <FormBuilder
      config={settingsConfig}
      initialValues={{ email: user.email, full_name: user.full_name }}
      onSubmit={(data) => updateUser(data)}
      onCancel={() => navigate(-1)}
    />
  )
}
```

## Conditional Fields

### Simple Trigger (Boolean)

Use `triggerField` for fields that should show when another field is truthy:

```typescript
const config: FormConfig = {
  fields: [
    { name: 'is_portal_user', label: 'Create as Portal User', type: 'checkbox' },
    {
      name: 'portal_role',
      label: 'Portal Role',
      type: 'select',
      triggerField: 'is_portal_user',  // Only shows when checkbox is checked
      options: [
        { value: 'viewer', label: 'Viewer' },
        { value: 'editor', label: 'Editor' },
        { value: 'admin', label: 'Admin' },
      ]
    },
  ]
}
```

### Complex Conditions

Use `showWhen` for conditions based on specific values:

```typescript
const config: FormConfig = {
  fields: [
    {
      name: 'auth_provider',
      label: 'Auth Provider',
      type: 'select',
      options: [
        { value: 'local', label: 'Local' },
        { value: 'ldap', label: 'LDAP' },
        { value: 'saml', label: 'SAML' },
      ]
    },
    {
      name: 'password',
      label: 'Password',
      type: 'password',
      showWhen: (values) => values.auth_provider === 'local'
    },
    {
      name: 'ldap_server',
      label: 'LDAP Server',
      type: 'url',
      showWhen: (values) => values.auth_provider === 'ldap'
    },
  ]
}
```

## Edit Forms with Initial Values

```typescript
const editServiceConfig: FormConfig = {
  fields: [
    { name: 'name', label: 'Name', type: 'text', required: true },
    { name: 'port', label: 'Port', type: 'number' },
    { name: 'paths', label: 'Paths (one per line)', type: 'multiline', rows: 4 },
  ],
  submitLabel: 'Update Service',
}

// In component:
<ModalFormBuilder
  isOpen={showEdit}
  onClose={() => setShowEdit(false)}
  title="Edit Service"
  config={editServiceConfig}
  initialValues={{
    name: service.name,
    port: service.port,
    paths: service.paths?.join('\n'),  // Convert array to multiline string
  }}
  onSubmit={(data) => updateMutation.mutate(data)}
  isLoading={updateMutation.isPending}
/>
```

## Manual Processing (for Custom Forms)

If you need to process values manually without using FormBuilder:

```typescript
import { processFieldValue, processFormData } from '@/types/form'

// Process single value
const email = processFieldValue(rawEmail, 'email')  // Strips all spaces

// Process all form values
const fields = [
  { name: 'email', type: 'email' },
  { name: 'name', type: 'text' },
]
const processed = processFormData(rawValues, fields)
```

## Best Practices

1. **Always use appropriate field types** - This ensures correct space handling
2. **Use `triggerField` for simple boolean conditions** - Cleaner than `showWhen`
3. **Provide `helpText` for non-obvious fields** - Especially for multiline fields
4. **Set sensible `defaultValue`** - Especially for select and checkbox fields
5. **Convert arrays to multiline strings** for edit forms using `paths.join('\n')`

## Migration Guide

To convert an existing form to FormBuilder:

1. Identify all form fields and their types
2. Map manual space handling to appropriate FieldType
3. Create FormConfig with field definitions
4. Replace form JSX with FormBuilder/ModalFormBuilder
5. Move mutation logic to onSubmit handler

### Before (Manual)

```typescript
const [name, setName] = useState('')
const [email, setEmail] = useState('')

const handleSubmit = (e) => {
  e.preventDefault()
  mutation.mutate({
    name: name.trim(),
    email: email.replace(/\s+/g, ''),
  })
}

return (
  <form onSubmit={handleSubmit}>
    <Input value={name} onChange={(e) => setName(e.target.value)} />
    <Input value={email} onChange={(e) => setEmail(e.target.value)} />
    <button>Submit</button>
  </form>
)
```

### After (FormBuilder)

```typescript
const config: FormConfig = {
  fields: [
    { name: 'name', label: 'Name', type: 'text', required: true },
    { name: 'email', label: 'Email', type: 'email', required: true },
  ],
  submitLabel: 'Submit',
}

return (
  <FormBuilder
    config={config}
    onSubmit={(data) => mutation.mutate(data)}
    isLoading={mutation.isPending}
  />
)
```
