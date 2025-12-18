<script setup lang="ts">
  import Card from "primevue/card";
  import { useDashboardPage } from "~/composables/admin/home/useDashboardPage";

  definePageMeta({
    layout: "app",
  });

  const { adminStats, getStatColorClasses, t } = useDashboardPage();
</script>

<template>
  <div class="admin-dashboard">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-surface-900 dark:text-surface-50">
        {{ t("dashboard.admin.title") }}
      </h1>
      <p class="text-surface-600 dark:text-surface-400 mt-2">
        {{ t("dashboard.admin.subtitle") }}
      </p>
    </div>

    <!-- Stats Widget -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div
        v-for="(stat, index) in adminStats"
        :key="index"
        class="bg-surface-0 dark:bg-surface-900 p-6 rounded-xl border border-surface-200 dark:border-surface-700 flex flex-col gap-2"
      >
        <div class="flex items-start gap-2 justify-between">
          <span class="text-xl font-light leading-tight">{{ t(stat.titleKey) }}</span>
          <span :class="['shrink-0 rounded-lg w-8 h-8 flex items-center justify-center border', getStatColorClasses(stat.color)]">
            <Icon :name="stat.icon" class="text-xl" />
          </span>
        </div>
        <div class="flex flex-col gap-1 w-full">
          <div class="text-3xl font-medium leading-tight">
            {{ stat.value }}
          </div>
          <div class="text-surface-600 dark:text-surface-400 text-sm leading-tight">
            {{ t(stat.subtitleKey) }}
          </div>
        </div>
      </div>
    </div>

    <!-- System Status -->
    <Card class="mt-6">
      <template #title>{{ t("dashboard.admin.systemStatus") }}</template>
      <template #content>
        <p class="text-surface-600 dark:text-surface-400">
          {{ t("dashboard.admin.systemStatusDescription") }}
        </p>
      </template>
    </Card>
  </div>
</template>
