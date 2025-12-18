<script setup lang="ts">
  import { ref, computed } from "vue";
  import { useToast } from "primevue/usetoast";
  import { useI18n } from "#imports";
  import type { Student } from "~/composables/students/types";
  import { useStudentColors } from "~/composables/students/useStudentColors";

  const emit = defineEmits<{
    "add-students": [];
  }>();

  const toast = useToast();
  const { t } = useI18n();
  const { getLevelSeverity } = useStudentColors();
  const searchQuery = ref("");
  const selectedStudents = ref<string[]>([]);

  // Mock search results - in real app, this would come from API
  const mockSearchResults: Student[] = [
    {
      id: "7",
      firstName: "María",
      lastName: "Gonzá",
      email: "leza.gonzalez@gmail.com",
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
      email: "pedro.ramirez@gmail.com",
      photo: "https://i.pravatar.cc/150?img=8",
      level: "A1",
      progress: 30,
      activitiesCompleted: 6,
      activitiesTotal: 20,
      studyTimeMinutes: 75,
      score: 75,
    },
    {
      id: "9",
      firstName: "Laura",
      lastName: "Martínez",
      email: "laura.martinez@gmail.com",
      photo: "https://i.pravatar.cc/150?img=9",
      level: "A1",
      progress: 20,
      activitiesCompleted: 4,
      activitiesTotal: 20,
      studyTimeMinutes: 50,
      score: 65,
    },
    {
      id: "10",
      firstName: "Diego",
      lastName: "Silva",
      email: "diego.silva@gmail.com",
      photo: "https://i.pravatar.cc/150?img=10",
      level: "A1",
      progress: 28,
      activitiesCompleted: 5,
      activitiesTotal: 20,
      studyTimeMinutes: 65,
      score: 72,
    },
  ];

  const filteredStudents = computed(() => {
    // Show all students by default, filter when there's a search query
    if (!searchQuery.value.trim()) {
      return mockSearchResults;
    }

    const query = searchQuery.value.toLowerCase();
    return mockSearchResults.filter(
      (student) =>
        student.firstName.toLowerCase().includes(query) ||
        student.lastName.toLowerCase().includes(query) ||
        student.email.toLowerCase().includes(query),
    );
  });

  const isSelected = (studentId: string) => {
    return selectedStudents.value.includes(studentId);
  };

  const toggleSelection = (studentId: string) => {
    const index = selectedStudents.value.indexOf(studentId);
    if (index > -1) {
      selectedStudents.value.splice(index, 1);
    } else {
      selectedStudents.value.push(studentId);
    }
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
    if (selectedStudents.value.length === 0) {
      return;
    }

    // TODO: Implement actual add logic when backend is ready
    toast.add({
      severity: "success",
      summary: t("common.success"),
      detail: t("students.studentsAdded", { count: selectedStudents.value.length }),
      life: 3000,
    });
    emit("add-students");
    selectedStudents.value = [];
    searchQuery.value = "";
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
        <InputText v-model="searchQuery" :placeholder="$t('students.searchStudentsPlaceholder')" class="w-full" />
      </IconField>
    </div>

    <!-- Search Results Grid -->
    <div v-if="filteredStudents.length > 0" class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div
        v-for="student in filteredStudents"
        :key="student.id"
        :class="[
          'border-2 rounded-lg p-4 transition-all cursor-pointer relative',
          isSelected(student.id)
            ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
            : 'border-surface-200 dark:border-surface-700 hover:border-primary-300 dark:hover:border-primary-700',
        ]"
        @click="toggleSelection(student.id)"
      >
        <!-- Level badge in top right corner -->
        <Chip
          :label="student.level"
          :class="[
            getLevelColorClass(student.level),
            'absolute top-2 right-2 border rounded-md px-2 py-0.5 text-xs font-medium',
          ]"
        />
        <div class="flex items-center gap-3">
          <div class="relative">
            <Avatar
              :image="student.photo || undefined"
              :label="getInitials(student.firstName, student.lastName)"
              shape="square"
              size="large"
              class="bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 rounded-lg"
            />
            <!-- Online status badge -->
            <span
              class="absolute bottom-0 right-0 w-3 h-3 bg-success-500 border-2 border-white dark:border-surface-900 rounded-full"
            />
          </div>
          <div class="flex-1 min-w-0">
            <h4 class="font-semibold text-surface-900 dark:text-surface-100 truncate">
              {{ student.firstName }} {{ student.lastName }}
            </h4>
            <p class="text-sm text-surface-600 dark:text-surface-400 truncate">
              {{ student.email }}
            </p>
          </div>
        </div>
        <div class="mt-3">
          <Button
            :label="isSelected(student.id) ? $t('common.selected') : $t('students.select')"
            :variant="isSelected(student.id) ? 'outlined' : 'outlined'"
            :class="[
              'w-full',
              isSelected(student.id)
                ? 'bg-primary-50 dark:bg-primary-900/30 border-primary-300 dark:border-primary-700 text-primary-700 dark:text-primary-300'
                : 'border-surface-300 dark:border-surface-600 text-surface-900 dark:text-surface-100',
            ]"
            size="small"
            @click.stop="toggleSelection(student.id)"
          >
            <template #icon>
              <Icon
                :name="isSelected(student.id) ? 'solar:check-circle-line-duotone' : 'solar:add-circle-line-duotone'"
              />
            </template>
          </Button>
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
        {{ $t("students.tryDifferentSearch") }}
      </p>
    </div>

    <!-- Add Button -->
    <div class="flex justify-end pt-4 border-surface-200 dark:border-surface-700">
      <Button
        :label="$t('students.addStudents')"
        :disabled="selectedStudents.length === 0"
        class="bg-primary-600 hover:bg-primary-700"
        @click="handleAdd"
      />
    </div>
  </div>
</template>
