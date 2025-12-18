<script setup lang="ts">
  import { computed } from "vue";
  import type { ButtonVariant, ButtonSize } from "../types";

  interface Props {
    variant?: ButtonVariant;
    size?: ButtonSize;
    disabled?: boolean;
    loading?: boolean;
    type?: "button" | "submit" | "reset";
    fullWidth?: boolean;
    /**
     * Accessible label for screen readers
     */
    ariaLabel?: string;
    /**
     * Test ID for automated testing
     */
    testId?: string;
  }

  const props = withDefaults(defineProps<Props>(), {
    variant: "primary",
    size: "md",
    disabled: false,
    loading: false,
    type: "button",
    fullWidth: false,
    ariaLabel: undefined,
    testId: undefined,
  });

  const computedTestId = computed(() => {
    return props.testId || `lq-button-${props.variant}`;
  });

  const computedAriaLabel = computed(() => {
    if (props.ariaLabel) return props.ariaLabel;
    if (props.loading) return "Loading";
    return undefined;
  });

  const emit = defineEmits<{
    click: [event: MouseEvent];
  }>();

  const buttonClasses = computed(() => {
    const base =
      "inline-flex items-center justify-center rounded-lg font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50";

    const variants = {
      primary: "bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500",
      secondary: "border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 focus:ring-gray-500",
      danger: "bg-red-600 text-white hover:bg-red-700 focus:ring-red-500",
      ghost: "text-gray-700 hover:bg-gray-100 focus:ring-gray-500",
    };

    const sizes = {
      sm: "px-3 py-1.5 text-sm",
      md: "px-4 py-2 text-base",
      lg: "px-6 py-3 text-lg",
    };

    const width = props.fullWidth ? "w-full" : "";

    return [base, variants[props.variant], sizes[props.size], width].join(" ");
  });

  const handleClick = (event: MouseEvent) => {
    if (!props.disabled && !props.loading) {
      emit("click", event);
    }
  };
</script>

<template>
  <button
    :class="buttonClasses"
    :disabled="disabled || loading"
    :type="type"
    :data-testid="computedTestId"
    :aria-label="computedAriaLabel"
    :aria-busy="loading"
    :aria-disabled="disabled || loading"
    @click="handleClick"
  >
    <span
      v-if="loading"
      class="mr-2 inline-block h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"
      role="status"
      aria-label="Loading"
    />
    <slot />
  </button>
</template>
