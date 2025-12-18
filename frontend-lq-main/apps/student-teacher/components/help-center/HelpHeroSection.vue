<script setup lang="ts">
  const searchQuery = ref("");

  const handleSearch = (value: string) => {
    searchQuery.value = value;
    // TODO: Implement search functionality
  };
</script>

<template>
  <div class="help-hero-section text-center">
    <!-- Title -->
    <h1 class="text-4xl md:text-5xl font-bold text-surface-900 dark:text-surface-50 mb-4">
      {{ $t("helpCenter.title") }}
    </h1>

    <!-- Description -->
    <p class="text-lg text-surface-600 dark:text-surface-400 mb-8 max-w-2xl mx-auto">
      {{ $t("helpCenter.description") }}
    </p>

    <!-- Search Bar -->
    <div class="max-w-2xl mx-auto">
      <IconField class="relative">
        <InputIcon class="absolute left-3 top-1/2 -translate-y-1/2">
          <Icon name="solar:magnifier-line-duotone" class="text-surface-400" />
        </InputIcon>
        <InputText
          v-model="searchQuery"
          :placeholder="$t('helpCenter.searchPlaceholder')"
          class="w-full pl-10 pr-4 py-3 rounded-lg border border-surface-200 dark:border-surface-700 bg-surface-0 dark:bg-surface-900 text-surface-900 dark:text-surface-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          @update:model-value="handleSearch"
        />
      </IconField>
    </div>
  </div>
</template>

<style scoped>
  .help-hero-section {
    padding: 2rem 0;
  }
</style>
