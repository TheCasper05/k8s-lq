<script setup lang="ts">
  export interface LqInfoItemProps {
    label: string;
    value?: string;
    icon?: string;
    iconColor?: string;
  }

  withDefaults(defineProps<LqInfoItemProps>(), {
    iconColor: "text-primary-600 dark:text-primary-400",
  });
</script>

<template>
  <div class="flex items-start gap-3">
    <!-- Icon -->
    <div
      v-if="icon"
      :class="[
        'flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center',
        'bg-primary-100 dark:bg-primary-900/30',
        iconColor,
      ]"
    >
      <Icon :name="icon" class="text-lg" />
    </div>

    <!-- Content -->
    <div class="flex-1 min-w-0">
      <p class="text-sm font-medium text-surface-500 dark:text-surface-400 mb-1">
        {{ label }}
      </p>
      <p class="text-base text-surface-900 dark:text-surface-100 break-words">
        <slot>{{ value }}</slot>
      </p>
    </div>
  </div>
</template>
