<script setup lang="ts">
  import type { QuickLink } from "~/composables/help-center/useHelpCenterData";

  interface Props {
    link: QuickLink;
  }

  const props = defineProps<Props>();

  const handleClick = () => {
    if (props.link.external) {
      window.open(props.link.url, "_blank", "noopener,noreferrer");
    } else {
      navigateTo(props.link.url);
    }
  };
</script>

<template>
  <div
    class="quick-link-item flex items-center justify-between p-4 rounded-lg bg-surface-50 dark:bg-surface-800/50 hover:bg-surface-100 dark:hover:bg-surface-800 cursor-pointer transition-colors duration-200"
    role="button"
    tabindex="0"
    :aria-label="link.label"
    @click="handleClick"
    @keydown.enter="handleClick"
    @keydown.space.prevent="handleClick"
  >
    <!-- Icon and Label -->
    <div class="flex items-center gap-3 flex-1">
      <Icon :name="link.icon" class="text-lg text-surface-600 dark:text-surface-400" aria-hidden="true" />
      <span class="text-sm font-medium text-surface-900 dark:text-surface-50">{{ link.label }}</span>
    </div>

    <!-- External Link Icon -->
    <Icon
      v-if="link.external"
      name="solar:external-link-line-duotone"
      class="text-base text-surface-400 dark:text-surface-500 flex-shrink-0"
      aria-hidden="true"
    />
  </div>
</template>
