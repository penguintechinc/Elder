import React, { useState, useCallback, useMemo } from 'react';

export interface FormField {
  name: string;
  type: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url' | 'textarea' | 'select' | 'checkbox' | 'radio' | 'date' | 'time' | 'datetime-local' | 'file';
  label: string;
  description?: string;
  defaultValue?: string | number | boolean;
  placeholder?: string;
  required?: boolean;
  options?: Array<{ value: string | number; label: string }>;
  min?: number;
  max?: number;
  pattern?: string;
  accept?: string;
  rows?: number;
  validation?: (value: any) => string | null;
  tab?: string;
}

export interface FormTab {
  id: string;
  label: string;
  fields: FormField[];
}

export interface ColorConfig {
  // Background colors
  modalBackground: string;
  headerBackground: string;
  footerBackground: string;
  overlayBackground: string;

  // Text colors
  titleText: string;
  labelText: string;
  descriptionText: string;
  errorText: string;
  buttonText: string;

  // Field colors
  fieldBackground: string;
  fieldBorder: string;
  fieldText: string;
  fieldPlaceholder: string;

  // Focus/Ring colors
  focusRing: string;
  focusBorder: string;

  // Button colors
  primaryButton: string;
  primaryButtonHover: string;
  secondaryButton: string;
  secondaryButtonHover: string;
  secondaryButtonBorder: string;

  // Tab colors
  activeTab: string;
  activeTabBorder: string;
  inactiveTab: string;
  inactiveTabHover: string;
  tabBorder: string;
  errorTabText: string;
  errorTabBorder: string;
}

export interface FormModalBuilderProps {
  title: string;
  fields: FormField[];
  tabs?: FormTab[];
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: Record<string, any>) => Promise<void> | void;
  submitButtonText?: string;
  cancelButtonText?: string;
  width?: 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  backgroundColor?: string;
  maxHeight?: string;
  zIndex?: number;
  autoTabThreshold?: number;
  fieldsPerTab?: number;
  colors?: ColorConfig;
}

// Default dark mode theme with navy background and gold accents
const DEFAULT_COLORS: ColorConfig = {
  // Background colors - Navy dark mode
  modalBackground: 'bg-slate-800',
  headerBackground: 'bg-slate-800',
  footerBackground: 'bg-slate-900',
  overlayBackground: 'bg-gray-900 bg-opacity-75',

  // Text colors - Gold and white
  titleText: 'text-amber-400',
  labelText: 'text-amber-300',
  descriptionText: 'text-slate-400',
  errorText: 'text-red-400',
  buttonText: 'text-slate-900',

  // Field colors - White backgrounds for contrast
  fieldBackground: 'bg-white',
  fieldBorder: 'border-slate-600',
  fieldText: 'text-slate-900',
  fieldPlaceholder: 'placeholder-slate-500',

  // Focus/Ring colors - Gold accents
  focusRing: 'focus:ring-amber-500',
  focusBorder: 'focus:border-amber-500',

  // Button colors - Gold primary
  primaryButton: 'bg-amber-500',
  primaryButtonHover: 'hover:bg-amber-600',
  secondaryButton: 'bg-slate-700',
  secondaryButtonHover: 'hover:bg-slate-600',
  secondaryButtonBorder: 'border-slate-600',

  // Tab colors - Gold active, slate inactive
  activeTab: 'text-amber-400',
  activeTabBorder: 'border-amber-500',
  inactiveTab: 'text-slate-400',
  inactiveTabHover: 'hover:text-slate-300 hover:border-slate-500',
  tabBorder: 'border-slate-700',
  errorTabText: 'text-red-400',
  errorTabBorder: 'border-red-500',
};

export const FormModalBuilder: React.FC<FormModalBuilderProps> = ({
  title,
  fields,
  tabs: manualTabs,
  isOpen,
  onClose,
  onSubmit,
  submitButtonText = 'Submit',
  cancelButtonText = 'Cancel',
  width = 'md',
  maxHeight = 'max-h-[80vh]',
  zIndex = 9999,
  autoTabThreshold = 8,
  fieldsPerTab = 6,
  colors,
}) => {
  const theme = colors || DEFAULT_COLORS;
  const [formData, setFormData] = useState<Record<string, any>>(() => {
    const initial: Record<string, any> = {};
    fields.forEach((field) => {
      initial[field.name] = field.defaultValue ?? (field.type === 'checkbox' ? false : '');
    });
    return initial;
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [activeTab, setActiveTab] = useState(0);

  const widthClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    '2xl': 'max-w-2xl',
  };

  // Auto-generate tabs if field count exceeds threshold
  const tabs = useMemo(() => {
    if (manualTabs && manualTabs.length > 0) {
      return manualTabs;
    }

    // Check if fields have tab assignments
    const hasTabAssignments = fields.some((f) => f.tab);
    if (hasTabAssignments) {
      const tabMap = new Map<string, FormField[]>();
      fields.forEach((field) => {
        const tabName = field.tab || 'General';
        if (!tabMap.has(tabName)) {
          tabMap.set(tabName, []);
        }
        tabMap.get(tabName)!.push(field);
      });

      return Array.from(tabMap.entries()).map(([label, tabFields], index) => ({
        id: `tab-${index}`,
        label,
        fields: tabFields,
      }));
    }

    // Auto-generate tabs if field count exceeds threshold
    if (fields.length > autoTabThreshold) {
      const generatedTabs: FormTab[] = [];
      const numTabs = Math.ceil(fields.length / fieldsPerTab);

      for (let i = 0; i < numTabs; i++) {
        const start = i * fieldsPerTab;
        const end = Math.min(start + fieldsPerTab, fields.length);
        generatedTabs.push({
          id: `tab-${i}`,
          label: i === 0 ? 'General' : `Step ${i + 1}`,
          fields: fields.slice(start, end),
        });
      }

      return generatedTabs;
    }

    // No tabs needed
    return null;
  }, [fields, manualTabs, autoTabThreshold, fieldsPerTab]);

  const currentFields = tabs ? tabs[activeTab]?.fields || [] : fields;

  const primaryButtonClasses = `w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 ${theme.primaryButton} text-base font-medium ${theme.buttonText} ${theme.primaryButtonHover} focus:outline-none focus:ring-2 focus:ring-offset-2 ${theme.focusRing} sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed`;

  const secondaryButtonClasses = `mt-3 w-full inline-flex justify-center rounded-md border ${theme.secondaryButtonBorder} shadow-sm px-4 py-2 ${theme.secondaryButton} text-base font-medium ${theme.labelText} ${theme.secondaryButtonHover} focus:outline-none focus:ring-2 focus:ring-offset-2 ${theme.focusRing} sm:mt-0 sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed`;

  const handleChange = useCallback((name: string, value: any) => {
    setFormData((prev) => ({ ...prev, [name]: value }));
    setErrors((prev) => ({ ...prev, [name]: '' }));
  }, []);

  const validate = useCallback((): boolean => {
    const newErrors: Record<string, string> = {};

    fields.forEach((field) => {
      const value = formData[field.name];

      if (field.required && !value && value !== 0) {
        newErrors[field.name] = `${field.label} is required`;
      }

      if (field.validation && value) {
        const error = field.validation(value);
        if (error) {
          newErrors[field.name] = error;
        }
      }

      if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
          newErrors[field.name] = 'Invalid email address';
        }
      }

      if (field.type === 'url' && value) {
        try {
          new URL(value);
        } catch {
          newErrors[field.name] = 'Invalid URL';
        }
      }

      if (field.type === 'number' && value !== '') {
        const numValue = Number(value);
        if (field.min !== undefined && numValue < field.min) {
          newErrors[field.name] = `Minimum value is ${field.min}`;
        }
        if (field.max !== undefined && numValue > field.max) {
          newErrors[field.name] = `Maximum value is ${field.max}`;
        }
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [fields, formData]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      // Find first tab with errors
      if (tabs) {
        for (let i = 0; i < tabs.length; i++) {
          const tabHasError = tabs[i].fields.some((field) => errors[field.name]);
          if (tabHasError) {
            setActiveTab(i);
            break;
          }
        }
      }
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(formData);
      onClose();
    } catch (error) {
      console.error('Form submission error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleNext = () => {
    if (tabs && activeTab < tabs.length - 1) {
      setActiveTab(activeTab + 1);
    }
  };

  const handlePrevious = () => {
    if (activeTab > 0) {
      setActiveTab(activeTab - 1);
    }
  };

  const renderField = (field: FormField) => {
    const commonClasses = `mt-1 block w-full rounded-md shadow-sm sm:text-sm ${theme.fieldBackground} ${theme.fieldBorder} ${theme.fieldText} ${theme.fieldPlaceholder} ${theme.focusBorder} ${theme.focusRing}`;
    const errorClasses = errors[field.name] ? `border-red-500 ${theme.errorText}` : '';

    switch (field.type) {
      case 'textarea':
        return (
          <textarea
            id={field.name}
            name={field.name}
            rows={field.rows || 3}
            value={formData[field.name] || ''}
            onChange={(e) => handleChange(field.name, e.target.value)}
            placeholder={field.placeholder}
            required={field.required}
            className={`${commonClasses} ${errorClasses}`}
          />
        );

      case 'select':
        return (
          <select
            id={field.name}
            name={field.name}
            value={formData[field.name] || ''}
            onChange={(e) => handleChange(field.name, e.target.value)}
            required={field.required}
            className={`${commonClasses} ${errorClasses}`}
          >
            <option value="">Select...</option>
            {field.options?.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        );

      case 'checkbox':
        return (
          <div className="flex items-center">
            <input
              id={field.name}
              name={field.name}
              type="checkbox"
              checked={formData[field.name] || false}
              onChange={(e) => handleChange(field.name, e.target.checked)}
              className={`h-4 w-4 rounded ${theme.fieldBorder} ${theme.focusRing} text-amber-500`}
            />
            <label htmlFor={field.name} className={`ml-2 block text-sm ${theme.labelText}`}>
              {field.label}
            </label>
          </div>
        );

      case 'radio':
        return (
          <div className="space-y-2">
            {field.options?.map((option) => (
              <div key={option.value} className="flex items-center">
                <input
                  id={`${field.name}-${option.value}`}
                  name={field.name}
                  type="radio"
                  value={option.value}
                  checked={formData[field.name] === option.value}
                  onChange={(e) => handleChange(field.name, e.target.value)}
                  className={`h-4 w-4 ${theme.fieldBorder} ${theme.focusRing} text-amber-500`}
                />
                <label htmlFor={`${field.name}-${option.value}`} className={`ml-2 block text-sm ${theme.labelText}`}>
                  {option.label}
                </label>
              </div>
            ))}
          </div>
        );

      default:
        return (
          <input
            id={field.name}
            name={field.name}
            type={field.type}
            value={formData[field.name] || ''}
            onChange={(e) => handleChange(field.name, e.target.value)}
            placeholder={field.placeholder}
            required={field.required}
            min={field.min}
            max={field.max}
            pattern={field.pattern}
            accept={field.accept}
            className={`${commonClasses} ${errorClasses}`}
          />
        );
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 overflow-y-auto" style={{ zIndex }} aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        <div className={`fixed inset-0 ${theme.overlayBackground} transition-opacity`} aria-hidden="true" onClick={onClose}></div>

        <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">
          &#8203;
        </span>

        <div className={`inline-block align-bottom ${theme.modalBackground} rounded-lg text-left shadow-xl transform transition-all sm:my-8 sm:align-middle ${widthClasses[width]} sm:w-full ${maxHeight} flex flex-col`}>
          {/* Fixed header */}
          <div className={`px-4 pt-5 pb-4 sm:p-6 sm:pb-4 border-b ${theme.tabBorder} ${theme.headerBackground}`}>
            <h3 className={`text-lg leading-6 font-medium ${theme.titleText}`} id="modal-title">
              {title}
            </h3>

            {/* Tab navigation */}
            {tabs && tabs.length > 1 && (
              <div className={`mt-4 border-b ${theme.tabBorder}`}>
                <nav className="-mb-px flex space-x-4 overflow-x-auto" aria-label="Tabs">
                  {tabs.map((tab, index) => {
                    const tabHasError = tab.fields.some((field) => errors[field.name]);
                    return (
                      <button
                        key={tab.id}
                        type="button"
                        onClick={() => setActiveTab(index)}
                        className={`
                          whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center gap-1
                          ${
                            activeTab === index
                              ? `${theme.activeTabBorder} ${theme.activeTab}`
                              : tabHasError
                              ? `${theme.errorTabBorder} ${theme.errorTabText} hover:border-red-400`
                              : `border-transparent ${theme.inactiveTab} ${theme.inactiveTabHover}`
                          }
                        `}
                      >
                        {tab.label}
                        {tabHasError && (
                          <span className={`inline-flex items-center justify-center w-4 h-4 text-xs font-bold ${theme.buttonText} bg-red-500 rounded-full`}>
                            !
                          </span>
                        )}
                      </button>
                    );
                  })}
                </nav>
              </div>
            )}
          </div>

          {/* Scrollable form content */}
          <div className="flex-1 overflow-y-auto px-4 py-4 sm:px-6">
            <form onSubmit={handleSubmit} className="space-y-4">
              {currentFields.map((field) => (
                <div key={field.name}>
                  {field.type !== 'checkbox' && (
                    <label htmlFor={field.name} className={`block text-sm font-medium ${theme.labelText}`}>
                      {field.label}
                      {field.required && <span className={`${theme.errorText} ml-1`}>*</span>}
                    </label>
                  )}
                  {field.description && <p className={`text-xs ${theme.descriptionText} mt-1`}>{field.description}</p>}
                  {renderField(field)}
                  {errors[field.name] && <p className={`mt-1 text-sm ${theme.errorText}`}>{errors[field.name]}</p>}
                </div>
              ))}
            </form>
          </div>

          {/* Fixed footer with buttons */}
          <div className={`px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse gap-3 border-t ${theme.tabBorder} ${theme.footerBackground}`}>
            {tabs && tabs.length > 1 ? (
              <>
                {activeTab === tabs.length - 1 ? (
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    onClick={handleSubmit}
                    className={primaryButtonClasses}
                  >
                    {isSubmitting ? 'Submitting...' : submitButtonText}
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={handleNext}
                    className={primaryButtonClasses}
                  >
                    Next
                  </button>
                )}
                {activeTab > 0 && (
                  <button
                    type="button"
                    onClick={handlePrevious}
                    className={secondaryButtonClasses}
                  >
                    Previous
                  </button>
                )}
                <button
                  type="button"
                  onClick={onClose}
                  disabled={isSubmitting}
                  className={secondaryButtonClasses}
                >
                  {cancelButtonText}
                </button>
              </>
            ) : (
              <>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  onClick={handleSubmit}
                  className={primaryButtonClasses}
                >
                  {isSubmitting ? 'Submitting...' : submitButtonText}
                </button>
                <button
                  type="button"
                  onClick={onClose}
                  disabled={isSubmitting}
                  className={secondaryButtonClasses}
                >
                  {cancelButtonText}
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
