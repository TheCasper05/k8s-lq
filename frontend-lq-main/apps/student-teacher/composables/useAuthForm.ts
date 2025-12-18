import { watch, type Ref } from "vue";
import { useField, useForm } from "vee-validate";
import { toTypedSchema } from "@vee-validate/zod";
import type { ZodSchema } from "zod";

export interface AuthFormField {
  /**
   * Field name for vee-validate
   */
  name: string;
  /**
   * Reactive value reference
   */
  value: Ref<unknown>;
  /**
   * Error message from validation
   */
  error: Ref<string | undefined>;
  /**
   * Manual validation trigger
   */
  validate: () => void;
}

export interface UseAuthFormOptions {
  /**
   * Zod schema for validation
   */
  schema: ZodSchema;
  /**
   * Field definitions
   */
  fields: Record<string, Ref<unknown>>;
}

/**
 * Composable for handling auth form validation with vee-validate
 * Automatically sets up form, fields, bidirectional watchers, and validation
 *
 * @example
 * ```ts
 * const email = ref("");
 * const password = ref("");
 *
 * const schema = z.object({
 *   email: z.string().email(),
 *   password: z.string().min(8),
 * });
 *
 * const { handleSubmit, fields } = useAuthForm({
 *   schema,
 *   fields: { email, password },
 * });
 *
 * const onSubmit = handleSubmit(async () => {
 *   // Form is valid, proceed with submission
 * });
 * ```
 */
export const useAuthForm = (options: UseAuthFormOptions) => {
  const { t } = useI18n();

  // Create typed schema
  const validationSchema = computed(() => toTypedSchema(options.schema));

  // Setup vee-validate form
  const { handleSubmit: veeHandleSubmit, resetForm } = useForm({
    validationSchema,
  });

  // Setup fields with vee-validate
  const authFields: Record<string, AuthFormField> = {};

  Object.entries(options.fields).forEach(([fieldName, fieldRef]) => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const { value: veeValue, errorMessage } = useField<any>(fieldName);

    // Bidirectional sync: ref -> vee-validate
    watch(fieldRef, (val) => {
      // Only update if values are different to prevent infinite loop
      if (veeValue.value !== val) {
        veeValue.value = val;
      }
    });

    // Bidirectional sync: vee-validate -> ref
    watch(veeValue, (val) => {
      const normalizedVal = val ?? (typeof fieldRef.value === "string" ? "" : null);
      // Only update if values are different to prevent infinite loop
      if (fieldRef.value !== normalizedVal) {
        fieldRef.value = normalizedVal;
      }
    });

    // Create field object
    authFields[fieldName] = {
      name: fieldName,
      value: fieldRef,
      error: errorMessage,
      validate: () => {
        veeValue.value = fieldRef.value;
      },
    };
  });

  /**
   * Handle form submission with validation
   */
  const handleSubmit = (onValid: () => void | Promise<void>) => {
    return veeHandleSubmit(async () => {
      await onValid();
    });
  };

  /**
   * Reset form to initial state
   */
  const reset = () => {
    resetForm();
    Object.values(options.fields).forEach((fieldRef) => {
      fieldRef.value = typeof fieldRef.value === "string" ? "" : null;
    });
  };

  /**
   * Check if form has any errors
   */
  const hasErrors = computed(() => {
    return Object.values(authFields).some((field) => !!field.error.value);
  });

  /**
   * Check if all required fields are filled
   */
  const isComplete = computed(() => {
    return Object.values(options.fields).every((fieldRef) => {
      const value = fieldRef.value;
      if (typeof value === "string") {
        return value.trim().length > 0;
      }
      return value !== null && value !== undefined;
    });
  });

  return {
    /**
     * Form submission handler
     */
    handleSubmit,

    /**
     * Field objects with validation
     */
    fields: authFields,

    /**
     * Reset form
     */
    reset,

    /**
     * Whether form has validation errors
     */
    hasErrors,

    /**
     * Whether all required fields are filled
     */
    isComplete,

    /**
     * Translation function
     */
    t,
  };
};
