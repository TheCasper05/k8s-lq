<script setup lang="ts">
  import type { Student } from "~/composables/students/types";
  import { LqAvatar } from "@lq/ui";
  import { useStudentColors } from "~/composables/students/useStudentColors";

  defineProps<{
    student: Student;
  }>();

  defineEmits<{
    "view-profile": [studentId: string];
  }>();

  const { getProgressSeverity, getLevelSeverity } = useStudentColors();

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
</script>

<template>
  <div
    class="bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 p-4 sm:p-6 hover:shadow-lg transition-all duration-200 flex flex-col gap-3 sm:gap-4"
  >
    <!-- Header: Avatar, Name, Email, Level -->
    <div class="flex items-start gap-3 sm:gap-4">
      <LqAvatar
        :src="student.photo || undefined"
        :initials="getInitials(student.firstName, student.lastName)"
        shape="square"
        size="2xl"
        avatar-class="bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 shadow-sm"
      />
      <div class="flex-1 min-w-0">
        <div class="flex items-start justify-between gap-2">
          <div class="flex-1 min-w-0">
            <h3 class="font-semibold text-base sm:text-lg text-surface-900 dark:text-surface-100 truncate">
              {{ student.firstName }} {{ student.lastName }}
            </h3>
            <p class="text-xs sm:text-sm text-surface-600 dark:text-surface-400 truncate">
              {{ student.email }}
            </p>
          </div>
          <div :class="getLevelColorClass(student.level)" class="rounded-lg px-2 py-1 text-xs sm:text-sm font-medium">
            {{ student.level }}
          </div>
        </div>
      </div>
    </div>

    <!-- Progress Bar -->
    <div class="flex flex-col gap-2">
      <div class="flex items-center justify-between text-sm">
        <span class="text-surface-600 dark:text-surface-400">{{ $t("students.courseProgress") }}</span>
        <span
          class="font-semibold bg-surface-100 dark:bg-surface-800 rounded-lg px-2 py-1 text-surface-900 dark:text-surface-100"
        >
          {{ student.progress }}%
        </span>
      </div>
      <div class="relative w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        <div
          :class="getProgressColorClass(student.progress)"
          class="h-full rounded-full transition-all duration-300"
          :style="{ width: `${student.progress}%` }"
        />
      </div>
    </div>

    <!-- Stats: Activities, Minutes, Points -->
    <div class="grid grid-cols-3 gap-2 sm:gap-4 pt-2">
      <div class="flex flex-col items-center gap-1 sm:gap-2">
        <div
          class="w-10 h-10 sm:w-12 sm:h-12 bg-info-100 dark:bg-info-900/30 rounded-lg flex items-center justify-center"
        >
          <Icon name="solar:book-line-duotone" class="text-info-600 dark:text-info-400 text-lg sm:text-xl" />
        </div>
        <span class="font-semibold text-base sm:text-lg text-surface-900 dark:text-surface-100">
          {{ student.activitiesCompleted }}
        </span>
        <span class="text-[10px] sm:text-xs text-surface-600 dark:text-surface-400 text-center">
          {{ $t("students.activities") }}
        </span>
      </div>
      <div class="flex flex-col items-center gap-1 sm:gap-2">
        <div
          class="w-10 h-10 sm:w-12 sm:h-12 bg-success-100 dark:bg-success-900/30 rounded-lg flex items-center justify-center"
        >
          <Icon
            name="solar:clock-circle-line-duotone"
            class="text-success-600 dark:text-success-400 text-lg sm:text-xl"
          />
        </div>
        <span class="font-semibold text-base sm:text-lg text-surface-900 dark:text-surface-100">
          {{ student.studyTimeMinutes }}
        </span>
        <span class="text-[10px] sm:text-xs text-surface-600 dark:text-surface-400 text-center">
          {{ $t("students.minutes") }}
        </span>
      </div>
      <div class="flex flex-col items-center gap-1 sm:gap-2">
        <div
          class="w-10 h-10 sm:w-12 sm:h-12 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center"
        >
          <Icon name="solar:star-line-duotone" class="text-primary-600 dark:text-primary-400 text-lg sm:text-xl" />
        </div>
        <span class="font-semibold text-base sm:text-lg text-surface-900 dark:text-surface-100">
          {{ student.score }}
        </span>
        <span class="text-[10px] sm:text-xs text-surface-600 dark:text-surface-400 text-center">
          {{ $t("students.points") }}
        </span>
      </div>
    </div>

    <!-- View Profile Button -->
    <div class="w-full mt-2 rounded-lg bg-gradient-to-r from-primary-500 to-success-500 p-[1px]">
      <button
        class="w-full bg-white dark:bg-surface-900 rounded-lg px-3 sm:px-4 py-2 sm:py-2.5 text-surface-700 dark:text-surface-300 font-medium hover:opacity-90 transition-opacity flex items-center justify-center gap-2 text-sm sm:text-base"
        @click="$emit('view-profile', student.id)"
      >
        <span>{{ $t("students.viewFullProfile") }}</span>
      </button>
    </div>
  </div>
</template>
