<script setup lang="ts">
  import { computed, ref } from "vue";
  import type { Student } from "~/composables/students/types";
  import { LqDataTable, LqSearchInput, type LqDataTableColumn, LqAvatar } from "@lq/ui";
  import Button from "primevue/button";
  import { useStudentColors } from "~/composables/students/useStudentColors";

  const props = defineProps<{
    students: Student[];
  }>();

  const emit = defineEmits<{
    "add-student": [];
    "view-profile": [studentId: string];
  }>();

  const searchQuery = ref("");
  const { getProgressSeverity } = useStudentColors();

  const filteredStudents = computed(() => {
    if (!searchQuery.value) {
      return props.students;
    }
    const query = searchQuery.value.toLowerCase();
    return props.students.filter(
      (student) =>
        student.firstName.toLowerCase().includes(query) ||
        student.lastName.toLowerCase().includes(query) ||
        student.email.toLowerCase().includes(query),
    );
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

  const getSkillColorClass = (score: number) => {
    if (score >= 80) {
      return "text-success-600 dark:text-success-400";
    } else if (score >= 60) {
      return "text-warning-600 dark:text-warning-400";
    } else {
      return "text-danger-600 dark:text-danger-400";
    }
  };

  const getScoreColorClass = (score: number) => {
    if (score >= 80) {
      return "text-success-600 dark:text-success-400";
    } else if (score >= 60) {
      return "text-warning-600 dark:text-warning-400";
    } else {
      return "text-danger-600 dark:text-danger-400";
    }
  };

  const formatSkillScore = (score?: number) => {
    if (!score && score !== 0) return "-";
    return `${score.toFixed(2)}%`;
  };

  const { t } = useI18n();

  const columns = computed<LqDataTableColumn[]>(() => [
    { field: "student", header: t("classes.students.student"), class: "min-w-[180px]" },
    { field: "progress", header: t("classes.students.progress"), class: "min-w-[110px]" },
    { field: "time", header: t("classes.students.totalTime"), class: "min-w-[110px]" },
    { field: "score", header: t("classes.students.generalScore"), class: "min-w-[100px]" },
    { field: "pronunciation", header: t("classes.students.pronunciation"), class: "min-w-[110px]" },
    { field: "vocabulary", header: t("classes.students.vocabulary"), class: "min-w-[110px]" },
    { field: "grammar", header: t("classes.students.grammar"), class: "min-w-[110px]" },
    { field: "fluency", header: t("classes.students.fluency"), class: "min-w-[110px]" },
    { field: "discourse", header: t("classes.students.discourse"), class: "min-w-[110px]" },
  ]);

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

  const handleAddStudent = () => {
    emit("add-student");
  };

  const handleRowClick = (event: { data?: { id?: string } }) => {
    if (event.data?.id) {
      emit("view-profile", event.data.id);
    }
  };
</script>

<template>
  <div class="w-full space-y-4">
    <!-- Header Section -->
    <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3 md:gap-4">
      <h2 class="text-xl md:text-2xl font-bold text-surface-900 dark:text-surface-100">
        {{ $t("classes.students.title") }}
      </h2>
      <div class="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 md:gap-4 flex-1 md:flex-initial">
        <!-- Search Bar -->
        <LqSearchInput
          v-model="searchQuery"
          :placeholder="$t('classes.students.searchPlaceholder')"
          container-class="w-full sm:w-64"
          width="w-full"
          icon="solar:magnifer-line-duotone"
        />
        <!-- Add Student Button -->
        <Button
          :label="$t('classes.students.addStudent')"
          class="bg-primary-600 text-white border-0 w-full sm:w-auto h-12"
          @click="handleAddStudent"
        >
          <template #icon>
            <Icon name="lucide:plus" />
          </template>
        </Button>
      </div>
    </div>

    <!-- Students Table -->
    <LqDataTable
      :data="filteredStudents"
      :columns="columns"
      :loading="false"
      :empty-message="$t('common.noStudentsFound')"
    >
      <!-- Student Column -->
      <template #cell-student="{ data }">
        <div class="flex items-center gap-3 py-2 cursor-pointer" @click="handleRowClick({ data })">
          <LqAvatar
            :src="data.photo || undefined"
            :initials="getInitials(data.firstName, data.lastName)"
            shape="square"
            size="large"
            class="!size-10 !rounded-full bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 !text-base font-bold"
          />
          <div class="flex flex-col">
            <span class="font-semibold text-surface-900 dark:text-surface-100">
              {{ data.firstName }} {{ data.lastName }}
            </span>
            <span class="text-sm text-surface-600 dark:text-surface-400">{{ data.level }}</span>
          </div>
        </div>
      </template>

      <!-- Progress Column -->
      <template #cell-progress="{ data }">
        <div class="flex flex-col gap-2">
          <div class="relative w-full h-2 bg-surface-200 dark:bg-surface-700 rounded-full overflow-hidden">
            <div
              :class="getProgressColorClass(data.progress)"
              class="h-full rounded-full transition-all duration-300"
              :style="{ width: `${data.progress}%` }"
            />
          </div>
          <span class="text-sm font-medium text-surface-700 dark:text-surface-300">
            {{ data.activitiesCompleted }}/{{ data.activitiesTotal }}
          </span>
        </div>
      </template>

      <!-- Total Time Column -->
      <template #cell-time="{ data }">
        <div class="flex items-center gap-2">
          <Icon name="solar:clock-circle-line-duotone" class="text-surface-600 dark:text-surface-400" />
          <span class="text-sm text-surface-700 dark:text-surface-300">
            {{ formatTime(data.studyTimeMinutes) }}
          </span>
        </div>
      </template>

      <!-- General Score Column -->
      <template #cell-score="{ data }">
        <div v-if="data.score && data.score > 0" class="flex items-center justify-center">
          <div class="relative w-12 h-12">
            <svg class="transform -rotate-90 w-12 h-12">
              <circle
                cx="24"
                cy="24"
                r="20"
                fill="none"
                stroke="currentColor"
                stroke-width="4"
                class="text-surface-200 dark:text-surface-700"
              />
              <circle
                cx="24"
                cy="24"
                r="20"
                fill="none"
                stroke="currentColor"
                stroke-width="4"
                :class="getScoreColorClass(data.score)"
                :stroke-dasharray="125.66"
                :stroke-dashoffset="125.66 * (1 - data.score / 100)"
                class="transition-all duration-300"
                stroke-linecap="round"
              />
            </svg>
            <div class="absolute inset-0 flex items-center justify-center">
              <span class="text-sm font-bold text-surface-900 dark:text-surface-100">{{ data.score }}</span>
            </div>
          </div>
        </div>
        <div v-else class="flex items-center justify-center">
          <span class="text-sm text-surface-500 dark:text-surface-500">
            {{ $t("classes.students.noScoreYet") }}
          </span>
        </div>
      </template>

      <!-- Pronunciation Column -->
      <template #cell-pronunciation="{ data }">
        <div class="flex items-center gap-2">
          <Icon name="solar:microphone-2-line-duotone" class="text-surface-600 dark:text-surface-400 text-lg" />
          <span :class="getSkillColorClass(data.skills?.pronunciation || 0)" class="text-sm font-medium">
            {{ formatSkillScore(data.skills?.pronunciation) }}
          </span>
        </div>
      </template>

      <!-- Vocabulary Column -->
      <template #cell-vocabulary="{ data }">
        <div class="flex items-center gap-2">
          <Icon name="solar:book-2-line-duotone" class="text-surface-600 dark:text-surface-400 text-lg" />
          <span :class="getSkillColorClass(data.skills?.vocabulary || 0)" class="text-sm font-medium">
            {{ formatSkillScore(data.skills?.vocabulary) }}
          </span>
        </div>
      </template>

      <!-- Grammar Column -->
      <template #cell-grammar="{ data }">
        <div class="flex items-center gap-2">
          <Icon name="solar:document-text-line-duotone" class="text-surface-600 dark:text-surface-400 text-lg" />
          <span :class="getSkillColorClass(data.skills?.grammar || 0)" class="text-sm font-medium">
            {{ formatSkillScore(data.skills?.grammar) }}
          </span>
        </div>
      </template>

      <!-- Fluency Column -->
      <template #cell-fluency="{ data }">
        <div class="flex items-center gap-2">
          <Icon name="solar:chat-round-line-duotone" class="text-surface-600 dark:text-surface-400 text-lg" />
          <span :class="getSkillColorClass(data.skills?.fluency || 0)" class="text-sm font-medium">
            {{ formatSkillScore(data.skills?.fluency) }}
          </span>
        </div>
      </template>

      <!-- Discourse Column -->
      <template #cell-discourse="{ data }">
        <div class="flex items-center gap-2">
          <Icon name="solar:document-text-line-duotone" class="text-surface-600 dark:text-surface-400 text-lg" />
          <span :class="getSkillColorClass(data.skills?.discourse || 0)" class="text-sm font-medium">
            {{ formatSkillScore(data.skills?.discourse) }}
          </span>
        </div>
      </template>
    </LqDataTable>
  </div>
</template>
