<script setup lang="ts">
  import type { Student } from "~/composables/students/types";
  import StudentCard from "./StudentCard.vue";

  defineProps<{
    students: Student[];
  }>();

  const emit = defineEmits<{
    "view-profile": [studentId: string];
  }>();

  const handleViewProfile = (studentId: string) => {
    emit("view-profile", studentId);
  };
</script>

<template>
  <div v-if="students.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <StudentCard v-for="student in students" :key="student.id" :student="student" @view-profile="handleViewProfile" />
  </div>
  <div v-else class="flex flex-col items-center justify-center py-12 text-center">
    <Icon name="solar:users-group-rounded-line-duotone" class="text-6xl text-surface-300 dark:text-surface-700 mb-4" />
    <p class="text-lg font-semibold text-surface-600 dark:text-surface-400 mb-2">
      {{ $t("common.noStudentsFound") }}
    </p>
    <p class="text-sm text-surface-500 dark:text-surface-500">
      {{ $t("students.noStudentsDescription") }}
    </p>
  </div>
</template>
