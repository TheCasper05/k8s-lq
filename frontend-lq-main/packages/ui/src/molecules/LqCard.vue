<script setup lang="ts">
  import { computed } from "vue";

  interface Props {
    /**
     * Variant of the card
     * - default: Standard card with optional header
     * - boxed: Compact card for metrics/KPIs
     * - horizontal: Horizontal layout with icon
     */
    variant?: "default" | "boxed" | "horizontal";
    /**
     * Custom padding class (overrides default padding)
     */
    padding?: string;
    /**
     * Custom border radius class (default: rounded-xl)
     */
    rounded?: string;
    /**
     * Enable hover shadow effect
     */
    hoverable?: boolean;
    /**
     * Test ID for automated testing
     */
    testId?: string;
    /**
     * ARIA label for the card
     */
    ariaLabel?: string;
  }

  const props = withDefaults(defineProps<Props>(), {
    variant: "default",
    padding: "",
    rounded: "rounded-2xl",
    hoverable: false,
    testId: undefined,
    ariaLabel: undefined,
  });

  const computedTestId = computed(() => {
    return props.testId || `lq-card-${props.variant}`;
  });

  const cardClasses = computed(() => {
    const base =
      "bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 shadow-sm flex flex-col";

    const paddingClasses = {
      default: "", // Padding handled by slots
      boxed: "p-4 sm:p-6",
      horizontal: "p-4 sm:p-6",
    };

    const hoverClass = props.hoverable ? "transition-all duration-300 hover:shadow-lg" : "";
    const roundedClass = props.rounded || "rounded-xl"; // Default to rounded-xl for all variants
    const paddingClass = props.padding || paddingClasses[props.variant];

    return [base, roundedClass, paddingClass, hoverClass].filter(Boolean).join(" ");
  });

  const headerClasses = computed(() => {
    if (props.variant === "default") {
      return "p-4 sm:p-6 pb-3 sm:pb-4 border-b border-surface-200 dark:border-surface-700";
    }
    return "";
  });

  const contentClasses = computed(() => {
    if (props.variant === "default") {
      return "p-1 flex flex-col gap-2";
    }
    return "flex flex-col gap-2";
  });
</script>

<template>
  <div :class="cardClasses" :data-testid="computedTestId" :aria-label="ariaLabel" role="region">
    <!-- Header slot (only for default variant) -->
    <div v-if="$slots.header && variant === 'default'" :class="headerClasses">
      <slot name="header" />
    </div>

    <!-- Main content -->
    <div :class="contentClasses">
      <slot />
    </div>

    <!-- Footer slot (optional) -->
    <div v-if="$slots.footer" class="px-4 sm:px-6 pb-4 sm:pb-6 pt-2">
      <slot name="footer" />
    </div>
  </div>
</template>
