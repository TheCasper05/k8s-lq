<script setup lang="ts">
  import { LqCard } from "@lq/ui";
  import type { PopularArticle } from "~/composables/help-center/useHelpCenterData";
  import PopularArticleItem from "./PopularArticleItem.vue";

  interface Props {
    articles: PopularArticle[];
  }

  defineProps<Props>();

  const handleArticleClick = (_articleId: string) => {
    // TODO: Navigate to article page
  };
</script>

<template>
  <LqCard>
    <template #header>
      <h3 class="text-xl font-bold text-surface-900 dark:text-surface-50">
        {{ $t("helpCenter.popularArticles") }}
      </h3>
    </template>

    <div class="space-y-2">
      <PopularArticleItem
        v-for="article in articles"
        :key="article.id"
        :article="article"
        @click="handleArticleClick"
      />
    </div>
  </LqCard>
</template>
