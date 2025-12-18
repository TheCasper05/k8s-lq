<script setup lang="ts">
  import type { Student } from "~/composables/students/types";
  import { LqDataTable, type LqDataTableColumn, LqAvatar } from "@lq/ui";
  import { useStudentColors } from "~/composables/students/useStudentColors";

  const props = defineProps<{
    students: Student[];
  }>();

  const emit = defineEmits<{
    "view-profile": [studentId: string];
  }>();

  const { getLevelSeverity, getProgressSeverity } = useStudentColors();

  const tableData = computed(() => props.students);

  const getInitials = (firstName: string, lastName: string) => {
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
  };

  const getLevelColorClass = (level: string) => {
    const severity = getLevelSeverity(level);
    const severityColors: Record<string, string> = {
      danger: "bg-danger-100 dark:bg-danger-900/30 text-danger-700 dark:text-danger-400",
      warn: "bg-warning-100 dark:bg-warning-900/30 text-warning-700 dark:text-warning-400",
      info: "bg-info-100 dark:bg-info-900/30 text-info-700 dark:text-info-400",
      success: "bg-success-100 dark:bg-success-900/30 text-success-700 dark:text-success-400",
      secondary: "bg-surface-100 dark:bg-surface-800 text-surface-700 dark:text-surface-300",
    };
    return severityColors[severity] || severityColors.secondary;
  };

  const getProgressColorClass = (progress: number) => {
    const severity = getProgressSeverity(progress);
    if (severity === "danger") {
      return "bg-danger-500";
    } else if (severity === "warn") {
      return "bg-warning-500";
    } else {
      return "bg-success-500";
    }
  };

  const getProgressValueColorClass = (progress: number) => {
    const severity = getProgressSeverity(progress);
    if (severity === "danger") {
      return "bg-danger-100 dark:bg-danger-900/30 text-danger-700 dark:text-danger-400";
    } else if (severity === "warn") {
      return "bg-warning-100 dark:bg-warning-900/30 text-warning-700 dark:text-warning-400";
    } else {
      return "bg-success-100 dark:bg-success-900/30 text-success-700 dark:text-success-400";
    }
  };

  const handleViewProfile = (studentId: string) => {
    emit("view-profile", studentId);
  };

  const { t } = useI18n();

  const columns = computed<LqDataTableColumn[]>(() => [
    { field: "student", header: t("students.student"), class: "min-w-[200px]" },
    { field: "level", header: t("students.level"), class: "min-w-[100px]" },
    { field: "progress", header: t("students.progress"), class: "min-w-[150px]" },
    { field: "activities", header: t("students.activities"), class: "min-w-[120px]" },
    { field: "time", header: t("students.time"), class: "min-w-[120px]" },
    { field: "score", header: t("students.score"), class: "min-w-[100px]" },
  ]);
</script>

<template>
  <LqDataTable :data="tableData" :columns="columns" :loading="false" :empty-message="$t('common.noStudentsFound')">
    <!-- Student Column -->
    <template #cell-student="{ data }">
      <div class="flex items-center gap-3">
        <div class="relative">
          <LqAvatar
            :src="data.photo || undefined"
            :initials="getInitials(data.firstName, data.lastName)"
            shape="square"
            size="large"
            class="bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 rounded-lg shadow-sm !size-12"
          />
          <span
            class="absolute bottom-0 right-0 w-2.5 h-2.5 bg-success-500 border-2 border-white dark:border-surface-900 rounded-full"
          />
        </div>
        <div class="flex flex-col">
          <span class="font-semibold text-surface-900 dark:text-surface-100">
            {{ data.firstName }} {{ data.lastName }}
          </span>
          <span class="text-sm text-surface-600 dark:text-surface-400">{{ data.email }}</span>
        </div>
      </div>
    </template>

    <!-- Level Column -->
    <template #cell-level="{ data }">
      <div
        :class="getLevelColorClass(data.level)"
        class="border border-surface-300 dark:border-surface-600 rounded-lg px-2 py-1 text-sm font-medium inline-block"
      >
        {{ data.level }}
      </div>
    </template>

    <!-- Progress Column -->
    <template #cell-progress="{ data }">
      <div class="flex items-center gap-3">
        <div class="relative flex-1 h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
          <div
            :class="getProgressColorClass(data.progress)"
            class="h-full rounded-full transition-all duration-300"
            :style="{ width: `${data.progress}%` }"
          />
        </div>
        <span
          :class="getProgressValueColorClass(data.progress)"
          class="text-sm font-semibold min-w-[3rem] text-right rounded-lg px-2 py-1"
        >
          {{ data.progress }}%
        </span>
      </div>
    </template>

    <!-- Activities Column -->
    <template #cell-activities="{ data }">
      <div class="flex items-center gap-2">
        <div class="w-8 h-8 bg-info-100 dark:bg-info-900/30 rounded-lg flex items-center justify-center">
          <Icon name="solar:book-line-duotone" class="text-info-600 dark:text-info-400 text-xl" />
        </div>
        <span>{{ data.activitiesCompleted }}/{{ data.activitiesTotal }}</span>
      </div>
    </template>

    <!-- Time Column -->
    <template #cell-time="{ data }">
      <div class="flex items-center gap-2">
        <div class="w-8 h-8 bg-success-100 dark:bg-success-900/30 rounded-lg flex items-center justify-center">
          <Icon name="solar:clock-circle-line-duotone" class="text-success-600 dark:text-success-400 text-xl" />
        </div>
        <span>{{ data.studyTimeMinutes }} {{ $t("students.min") }}</span>
      </div>
    </template>

    <!-- Score Column -->
    <template #cell-score="{ data }">
      <div class="flex items-center gap-2">
        <div class="w-8 h-8 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center">
          <Icon name="solar:star-line-duotone" class="text-primary-600 dark:text-primary-400 text-xl" />
        </div>
        <span class="font-semibold">{{ data.score }}</span>
      </div>
    </template>

    <!-- Actions Column -->
    <template #actions="{ data }">
      <Button
        variant="text"
        class="text-surface-600 dark:text-surface-400 hover:text-primary-600 dark:hover:text-primary-400"
        @click="handleViewProfile(data.id)"
      >
        <template #icon>
          <Icon name="solar:eye-line-duotone" />
        </template>
      </Button>
    </template>
  </LqDataTable>
</template>
