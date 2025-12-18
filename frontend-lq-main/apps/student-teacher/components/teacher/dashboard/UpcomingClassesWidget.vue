<script setup lang="ts">
  import { computed } from "vue";
  import type { UpcomingClass } from "~/composables/teacher/types";
  import { LqCard } from "@lq/ui";
  import { useRoleLayout } from "~/composables/useRoleLayout";

  interface Props {
    classes: UpcomingClass[];
    maxItems?: number;
  }

  const props = withDefaults(defineProps<Props>(), {
    maxItems: 5,
  });

  const { withRolePrefix } = useRoleLayout();
  const router = useRouter();

  const displayedClasses = computed(() => props.classes.slice(0, props.maxItems));

  const handleClassClick = (classId: string) => {
    const route = withRolePrefix(`/classes/${classId}`);
    router.push(route);
  };

  const handleKeyDown = (event: KeyboardEvent, classItem: UpcomingClass) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      handleClassClick(classItem.id);
    }
  };

  const handleViewAll = () => {
    const route = withRolePrefix("/classes");
    router.push(route);
  };

  const formatDateTime = (classItem: UpcomingClass): string => {
    // For mock data, we'll use a simple check
    if (classItem.dateLabel) {
      return `${classItem.dateLabel}, ${classItem.time}`;
    }
    return classItem.time;
  };
</script>

<template>
  <LqCard data-testid="upcoming-classes-widget" class="h-full">
    <template #header>
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <Icon name="solar:calendar-mark-line-duotone" class="text-xl text-primary-600 dark:text-primary-400" />
          <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-50">
            {{ $t("teacher.dashboard.upcomingClasses.title") }}
          </h3>
        </div>
        <Button
          :label="$t('teacher.dashboard.upcomingClasses.viewAll')"
          text
          size="small"
          icon-pos="right"
          data-testid="view-all-classes-button"
          @click="handleViewAll"
        >
          <template #icon>
            <Icon name="solar:arrow-right-line-duotone" />
          </template>
        </Button>
      </div>
    </template>

    <div v-if="displayedClasses.length === 0" class="text-center py-8 text-surface-500 dark:text-surface-400">
      {{ $t("teacher.dashboard.upcomingClasses.empty") }}
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="(classItem, i) in displayedClasses"
        :key="classItem.id"
        class="flex items-start gap-3 p-3 rounded-lg border border-surface-200 dark:border-surface-700 bg-surface-50 dark:bg-surface-800/50 hover:bg-surface-100 dark:hover:bg-surface-800 cursor-pointer transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
        role="button"
        :tabindex="0"
        :aria-label="`${classItem.name}, ${formatDateTime(classItem)}, ${classItem.studentCount} ${$t('teacher.dashboard.upcomingClasses.students')}`"
        data-testid="upcoming-class-item"
        @click="handleClassClick(classItem.id)"
        @keydown="handleKeyDown($event, classItem)"
      >
        <!-- Book Icon -->
        <div class="shrink-0">
          <div
            class="w-10 h-10 rounded-md flex items-center justify-center"
            :class="{
              'bg-primary-500 text-white dark:bg-primary-900/30': i === 0,
              'bg-info-500 text-white dark:bg-info-900/30': i === 1,
              'bg-success-500 text-white dark:bg-success-900/30': i === 2,
            }"
          >
            <Icon name="solar:book-line-duotone" class="text-xl" aria-hidden="true" />
          </div>
        </div>

        <!-- Class Info -->
        <div class="flex-1 min-w-0">
          <h4 class="font-semibold text-sm text-surface-900 dark:text-surface-50 mb-1">
            {{ classItem.name }}
          </h4>
          <div class="flex items-center gap-3 text-xs text-surface-600 dark:text-surface-400">
            <span>{{ formatDateTime(classItem) }}</span>
            <div class="flex items-center gap-1">
              <Icon name="solar:users-group-rounded-line-duotone" class="text-sm" aria-hidden="true" />
              <span>{{ classItem.studentCount }} {{ $t("teacher.dashboard.upcomingClasses.students") }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </LqCard>
</template>
