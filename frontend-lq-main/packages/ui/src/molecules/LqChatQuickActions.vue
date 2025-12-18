<script setup lang="ts">
  import Chip from "primevue/chip";

  interface Props {
    actions: string[];
  }

  defineProps<Props>();

  const emit = defineEmits<{
    action: [action: string];
  }>();
</script>

<template>
  <div class="flex flex-wrap gap-2">
    <Chip
      v-for="action in actions"
      :key="action"
      :label="action"
      class="!px-3 !py-1.5 !bg-white dark:!bg-surface-800 !border !border-surface-200 dark:!border-surface-700 !rounded-full !text-xs !font-medium !text-surface-600 dark:!text-surface-300 hover:!bg-surface-100 dark:hover:!bg-surface-700 !transition-colors !shadow-sm cursor-pointer"
      @click="emit('action', action)"
    />
    <slot name="secondary-actions" />
  </div>
</template>
