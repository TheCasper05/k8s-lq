<script setup lang="ts">
  import { computed, ref } from "vue";
  import { LqDataTable, type LqDataTableColumn } from "@lq/ui";
  import Button from "primevue/button";
  import type { Assignment, AssignmentType } from "~/composables/classes/types";

  const props = defineProps<{
    assignments: Assignment[];
  }>();

  const emit = defineEmits<{
    "view-details": [assignmentId: string];
    "edit": [assignmentId: string];
  }>();

  const expandedCourses = ref<Set<string>>(new Set());

  const toggleCourse = (courseId: string) => {
    if (expandedCourses.value.has(courseId)) {
      expandedCourses.value.delete(courseId);
    } else {
      expandedCourses.value.add(courseId);
    }
  };

  const handleViewDetails = (assignmentId: string) => {
    emit("view-details", assignmentId);
  };

  const handleEdit = (assignmentId: string) => {
    emit("edit", assignmentId);
  };

  const { t } = useI18n();

  // Define columns
  const columns = computed<LqDataTableColumn[]>(() => [
    { field: "name", header: t("classes.assignments.list.name"), class: "min-w-[200px]" },
    { field: "type", header: t("classes.assignments.list.type"), class: "min-w-[120px]" },
    { field: "assignedStudents", header: t("classes.assignments.list.assignedStudents"), class: "min-w-[180px]" },
    { field: "date", header: t("classes.assignments.list.date"), class: "min-w-[110px]" },
    { field: "actions", header: t("classes.assignments.list.actions"), class: "min-w-[100px]" },
  ]);

  // Flatten data with sub-assignments
  const tableData = computed<Record<string, unknown>[]>(() => {
    const flattened: Record<string, unknown>[] = [];

    props.assignments.forEach((assignment: Assignment) => {
      flattened.push({
        ...assignment,
        isSubAssignment: false,
        isExpanded: expandedCourses.value.has(assignment.id),
      });

      // Add sub-assignments if expanded
      if (assignment.isCourse && expandedCourses.value.has(assignment.id) && assignment.subAssignments) {
        assignment.subAssignments.forEach((subAssignment: Assignment) => {
          flattened.push({
            ...subAssignment,
            isSubAssignment: true,
          });
        });
      }
    });

    return flattened;
  });

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
      activity: "bg-purple-100 text-purple-700 dark:bg-purple-500/20 dark:text-purple-300",
      course: "bg-orange-100 text-orange-700 dark:bg-orange-500/20 dark:text-orange-300",
      vocabulary: "bg-teal-100 text-teal-700 dark:bg-teal-500/20 dark:text-teal-300",
      speaking: "bg-orange-100 text-orange-700 dark:bg-orange-500/20 dark:text-orange-300",
      writing: "bg-purple-100 text-purple-700 dark:bg-purple-500/20 dark:text-purple-300",
      reading: "bg-cyan-100 text-cyan-700 dark:bg-cyan-500/20 dark:text-cyan-300",
      listening: "bg-violet-100 text-violet-700 dark:bg-violet-500/20 dark:text-violet-300",
    };
    return classes[type] || "bg-surface-100 text-surface-600 dark:bg-surface-500/20 dark:text-surface-400";
  };

  const getSubAssignmentBorderClass = (type: AssignmentType): string => {
    const classes: Record<AssignmentType, string> = {
      activity: "bg-purple-500",
      course: "bg-orange-500",
      vocabulary: "bg-teal-500",
      speaking: "bg-orange-500",
      writing: "bg-purple-500",
      reading: "bg-cyan-500",
      listening: "bg-violet-500",
    };
    return classes[type] || "bg-surface-300";
  };

  const getProgressPercentage = (data: Record<string, unknown>): number => {
    const completed = (data.completedStudents as number) || 0;
    const total = (data.assignedStudents as number) || 0;
    if (total === 0) return 0;
    return Math.round((completed / total) * 100);
  };
</script>

<template>
  <LqDataTable
    :data="tableData"
    :columns="columns"
    :loading="false"
    :empty-message="$t('classes.assignments.list.noAssignments')"
  >
    <!-- Name Column -->
    <template #cell-name="{ data }">
      <div class="flex items-center gap-2 min-w-0">
        <!-- Sub-assignment border (centered) -->
        <div
          v-if="data.isSubAssignment"
          :class="['w-1 h-8 rounded-full flex-shrink-0 ml-7', getSubAssignmentBorderClass(data.type)]"
        />
        <div v-else class="w-1 flex-shrink-0" />

        <!-- Chevron button or spacer -->
        <button
          v-if="data.isCourse && !data.isSubAssignment"
          type="button"
          class="flex items-center justify-center w-5 h-5 rounded hover:bg-surface-100 dark:hover:bg-surface-700 transition-colors flex-shrink-0"
          @click="toggleCourse(data.id)"
        >
          <Icon
            :name="data.isExpanded ? 'lucide:chevron-down' : 'lucide:chevron-right'"
            class="text-surface-600 dark:text-surface-400 text-base"
          />
        </button>
        <div v-else-if="!data.isSubAssignment" class="w-5 h-5 flex-shrink-0" />

        <div class="flex flex-col min-w-0">
          <span class="font-medium text-surface-900 dark:text-surface-100 truncate">{{ data.name }}</span>
          <span v-if="data.level" class="text-xs text-surface-500 dark:text-surface-400">Level: {{ data.level }}</span>
        </div>
      </div>
    </template>

    <!-- Type Column -->
    <template #cell-type="{ data }">
      <span
        :class="getTypeBadgeClass(data.type)"
        class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold"
      >
        <Icon :name="getTypeIcon(data.type)" class="text-sm" />
        {{ getTypeLabel(data.type) }}
      </span>
    </template>

    <!-- Assigned Students Column -->
    <template #cell-assignedStudents="{ data }">
      <div class="flex items-center gap-3 min-w-0">
        <!-- Progress Bar -->
        <div class="flex-1 min-w-0">
          <div class="w-full h-1.5 bg-surface-200 dark:bg-surface-700 rounded-full overflow-hidden">
            <div
              :style="{ width: `${getProgressPercentage(data)}%` }"
              class="h-full bg-warning-500 dark:bg-warning-400 rounded-full transition-all"
            />
          </div>
        </div>
        <!-- Count -->
        <div class="flex items-center gap-1 text-xs text-surface-600 dark:text-surface-400 flex-shrink-0">
          <Icon name="solar:clock-circle-line-duotone" class="text-sm" />
          <span class="font-medium">{{ data.completedStudents || 0 }}/{{ data.assignedStudents || 0 }}</span>
        </div>
      </div>
    </template>

    <!-- Date Column -->
    <template #cell-date="{ data }">
      <span class="text-surface-700 dark:text-surface-300">{{ formatDate(data.dueDate) }}</span>
    </template>

    <!-- Actions Column -->
    <template #cell-actions="{ data }">
      <div class="flex items-center gap-2">
        <Button text rounded severity="secondary" class="!w-8 !h-8" @click="handleViewDetails(data.id)">
          <template #icon>
            <Icon name="solar:eye-linear" />
          </template>
        </Button>
        <Button text rounded severity="secondary" class="!w-8 !h-8" @click="handleEdit(data.id)">
          <template #icon>
            <Icon name="solar:pen-new-square-linear" />
          </template>
        </Button>
      </div>
    </template>
  </LqDataTable>
</template>
