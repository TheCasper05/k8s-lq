<script setup lang="ts">
  import { computed, nextTick, ref } from "vue";
  import { LqDataTable, type LqDataTableColumn, LqAvatar } from "@lq/ui";
  import Button from "primevue/button";
  import Popover from "primevue/popover";
  import type { Assignment, AssignmentGrade } from "~/composables/classes/types";
  import type { Student } from "~/composables/students/types";

  const props = defineProps<{
    assignments: Assignment[];
    students: Student[];
    grades: AssignmentGrade[];
  }>();

  const emit = defineEmits<{
    "cell-click": [data: { assignmentId: string; studentId: string }];
    "export-gradebook": [];
    "add-activity": [];
    "view-practice": [];
  }>();

  const popoverRef = ref();
  const selectedGrade = ref<AssignmentGrade | null>(null);
  const selectedAssignmentName = ref<string>("");
  const selectedStudentName = ref<string>("");

  // Create a map of grades for quick lookup
  const gradesMap = computed(() => {
    const map: Record<string, Record<string, AssignmentGrade>> = {};
    props.grades.forEach((grade) => {
      if (!map[grade.studentId]) {
        map[grade.studentId] = {};
      }
      map[grade.studentId][grade.assignmentId] = grade;
    });
    return map;
  });

  // Transform data for table
  const tableData = computed(() => {
    return props.students.map((student) => {
      const studentGrades: Record<string, AssignmentGrade> = {};
      props.assignments.forEach((assignment) => {
        studentGrades[assignment.id] = gradesMap.value[student.id]?.[assignment.id] || {
          assignmentId: assignment.id,
          studentId: student.id,
          status: "pending",
        };
      });

      // Calculate average for this student
      const completedGrades = Object.values(studentGrades).filter(
        (grade) =>
          (grade.status === "completed" || grade.status === "graded") &&
          grade.score !== null &&
          grade.score !== undefined,
      );

      let average = 0;
      let accumulated = 0;
      let total = 0;

      if (completedGrades.length > 0) {
        accumulated = completedGrades.reduce((sum, grade) => sum + (grade.score || 0), 0);
        average = Math.round(accumulated / completedGrades.length);
        total = completedGrades.length * 100;
      }

      return {
        studentId: student.id,
        student,
        grades: studentGrades,
        average,
        accumulated,
        total,
      };
    });
  });

  const getInitials = (firstName: string, lastName: string) => {
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
  };

  const { t } = useI18n();

  // Generate dynamic columns
  const columns = computed<LqDataTableColumn[]>(() => {
    const cols: LqDataTableColumn[] = [
      { field: "student", header: t("classes.assignments.gradebook.student"), class: "min-w-[160px]" },
    ];

    // Add assignment columns
    props.assignments.forEach((assignment) => {
      cols.push({
        field: `assignment_${assignment.id}`,
        header: assignment.name,
        class: "min-w-[120px] text-center",
      });
    });

    // Add average column
    cols.push({
      field: "average",
      header: t("classes.assignments.gradebook.average"),
      class: "min-w-[120px] text-center",
    });

    return cols;
  });

  const getLevelBadgeClass = (level: string): string => {
    const levelColors: Record<string, string> = {
      A1: "bg-danger-100 dark:bg-danger-900/30 text-danger-700 dark:text-danger-400",
      A2: "bg-warning-100 dark:bg-warning-900/30 text-warning-700 dark:text-warning-400",
      B1: "bg-info-100 dark:bg-info-900/30 text-info-700 dark:text-info-400",
      B2: "bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400",
      C1: "bg-success-100 dark:bg-success-900/30 text-success-700 dark:text-success-400",
      C2: "bg-success-100 dark:bg-success-900/30 text-success-700 dark:text-success-400",
    };
    return levelColors[level] || "bg-surface-100 dark:bg-surface-800 text-surface-700 dark:text-surface-300";
  };

  const getScoreColorClass = (score: number): string => {
    if (score >= 90) {
      return "text-success-600 dark:text-success-400";
    }
    return "text-primary-600 dark:text-primary-400";
  };

  const getSkillColor = (value: number): string => {
    if (value >= 90) return "text-green-600 dark:text-green-400";
    if (value >= 80) return "text-blue-600 dark:text-blue-400";
    if (value >= 70) return "text-yellow-600 dark:text-yellow-400";
    return "text-orange-600 dark:text-orange-400";
  };

  const skillsList = computed(() => {
    if (!selectedGrade.value?.skills) return [];
    return [
      { name: "Grammar", value: selectedGrade.value.skills.grammar || 0 },
      { name: "Pronunciation", value: selectedGrade.value.skills.pronunciation || 0 },
      { name: "Vocabulary", value: selectedGrade.value.skills.vocabulary || 0 },
      { name: "Fluency", value: selectedGrade.value.skills.fluency || 0 },
      { name: "Cohesion", value: selectedGrade.value.skills.cohesion || 0 },
    ];
  });

  const handleCellClick = (event: MouseEvent, assignmentId: string, studentId: string) => {
    // Find the grade
    const grade = props.grades.find((g) => g.assignmentId === assignmentId && g.studentId === studentId);

    // Only show popover if the assignment has a score
    if (grade && (grade.status === "completed" || grade.status === "graded") && grade.score !== null) {
      const target = event.currentTarget as HTMLElement;

      // Check if clicking the same cell - if so, toggle
      const isSameCell =
        selectedGrade.value?.assignmentId === assignmentId && selectedGrade.value?.studentId === studentId;

      if (isSameCell && popoverRef.value) {
        // Toggle if clicking the same cell
        popoverRef.value.toggle(event, target);
        return;
      }

      // Update selected grade data first
      selectedGrade.value = grade;

      // Find assignment and student names
      const assignment = props.assignments.find((a) => a.id === assignmentId);
      const student = props.students.find((s) => s.id === studentId);

      selectedAssignmentName.value = assignment?.name || "Assignment";
      selectedStudentName.value = student ? `${student.firstName} ${student.lastName}` : "Student";

      // Hide any open popover first, then show the new one
      // This ensures the position is recalculated for the new target
      if (popoverRef.value) {
        popoverRef.value.hide();
        // Use nextTick to ensure the data is updated before showing
        nextTick(() => {
          if (popoverRef.value) {
            popoverRef.value.toggle(event, target);
          }
        });
      } else {
        // If no popover ref yet, just show directly
        nextTick(() => {
          if (popoverRef.value) {
            popoverRef.value.toggle(event, target);
          }
        });
      }
    } else {
      // Hide popover if clicking on a cell without a grade
      if (popoverRef.value) {
        popoverRef.value.hide();
      }
      // Emit event for other cases if needed
      emit("cell-click", { assignmentId, studentId });
    }
  };

  const handleViewPractice = () => {
    popoverRef.value?.hide();
    emit("view-practice");
  };

  const handleExportGradebook = () => {
    emit("export-gradebook");
  };

  const handleAddActivity = () => {
    emit("add-activity");
  };
</script>

<template>
  <div class="w-full space-y-4 md:space-y-6">
    <!-- Header Section with Action Buttons -->
    <div class="flex flex-col md:flex-row md:items-center md:justify-end gap-3 md:gap-4">
      <div
        class="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 sm:gap-3 flex-shrink-0 w-full md:w-auto"
      >
        <Button
          :label="$t('classes.assignments.gradebook.exportGradebook')"
          class="bg-primary-600 hover:bg-primary-700 text-white border-0 whitespace-nowrap w-full sm:w-auto"
          size="small"
          @click="handleExportGradebook"
        >
          <template #icon>
            <Icon name="solar:download-line-duotone" />
          </template>
        </Button>
        <Button
          :label="$t('classes.assignments.gradebook.addActivity')"
          class="bg-surface-900 dark:bg-surface-100 text-white dark:text-surface-900 border-0 whitespace-nowrap w-full sm:w-auto"
          size="small"
          @click="handleAddActivity"
        >
          <template #icon>
            <Icon name="solar:document-add-line-duotone" />
          </template>
        </Button>
      </div>
    </div>

    <!-- Gradebook Table -->
    <div class="-mx-4 md:mx-0">
      <LqDataTable :data="tableData" :columns="columns" :loading="false" :scrollable="true">
        <!-- Student Column -->
        <template #cell-student="{ data }">
          <div class="flex items-center gap-3">
            <LqAvatar
              :src="data.student.photo || undefined"
              :initials="getInitials(data.student.firstName, data.student.lastName)"
              shape="square"
              size="md"
              avatar-class="bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300"
            />
            <span class="font-medium text-surface-900 dark:text-surface-100">
              {{ data.student.firstName }} {{ data.student.lastName }}
            </span>
          </div>
        </template>

        <!-- Assignment Columns (Dynamic) -->
        <template
          v-for="assignment in assignments"
          :key="assignment.id"
          #[`cell-assignment_${assignment.id}`]="{ data }"
        >
          <div class="px-3 py-2 flex items-center justify-center">
            <!-- Graded/Completed with Score -->
            <div
              v-if="
                data.grades[assignment.id]?.status === 'completed' || data.grades[assignment.id]?.status === 'graded'
              "
              class="inline-flex flex-col items-center justify-center gap-1.5 px-3 py-2 rounded-lg cursor-pointer hover:bg-surface-50 dark:hover:bg-surface-800 transition-colors"
              @click="(event) => handleCellClick(event, assignment.id, data.student.id)"
            >
              <span :class="getScoreColorClass(data.grades[assignment.id]?.score || 0)" class="text-lg font-semibold">
                {{ data.grades[assignment.id]?.score || 0 }}/100
              </span>
              <span
                v-if="data.grades[assignment.id]?.cefrLevel"
                :class="getLevelBadgeClass(data.grades[assignment.id]?.cefrLevel || '')"
                class="px-2 py-0.5 rounded text-xs font-medium"
              >
                {{ data.grades[assignment.id]?.cefrLevel }}
              </span>
            </div>

            <!-- In Progress -->
            <div
              v-else-if="data.grades[assignment.id]?.status === 'in_progress'"
              class="flex items-center justify-center"
            >
              <span
                class="px-2.5 py-1 rounded text-xs font-medium bg-warning-100 dark:bg-warning-900/30 text-warning-700 dark:text-warning-300"
              >
                {{ $t("classes.assignments.gradebook.inProgress") }}
              </span>
            </div>

            <!-- Not Started / Pending -->
            <div v-else class="flex items-center justify-center">
              <span
                class="px-2.5 py-1 rounded text-xs font-medium bg-surface-200 dark:bg-surface-700 text-surface-600 dark:text-surface-400"
              >
                {{ $t("classes.assignments.gradebook.notStarted") }}
              </span>
            </div>
          </div>
        </template>

        <!-- Average Column -->
        <template #cell-average="{ data }">
          <div class="px-3 py-2">
            <div v-if="data.average > 0" class="flex flex-col items-center justify-center gap-1.5">
              <span :class="getScoreColorClass(data.average)" class="text-lg font-semibold">{{ data.average }}%</span>
              <span class="text-xs text-surface-500 dark:text-surface-400">
                {{ data.accumulated }}/{{ data.total }}
              </span>
            </div>
            <div v-else class="flex items-center justify-center">
              <span class="text-xs text-surface-400 dark:text-surface-500">-</span>
            </div>
          </div>
        </template>
      </LqDataTable>
    </div>

    <!-- Grade Details Popover -->
    <Popover ref="popoverRef" class="w-80">
      <div v-if="selectedGrade" class="p-4">
        <!-- Header -->
        <div class="mb-4">
          <h3 class="text-lg font-bold text-surface-900 dark:text-surface-100 truncate">
            {{ selectedAssignmentName }}
          </h3>
          <p class="text-sm text-surface-600 dark:text-surface-400 mt-1">
            {{ selectedStudentName }}
          </p>
        </div>

        <!-- Overall Score -->
        <div class="text-center mb-4 pb-4 border-b border-surface-200 dark:border-surface-700">
          <p class="text-xs text-surface-600 dark:text-surface-400 mb-2">
            {{ $t("classes.assignments.gradeDetails.overallScore") }}
          </p>
          <p class="text-4xl font-bold text-yellow-500 dark:text-yellow-400">{{ selectedGrade.score }}%</p>
        </div>

        <!-- CEFR Level and Practice Time -->
        <div class="grid grid-cols-2 gap-3 mb-4">
          <div class="flex flex-col items-center p-3 bg-surface-50 dark:bg-surface-800 rounded-lg">
            <div class="flex items-center gap-1.5 mb-1.5">
              <Icon name="solar:medal-star-line-duotone" class="text-lg text-primary-600 dark:text-primary-400" />
              <span class="text-xs text-surface-600 dark:text-surface-400 font-medium">
                {{ $t("classes.assignments.gradeDetails.cefrLevel") }}
              </span>
            </div>
            <span class="text-xl font-bold text-primary-600 dark:text-primary-400">
              {{ selectedGrade.cefrLevel || "B1" }}
            </span>
          </div>

          <div class="flex flex-col items-center p-3 bg-surface-50 dark:bg-surface-800 rounded-lg">
            <div class="flex items-center gap-1.5 mb-1.5">
              <Icon name="solar:clock-circle-line-duotone" class="text-lg text-surface-600 dark:text-surface-400" />
              <span class="text-xs text-surface-600 dark:text-surface-400 font-medium">
                {{ $t("classes.assignments.gradeDetails.practiceTime") }}
              </span>
            </div>
            <span class="text-xl font-bold text-surface-900 dark:text-surface-100">
              {{ selectedGrade.practiceTime || "2h 7m" }}
            </span>
          </div>
        </div>

        <!-- Skills Evaluated -->
        <div class="mb-4">
          <h4 class="text-xs font-semibold text-surface-900 dark:text-surface-100 mb-2">
            {{ $t("classes.assignments.gradeDetails.skillsEvaluated") }}
          </h4>
          <div class="space-y-1.5">
            <div v-for="skill in skillsList" :key="skill.name" class="flex items-center justify-between">
              <span class="text-xs text-surface-700 dark:text-surface-300">{{ skill.name }}:</span>
              <span :class="getSkillColor(skill.value)" class="text-xs font-bold">{{ skill.value }}%</span>
            </div>
          </div>
        </div>

        <!-- View Practice Button -->
        <Button
          :label="$t('classes.assignments.gradeDetails.viewPractice')"
          class="w-full bg-surface-900 dark:bg-surface-100 text-white dark:text-surface-900 border-0 flex items-center justify-center gap-2 text-sm"
          @click="handleViewPractice"
        >
          <template #icon>
            <Icon name="solar:eye-line-duotone" class="text-base" />
          </template>
        </Button>
      </div>
    </Popover>
  </div>
</template>
