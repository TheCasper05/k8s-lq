<script setup lang="ts">
  import type { PopularArticle } from "~/composables/help-center/useHelpCenterData";

  interface Props {
    article: PopularArticle;
  }

  const props = defineProps<Props>();

  const emit = defineEmits<{
    click: [articleId: string];
  }>();

  const handleClick = () => {
    emit("click", props.article.id);
  };
</script>

<template>
  <div
    class="popular-article-item flex items-start gap-4 p-4 rounded-lg bg-surface-50 dark:bg-surface-800/50 hover:bg-surface-100 dark:hover:bg-surface-800 cursor-pointer transition-colors duration-200"
    role="button"
    tabindex="0"
    :aria-label="article.title"
    @click="handleClick"
    @keydown.enter="handleClick"
    @keydown.space.prevent="handleClick"
  >
    <!-- Number Square -->
    <div class="flex-shrink-0 w-10 h-10 rounded-lg bg-surface-200 dark:bg-surface-700 flex items-center justify-center">
      <span class="text-base font-bold text-surface-900 dark:text-surface-50">{{ article.rank }}</span>
    </div>

    <!-- Content -->
    <div class="flex-1 min-w-0">
      <!-- Title -->
      <h4 class="text-base font-bold text-surface-900 dark:text-surface-50 mb-2 line-clamp-2">
        {{ article.title }}
      </h4>

      <!-- Metadata -->
      <div class="flex items-center gap-2 text-sm text-surface-500 dark:text-surface-400">
        <span>{{ article.category }}</span>
        <span>•</span>
        <div class="flex items-center gap-1">
          <Icon name="solar:clock-circle-line-duotone" class="text-base" aria-hidden="true" />
          <span>{{ article.readTime }} {{ $t("helpCenter.min") }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
