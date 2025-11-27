/**
 * Confirmation action utilities for consistent user confirmation patterns.
 *
 * Provides hooks and utilities for confirming destructive actions
 * like deletions, with consistent UX across the application.
 */

/**
 * Hook for confirming delete actions
 *
 * @returns Function to confirm and execute delete
 *
 * @example
 * const confirmDelete = useConfirmDelete();
 * confirmDelete('Server1', () => deleteMutation.mutate(id));
 */
export const useConfirmDelete = () => {
  return (resourceName: string, onConfirm: () => void) => {
    if (window.confirm(`Are you sure you want to delete "${resourceName}"?`)) {
      onConfirm();
    }
  };
};

/**
 * Hook for confirming generic actions
 *
 * @returns Function to confirm and execute action
 *
 * @example
 * const confirmAction = useConfirmAction();
 * confirmAction('archive this project', () => archiveMutation.mutate(id));
 */
export const useConfirmAction = () => {
  return (actionDescription: string, onConfirm: () => void) => {
    if (window.confirm(`Are you sure you want to ${actionDescription}?`)) {
      onConfirm();
    }
  };
};

/**
 * Direct confirmation for delete actions
 *
 * @param resourceName Name of resource to delete
 * @param onConfirm Callback to execute if confirmed
 *
 * @example
 * confirmDelete('Server1', () => deleteMutation.mutate(id));
 */
export const confirmDelete = (resourceName: string, onConfirm: () => void) => {
  if (window.confirm(`Are you sure you want to delete "${resourceName}"?`)) {
    onConfirm();
  }
};

/**
 * Direct confirmation for generic actions
 *
 * @param actionDescription Description of action to confirm
 * @param onConfirm Callback to execute if confirmed
 *
 * @example
 * confirmAction('archive this project', () => archiveMutation.mutate(id));
 */
export const confirmAction = (actionDescription: string, onConfirm: () => void) => {
  if (window.confirm(`Are you sure you want to ${actionDescription}?`)) {
    onConfirm();
  }
};
