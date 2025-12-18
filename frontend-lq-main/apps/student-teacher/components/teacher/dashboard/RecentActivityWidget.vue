<script setup lang="ts">
  import { computed } from "vue";
  import { useRoleLayout } from "~/composables/useRoleLayout";
  import type { ActivityItem } from "~/composables/teacher/types";
  import { LqCard } from "@lq/ui";

  interface Props {
    activities: ActivityItem[];
    maxItems?: number;
  }

  const props = withDefaults(defineProps<Props>(), {
    maxItems: 5,
  });

  const { withRolePrefix } = useRoleLayout();
  const router = useRouter();

  const displayedActivities = computed(() => props.activities.slice(0, props.maxItems));

  const handleViewAll = () => {
    const route = withRolePrefix("/activity");
    router.push(route);
  };

  const getInitials = (name?: string): string => {
    if (!name) return "";
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };
</script>

<template>
  <LqCard data-testid="recent-activity-widget" class="h-full">
    <template #header>
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <Icon name="solar:graph-up-line-duotone" class="text-xl text-success-600 dark:text-success-400" />
          <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-50">
            {{ $t("teacher.dashboard.recentActivity.title") }}
          </h3>
        </div>
        <Button
          :label="$t('teacher.dashboard.recentActivity.viewAll')"
          text
          size="small"
          icon-pos="right"
          data-testid="view-all-activity-button"
          @click="handleViewAll"
        >
          <template #icon>
            <Icon name="solar:arrow-right-line-duotone" />
          </template>
        </Button>
      </div>
    </template>

    <div v-if="displayedActivities.length === 0" class="text-center py-8 text-surface-500 dark:text-surface-400">
      {{ $t("teacher.dashboard.recentActivity.empty") }}
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="activity in displayedActivities"
        :key="activity.id"
        class="flex items-start gap-3 p-3 rounded-lg bg-surface-50 dark:bg-surface-800 border border-surface-200 dark:border-surface-700 hover:bg-surface-100 dark:hover:bg-surface-700 transition-colors"
        data-testid="activity-item"
      >
        <!-- Avatar for completion type, Icon for others -->
        <LqAvatar
          v-if="activity.type === 'completion' && activity.studentName"
          :src="activity.studentAvatar"
          :initials="getInitials(activity.studentName)"
          size="md"
          class="rounded-md"
        />
        <div
          v-else
          :class="[
            'w-10 h-10 rounded-md flex items-center justify-center shrink-0',
            activity.type === 'assignment' && activity.icon.includes('book')
              ? 'bg-info-100 dark:bg-info-900/30'
              : 'bg-primary-100 dark:bg-primary-900/30',
          ]"
        >
          <Icon
            :name="activity.icon"
            :class="[
              'text-lg',
              activity.type === 'assignment' && activity.icon.includes('book')
                ? 'text-info-600 dark:text-info-400'
                : 'text-primary-600 dark:text-primary-400',
            ]"
          />
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-semibold text-surface-900 dark:text-surface-50">{{ activity.title }}</p>
          <p class="text-xs text-surface-600 dark:text-surface-400">{{ activity.description }}</p>
        </div>
      </div>
    </div>
  </LqCard>
</template>
