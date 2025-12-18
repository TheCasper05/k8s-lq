<script setup lang="ts">
  import Dialog from "primevue/dialog";
  import Button from "primevue/button";
  import InputText from "primevue/inputtext";
  import IconField from "primevue/iconfield";
  import InputIcon from "primevue/inputicon";
  import { LqAvatar } from "@lq/ui";
  import { CEFRLevel, type Activity, type ClassData } from "~/types/activities";
  import { getMockClasses } from "~/utils/mockActivities";
  import CEFRBadge from "~/components/shared/CEFRBadge.vue";

  interface Student {
    id: string;
    name: string;
    level: CEFRLevel;
    className: string;
  }

  interface Props {
    visible: boolean;
    activity: Activity | null;
  }

  interface Emits {
    "update:visible": [value: boolean];
    "assign": [data: { classIds: string[]; studentIds: string[] }];
  }

  const props = defineProps<Props>();
  const emit = defineEmits<Emits>();

  const { t } = useI18n();

  const activeTab = ref<"classes" | "students">("classes");
  const searchQuery = ref("");
  const selectedClasses = ref<string[]>([]);
  const selectedStudents = ref<string[]>([]);
  const assigning = ref(false);

  const classes = getMockClasses();

  // Mock students data
  const students: Student[] = [
    { id: "1", name: "Emma Johnson", level: CEFRLevel.C1, className: "Business English Advanced" },
    { id: "2", name: "Michael Chen", level: CEFRLevel.B2, className: "English Grammar Intensive" },
    { id: "3", name: "Sofia Martinez", level: CEFRLevel.B1, className: "Conversational English" },
    { id: "4", name: "James Wilson", level: CEFRLevel.A2, className: "English for Travel" },
    { id: "5", name: "Yuki Tanaka", level: CEFRLevel.C1, className: "Academic English" },
    { id: "6", name: "Lucas Silva", level: CEFRLevel.B1, className: "Conversational English" },
  ];

  const dialogVisible = computed({
    get: () => props.visible,
    set: (value) => emit("update:visible", value),
  });

  const filteredClasses = computed<ClassData[]>(() => {
    if (!searchQuery.value) return classes;

    const query = searchQuery.value.toLowerCase();
    return classes.filter((c) => c.name.toLowerCase().includes(query) || c.level.toLowerCase().includes(query));
  });

  const filteredStudents = computed<Student[]>(() => {
    if (!searchQuery.value) return students;

    const query = searchQuery.value.toLowerCase();
    return students.filter((s) => s.name.toLowerCase().includes(query) || s.className.toLowerCase().includes(query));
  });

  const hasSelection = computed(() => {
    return selectedClasses.value.length > 0 || selectedStudents.value.length > 0;
  });

  watch(
    () => props.visible,
    (newVal) => {
      if (newVal) {
        selectedClasses.value = [];
        selectedStudents.value = [];
        searchQuery.value = "";
        activeTab.value = "classes";
      }
    },
  );

  const isClassSelected = (classId: string) => {
    return selectedClasses.value.includes(classId);
  };

  const isStudentSelected = (studentId: string) => {
    return selectedStudents.value.includes(studentId);
  };

  const toggleClass = (classId: string) => {
    const index = selectedClasses.value.indexOf(classId);
    if (index > -1) {
      selectedClasses.value.splice(index, 1);
    } else {
      selectedClasses.value.push(classId);
    }
  };

  const toggleStudent = (studentId: string) => {
    const index = selectedStudents.value.indexOf(studentId);
    if (index > -1) {
      selectedStudents.value.splice(index, 1);
    } else {
      selectedStudents.value.push(studentId);
    }
  };

  const assignScenario = async () => {
    assigning.value = true;
    await new Promise((resolve) => setTimeout(resolve, 1000));
    emit("assign", {
      classIds: selectedClasses.value,
      studentIds: selectedStudents.value,
    });
    assigning.value = false;
    dialogVisible.value = false;
  };
</script>

<template>
  <Dialog
    :visible="visible"
    modal
    :closable="false"
    :draggable="false"
    class="w-full max-w-3xl"
    :pt="{
      root: { class: '!rounded-xl !overflow-hidden' },
      mask: { class: 'backdrop-blur-sm' },
      header: { class: '!hidden' },
      content: { class: '!p-0 !m-0' },
      footer: {
        class:
          '!px-6 !py-4 !m-0 !bg-surface-50 dark:!bg-surface-900 !border-t !border-surface-200 dark:!border-surface-700',
      },
    }"
    @update:visible="emit('update:visible', $event)"
  >
    <!-- Custom Header -->
    <div class="bg-primary-600 px-6 pt-6 pb-4">
      <div class="flex items-start justify-between mb-4">
        <div>
          <h3 class="text-xl font-semibold text-white mb-1">{{ t("teacher.scenarios.assignModal.title") }}</h3>
          <p class="text-primary-100 text-sm">{{ t("teacher.scenarios.assignModal.subtitle") }}</p>
        </div>
        <button
          class="text-white hover:bg-white/10 rounded-full p-1.5 transition-colors"
          @click="dialogVisible = false"
        >
          <Icon name="solar:close-circle-linear" class="text-lg" />
        </button>
      </div>

      <!-- Tabs -->
      <div class="flex gap-2">
        <button
          class="flex-1 px-4 py-2.5 rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2 border-0 outline-none"
          :class="[
            activeTab === 'classes'
              ? 'bg-surface-0 dark:bg-surface-800 text-primary-700 dark:text-primary-400 shadow-sm'
              : 'bg-primary-500/50 text-white hover:bg-primary-500/40',
          ]"
          @click="activeTab = 'classes'"
        >
          <div class="flex items-center justify-center gap-2">
            <Icon name="lucide:book-open" class="text-lg mt-1" />
            <span>{{ t("teacher.scenarios.assignModal.tabs.classes") }}</span>
          </div>
        </button>
        <button
          class="flex-1 px-4 py-2.5 rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2 border-0 outline-none"
          :class="[
            activeTab === 'students'
              ? 'bg-surface-0 dark:bg-surface-800 text-primary-700 dark:text-primary-400 shadow-sm'
              : 'bg-primary-500/30 text-white/90 hover:bg-primary-500/40',
          ]"
          @click="activeTab = 'students'"
        >
          <Icon name="solar:user-rounded-linear" class="text-lg mt-1" />
          <span>{{ t("teacher.scenarios.assignModal.tabs.students") }}</span>
        </button>
      </div>
    </div>

    <!-- Content -->
    <div class="px-6 pt-5 pb-4 bg-surface-0 dark:bg-surface-900">
      <!-- Search Bar -->
      <div class="mb-4">
        <IconField>
          <InputIcon>
            <Icon name="solar:magnifer-linear" />
          </InputIcon>
          <InputText
            v-model="searchQuery"
            :placeholder="
              activeTab === 'classes'
                ? t('teacher.scenarios.assignModal.searchClasses')
                : t('teacher.scenarios.assignModal.searchStudents')
            "
            class="w-full"
          />
        </IconField>
      </div>

      <!-- Classes Tab -->
      <div v-if="activeTab === 'classes'" class="space-y-2.5 max-h-96 overflow-y-auto pr-1">
        <div
          v-for="classItem in filteredClasses"
          :key="classItem.id"
          class="group relative rounded-lg border-2 transition-all duration-200 cursor-pointer p-3.5"
          :class="[
            isClassSelected(classItem.id)
              ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/10'
              : 'border-surface-200 dark:border-surface-700 hover:border-primary-300 dark:hover:border-primary-700',
          ]"
          @click="toggleClass(classItem.id)"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <div
                class="flex items-center justify-center gap-2 size-10 bg-surface-200 dark:bg-surface-800 rounded-lg p-1"
              >
                <Icon :name="classItem.flag" class="text-lg" />
              </div>
              <div>
                <h4 class="font-semibold text-surface-900 dark:text-surface-0 text-sm">
                  {{ classItem.name }}
                </h4>
                <div class="flex items-center gap-2 text-xs text-surface-600 dark:text-surface-400 mt-0.5">
                  <CEFRBadge no-color :level="classItem.level" size="sm" />
                  <span>{{ classItem.studentCount }} {{ t("teacher.dashboard.stats.students") }}</span>
                </div>
              </div>
            </div>

            <!-- Checkbox -->
            <div
              class="w-5 h-5 rounded border-2 flex items-center justify-center transition-all flex-shrink-0"
              :class="[
                isClassSelected(classItem.id)
                  ? 'bg-primary-500 border-primary-500'
                  : 'border-surface-300 dark:border-surface-600',
              ]"
            >
              <Icon
                v-if="isClassSelected(classItem.id)"
                name="solar:check-circle-linear"
                class="text-white text-[10px]"
              />
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="!filteredClasses.length" class="text-center py-12">
          <Icon name="solar:inbox-linear" class="text-4xl text-surface-400 mb-2" />
          <p class="text-surface-600 dark:text-surface-400 text-sm">
            {{ t("teacher.scenarios.assignModal.noClasses") }}
          </p>
        </div>
      </div>

      <!-- Students Tab -->
      <div v-else class="space-y-2.5 max-h-96 overflow-y-auto pr-1">
        <div
          v-for="student in filteredStudents"
          :key="student.id"
          class="group relative rounded-lg border-2 transition-all duration-200 cursor-pointer p-3.5"
          :class="[
            isStudentSelected(student.id)
              ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/10'
              : 'border-surface-200 dark:border-surface-700 hover:border-primary-300 dark:hover:border-primary-700',
          ]"
          @click="toggleStudent(student.id)"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-3">
              <LqAvatar
                :initials="student.name.charAt(0)"
                shape="circle"
                size="md"
                avatar-class="bg-primary-100 dark:bg-primary-900/20 text-primary-700 dark:text-primary-400"
              />
              <div>
                <h4 class="font-semibold text-surface-900 dark:text-surface-0 text-sm">
                  {{ student.name }}
                </h4>
                <div class="flex items-center gap-2 text-xs text-surface-600 dark:text-surface-400 mt-0.5">
                  <CEFRBadge no-color :level="student.level" size="sm" />
                  <span>{{ student.className }}</span>
                </div>
              </div>
            </div>

            <!-- Checkbox -->
            <div
              class="w-5 h-5 rounded border-2 flex items-center justify-center transition-all flex-shrink-0"
              :class="[
                isStudentSelected(student.id)
                  ? 'bg-primary-500 border-primary-500'
                  : 'border-surface-300 dark:border-surface-600',
              ]"
            >
              <Icon
                v-if="isStudentSelected(student.id)"
                name="solar:check-circle-linear"
                class="text-white text-[10px]"
              />
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-if="!filteredStudents.length" class="text-center py-12">
          <Icon name="solar:inbox-linear" class="text-4xl text-surface-400 mb-2" />
          <p class="text-surface-600 dark:text-surface-400 text-sm">
            {{ t("teacher.scenarios.assignModal.noStudents") }}
          </p>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <template #footer>
      <div class="flex items-center justify-between w-full">
        <div class="text-sm">
          <span class="font-medium text-surface-900 dark:text-surface-0">
            <span v-if="activeTab === 'classes'">
              {{ selectedClasses.length }}
              {{
                selectedClasses.length === 1 ? t("teacher.dashboard.stats.class") : t("teacher.dashboard.stats.classes")
              }}
            </span>
            <span v-else>
              {{ selectedStudents.length }}
              {{
                selectedStudents.length === 1
                  ? t("teacher.dashboard.stats.student")
                  : t("teacher.dashboard.stats.students")
              }}
            </span>
            <span class="font-normal">{{ t("teacher.scenarios.assignModal.selected") }}</span>
          </span>
          <span class="text-surface-500 dark:text-surface-400 ml-1">
            {{ t("teacher.scenarios.assignModal.willReceive") }}
          </span>
        </div>
        <div class="flex gap-2">
          <Button :label="t('common.actions.cancel')" severity="secondary" outlined @click="dialogVisible = false" />
          <Button
            :label="t('common.actions.assign')"
            :disabled="!hasSelection"
            :loading="assigning"
            class="!text-white"
            @click="assignScenario"
          >
            <template #icon>
              <Icon name="solar:user-plus-broken" />
            </template>
          </Button>
        </div>
      </div>
    </template>
  </Dialog>
</template>
