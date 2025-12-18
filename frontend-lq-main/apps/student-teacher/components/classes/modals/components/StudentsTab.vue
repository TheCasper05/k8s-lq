<script setup lang="ts">
  import type { CreateClassFormData } from "~/composables/classes/useCreateClass";
  import { LqAvatar } from "@lq/ui";

  const props = defineProps<{
    formData: CreateClassFormData;
  }>();

  const emit = defineEmits<{
    "update:formData": [data: Partial<CreateClassFormData>];
  }>();

  const searchQuery = ref("");
  const activeMethod = ref<"email" | "search">("search");

  // Mock students data
  const mockStudents = [
    {
      id: "s1",
      firstName: "Alex",
      lastName: "Martinez",
      email: "alex.martinez@school.com",
      photo: "https://i.pravatar.cc/150?img=15",
    },
    {
      id: "s2",
      firstName: "Sophia",
      lastName: "Lee",
      email: "sophia.lee@school.com",
      photo: "https://i.pravatar.cc/150?img=16",
    },
    {
      id: "s3",
      firstName: "David",
      lastName: "Kim",
      email: "david.kim@school.com",
      photo: "https://i.pravatar.cc/150?img=17",
    },
    {
      id: "s4",
      firstName: "Emma",
      lastName: "Garcia",
      email: "emma.garcia@school.com",
      photo: "https://i.pravatar.cc/150?img=18",
    },
    {
      id: "s5",
      firstName: "Lucas",
      lastName: "Rodriguez",
      email: "lucas.rodriguez@school.com",
      photo: "https://i.pravatar.cc/150?img=21",
    },
    {
      id: "s6",
      firstName: "Olivia",
      lastName: "White",
      email: "olivia.white@school.com",
      photo: "https://i.pravatar.cc/150?img=22",
    },
    {
      id: "s7",
      firstName: "Noah",
      lastName: "Thompson",
      email: "noah.thompson@school.com",
      photo: "https://i.pravatar.cc/150?img=23",
    },
    {
      id: "s8",
      firstName: "Isabella",
      lastName: "Davis",
      email: "isabella.davis@school.com",
      photo: "https://i.pravatar.cc/150?img=24",
    },
  ];

  const selectedStudentsList = computed(() => {
    return mockStudents.filter((student) => props.formData.selectedStudents.includes(student.id));
  });

  const filteredStudents = computed(() => {
    if (!searchQuery.value.trim()) {
      return mockStudents.filter((student) => !props.formData.selectedStudents.includes(student.id));
    }

    const query = searchQuery.value.toLowerCase();
    return mockStudents.filter(
      (student) =>
        !props.formData.selectedStudents.includes(student.id) &&
        (student.firstName.toLowerCase().includes(query) ||
          student.lastName.toLowerCase().includes(query) ||
          student.email.toLowerCase().includes(query)),
    );
  });

  const getInitials = (firstName: string, lastName: string) => {
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
  };

  const addStudent = (studentId: string) => {
    const currentStudents = [...props.formData.selectedStudents];
    if (!currentStudents.includes(studentId)) {
      currentStudents.push(studentId);
      emit("update:formData", { selectedStudents: currentStudents });
    }
  };

  const removeStudent = (studentId: string) => {
    const currentStudents = props.formData.selectedStudents.filter((id) => id !== studentId);
    emit("update:formData", { selectedStudents: currentStudents });
  };

  const isStudentSelected = (studentId: string) => {
    return props.formData.selectedStudents.includes(studentId);
  };
</script>

<template>
  <div class="flex flex-col gap-6 py-4">
    <!-- Selected Students Section -->
    <div v-if="selectedStudentsList.length > 0">
      <h3 class="text-sm font-semibold text-surface-700 dark:text-surface-300 mb-3">
        {{ $t("classes.createModal.selectedStudents") }} ({{ selectedStudentsList.length }})
      </h3>
      <div class="flex flex-wrap gap-3">
        <div
          v-for="student in selectedStudentsList"
          :key="student.id"
          class="bg-primary-50 dark:bg-primary-900/30 border-2 border-primary-500 dark:border-primary-600 rounded-lg p-3 flex items-center gap-3 min-w-[200px]"
        >
          <LqAvatar
            :src="student.photo || undefined"
            :initials="getInitials(student.firstName, student.lastName)"
            shape="square"
            size="md"
            avatar-class="bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 text-sm shrink-0"
          />
          <div class="flex flex-col flex-1 min-w-0">
            <span class="font-medium text-surface-900 dark:text-surface-100 text-sm truncate">
              {{ student.firstName }} {{ student.lastName }}
            </span>
            <span class="text-xs text-surface-600 dark:text-surface-400 truncate">
              {{ student.email }}
            </span>
          </div>
          <button
            type="button"
            class="shrink-0 p-1 text-surface-500 hover:text-danger-500 dark:text-surface-400 dark:hover:text-danger-400 transition-colors rounded"
            @click="removeStudent(student.id)"
          >
            <Icon name="solar:close-circle-bold-duotone" class="text-lg" />
          </button>
        </div>
      </div>
    </div>

    <!-- Add Students Section -->
    <div>
      <h3 class="text-sm font-semibold text-surface-700 dark:text-surface-300 mb-3">
        {{ $t("classes.createModal.addStudentsOptional") }}
      </h3>

      <!-- Method Selection Buttons -->
      <div class="flex gap-3 mb-4">
        <Button
          :label="$t('classes.createModal.byEmail')"
          :variant="activeMethod === 'email' ? undefined : 'outlined'"
          :class="activeMethod === 'email' ? 'bg-primary-600 text-white' : ''"
          class="flex-1"
          @click="activeMethod = 'email'"
        >
          <template #icon>
            <Icon name="solar:letter-line-duotone" />
          </template>
        </Button>
        <Button
          :label="$t('students.searchStudents')"
          :variant="activeMethod === 'search' ? undefined : 'outlined'"
          :class="activeMethod === 'search' ? 'bg-primary-600 text-white' : ''"
          class="flex-1"
          @click="activeMethod = 'search'"
        >
          <template #icon>
            <Icon name="solar:magnifer-zoom-in-line-duotone" />
          </template>
        </Button>
      </div>

      <!-- Search Input (shown when search method is active) -->
      <div v-if="activeMethod === 'search'" class="mb-4">
        <IconField class="w-full">
          <InputIcon>
            <Icon name="solar:magnifer-zoom-in-line-duotone" />
          </InputIcon>
          <InputText v-model="searchQuery" :placeholder="$t('students.searchStudentsPlaceholder')" class="w-full" />
        </IconField>
      </div>

      <!-- Students List -->
      <div v-if="activeMethod === 'search'" class="flex flex-col gap-3">
        <div
          v-for="student in filteredStudents"
          :key="student.id"
          class="bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-lg p-4 flex items-center justify-between"
        >
          <div class="flex items-center gap-3">
            <LqAvatar
              :src="student.photo || undefined"
              :initials="getInitials(student.firstName, student.lastName)"
              shape="square"
              size="lg"
              avatar-class="bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 text-sm"
            />
            <div class="flex flex-col">
              <span class="font-medium text-surface-900 dark:text-surface-100">
                {{ student.firstName }} {{ student.lastName }}
              </span>
              <span class="text-sm text-surface-600 dark:text-surface-400">
                {{ student.email }}
              </span>
            </div>
          </div>
          <Button
            :label="$t('classes.createModal.add')"
            class="bg-primary-600 text-white border-0"
            size="small"
            :disabled="isStudentSelected(student.id)"
            @click="addStudent(student.id)"
          />
        </div>

        <!-- Empty State -->
        <div v-if="filteredStudents.length === 0" class="flex flex-col items-center justify-center py-8 text-center">
          <Icon
            name="solar:magnifer-zoom-in-line-duotone"
            class="text-4xl text-surface-300 dark:text-surface-700 mb-2"
          />
          <p class="text-sm text-surface-600 dark:text-surface-400">
            {{ $t("common.noStudentsFound") }}
          </p>
        </div>
      </div>

      <!-- By Email Method (placeholder) -->
      <div v-if="activeMethod === 'email'" class="bg-surface-50 dark:bg-surface-800 rounded-lg p-6 text-center">
        <Icon name="solar:letter-line-duotone" class="text-4xl text-surface-400 dark:text-surface-600 mb-2" />
        <p class="text-sm text-surface-600 dark:text-surface-400">
          {{ $t("classes.createModal.byEmail") }} - {{ $t("classes.createModal.comingSoon") }}
        </p>
      </div>
    </div>
  </div>
</template>
