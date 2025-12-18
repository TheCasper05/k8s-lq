<script setup lang="ts">
  import { computed } from "vue";

  export interface LqTagProps {
    label: string;
    removable?: boolean;
    variant?: "primary" | "secondary" | "neutral" | "success" | "info";
  }

  const props = withDefaults(defineProps<LqTagProps>(), {
    removable: false,
    variant: "neutral",
  });

  const emit = defineEmits<{
    remove: [];
  }>();

  const variantClasses = computed(() => {
    const variants = {
      primary:
        "bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 border-primary-200 dark:border-primary-800",
      secondary:
        "bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 border-purple-200 dark:border-purple-800",
      neutral:
        "bg-surface-100 dark:bg-surface-800 text-surface-700 dark:text-surface-300 border-surface-200 dark:border-surface-700",
      success:
        "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 border-green-200 dark:border-green-800",
      info: "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-800",
    };
    return variants[props.variant];
  });

  const handleRemove = () => {
    emit("remove");
  };
</script>

<template>
  <span
    :class="[
      'inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium border',
      'transition-colors',
      variantClasses,
    ]"
  >
    <span>{{ label }}</span>
    <button v-if="removable" type="button" class="hover:opacity-70 transition-opacity" @click="handleRemove">
      <Icon name="pi:times" class="text-xs" />
    </button>
  </span>
</template>
