<script setup lang="ts">
  import { computed, watch } from "vue";
  import { useI18n } from "vue-i18n";
  import { LqAvatar } from "@lq/ui";
  import { useStudentProfile } from "~/composables/classes/useStudentProfile";
  import { useStudentColors } from "~/composables/students/useStudentColors";

  const props = defineProps<{
    visible: boolean;
  }>();

  const emit = defineEmits<{
    "update:visible": [value: boolean];
  }>();

  const { t } = useI18n();
  const { studentData, closeModal } = useStudentProfile();
  const { getProgressSeverity } = useStudentColors();

  // Mock recent activities - in real app, this would come from API
  const recentActivities = computed(() => {
    if (!studentData.value) return [];
    return [
      {
        id: "1",
        name: "Basic Negotiation Skills...",
        date: "2024-11-28",
        score: 79,
      },
      {
        id: "2",
        name: "Using Second Conditional...",
        date: "2024-11-25",
        score: 79,
      },
      {
        id: "3",
        name: "Talking About Baseball...",
        date: "2024-11-20",
        score: 68,
      },
    ];
  });

  const getInitials = (firstName: string, lastName: string) => {
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
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

  const formatSkillScore = (score?: number) => {
    if (!score && score !== 0) return "-";
    return Math.round(score);
  };

  const formatTime = (minutes: number) => {
    if (minutes < 60) {
      return `${minutes} ${t("classes.students.min")}`;
    }
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    if (remainingMinutes === 0) {
      return `${hours} ${t("classes.students.hour", hours)}`;
    }
    return `${hours} ${t("classes.students.hour", hours)} ${remainingMinutes} ${t("classes.students.min")}`;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("es-ES", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  const _getScoreColorClass = (score: number) => {
    if (score >= 80) {
      return "bg-success-100 dark:bg-success-900/30 text-success-700 dark:text-success-400";
    } else if (score >= 60) {
      return "bg-warning-100 dark:bg-warning-900/30 text-warning-700 dark:text-warning-400";
    } else {
      return "bg-danger-100 dark:bg-danger-900/30 text-danger-700 dark:text-danger-400";
    }
  };

  const handleClose = () => {
    closeModal();
    emit("update:visible", false);
  };

  watch(
    () => props.visible,
    (newValue) => {
      if (!newValue) {
        closeModal();
      }
    },
  );
</script>

<template>
  <Dialog
    :visible="visible"
    modal
    closable
    :draggable="false"
    class="w-full max-w-4xl"
    :pt="{
      root: { class: '!rounded-xl' },
      header: { class: '!border-b-0 !pb-0' },
      content: { class: '!pt-0' },
    }"
    @update:visible="handleClose"
  >
    <template #header>
      <div v-if="studentData" class="flex items-center justify-between w-full">
        <div class="flex items-center gap-4 flex-1">
          <!-- Avatar -->
          <LqAvatar
            :src="studentData.photo || undefined"
            :initials="getInitials(studentData.firstName, studentData.lastName)"
            shape="square"
            class="bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 flex-shrink-0"
            style="width: 64px; height: 64px; font-size: 1.5rem"
          />
          <!-- Student Info -->
          <div class="flex flex-col gap-1 flex-1 min-w-0">
            <h2 class="text-xl font-bold text-surface-900 dark:text-surface-100">
              {{ studentData.firstName }} {{ studentData.lastName }}
            </h2>
            <p class="text-sm text-surface-600 dark:text-surface-400">{{ studentData.email }}</p>
            <div class="flex items-center gap-4 text-xs text-surface-500 dark:text-surface-500">
              <span class="flex items-center gap-1">
                <Icon name="solar:calendar-line-duotone" class="text-base" />
                {{ $t("classes.students.profileModal.enrolled") }}:
                {{ formatDate(studentData.enrolledAt || new Date().toISOString()) }}
              </span>
              <span class="flex items-center gap-1">
                <Icon name="solar:clock-circle-line-duotone" class="text-base" />
                {{ formatTime(studentData.studyTimeMinutes) }} {{ $t("classes.students.profileModal.total") }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </template>

    <div v-if="studentData" class="space-y-6">
      <!-- Metrics Cards -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Progress Card -->
        <div class="bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-xl p-5">
          <div class="flex items-center gap-3 mb-4">
            <div
              class="w-10 h-10 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center flex-shrink-0"
            >
              <Icon name="solar:chart-line-duotone" class="text-primary-600 dark:text-primary-400 text-xl" />
            </div>
            <h4 class="text-sm font-semibold text-surface-600 dark:text-surface-400">
              {{ $t("classes.students.profileModal.progress") }}
            </h4>
          </div>
          <div class="flex items-end gap-2 mb-3">
            <span class="text-4xl font-bold text-surface-900 dark:text-surface-100">
              {{ studentData.activitiesCompleted }}
            </span>
            <span class="text-2xl text-surface-500 dark:text-surface-500 mb-1">
              / {{ studentData.activitiesTotal }}
            </span>
          </div>
          <div class="relative w-full h-2.5 bg-surface-200 dark:bg-surface-700 rounded-full overflow-hidden mb-2">
            <div
              :class="getProgressColorClass(studentData.progress)"
              class="h-full rounded-full transition-all duration-300"
              :style="{ width: `${studentData.progress}%` }"
            />
          </div>
          <p class="text-sm text-surface-600 dark:text-surface-400">
            {{ $t("classes.students.profileModal.assignmentsCompleted") }}
          </p>
        </div>

        <!-- General Score Card -->
        <div class="bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-xl p-5">
          <div class="flex items-center gap-3 mb-4">
            <div
              class="w-10 h-10 bg-success-100 dark:bg-success-900/30 rounded-lg flex items-center justify-center flex-shrink-0"
            >
              <Icon
                name="solar:medal-ribbons-star-line-duotone"
                class="text-success-600 dark:text-success-400 text-xl"
              />
            </div>
            <h4 class="text-sm font-semibold text-surface-600 dark:text-surface-400">
              {{ $t("classes.students.profileModal.generalScore") }}
            </h4>
          </div>
          <div class="flex items-center gap-3 mb-3">
            <span class="text-5xl font-bold text-success-600 dark:text-success-400">B1</span>
            <div class="flex-1">
              <div class="relative w-full h-2.5 bg-surface-200 dark:bg-surface-700 rounded-full overflow-hidden">
                <div class="h-full bg-success-500 rounded-full transition-all duration-300" :style="{ width: '82%' }">
                  <span class="absolute inset-0 flex items-center justify-center text-xs font-semibold text-white">
                    82%
                  </span>
                </div>
              </div>
            </div>
          </div>
          <p class="text-sm text-surface-600 dark:text-surface-400">
            {{ $t("classes.students.profileModal.assignmentsCompleted") }}
          </p>
        </div>
      </div>

      <!-- Skills Breakdown -->
      <div class="space-y-4">
        <h4 class="text-lg font-semibold text-surface-900 dark:text-surface-100">
          {{ $t("classes.students.profileModal.skillsBreakdown") }}
        </h4>
        <div class="grid grid-cols-5 gap-3">
          <!-- Pronunciation -->
          <div
            class="bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-xl p-4 flex flex-col items-center justify-center text-center hover:shadow-md transition-shadow"
          >
            <div
              class="w-12 h-12 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center mb-3"
            >
              <Icon name="solar:microphone-line-duotone" class="text-primary-600 dark:text-primary-400 text-2xl" />
            </div>
            <p class="text-sm text-surface-600 dark:text-surface-400 mb-2">
              {{ $t("classes.students.pronunciation") }}
            </p>
            <p class="text-2xl font-bold text-primary-600 dark:text-primary-400">
              {{ formatSkillScore(studentData.skills?.pronunciation) }}%
            </p>
          </div>

          <!-- Vocabulary -->
          <div
            class="bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-xl p-4 flex flex-col items-center justify-center text-center hover:shadow-md transition-shadow"
          >
            <div class="w-12 h-12 bg-info-100 dark:bg-info-900/30 rounded-lg flex items-center justify-center mb-3">
              <Icon name="solar:book-2-line-duotone" class="text-info-600 dark:text-info-400 text-2xl" />
            </div>
            <p class="text-sm text-surface-600 dark:text-surface-400 mb-2">{{ $t("classes.students.vocabulary") }}</p>
            <p class="text-2xl font-bold text-info-600 dark:text-info-400">
              {{ formatSkillScore(studentData.skills?.vocabulary) }}%
            </p>
          </div>

          <!-- Grammar -->
          <div
            class="bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-xl p-4 flex flex-col items-center justify-center text-center hover:shadow-md transition-shadow"
          >
            <div
              class="w-12 h-12 bg-warning-100 dark:bg-warning-900/30 rounded-lg flex items-center justify-center mb-3"
            >
              <Icon name="solar:document-line-duotone" class="text-warning-600 dark:text-warning-400 text-2xl" />
            </div>
            <p class="text-sm text-surface-600 dark:text-surface-400 mb-2">{{ $t("classes.students.grammar") }}</p>
            <p class="text-2xl font-bold text-warning-600 dark:text-warning-400">
              {{ formatSkillScore(studentData.skills?.grammar) }}%
            </p>
          </div>

          <!-- Fluency -->
          <div
            class="bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-xl p-4 flex flex-col items-center justify-center text-center hover:shadow-md transition-shadow"
          >
            <div
              class="w-12 h-12 bg-success-100 dark:bg-success-900/30 rounded-lg flex items-center justify-center mb-3"
            >
              <Icon name="solar:star-line-duotone" class="text-success-600 dark:text-success-400 text-2xl" />
            </div>
            <p class="text-sm text-surface-600 dark:text-surface-400 mb-2">{{ $t("classes.students.fluency") }}</p>
            <p class="text-2xl font-bold text-success-600 dark:text-success-400">
              {{ formatSkillScore(studentData.skills?.fluency) }}%
            </p>
          </div>

          <!-- Discourse -->
          <div
            class="bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-xl p-4 flex flex-col items-center justify-center text-center hover:shadow-md transition-shadow"
          >
            <div class="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center mb-3">
              <Icon name="solar:document-text-line-duotone" class="text-purple-600 dark:text-purple-400 text-2xl" />
            </div>
            <p class="text-sm text-surface-600 dark:text-surface-400 mb-2">{{ $t("classes.students.discourse") }}</p>
            <p class="text-2xl font-bold text-purple-600 dark:text-purple-400">
              {{ formatSkillScore(studentData.skills?.discourse) }}%
            </p>
          </div>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="space-y-4">
        <h4 class="text-lg font-semibold text-surface-900 dark:text-surface-100">
          {{ $t("classes.students.profileModal.recentActivity") }}
        </h4>
        <div class="space-y-3">
          <div
            v-for="activity in recentActivities"
            :key="activity.id"
            class="flex items-center justify-between p-4 bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-xl hover:shadow-md transition-all"
          >
            <div class="flex-1 min-w-0">
              <p class="font-semibold text-surface-900 dark:text-surface-100 mb-1">{{ activity.name }}</p>
              <p class="text-sm text-surface-500 dark:text-surface-500">{{ formatDate(activity.date) }}</p>
            </div>
            <div class="relative w-14 h-14 flex-shrink-0">
              <!-- Circular progress background -->
              <svg class="w-14 h-14 transform -rotate-90" viewBox="0 0 56 56">
                <circle
                  cx="28"
                  cy="28"
                  r="24"
                  stroke="currentColor"
                  stroke-width="4"
                  fill="none"
                  class="text-surface-200 dark:text-surface-700"
                />
                <circle
                  cx="28"
                  cy="28"
                  r="24"
                  stroke="currentColor"
                  stroke-width="4"
                  fill="none"
                  :stroke-dasharray="`${(activity.score / 100) * 150.8} 150.8`"
                  :class="
                    activity.score >= 80
                      ? 'text-primary-500'
                      : activity.score >= 60
                        ? 'text-warning-500'
                        : 'text-danger-500'
                  "
                  class="transition-all duration-300"
                  stroke-linecap="round"
                />
              </svg>
              <!-- Score text centered -->
              <div class="absolute inset-0 flex items-center justify-center">
                <span class="text-sm font-bold text-surface-900 dark:text-surface-100">{{ activity.score }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Dialog>
</template>
