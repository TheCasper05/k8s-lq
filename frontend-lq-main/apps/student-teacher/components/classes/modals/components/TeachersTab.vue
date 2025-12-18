<script setup lang="ts">
  import { useAuthStore } from "@lq/stores";
  import type { CreateClassFormData } from "~/composables/classes/useCreateClass";
  import { LqAvatar } from "@lq/ui";

  const props = defineProps<{
    formData: CreateClassFormData;
  }>();

  const emit = defineEmits<{
    "update:formData": [data: Partial<CreateClassFormData>];
  }>();

  const authStore = useAuthStore();
  const searchQuery = ref("");
  const activeMethod = ref<"email" | "search">("search");

  // Mock teachers data
  const mockTeachers = [
    {
      id: "t1",
      firstName: "Michael",
      lastName: "Chen",
      email: "michael.chen@school.com",
      photo: "https://i.pravatar.cc/150?img=12",
    },
    {
      id: "t2",
      firstName: "Emma",
      lastName: "Wilson",
      email: "emma.wilson@school.com",
      photo: "https://i.pravatar.cc/150?img=13",
    },
    {
      id: "t3",
      firstName: "James",
      lastName: "Brown",
      email: "james.brown@school.com",
      photo: "https://i.pravatar.cc/150?img=14",
    },
    {
      id: "t4",
      firstName: "Sarah",
      lastName: "Anderson",
      email: "sarah.anderson@school.com",
      photo: "https://i.pravatar.cc/150?img=19",
    },
    {
      id: "t5",
      firstName: "Robert",
      lastName: "Taylor",
      email: "robert.taylor@school.com",
      photo: "https://i.pravatar.cc/150?img=20",
    },
  ];

  const selectedTeachersList = computed(() => {
    return mockTeachers.filter((teacher) => props.formData.selectedTeachers.includes(teacher.id));
  });

  const filteredTeachers = computed(() => {
    if (!searchQuery.value.trim()) {
      return mockTeachers.filter((teacher) => !props.formData.selectedTeachers.includes(teacher.id));
    }

    const query = searchQuery.value.toLowerCase();
    return mockTeachers.filter(
      (teacher) =>
        !props.formData.selectedTeachers.includes(teacher.id) &&
        (teacher.firstName.toLowerCase().includes(query) ||
          teacher.lastName.toLowerCase().includes(query) ||
          teacher.email.toLowerCase().includes(query)),
    );
  });

  const classOwner = computed(() => {
    const userProfile = authStore.userProfile || authStore.userProfileComplete;
    const userAuth = authStore.userAuth;
    return {
      id: userAuth?.id || userProfile?.id || "",
      firstName: userProfile?.firstName || "Sarah",
      lastName: userProfile?.lastName || "Johnson",
      email: userAuth?.email || userProfile?.user?.email || "sarah.johnson@school.com",
      photo: userProfile?.photo || null,
    };
  });

  const getInitials = (firstName: string, lastName: string) => {
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
  };

  const addTeacher = (teacherId: string) => {
    const currentTeachers = [...props.formData.selectedTeachers];
    if (!currentTeachers.includes(teacherId)) {
      currentTeachers.push(teacherId);
      emit("update:formData", { selectedTeachers: currentTeachers });
    }
  };

  const removeTeacher = (teacherId: string) => {
    const currentTeachers = props.formData.selectedTeachers.filter((id) => id !== teacherId);
    emit("update:formData", { selectedTeachers: currentTeachers });
  };

  const isTeacherSelected = (teacherId: string) => {
    return props.formData.selectedTeachers.includes(teacherId);
  };
</script>

<template>
  <div class="flex flex-col gap-6 py-4">
    <!-- Class Owner Section -->
    <div>
      <h3 class="text-sm font-semibold text-surface-700 dark:text-surface-300 mb-3">
        {{ $t("classes.createModal.classOwner") }}
      </h3>
      <div class="bg-primary-50 dark:bg-primary-900/20 rounded-lg p-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <LqAvatar
            :src="classOwner.photo || undefined"
            :initials="getInitials(classOwner.firstName, classOwner.lastName)"
            shape="square"
            size="xl"
            avatar-class="bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300"
          />
          <div class="flex flex-col">
            <span class="font-semibold text-surface-900 dark:text-surface-100">
              {{ classOwner.firstName }} {{ classOwner.lastName }}
            </span>
            <span class="text-sm text-surface-600 dark:text-surface-400">
              {{ classOwner.email }}
            </span>
          </div>
        </div>
        <Button :label="$t('classes.createModal.owner')" class="bg-primary-600 text-white border-0" size="small">
          <template #icon>
            <Icon name="solar:crown-line-duotone" />
          </template>
        </Button>
      </div>
    </div>

    <!-- Selected Teachers Section -->
    <div v-if="selectedTeachersList.length > 0">
      <h3 class="text-sm font-semibold text-surface-700 dark:text-surface-300 mb-3">
        {{ $t("classes.createModal.selectedTeachers") }} ({{ selectedTeachersList.length }})
      </h3>
      <div class="flex flex-wrap gap-3">
        <div
          v-for="teacher in selectedTeachersList"
          :key="teacher.id"
          class="bg-primary-50 dark:bg-primary-900/30 border-2 border-primary-500 dark:border-primary-600 rounded-lg p-3 flex items-center gap-3 min-w-[200px]"
        >
          <LqAvatar
            :src="teacher.photo || undefined"
            :initials="getInitials(teacher.firstName, teacher.lastName)"
            shape="square"
            size="md"
            avatar-class="bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 text-sm shrink-0"
          />
          <div class="flex flex-col flex-1 min-w-0">
            <span class="font-medium text-surface-900 dark:text-surface-100 text-sm truncate">
              {{ teacher.firstName }} {{ teacher.lastName }}
            </span>
            <span class="text-xs text-surface-600 dark:text-surface-400 truncate">
              {{ teacher.email }}
            </span>
          </div>
          <button
            type="button"
            class="shrink-0 p-1 text-surface-500 hover:text-danger-500 dark:text-surface-400 dark:hover:text-danger-400 transition-colors rounded"
            @click="removeTeacher(teacher.id)"
          >
            <Icon name="solar:close-circle-bold-duotone" class="text-lg" />
          </button>
        </div>
      </div>
    </div>

    <!-- Add Teachers Section -->
    <div>
      <h3 class="text-sm font-semibold text-surface-700 dark:text-surface-300 mb-3">
        {{ $t("classes.createModal.addTeachersOptional") }}
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
          :label="$t('classes.createModal.searchTeachers')"
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
          <InputText v-model="searchQuery" :placeholder="$t('classes.createModal.searchPlaceholder')" class="w-full" />
        </IconField>
      </div>

      <!-- Teachers List -->
      <div v-if="activeMethod === 'search'" class="flex flex-col gap-3">
        <div
          v-for="teacher in filteredTeachers"
          :key="teacher.id"
          class="bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-lg p-4 flex items-center justify-between"
        >
          <div class="flex items-center gap-3">
            <LqAvatar
              :src="teacher.photo || undefined"
              :initials="getInitials(teacher.firstName, teacher.lastName)"
              shape="square"
              size="lg"
              avatar-class="bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 text-sm"
            />
            <div class="flex flex-col">
              <span class="font-medium text-surface-900 dark:text-surface-100">
                {{ teacher.firstName }} {{ teacher.lastName }}
              </span>
              <span class="text-sm text-surface-600 dark:text-surface-400">
                {{ teacher.email }}
              </span>
            </div>
          </div>
          <Button
            :label="$t('classes.createModal.add')"
            class="bg-primary-600 text-white border-0"
            size="small"
            :disabled="isTeacherSelected(teacher.id)"
            @click="addTeacher(teacher.id)"
          />
        </div>

        <!-- Empty State -->
        <div v-if="filteredTeachers.length === 0" class="flex flex-col items-center justify-center py-8 text-center">
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
