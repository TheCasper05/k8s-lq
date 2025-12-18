<script setup lang="ts">
  import Button from "primevue/button";
  import type { Assignment, AssignmentType } from "~/composables/classes/types";

  const props = defineProps<{
    assignment: Assignment;
    isSubAssignment?: boolean;
    isExpanded?: boolean;
  }>();

  const emit = defineEmits<{
    "view-details": [assignmentId: string];
    "edit": [assignmentId: string];
    "toggle-expand": [];
  }>();

  const formatDate = (date: string | null | undefined): string => {
    if (!date) return "-";
    try {
      const dateObj = new Date(date);
      const day = String(dateObj.getDate()).padStart(2, "0");
      const month = String(dateObj.getMonth() + 1).padStart(2, "0");
      const year = dateObj.getFullYear();
      return `${day}/${month}/${year}`;
    } catch {
      return "-";
    }
  };

  const getTypeIcon = (type: AssignmentType): string => {
    const icons: Record<AssignmentType, string> = {
      activity: "solar:clock-circle-line-duotone",
      course: "solar:document-line-duotone",
      vocabulary: "solar:book-2-line-duotone",
      speaking: "solar:microphone-line-duotone",
      writing: "solar:pen-new-square-line-duotone",
      reading: "solar:book-line-duotone",
      listening: "solar:headphones-round-sound-line-duotone",
    };
    return icons[type] || "solar:document-line-duotone";
  };

  const getTypeLabel = (type: AssignmentType): string => {
    const labels: Record<AssignmentType, string> = {
      activity: "Activity",
      course: "Course",
      vocabulary: "Vocabulary",
      speaking: "Speaking",
      writing: "Writing",
      reading: "Reading",
      listening: "Listening",
    };
    return labels[type] || type;
  };

  const getTypeBadgeClass = (type: AssignmentType): string => {
    const classes: Record<AssignmentType, string> = {
      activity: "bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400",
      course: "bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400",
      vocabulary: "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400",
      speaking: "bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400",
      writing: "bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400",
      reading: "bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400",
      listening: "bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400",
    };
    return classes[type] || "bg-surface-100 dark:bg-surface-800 text-surface-700 dark:text-surface-300";
  };

  const getProgressColorClass = (progress: number): string => {
    if (progress === 0) {
      return "bg-surface-200 dark:bg-surface-700";
    } else if (progress < 100) {
      return "bg-warning-500";
    } else {
      return "bg-success-500";
    }
  };

  const handleEdit = () => {
    emit("edit", props.assignment.id);
  };

  const handleCopy = () => {
    // TODO: Implement copy functionality
    emit("edit", props.assignment.id);
  };
</script>

<template>
  <div
    :class="[
      'grid grid-cols-12 gap-4 px-4 py-4 border-b border-surface-200 dark:border-surface-700',
      isSubAssignment
        ? 'pl-8 border-l-2 border-primary-200 dark:border-primary-800 bg-surface-50 dark:bg-surface-800/50'
        : '',
      'hover:bg-surface-50 dark:hover:bg-surface-800 transition-colors',
    ]"
    style="min-width: 850px"
  >
    <!-- Name Column -->
    <div class="col-span-4 flex items-center gap-2 min-w-0" style="min-width: 200px">
      <button
        v-if="assignment.isCourse && !isSubAssignment"
        type="button"
        class="flex items-center justify-center p-0.5 hover:bg-surface-200 dark:hover:bg-surface-700 rounded transition-colors flex-shrink-0"
        @click="$emit('toggle-expand')"
      >
        <Icon
          :name="isExpanded ? 'solar:alt-arrow-down-line-duotone' : 'solar:alt-arrow-right-line-duotone'"
          class="text-surface-500 dark:text-surface-400 text-sm"
        />
      </button>
      <span class="font-medium text-surface-900 dark:text-surface-100 truncate">{{ assignment.name }}</span>
    </div>

    <!-- Type Column -->
    <div class="col-span-2 flex items-center" style="min-width: 120px">
      <span
        :class="getTypeBadgeClass(assignment.type)"
        class="inline-flex items-center gap-1.5 px-2 py-1 rounded-lg text-xs font-semibold whitespace-nowrap"
      >
        <Icon :name="getTypeIcon(assignment.type)" class="text-sm" />
        {{ getTypeLabel(assignment.type) }}
      </span>
    </div>

    <!-- Assigned Students Column -->
    <div class="col-span-2 flex items-center gap-2" style="min-width: 180px">
      <div class="relative w-20 h-2 bg-surface-200 dark:bg-surface-700 rounded-full overflow-hidden flex-shrink-0">
        <div
          :class="getProgressColorClass(assignment.progress)"
          class="h-full rounded-full transition-all duration-300"
          :style="{ width: `${assignment.progress}%` }"
        />
      </div>
      <div class="flex items-center gap-1.5 text-sm flex-shrink-0 min-w-0">
        <Icon
          name="solar:users-group-two-rounded-line-duotone"
          class="text-surface-500 dark:text-surface-400 text-sm flex-shrink-0"
        />
        <span class="text-surface-700 dark:text-surface-300 whitespace-nowrap">
          {{ assignment.assignedStudents }}/{{ assignment.totalStudents }}
        </span>
      </div>
    </div>

    <!-- Date Column -->
    <div class="col-span-2 flex items-center" style="min-width: 110px">
      <span class="text-sm text-surface-600 dark:text-surface-400 whitespace-nowrap">
        {{ formatDate(assignment.dueDate) }}
      </span>
    </div>

    <!-- Actions Column -->
    <div class="col-span-2 flex items-center gap-2" style="min-width: 100px">
      <Button
        variant="text"
        size="small"
        class="p-1 text-surface-600 dark:text-surface-400 hover:text-primary-600 dark:hover:text-primary-400"
        @click="handleEdit"
      >
        <template #icon>
          <Icon name="solar:pen-line-duotone" />
        </template>
      </Button>
      <Button
        variant="text"
        size="small"
        class="p-1 text-surface-600 dark:text-surface-400 hover:text-primary-600 dark:hover:text-primary-400"
        @click="handleCopy"
      >
        <template #icon>
          <Icon name="solar:copy-line-duotone" />
        </template>
      </Button>
    </div>
  </div>
</template>
