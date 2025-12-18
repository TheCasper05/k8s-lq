<script setup lang="ts">
  defineEmits<{
    "add-student": [];
  }>();
</script>

<template>
  <div
    class="bg-primary-600 dark:bg-primary-700 rounded-xl p-4 sm:p-6 md:p-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 sm:gap-4"
  >
    <div class="flex items-center gap-3 sm:gap-4">
      <div class="bg-white/10 rounded-lg p-2 sm:p-3">
        <Icon name="solar:users-group-rounded-line-duotone" class="text-white text-xl sm:text-2xl" />
      </div>
      <div class="flex flex-col">
        <h1 class="text-xl sm:text-2xl md:text-3xl font-bold text-white">
          {{ $t("students.title") }}
        </h1>
        <p class="text-primary-100 dark:text-primary-200 text-xs sm:text-sm md:text-base mt-1">
          {{ $t("students.subtitle") }}
        </p>
      </div>
    </div>
    <Button
      :label="$t('students.addStudent')"
      class="bg-white text-primary-600 hover:bg-primary-50 border-0 font-semibold w-full sm:w-auto text-sm sm:text-base"
      @click="$emit('add-student')"
    >
      <template #icon>
        <Icon name="solar:add-circle-line-duotone" />
      </template>
    </Button>
  </div>
</template>
