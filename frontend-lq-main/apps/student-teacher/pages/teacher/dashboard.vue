<script setup lang="ts">
  import { useTeacherDashboardData } from "~/composables/teacher/useTeacherDashboardData";
  import QuickActionCards from "~/components/teacher/dashboard/QuickActionCards.vue";
  import MetricsCards from "~/components/teacher/dashboard/MetricsCards.vue";
  import NeedsAttentionWidget from "~/components/teacher/dashboard/NeedsAttentionWidget.vue";
  import RecentActivityWidget from "~/components/teacher/dashboard/RecentActivityWidget.vue";
  import RecentCompletionsWidget from "~/components/teacher/dashboard/RecentCompletionsWidget.vue";
  import UpcomingClassesWidget from "~/components/teacher/dashboard/UpcomingClassesWidget.vue";

  definePageMeta({
    layout: "app",
  });

  const {
    quickActions,
    metrics,
    needsAttention,
    recentActivity,
    recentCompletions,
    upcomingClasses,
    isLoading,
    error,
  } = useTeacherDashboardData();
</script>

<template>
  <div class="teacher-dashboard lq-container" data-testid="teacher-dashboard">
    <!-- Header -->
    <div class="mb-6 sm:mb-8">
      <h1 class="text-2xl sm:text-3xl font-bold text-surface-900 dark:text-surface-50 mb-2">
        {{ $t("teacher.dashboard.greeting") }}
      </h1>
      <p class="text-sm sm:text-base text-surface-600 dark:text-surface-400">
        {{ $t("teacher.dashboard.greetingDescription") }}
      </p>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex items-center justify-center py-12" data-testid="dashboard-loading">
      <div class="text-center">
        <Icon
          name="solar:refresh-line-duotone"
          class="text-4xl text-primary-600 dark:text-primary-400 animate-spin mb-4"
        />
        <p class="text-surface-600 dark:text-surface-400">{{ $t("common.loading") }}</p>
      </div>
    </div>

    <!-- Error State -->
    <div
      v-else-if="error"
      class="bg-danger-50 dark:bg-danger-900/20 border border-danger-200 dark:border-danger-800 rounded-lg p-6 mb-8"
      data-testid="dashboard-error"
    >
      <div class="flex items-center gap-3">
        <Icon name="solar:danger-triangle-line-duotone" class="text-xl text-danger-600 dark:text-danger-400" />
        <div>
          <h3 class="font-semibold text-danger-900 dark:text-danger-100 mb-1">{{ $t("common.error") }}</h3>
          <p class="text-sm text-danger-700 dark:text-danger-300">{{ error }}</p>
        </div>
      </div>
    </div>

    <!-- Dashboard Content -->
    <template v-else>
      <!-- Quick Action Cards -->
      <div class="mb-6 sm:mb-8">
        <QuickActionCards :actions="quickActions" />
      </div>

      <!-- Metrics Cards -->
      <div class="mb-6 sm:mb-8">
        <MetricsCards :metrics="metrics" />
      </div>

      <!-- Main Content Grid - 80/20 proportion -->
      <div class="space-y-4 sm:space-y-6 mb-6 sm:mb-8">
        <!-- First Row: Needs Attention (80%) and Recent Activity (20%) -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-4 sm:gap-6">
          <div class="col-span-12 lg:col-span-7">
            <NeedsAttentionWidget :items="needsAttention" />
          </div>
          <div class="col-span-12 lg:col-span-5">
            <RecentActivityWidget :activities="recentActivity" />
          </div>
        </div>

        <!-- Second Row: Recent Completions (80%) and Upcoming Classes (20%) -->
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-4 sm:gap-6">
          <div class="col-span-12 lg:col-span-7">
            <RecentCompletionsWidget :completions="recentCompletions" />
          </div>
          <div class="col-span-12 lg:col-span-5">
            <UpcomingClassesWidget :classes="upcomingClasses" />
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
  .teacher-dashboard {
    min-height: calc(100vh - 200px);
  }
</style>
