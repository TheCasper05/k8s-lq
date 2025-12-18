<script setup lang="ts">
  import type { FAQ } from "~/composables/help-center/useHelpCenterData";

  interface Props {
    faq: FAQ;
  }

  const props = defineProps<Props>();

  const emit = defineEmits<{
    click: [faqId: string];
  }>();

  const handleClick = () => {
    emit("click", props.faq.id);
    // TODO: Implement expand/collapse functionality
  };
</script>

<template>
  <div
    class="faq-item flex items-center justify-between p-4 rounded-lg bg-surface-50 dark:bg-surface-800/50 hover:bg-surface-100 dark:hover:bg-surface-800 cursor-pointer transition-colors duration-200"
    role="button"
    tabindex="0"
    :aria-label="faq.question"
    @click="handleClick"
    @keydown.enter="handleClick"
    @keydown.space.prevent="handleClick"
  >
    <!-- Question -->
    <span class="text-sm font-medium text-surface-900 dark:text-surface-50 flex-1 pr-4">
      {{ faq.question }}
    </span>

    <!-- Chevron -->
    <Icon
      name="solar:alt-arrow-right-line-duotone"
      class="text-base text-surface-400 dark:text-surface-500 flex-shrink-0"
      aria-hidden="true"
    />
  </div>
</template>
