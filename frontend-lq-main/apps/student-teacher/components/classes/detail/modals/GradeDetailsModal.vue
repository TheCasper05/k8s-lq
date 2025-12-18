<script setup lang="ts">
  import { computed } from "vue";
  import Dialog from "primevue/dialog";
  import Button from "primevue/button";
  import Divider from "primevue/divider";
  import type { AssignmentGrade } from "~/composables/classes/types";

  const props = defineProps<{
    visible: boolean;
    grade?: AssignmentGrade | null;
    assignmentName?: string;
    studentName?: string;
    practiceTime?: string;
    cefrLevel?: string;
  }>();

  const emit = defineEmits<{
    "update:visible": [value: boolean];
    "view-practice": [];
  }>();

  const handleClose = () => {
    emit("update:visible", false);
  };

  const handleViewPractice = () => {
    emit("view-practice");
  };

  const overallScore = computed(() => props.grade?.score || 0);

  const skillsList = computed(() => {
    if (!props.grade?.skills) return [];
    return [
      { name: "Grammar", value: props.grade.skills.grammar || 0 },
      { name: "Pronunciation", value: props.grade.skills.pronunciation || 0 },
      { name: "Vocabulary", value: props.grade.skills.vocabulary || 0 },
      { name: "Fluency", value: props.grade.skills.fluency || 0 },
      { name: "Cohesion", value: props.grade.skills.cohesion || 0 },
    ];
  });

  const getSkillColor = (value: number): string => {
    if (value >= 90) return "text-green-600 dark:text-green-400";
    if (value >= 80) return "text-blue-600 dark:text-blue-400";
    if (value >= 70) return "text-yellow-600 dark:text-yellow-400";
    return "text-orange-600 dark:text-orange-400";
  };
</script>

<template>
  <Dialog
    :visible="visible"
    modal
    :closable="false"
    :draggable="false"
    class="w-full max-w-md"
    :pt="{
      root: { class: '!rounded-xl' },
      header: { class: '!p-0 !border-0' },
      content: { class: '!p-0' },
    }"
    @update:visible="handleClose"
  >
    <template #header>
      <div class="flex items-start justify-between p-6 pb-4 w-full">
        <div class="flex flex-col flex-1 min-w-0">
          <h2 class="text-xl font-bold text-surface-900 dark:text-surface-100 truncate">
            {{ assignmentName || "Assignment" }}
          </h2>
          <p class="text-sm text-surface-600 dark:text-surface-400 mt-1">
            {{ studentName || "Student" }}
          </p>
        </div>
        <button
          class="w-8 h-8 rounded-full bg-surface-100 dark:bg-surface-800 flex items-center justify-center hover:bg-surface-200 dark:hover:bg-surface-700 transition-colors flex-shrink-0 ml-4"
          @click="handleClose"
        >
          <Icon name="solar:close-circle-line-duotone" class="text-xl text-surface-600 dark:text-surface-400" />
        </button>
      </div>
    </template>

    <div class="px-6 pb-6">
      <Divider class="my-0 mb-4" />

      <!-- Overall Score -->
      <div class="text-center mb-6">
        <p class="text-sm text-surface-600 dark:text-surface-400 mb-2">
          {{ $t("classes.assignments.gradeDetails.overallScore") }}
        </p>
        <p class="text-5xl font-bold text-yellow-500 dark:text-yellow-400">{{ overallScore }}%</p>
      </div>

      <!-- CEFR Level and Practice Time -->
      <div class="grid grid-cols-2 gap-4 mb-6">
        <div class="flex flex-col items-center p-4 bg-surface-50 dark:bg-surface-800 rounded-lg">
          <div class="flex items-center gap-2 mb-2">
            <Icon name="solar:medal-star-line-duotone" class="text-xl text-primary-600 dark:text-primary-400" />
            <span class="text-xs text-surface-600 dark:text-surface-400 font-medium">
              {{ $t("classes.assignments.gradeDetails.cefrLevel") }}
            </span>
          </div>
          <span class="text-2xl font-bold text-primary-600 dark:text-primary-400">{{ cefrLevel || "B1" }}</span>
        </div>

        <div class="flex flex-col items-center p-4 bg-surface-50 dark:bg-surface-800 rounded-lg">
          <div class="flex items-center gap-2 mb-2">
            <Icon name="solar:clock-circle-line-duotone" class="text-xl text-surface-600 dark:text-surface-400" />
            <span class="text-xs text-surface-600 dark:text-surface-400 font-medium">
              {{ $t("classes.assignments.gradeDetails.practiceTime") }}
            </span>
          </div>
          <span class="text-2xl font-bold text-surface-900 dark:text-surface-100">{{ practiceTime || "2h 7m" }}</span>
        </div>
      </div>

      <!-- Skills Evaluated -->
      <div class="mb-6">
        <h3 class="text-sm font-semibold text-surface-900 dark:text-surface-100 mb-3">
          {{ $t("classes.assignments.gradeDetails.skillsEvaluated") }}
        </h3>
        <div class="space-y-2">
          <div v-for="skill in skillsList" :key="skill.name" class="flex items-center justify-between">
            <span class="text-sm text-surface-700 dark:text-surface-300">{{ skill.name }}:</span>
            <span :class="getSkillColor(skill.value)" class="text-sm font-bold">{{ skill.value }}%</span>
          </div>
        </div>
      </div>

      <!-- View Practice Button -->
      <Button
        :label="$t('classes.assignments.gradeDetails.viewPractice')"
        class="w-full bg-surface-900 dark:bg-surface-100 text-white dark:text-surface-900 border-0 flex items-center justify-center gap-2"
        @click="handleViewPractice"
      >
        <template #icon>
          <Icon name="solar:eye-line-duotone" class="text-lg" />
        </template>
      </Button>
    </div>
  </Dialog>
</template>
