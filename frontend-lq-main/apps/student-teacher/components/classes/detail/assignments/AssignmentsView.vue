<script setup lang="ts">
  import Button from "primevue/button";
  import type { Assignment } from "~/composables/classes/types";
  import AssignmentsList from "./AssignmentsList.vue";

  defineProps<{
    assignments: Assignment[];
  }>();

  defineEmits<{
    "add-activity": [];
    "view-details": [assignmentId: string];
    "edit": [assignmentId: string];
  }>();

  const handleDownloadExcel = () => {
    // TODO: Implement Excel download
    // Download Excel
  };
</script>

<template>
  <div class="w-full space-y-4 md:space-y-6">
    <!-- Header Section -->
    <div class="flex flex-col md:flex-row md:items-center md:justify-end gap-3 md:gap-4">
      <!-- Action Buttons -->
      <div
        class="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 sm:gap-3 flex-shrink-0 w-full md:w-auto"
      >
        <Button
          label="Download Excel"
          severity="success"
          size="small"
          class="whitespace-nowrap w-full sm:w-auto"
          @click="handleDownloadExcel"
        >
          <template #icon>
            <Icon name="solar:download-line-duotone" />
          </template>
        </Button>
        <Button
          label="Add Activity"
          class="bg-surface-900 dark:bg-surface-100 text-white dark:text-surface-900 border-0 whitespace-nowrap w-full sm:w-auto"
          size="small"
          @click="$emit('add-activity')"
        >
          <template #icon>
            <Icon name="solar:document-add-line-duotone" />
          </template>
        </Button>
      </div>
    </div>

    <!-- Content Section -->
    <div class="w-full">
      <AssignmentsList
        :assignments="assignments"
        @view-details="(id) => $emit('view-details', id)"
        @edit="(id) => $emit('edit', id)"
      />
    </div>
  </div>
</template>
