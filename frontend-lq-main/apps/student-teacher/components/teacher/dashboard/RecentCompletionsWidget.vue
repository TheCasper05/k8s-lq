<script setup lang="ts">
  import { useRoleLayout } from "~/composables/useRoleLayout";
  import type { CompletionItem } from "~/composables/teacher/types";
  import { LqCard } from "@lq/ui";

  interface Props {
    completions: CompletionItem[];
    maxItems?: number;
  }

  const props = withDefaults(defineProps<Props>(), {
    maxItems: 5,
  });

  const { t } = useI18n();
  const { withRolePrefix } = useRoleLayout();
  const router = useRouter();

  const displayedCompletions = computed(() => props.completions.slice(0, props.maxItems));

  const formatDate = (date: Date): string => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(diff / (24 * 60 * 60 * 1000));

    if (minutes < 1) return t("teacher.dashboard.recentCompletions.justNow");
    if (minutes < 60) return t("teacher.dashboard.recentCompletions.minutesAgo", { count: minutes });
    if (hours < 24) return t("teacher.dashboard.recentCompletions.hoursAgo", { count: hours });
    return t("teacher.dashboard.recentCompletions.daysAgo", { count: days });
  };

  const getInitials = (name: string): string => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  const handleViewAll = () => {
    const route = withRolePrefix("/completions");
    router.push(route);
  };

  const getScoreBadgeClass = (score?: number) => {
    if (!score) return "bg-success-100 dark:bg-success-900/30 text-success-700 dark:text-success-400";
    if (score >= 90) return "bg-success-100 dark:bg-success-900/30 text-success-700 dark:text-success-400";
    return "bg-info-100 dark:bg-info-900/30 text-info-700 dark:text-info-400";
  };
</script>

<template>
  <LqCard data-testid="recent-completions-widget">
    <template #header>
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <Icon name="solar:check-circle-line-duotone" class="text-xl text-success-600 dark:text-success-400" />
          <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-50">
            {{ $t("teacher.dashboard.recentCompletions.title") }}
          </h3>
        </div>
        <Button
          :label="$t('teacher.dashboard.recentCompletions.viewAll')"
          text
          size="small"
          icon-pos="right"
          data-testid="view-all-completions-button"
          @click="handleViewAll"
        >
          <template #icon>
            <Icon name="solar:arrow-right-line-duotone" />
          </template>
        </Button>
      </div>
    </template>

    <div v-if="displayedCompletions.length === 0" class="text-center py-8 text-surface-500 dark:text-surface-400">
      {{ $t("teacher.dashboard.recentCompletions.empty") }}
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="completion in displayedCompletions"
        :key="completion.id"
        class="flex items-center gap-3 p-3 bg-surface-50 dark:bg-surface-800 border border-surface-200 dark:border-surface-700 rounded-lg hover:bg-surface-100 dark:hover:bg-surface-700 transition-colors"
        data-testid="completion-item"
      >
        <!-- Avatar -->
        <LqAvatar
          :src="completion.studentAvatar"
          :initials="getInitials(completion.studentName)"
          :alt="completion.studentName"
          size="md"
        />

        <!-- Name, Activity and Time -->
        <div class="flex-1 min-w-0">
          <p class="text-sm font-semibold text-surface-900 dark:text-surface-50 mb-0.5">
            {{ completion.studentName }}
          </p>
          <p class="text-xs text-surface-600 dark:text-surface-400">
            {{ completion.activityName }} • {{ formatDate(completion.completedAt) }}
          </p>
        </div>

        <!-- Score Badge -->
        <div
          v-if="completion.score"
          :class="['px-2 py-1 text-xs font-semibold rounded shrink-0', getScoreBadgeClass(completion.score)]"
          data-testid="completion-score-badge"
        >
          {{ completion.score }}%
        </div>
      </div>
    </div>
  </LqCard>
</template>
