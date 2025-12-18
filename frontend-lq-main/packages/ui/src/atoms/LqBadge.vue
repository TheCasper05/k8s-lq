<template>
  <span :class="badgeClasses">
    <slot />
  </span>
</template>

<script setup lang="ts">
  import { computed } from "vue";
  import type { BadgeVariant } from "../types";

  interface Props {
    variant?: BadgeVariant;
    dot?: boolean;
  }

  const props = withDefaults(defineProps<Props>(), {
    variant: "info",
    dot: false,
  });

  const badgeClasses = computed(() => {
    const base = "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium";

    const variants = {
      success: "bg-green-100 text-green-800",
      warning: "bg-yellow-100 text-yellow-800",
      error: "bg-red-100 text-red-800",
      info: "bg-blue-100 text-blue-800",
    };

    return [base, variants[props.variant]].join(" ");
  });
</script>
