<script setup lang="ts">
  import type { AccountType } from "@lq/types";

  interface Props {
    icon: string;
    label: string;
    value: AccountType;
    selected?: boolean;
  }

  withDefaults(defineProps<Props>(), {
    selected: false,
  });
  const emit = defineEmits<{
    select: [value: AccountType];
  }>();
</script>

<template>
  <Button
    type="button"
    unstyled
    :class="[
      'w-full p-4 sm:p-5 lg:p-6 rounded-xl sm:rounded-2xl border-2 transition-all duration-200 text-left hover:shadow-md',
      selected
        ? 'border-secondary-300 bg-secondary-100 dark:border-secondary-600 dark:bg-secondary-900/30'
        : 'border-gray-200 bg-white hover:bg-surface-100 hover:border-gray-300 hover:shadow-md dark:bg-surface-800 dark:border-surface-600 dark:hover:border-surface-500',
    ]"
    @click="emit('select', value)"
  >
    <div class="flex items-center gap-3 sm:gap-4">
      <!-- Icon -->
      <div
        class="flex items-center justify-center w-10 h-10 sm:w-12 sm:h-12 rounded-xl sm:rounded-2xl bg-secondary-200 text-secondary-600 dark:bg-secondary-800 dark:text-secondary-300"
      >
        <Icon :name="icon" :size="20" class="sm:text-2xl" />
      </div>

      <!-- Label -->
      <span
        :class="[
          'text-base sm:text-lg font-semibold',
          selected ? 'text-secondary-700 dark:text-secondary-300' : 'text-gray-700 dark:text-surface-200',
        ]"
      >
        {{ label }}
      </span>
    </div>
  </Button>
</template>
