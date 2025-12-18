<template>
  <div class="flex min-h-screen items-center justify-center bg-gray-100">
    <div class="text-center">
      <h1 class="mb-4 text-6xl font-bold text-gray-800">403</h1>
      <p class="mb-8 text-xl text-gray-600">{{ t("errors.unauthorized") }}</p>
      <RouterLink to="/" class="btn-primary">
        {{ t("errors.goHome") }}
      </RouterLink>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { useI18n } from "vue-i18n";

  const { t } = useI18n();
</script>
