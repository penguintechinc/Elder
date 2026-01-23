import { FormModalBuilder, FormField as SharedFormField } from '@/lib/shared/FormModalBuilder'
import { FormConfig, FormField } from '@/types/form'

export interface ModalFormBuilderProps {
  isOpen?: boolean
  onClose: () => void
  title: string
  config: FormConfig
  initialValues?: Record<string, any>
  onSubmit: (data: Record<string, any>) => void
  isLoading?: boolean
  submitLabel?: string
}

// Convert our FormField type to the shared library's FormField type
function convertField(field: FormField): SharedFormField {
  // Map our types to shared library types
  const typeMap: Record<string, SharedFormField['type']> = {
    text: 'text',
    email: 'email',
    password: 'password',
    number: 'number',
    tel: 'tel',
    url: 'url',
    textarea: 'textarea',
    multiline: 'textarea',
    select: 'select',
    checkbox: 'checkbox',
    date: 'date',
    time: 'time',
    password_generate: 'password',
    username: 'text',
    domain: 'text',
    ip: 'text',
    path: 'text',
    slug: 'text',
    color: 'text',
  }

  return {
    name: field.name,
    type: typeMap[field.type] || 'text',
    label: field.label,
    description: field.helpText,
    defaultValue: field.defaultValue,
    placeholder: field.placeholder,
    required: field.required,
    options: field.options,
    rows: field.rows,
    tab: field.tab,
  }
}

export default function ModalFormBuilder({
  isOpen = true,
  onClose,
  title,
  config,
  initialValues,
  onSubmit,
  isLoading = false,
  submitLabel,
}: ModalFormBuilderProps) {
  // Convert fields to shared library format
  const sharedFields = config.fields
    .filter(f => !f.hidden)
    .map(convertField)

  // Set initial values including defaults
  const combinedInitialValues = { ...initialValues }
  config.fields.forEach(field => {
    if (field.defaultValue !== undefined && combinedInitialValues[field.name] === undefined) {
      combinedInitialValues[field.name] = field.defaultValue
    }
  })

  const handleSubmit = async (data: Record<string, any>) => {
    onSubmit(data)
  }

  return (
    <FormModalBuilder
      title={title}
      fields={sharedFields}
      isOpen={isOpen}
      onClose={onClose}
      onSubmit={handleSubmit}
      submitButtonText={submitLabel || config.submitLabel || 'Submit'}
      cancelButtonText={config.cancelLabel || 'Cancel'}
      width="md"
      autoTabThreshold={8}
      fieldsPerTab={6}
    />
  )
}

// Re-export types for convenience
export type { FormField, FormConfig } from '@/types/form'
