import { useEffect } from 'react'
import Card, { CardHeader, CardContent } from '@/components/Card'
import FormBuilder from '@/components/FormBuilder'
import { FormConfig } from '@/types/form'

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
  // Prevent body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
      return () => {
        document.body.style.overflow = ''
      }
    }
  }, [isOpen])

  if (!isOpen) return null

  // Merge submitLabel into config if provided as prop
  const finalConfig = submitLabel ? { ...config, submitLabel } : config

  // Handle backdrop click
  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose()
    }
  }

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      onClick={handleBackdropClick}
    >
      <Card className="w-full max-w-md max-h-[90vh] flex flex-col">
        <CardHeader className="flex-shrink-0">
          <h2 className="text-xl font-semibold text-white">{title}</h2>
        </CardHeader>
        <CardContent className="flex-1 overflow-y-auto overflow-x-hidden">
          <FormBuilder
            config={finalConfig}
            initialValues={initialValues}
            onSubmit={onSubmit}
            onCancel={onClose}
            isLoading={isLoading}
          />
        </CardContent>
      </Card>
    </div>
  )
}
