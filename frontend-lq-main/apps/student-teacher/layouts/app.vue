<script setup lang="ts">
  import { useRoleLayout } from "~/composables/useRoleLayout";
  import StudentLayoutProvider from "~/components/layout-providers/StudentLayoutProvider.vue";
  import TeacherLayoutProvider from "~/components/layout-providers/TeacherLayoutProvider.vue";
  import AdminLayoutProvider from "~/components/layout-providers/AdminLayoutProvider.vue";

  const { layoutConfig } = useRoleLayout();

  // Map provider names to actual components
  const providerComponents = {
    StudentLayoutProvider,
    TeacherLayoutProvider,
    AdminLayoutProvider,
  };

  // Dynamically select provider based on role
  const currentProvider = computed(() => {
    const providerName = layoutConfig.value?.provider;
    return providerName ? providerComponents[providerName as keyof typeof providerComponents] : null;
  });
</script>

<template>
  <div class="app-layout">
    <component :is="currentProvider" v-if="currentProvider">
      <slot />
    </component>
    <div v-else class="flex items-center justify-center min-h-screen">
      <div class="text-center">
        <p class="text-lg text-surface-600 dark:text-surface-400">Loading...</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
  .app-layout {
    min-height: 100vh;
    background: var(--surface-ground);
  }
</style>
