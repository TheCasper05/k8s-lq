<script setup lang="ts">
  import type { HelpCategory } from "~/composables/help-center/useHelpCenterData";

  interface Props {
    category: HelpCategory;
  }

  const props = defineProps<Props>();

  const emit = defineEmits<{
    click: [categoryId: string];
  }>();

  const getIconBgColor = (color: string) => {
    const colorMap: Record<string, string> = {
      success: "bg-success-50 dark:bg-success-900/30",
      primary: "bg-primary-50 dark:bg-primary-900/30",
      warning: "bg-warning-50 dark:bg-warning-900/30",
      secondary: "bg-secondary-50 dark:bg-secondary-900/30",
      danger: "bg-danger-50 dark:bg-danger-900/30",
      surface: "bg-surface-100 dark:bg-surface-800",
    };
    return colorMap[color] || colorMap.surface;
  };

  const getIconColor = (color: string) => {
    const colorMap: Record<string, string> = {
      success: "text-success-600 dark:text-success-400",
      primary: "text-primary-600 dark:text-primary-400",
      warning: "text-warning-600 dark:text-warning-400",
      secondary: "text-secondary-600 dark:text-secondary-400",
      danger: "text-danger-600 dark:text-danger-400",
      surface: "text-surface-600 dark:text-surface-400",
    };
    return colorMap[color] || colorMap.surface;
  };

  const handleClick = () => {
    emit("click", props.category.id);
  };
</script>

<template>
  <div
    class="category-card bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 p-6 cursor-pointer transition-all duration-200 hover:shadow-lg"
    role="button"
    tabindex="0"
    :aria-label="`${category.title}: ${category.description}`"
    @click="handleClick"
    @keydown.enter="handleClick"
    @keydown.space.prevent="handleClick"
  >
    <!-- Icon with tonal background -->
    <div class="mb-4">
      <div :class="['w-12 h-12 rounded-lg flex items-center justify-center', getIconBgColor(category.iconColor)]">
        <Icon :name="category.icon" :class="['text-2xl', getIconColor(category.iconColor)]" aria-hidden="true" />
      </div>
    </div>

    <!-- Title -->
    <h3 class="text-lg font-bold text-surface-900 dark:text-surface-50 mb-2">
      {{ category.title }}
    </h3>

    <!-- Description -->
    <p class="text-sm text-surface-600 dark:text-surface-400 mb-4">
      {{ category.description }}
    </p>

    <!-- Article Count -->
    <div class="flex items-center gap-2 text-sm text-surface-500 dark:text-surface-400">
      <Icon name="solar:document-text-line-duotone" class="text-base" aria-hidden="true" />
      <span>{{ category.articleCount }} {{ $t("helpCenter.articles") }}</span>
    </div>
  </div>
</template>
