<script setup lang="ts">
  definePageMeta({
    layout: "app",
  });
</script>

<template>
  <div class="student-dashboard lq-container">
    <div class="mb-4 sm:mb-6">
      <h1 class="text-2xl sm:text-3xl font-bold text-surface-900 dark:text-surface-50">
        {{ $t("student.dashboard.title") }}
      </h1>
      <p class="text-sm sm:text-base text-surface-600 dark:text-surface-400 mt-2">
        {{ $t("student.dashboard.welcomeBack") }}
      </p>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
      <!-- Quick Stats Cards -->
      <Card>
        <template #title>
          <div class="flex items-center gap-2">
            <Icon name="solar:book-linear" class="text-xl sm:text-2xl text-primary-500" />
            <span class="text-sm sm:text-base">{{ $t("student.dashboard.myCourses") }}</span>
          </div>
        </template>
        <template #content>
          <p class="text-3xl sm:text-4xl font-bold text-primary-500">5</p>
          <p class="text-xs sm:text-sm text-surface-600 dark:text-surface-400 mt-2">
            {{ $t("student.dashboard.activeCourses") }}
          </p>
        </template>
      </Card>

      <Card>
        <template #title>
          <div class="flex items-center gap-2">
            <Icon name="solar:clipboard-list-linear" class="text-xl sm:text-2xl text-orange-500" />
            <span class="text-sm sm:text-base">{{ $t("student.dashboard.assignments") }}</span>
          </div>
        </template>
        <template #content>
          <p class="text-3xl sm:text-4xl font-bold text-orange-500">3</p>
          <p class="text-xs sm:text-sm text-surface-600 dark:text-surface-400 mt-2">
            {{ $t("student.dashboard.pendingSubmissions") }}
          </p>
        </template>
      </Card>

      <Card>
        <template #title>
          <div class="flex items-center gap-2">
            <Icon name="solar:chart-linear" class="text-xl sm:text-2xl text-green-500" />
            <span class="text-sm sm:text-base">{{ $t("student.dashboard.progress") }}</span>
          </div>
        </template>
        <template #content>
          <p class="text-3xl sm:text-4xl font-bold text-green-500">78%</p>
          <p class="text-xs sm:text-sm text-surface-600 dark:text-surface-400 mt-2">
            {{ $t("student.dashboard.overallCompletion") }}
          </p>
        </template>
      </Card>
    </div>

    <!-- Recent Activity -->
    <Card class="mt-4 sm:mt-6">
      <template #title>{{ $t("student.dashboard.recentActivity") }}</template>
      <template #content>
        <p class="text-surface-600 dark:text-surface-400">
          {{ $t("student.dashboard.recentActivityDescription") }}
        </p>
      </template>
    </Card>
  </div>
</template>
