import Card, { CardHeader, CardContent } from '@/components/Card'
import FormBuilder from '@/components/FormBuilder'
import { FormConfig } from '@/types/form'

interface ModalFormBuilderProps {
  isOpen: boolean
  onClose: () => void
  title: string
  config: FormConfig
  initialValues?: Record<string, any>
  onSubmit: (data: Record<string, any>) => void
  isLoading?: boolean
}

export default function ModalFormBuilder({
  isOpen,
  onClose,
  title,
  config,
  initialValues,
  onSubmit,
  isLoading = false,
}: ModalFormBuilderProps) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-md max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <h2 className="text-xl font-semibold text-white">{title}</h2>
        </CardHeader>
        <CardContent>
          <FormBuilder
            config={config}
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
