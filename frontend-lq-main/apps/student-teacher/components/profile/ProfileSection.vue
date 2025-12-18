<script setup lang="ts">
  export interface ProfileSectionProps {
    title: string;
    icon?: string;
    iconColor?: string;
    iconBg?: string;
  }

  withDefaults(defineProps<ProfileSectionProps>(), {
    iconColor: "text-primary-600 dark:text-primary-400",
    iconBg: "bg-primary-100 dark:bg-primary-900/30",
  });
</script>

<template>
  <div class="bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-3">
        <div v-if="icon" :class="['w-10 h-10 rounded-full flex items-center justify-center', iconBg, iconColor]">
          <Icon :name="icon" class="text-lg" />
        </div>
        <h2 class="text-xl font-semibold text-surface-900 dark:text-surface-100">
          {{ title }}
        </h2>
      </div>
      <slot name="actions" />
    </div>

    <!-- Content -->
    <div class="space-y-4">
      <slot />
    </div>
  </div>
</template>
