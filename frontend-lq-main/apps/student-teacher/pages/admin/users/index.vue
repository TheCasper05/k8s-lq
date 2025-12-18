<script setup lang="ts">
  import { useUsersPage } from "~/composables/admin/user/useUsersPage";

  definePageMeta({
    layout: "app",
  });

  const { pageTitle, pageDescription } = useUsersPage();
</script>

<template>
  <div>
    <h1 class="text-3xl font-bold text-surface-900 dark:text-surface-50 mb-4">{{ pageTitle }}</h1>
    <p class="text-surface-600 dark:text-surface-400">{{ pageDescription }}</p>
  </div>
</template>
