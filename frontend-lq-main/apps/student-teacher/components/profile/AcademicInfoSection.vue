<script setup lang="ts">
  export interface AcademicInfoSectionProps {
    user: {
      id: string;
      grade: string;
      classrooms: string[];
    };
  }

  defineProps<AcademicInfoSectionProps>();
</script>

<template>
  <div
    class="bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 p-6 shadow-sm"
  >
    <div class="flex items-center gap-3 mb-6">
      <div
        class="w-10 h-10 rounded-full bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center text-purple-600 dark:text-purple-400"
      >
        <Icon name="solar:diploma-bold-duotone" class="text-xl" />
      </div>
      <h2 class="text-xl font-bold text-surface-900 dark:text-surface-100">{{ $t("profile.academicInfo") }}</h2>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Student ID Card -->
      <div class="bg-purple-50 dark:bg-purple-900/20 border border-purple-100 dark:border-purple-800 rounded-xl p-4">
        <p class="text-xs font-bold text-purple-600 dark:text-purple-400 mb-1">{{ $t("profile.studentId") }}</p>
        <p class="text-lg font-bold text-surface-900 dark:text-surface-100">{{ user.id }}</p>
      </div>

      <!-- Grade Card -->
      <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-800 rounded-xl p-4">
        <p class="text-xs font-bold text-blue-600 dark:text-blue-400 mb-1">{{ $t("profile.grade") }}</p>
        <p class="text-lg font-bold text-surface-900 dark:text-surface-100">{{ user.grade }}</p>
      </div>

      <!-- Classrooms Card (Full Width) -->
      <div
        class="md:col-span-2 bg-green-50 dark:bg-green-900/20 border border-green-100 dark:border-green-800 rounded-xl p-4"
      >
        <p class="text-xs font-bold text-green-600 dark:text-green-400 mb-2">{{ $t("profile.classroomAssigned") }}</p>
        <div class="flex flex-wrap gap-4">
          <span
            v-for="classroom in user.classrooms"
            :key="classroom"
            class="text-base font-bold text-surface-900 dark:text-surface-100"
          >
            {{ classroom }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
