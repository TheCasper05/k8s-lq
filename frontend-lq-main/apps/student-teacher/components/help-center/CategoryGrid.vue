<script setup lang="ts">
  import type { HelpCategory } from "~/composables/help-center/useHelpCenterData";
  import CategoryCard from "./CategoryCard.vue";

  interface Props {
    categories: HelpCategory[];
  }

  defineProps<Props>();

  const handleCategoryClick = (_categoryId: string) => {
    // TODO: Navigate to category page or filter articles
  };
</script>

<template>
  <div class="category-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <CategoryCard v-for="category in categories" :key="category.id" :category="category" @click="handleCategoryClick" />
  </div>
</template>
