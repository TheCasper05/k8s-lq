<script setup lang="ts">
  import { ref, computed, watch } from "vue";
  import { useToast } from "primevue/usetoast";
  import type { Student } from "~/composables/students/types";
  import { useStudentColors } from "~/composables/students/useStudentColors";
  import { useAddClassStudents } from "~/composables/classes/useAddClassStudents";

  const emit = defineEmits<{
    "add-students": [];
    "update:search-query": [query: string];
    "toggle-selection": [studentId: string];
  }>();

  const _toast = useToast();
  const { getLevelSeverity } = useStudentColors();
  const { searchQuery, selectedStudents, toggleStudentSelection, isStudentSelected } = useAddClassStudents();
  const localSearchQuery = ref(searchQuery.value);

  watch(
    () => searchQuery.value,
    (newValue) => {
      localSearchQuery.value = newValue;
    },
  );

  // Mock search results - in real app, this would come from API
  const mockSearchResults: Student[] = [
    {
      id: "7",
      firstName: "María",
      lastName: "Gonzá",
      email: "maria.gonza@aliga...",
      photo: "https://i.pravatar.cc/150?img=7",
      level: "A1",
      progress: 25,
      activitiesCompleted: 5,
      activitiesTotal: 20,
      studyTimeMinutes: 60,
      score: 70,
    },
    {
      id: "8",
      firstName: "Pedro",
      lastName: "Ramírez",
      email: "pedro.ramirez@em...",
      photo: "https://i.pravatar.cc/150?img=8",
      level: "A2",
      progress: 30,
      activitiesCompleted: 6,
      activitiesTotal: 20,
      studyTimeMinutes: 75,
      score: 75,
    },
  ];

  const filteredStudents = computed(() => {
    // Show all students by default, filter when there's a search query
    if (!localSearchQuery.value.trim()) {
      return mockSearchResults;
    }

    const query = localSearchQuery.value.toLowerCase();
    return mockSearchResults.filter(
      (student) =>
        student.firstName.toLowerCase().includes(query) ||
        student.lastName.toLowerCase().includes(query) ||
        student.email.toLowerCase().includes(query),
    );
  });

  const selectedCount = computed(() => selectedStudents.value.length);

  const isSelected = (studentId: string) => {
    return isStudentSelected(studentId);
  };

  const handleSearchUpdate = (value: string) => {
    localSearchQuery.value = value;
    emit("update:search-query", value);
  };

  const handleToggleSelection = (studentId: string) => {
    toggleStudentSelection(studentId);
    emit("toggle-selection", studentId);
  };

  const getInitials = (firstName: string, lastName: string) => {
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
  };

  const getLevelColorClass = (level: string) => {
    const severity = getLevelSeverity(level);
    const severityColors: Record<string, string> = {
      danger:
        "bg-danger-100 dark:bg-danger-900/30 text-danger-700 dark:text-danger-400 border-danger-300 dark:border-danger-700",
      warn: "bg-warning-100 dark:bg-warning-900/30 text-warning-700 dark:text-warning-400 border-warning-300 dark:border-warning-700",
      info: "bg-info-100 dark:bg-info-900/30 text-info-700 dark:text-info-400 border-info-300 dark:border-info-700",
      success:
        "bg-success-100 dark:bg-success-900/30 text-success-700 dark:text-success-400 border-success-300 dark:border-success-700",
      secondary:
        "bg-surface-100 dark:bg-surface-800 text-surface-700 dark:text-surface-300 border-surface-300 dark:border-surface-600",
    };
    return severityColors[severity] || severityColors.secondary;
  };

  const handleAdd = () => {
    if (selectedCount.value === 0) {
      return;
    }

    emit("add-students");
  };
</script>

<template>
  <div class="flex flex-col gap-6 py-4">
    <!-- Search Input -->
    <div class="flex flex-col gap-2">
      <IconField class="w-full">
        <InputIcon>
          <Icon name="solar:magnifer-zoom-in-line-duotone" />
        </InputIcon>
        <InputText
          :model-value="localSearchQuery"
          :placeholder="$t('classes.students.searchPlaceholder')"
          class="w-full"
          @update:model-value="handleSearchUpdate"
        />
      </IconField>
    </div>

    <!-- Search Results List -->
    <div v-if="filteredStudents.length > 0" class="max-h-96 overflow-y-auto space-y-3">
      <div
        v-for="student in filteredStudents"
        :key="student.id"
        :class="[
          'border rounded-lg p-4 transition-all cursor-pointer',
          isSelected(student.id)
            ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
            : 'border-surface-200 dark:border-surface-700 hover:border-primary-300 dark:hover:border-primary-700 bg-surface-0 dark:bg-surface-900',
        ]"
        @click="handleToggleSelection(student.id)"
      >
        <div class="flex items-center justify-between gap-4">
          <div class="flex items-center gap-3 flex-1 min-w-0">
            <Avatar
              :image="student.photo || undefined"
              :label="getInitials(student.firstName, student.lastName)"
              shape="circle"
              size="large"
              class="bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 flex-shrink-0"
              style="width: 48px; height: 48px"
            />
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                <h4 class="font-medium text-surface-900 dark:text-surface-100 truncate">
                  {{ student.firstName }} {{ student.lastName }}
                </h4>
                <Chip
                  :label="student.level"
                  :class="[
                    getLevelColorClass(student.level),
                    'border rounded-md px-2 py-1 text-xs font-medium flex-shrink-0',
                  ]"
                />
              </div>
              <p class="text-sm text-surface-600 dark:text-surface-400 truncate">
                {{ student.email }}
              </p>
            </div>
          </div>
          <div class="flex items-center flex-shrink-0">
            <Button
              :label="isSelected(student.id) ? $t('common.selected') : $t('classes.students.select')"
              :variant="isSelected(student.id) ? 'outlined' : 'outlined'"
              :class="[
                isSelected(student.id)
                  ? 'bg-primary-50 dark:bg-primary-900/30 border-primary-300 dark:border-primary-700 text-primary-700 dark:text-primary-300'
                  : 'border-primary-600 text-primary-600 dark:text-primary-400',
              ]"
              size="small"
              @click.stop="handleToggleSelection(student.id)"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="flex flex-col items-center justify-center py-12 text-center">
      <Icon name="solar:magnifer-zoom-in-line-duotone" class="text-6xl text-surface-300 dark:text-surface-700 mb-4" />
      <p class="text-lg font-semibold text-surface-600 dark:text-surface-400 mb-2">
        {{ $t("common.noStudentsFound") }}
      </p>
      <p class="text-sm text-surface-500 dark:text-surface-500">
        {{ $t("classes.students.tryDifferentSearch") }}
      </p>
    </div>

    <!-- Add Button -->
    <div class="flex justify-end pt-4 border-t border-surface-200 dark:border-surface-700">
      <Button
        :label="$t('classes.students.addStudents')"
        :disabled="selectedCount === 0"
        class="bg-primary-600 hover:bg-primary-700"
        @click="handleAdd"
      />
    </div>
  </div>
</template>
