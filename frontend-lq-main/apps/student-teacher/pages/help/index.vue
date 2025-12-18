<script setup lang="ts">
  import HelpHeroSection from "~/components/help-center/HelpHeroSection.vue";
  import CategoryGrid from "~/components/help-center/CategoryGrid.vue";
  import PopularArticlesSection from "~/components/help-center/PopularArticlesSection.vue";
  import VideoTutorialsSection from "~/components/help-center/VideoTutorialsSection.vue";
  import FAQsSection from "~/components/help-center/FAQsSection.vue";
  import SupportButtons from "~/components/help-center/SupportButtons.vue";
  import QuickLinksSection from "~/components/help-center/QuickLinksSection.vue";
  import { useHelpCenterData } from "~/composables/help-center/useHelpCenterData";

  definePageMeta({
    layout: "app",
  });

  const { categories, popularArticles, videoTutorials, faqs, quickLinks } = useHelpCenterData();
</script>

<template>
  <div class="help-center lq-container">
    <!-- Hero Section -->
    <HelpHeroSection class="mb-8 sm:mb-12" />

    <!-- Category Grid -->
    <div class="mb-8 sm:mb-12">
      <h2 class="text-xl sm:text-2xl font-bold text-surface-900 dark:text-surface-50 mb-4 sm:mb-6">
        {{ $t("helpCenter.browseByCategory") }}
      </h2>
      <CategoryGrid :categories="categories" />
    </div>

    <!-- Main Content Grid - 80/20 proportion -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-4 sm:gap-6">
      <!-- Left Column (80%) -->
      <div class="col-span-12 lg:col-span-8 space-y-4 sm:space-y-6">
        <PopularArticlesSection :articles="popularArticles" />
        <VideoTutorialsSection :videos="videoTutorials" />
      </div>

      <!-- Right Column (20%) -->
      <div class="col-span-12 lg:col-span-4 space-y-4 sm:space-y-6">
        <FAQsSection :faqs="faqs" />
        <SupportButtons />
        <QuickLinksSection :links="quickLinks" />
      </div>
    </div>
  </div>
</template>

<style scoped>
  .help-center {
    min-height: calc(100vh - 200px);
  }
</style>
