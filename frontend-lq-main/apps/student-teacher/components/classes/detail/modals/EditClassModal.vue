<script setup lang="ts">
  import { ref, computed, watch } from "vue";
  import { SUPPORTED_LOCALES } from "@lq/i18n/config";
  import Dialog from "primevue/dialog";
  import Button from "primevue/button";
  import InputText from "primevue/inputtext";
  import Textarea from "primevue/textarea";
  import Select from "primevue/select";
  import SelectButton from "primevue/selectbutton";
  import { LqAvatar } from "@lq/ui";
  import Badge from "primevue/badge";
  import { useEditClass } from "~/composables/classes/useEditClass";
  import { getMockClassStudents } from "~/composables/classes/useClassStudents";
  import AddTeacherSection from "./components/AddTeacherSection.vue";
  import AddStudentsSection from "./components/AddStudentsSection.vue";

  import type { Class } from "~/composables/classes/types";

  const props = defineProps<{
    visible: boolean;
    classData?: Class | null;
  }>();

  const emit = defineEmits<{
    "update:visible": [value: boolean];
    "save-complete": [updatedClass?: Class | null];
  }>();

  const {
    showAddTeacher,
    showAddStudents,
    addStudentsMethod: _addStudentsMethod,
    closeModal,
    toggleAddTeacher,
    toggleAddStudents,
    setAddStudentsMethod,
    closeAddStudents,
    cancelAddTeacher,
    saveChanges: _saveChanges,
  } = useEditClass();

  const fileInputRef = ref<HTMLInputElement | null>(null);
  const isDragging = ref(false);
  const coverImagePreview = ref<string | null>(null);
  const className = ref("");
  const level = ref<string | null>(null);
  const description = ref("");
  const language = ref<string | null>(null);
  const teachers = ref<Array<{ id: string; name: string; email: string; isOwner: boolean }>>([]);
  const students = ref<Array<{ id: string; firstName: string; lastName: string; photo?: string | null }>>([]);
  const errors = ref<{
    className?: string;
    level?: string;
    language?: string;
  }>({});

  const levels = [
    { label: "A1", value: "A1" },
    { label: "A2", value: "A2" },
    { label: "B1", value: "B1" },
    { label: "B2", value: "B2" },
    { label: "C1", value: "C1" },
    { label: "C2", value: "C2" },
  ];

  const availableLanguages = computed(() =>
    SUPPORTED_LOCALES.map((locale) => ({
      code: locale.code,
      name: locale.name,
      flag: locale.flag,
    })),
  );

  const isFormValid = computed(() => {
    return !!(className.value.trim() && level.value && language.value);
  });

  const isValidImageType = (file: File): boolean => {
    const validTypes = ["image/jpeg", "image/png", "image/webp"];
    return validTypes.includes(file.type);
  };

  const openFileSelector = () => {
    fileInputRef.value?.click();
  };

  const handleFileSelect = (event: Event) => {
    const target = event.target as HTMLInputElement;
    const file = target.files?.[0];
    if (file && isValidImageType(file)) {
      const reader = new FileReader();
      reader.onload = (e) => {
        coverImagePreview.value = e.target?.result as string;
      };
      reader.readAsDataURL(file);
    }
  };

  const handleDrop = (event: DragEvent) => {
    event.preventDefault();
    isDragging.value = false;
    const file = event.dataTransfer?.files[0];
    if (file && isValidImageType(file)) {
      const reader = new FileReader();
      reader.onload = (e) => {
        coverImagePreview.value = e.target?.result as string;
      };
      reader.readAsDataURL(file);
    }
  };

  const handleDragOver = (event: DragEvent) => {
    event.preventDefault();
    isDragging.value = true;
  };

  const handleDragLeave = () => {
    isDragging.value = false;
  };

  const removeImage = () => {
    coverImagePreview.value = null;
    if (fileInputRef.value) {
      fileInputRef.value.value = "";
    }
  };

  const getLanguageFlag = (code: string): string => {
    const locale = SUPPORTED_LOCALES.find((l) => l.code === code);
    return locale?.flag || code.toLowerCase();
  };

  const getLanguageName = (code: string): string => {
    const locale = SUPPORTED_LOCALES.find((l) => l.code === code);
    return locale?.name || code;
  };

  const getInitials = (name: string): string => {
    return name
      .split(" ")
      .map((n) => n.charAt(0))
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  const getStudentInitials = (student: { firstName: string; lastName: string }): string => {
    return `${student.firstName.charAt(0)}${student.lastName.charAt(0)}`.toUpperCase();
  };

  const handleAddTeacher = (email: string) => {
    // Mock teachers list
    const allMockTeachers = [
      { id: "t1", name: "Michael Chen", email: "michael.chen@school.com" },
      { id: "t2", name: "Emma Wilson", email: "emma.wilson@school.com" },
      { id: "t3", name: "James Brown", email: "james.brown@school.com" },
      { id: "t4", name: "Sarah Anderson", email: "sarah.anderson@school.com" },
      { id: "t5", name: "Robert Taylor", email: "robert.taylor@school.com" },
    ];

    // Try to find teacher by email
    const foundTeacher = allMockTeachers.find((t) => t.email.toLowerCase() === email.toLowerCase());
    if (foundTeacher && !teachers.value.find((t) => t.id === foundTeacher.id)) {
      teachers.value.push({
        ...foundTeacher,
        isOwner: false,
      });
    } else if (!foundTeacher) {
      // If not found, create a new teacher entry
      teachers.value.push({
        id: `teacher-${Date.now()}`,
        name: email.split("@")[0],
        email,
        isOwner: false,
      });
    }
  };

  const _handleRemoveTeacher = (teacherId: string) => {
    // Don't allow removing owner
    const teacher = teachers.value.find((t) => t.id === teacherId);
    if (teacher && !teacher.isOwner) {
      teachers.value = teachers.value.filter((t) => t.id !== teacherId);
    }
  };

  const handleCancelAddTeacher = () => {
    cancelAddTeacher();
  };

  const handleSelectMethod = (method: "invitation-code" | "search") => {
    setAddStudentsMethod(method);
  };

  const handleAddStudentsFromSearch = (studentIds: string[]) => {
    // Get all mock students for this class
    const mockStudents = getMockClassStudents(props.classData?.id || "");
    const studentMap = new Map(mockStudents.map((s) => [s.id, s]));

    // Add new students that aren't already in the list
    studentIds.forEach((studentId) => {
      if (!students.value.find((s) => s.id === studentId)) {
        const student = studentMap.get(studentId);
        if (student) {
          students.value.push({
            id: student.id,
            firstName: student.firstName,
            lastName: student.lastName,
            photo: student.photo || null,
          });
        }
      }
    });
  };

  const _handleRemoveStudent = (studentId: string) => {
    students.value = students.value.filter((s) => s.id !== studentId);
  };

  const handleCancelAddStudents = () => {
    closeAddStudents();
  };

  const handleClose = () => {
    closeModal();
    emit("update:visible", false);
  };

  const saveChanges = async () => {
    errors.value = {};
    if (!className.value.trim()) {
      errors.value.className = "classes.editModal.classNameRequired";
    }
    if (!level.value) {
      errors.value.level = "classes.editModal.levelRequired";
    }
    if (!language.value) {
      errors.value.language = "classes.editModal.languageRequired";
    }

    if (Object.keys(errors.value).length > 0) {
      return;
    }

    // Prepare updated data from form values
    const updatedData = {
      name: className.value.trim(),
      level: level.value || "",
      description: description.value.trim() || undefined,
      languageCode: language.value || "",
      coverImage: coverImagePreview.value,
    };

    // Build the complete updated class object from props.classData and form values
    // This ensures we have all the required fields even if classData.value is null
    if (!props.classData) {
      return;
    }
    const baseClass = props.classData;

    // Get language name from code
    const languageName = updatedData.languageCode
      ? SUPPORTED_LOCALES.find((l) => l.code === updatedData.languageCode?.toLowerCase())?.name ||
        updatedData.languageCode
      : baseClass.language;

    // Get studentIds and teacherIds from current state
    const studentIds = students.value.map((s) => s.id);
    const teacherIds = teachers.value.filter((t) => !t.isOwner).map((t) => t.id);

    const updatedClass: Class = {
      ...baseClass,
      name: updatedData.name,
      level: updatedData.level,
      description: updatedData.description ?? baseClass.description,
      languageCode: updatedData.languageCode,
      language: languageName,
      coverImage: updatedData.coverImage ?? baseClass.coverImage,
      studentIds,
      teacherIds,
      students: studentIds.length,
      updatedAt: new Date().toISOString(),
    };

    // Update classData with form values (for useEditClass internal state)
    await _saveChanges(updatedData);
    emit("update:visible", false);
    emit("save-complete", updatedClass);
  };

  // Load class data when modal opens or classData prop changes
  const loadClassData = (newClassData: Class) => {
    className.value = newClassData.name || "";
    level.value = newClassData.level || null;
    description.value = newClassData.description || "";
    language.value = newClassData.languageCode || null;
    coverImagePreview.value = newClassData.coverImage || null;

    // Load owner as teacher
    if (newClassData.ownerName && newClassData.ownerEmail) {
      const ownerTeacher = {
        id: newClassData.ownerId,
        name: newClassData.ownerName,
        email: newClassData.ownerEmail,
        isOwner: true,
      };

      // Load other teachers from classData
      const otherTeacherIds = newClassData.teacherIds || [];
      const allMockTeachers = [
        { id: "t1", name: "Michael Chen", email: "michael.chen@school.com" },
        { id: "t2", name: "Emma Wilson", email: "emma.wilson@school.com" },
        { id: "t3", name: "James Brown", email: "james.brown@school.com" },
        { id: "t4", name: "Sarah Anderson", email: "sarah.anderson@school.com" },
        { id: "t5", name: "Robert Taylor", email: "robert.taylor@school.com" },
      ];
      const otherTeachers = otherTeacherIds
        .map((id: string) => allMockTeachers.find((t: (typeof allMockTeachers)[0]) => t.id === id))
        .filter((t: (typeof allMockTeachers)[0] | undefined): t is (typeof allMockTeachers)[0] => t !== undefined)
        .map((t: (typeof allMockTeachers)[0]) => ({ ...t, isOwner: false }));

      teachers.value = [ownerTeacher, ...otherTeachers];
    }

    // Load students from classData.studentIds
    const studentIds = newClassData.studentIds || [];
    if (studentIds.length > 0) {
      const mockStudents = getMockClassStudents(newClassData.id);
      const studentMap = new Map(mockStudents.map((s) => [s.id, s]));
      students.value = studentIds
        .map((id: string) => studentMap.get(id))
        .filter((s): s is NonNullable<typeof s> => s !== undefined)
        .map((student: NonNullable<ReturnType<typeof studentMap.get>>) => ({
          id: student.id,
          firstName: student.firstName,
          lastName: student.lastName,
          photo: student.photo || null,
        }));
    } else {
      // Fallback to all mock students if no studentIds
      const mockStudents = getMockClassStudents(newClassData.id);
      students.value = mockStudents.map((student) => ({
        id: student.id,
        firstName: student.firstName,
        lastName: student.lastName,
        photo: student.photo || null,
      }));
    }
  };

  watch(
    () => props.visible,
    (newVisible) => {
      if (!newVisible) {
        closeModal();
        // Reset form
        className.value = "";
        level.value = null;
        description.value = "";
        language.value = null;
        coverImagePreview.value = null;
        teachers.value = [];
        students.value = [];
        errors.value = {};
      } else if (props.classData) {
        loadClassData(props.classData);
      }
    },
    { immediate: true },
  );

  // Also watch classData separately
  watch(
    () => props.classData,
    (newClassData) => {
      if (props.visible && newClassData) {
        loadClassData(newClassData);
      }
    },
    { immediate: true },
  );
</script>

<template>
  <Dialog
    :visible="visible"
    modal
    closable
    :draggable="false"
    class="w-full max-w-[95vw] md:max-w-4xl"
    :pt="{
      root: { class: '!rounded-xl' },
      header: { class: '!border-b-0 !pb-0' },
      content: { class: '!pt-0 !overflow-y-auto !max-h-[calc(90vh-120px)]' },
    }"
    @update:visible="handleClose"
  >
    <template #header>
      <div class="flex items-center gap-3 md:gap-4 px-4 md:px-0">
        <div class="bg-primary-100 dark:bg-primary-900/30 rounded-lg p-2 md:p-3">
          <Icon name="solar:book-line-duotone" class="text-xl md:text-2xl text-primary-600 dark:text-primary-400" />
        </div>
        <div class="flex flex-col flex-1">
          <h2 class="text-xl md:text-2xl font-bold text-surface-900 dark:text-surface-100">
            {{ $t("classes.editModal.title") }}
          </h2>
        </div>
      </div>
    </template>

    <div class="p-4 md:p-6 space-y-4 md:space-y-6">
      <!-- Class Image -->
      <div>
        <label class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
          {{ $t("classes.editModal.classImage") }}
        </label>
        <div
          v-if="!coverImagePreview"
          :class="[
            'border-2 border-dashed rounded-lg p-8 flex flex-col items-center justify-center transition-all cursor-pointer',
            isDragging
              ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
              : 'border-surface-300 dark:border-surface-700 bg-surface-50 dark:bg-surface-800 hover:border-primary-400 dark:hover:border-primary-600',
          ]"
          @drop.prevent="handleDrop"
          @dragover.prevent="handleDragOver"
          @dragleave="handleDragLeave"
          @click="openFileSelector"
        >
          <div class="w-16 h-16 bg-primary-100 dark:bg-primary-900/30 rounded-xl flex items-center justify-center mb-4">
            <Icon name="solar:upload-line-duotone" class="text-2xl text-primary-600 dark:text-primary-400" />
          </div>
          <p class="text-sm font-medium text-surface-700 dark:text-surface-300 mb-1">
            {{ $t("classes.editModal.clickToUpload") }}
          </p>
          <p class="text-xs text-surface-500 dark:text-surface-500">{{ $t("classes.editModal.imageFormats") }}</p>
          <input
            ref="fileInputRef"
            type="file"
            accept="image/jpeg,image/png,image/webp"
            class="hidden"
            @change="handleFileSelect"
          />
        </div>
        <div v-else class="relative rounded-xl overflow-hidden border border-surface-200 dark:border-surface-700">
          <img :src="coverImagePreview" alt="Class cover" class="w-full h-48 object-cover" />
          <Button variant="text" severity="danger" class="absolute top-2 right-2" @click="removeImage">
            <template #icon>
              <Icon name="solar:trash-bin-minimalistic-line-duotone" />
            </template>
          </Button>
        </div>
      </div>

      <!-- Class Name -->
      <div>
        <label for="className" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
          {{ $t("classes.editModal.className") }} *
        </label>
        <InputText
          id="className"
          v-model="className"
          :placeholder="$t('classes.editModal.classNamePlaceholder')"
          class="w-full"
          :class="{ 'p-invalid': errors.className }"
        />
        <small v-if="errors.className" class="p-error mt-1 block">
          {{ $t(errors.className) }}
        </small>
      </div>

      <!-- Level -->
      <div>
        <label class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
          {{ $t("classes.editModal.level") }} *
        </label>
        <SelectButton
          v-model="level"
          :options="levels"
          option-label="label"
          option-value="value"
          data-key="value"
          class="w-full"
        >
          <template #option="slotProps">
            <span>{{ slotProps.option.value }}</span>
          </template>
        </SelectButton>
        <small v-if="errors.level" class="p-error mt-1 block">
          {{ $t(errors.level) }}
        </small>
      </div>

      <!-- Description -->
      <div>
        <label for="description" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
          {{ $t("classes.editModal.description") }} ({{ $t("common.optional") }})
        </label>
        <Textarea
          id="description"
          v-model="description"
          :placeholder="$t('classes.editModal.descriptionPlaceholder')"
          :rows="4"
          class="w-full"
        />
      </div>

      <!-- Language -->
      <div>
        <label for="language" class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
          {{ $t("classes.editModal.language") }} *
        </label>
        <Select
          id="language"
          v-model="language"
          :options="availableLanguages"
          option-label="name"
          option-value="code"
          :placeholder="$t('classes.editModal.languagePlaceholder')"
          class="w-full"
          :class="{ 'p-invalid': errors.language }"
        >
          <template #value="slotProps">
            <div v-if="slotProps.value" class="flex items-center gap-2">
              <img
                :src="`https://flagcdn.com/w20/${getLanguageFlag(slotProps.value)}.png`"
                :alt="getLanguageName(slotProps.value)"
                class="w-5 h-4 object-cover rounded"
              />
              <span>{{ getLanguageName(slotProps.value) }}</span>
            </div>
            <span v-else>{{ $t("classes.editModal.languagePlaceholder") }}</span>
          </template>
          <template #option="slotProps">
            <div class="flex items-center gap-2">
              <img
                :src="`https://flagcdn.com/w20/${slotProps.option.flag}.png`"
                :alt="slotProps.option.name"
                class="w-5 h-4 object-cover rounded"
              />
              <span>{{ slotProps.option.name }}</span>
            </div>
          </template>
        </Select>
        <small v-if="errors.language" class="p-error mt-1 block">
          {{ $t(errors.language) }}
        </small>
      </div>

      <!-- Teachers Section -->
      <div>
        <div class="flex items-center justify-between mb-3">
          <label class="block text-sm font-medium text-surface-700 dark:text-surface-300">
            {{ $t("classes.editModal.teachers") }} ({{ teachers.length }})
          </label>
          <Button
            :label="$t('classes.editModal.addTeacher')"
            size="small"
            class="bg-primary-600 text-white border-0"
            @click="toggleAddTeacher"
          >
            <template #icon>
              <Icon name="solar:add-circle-line-duotone" />
            </template>
          </Button>
        </div>
        <!-- Initial State: Avatar Group Card -->
        <div
          v-if="!showAddTeacher && teachers.length > 0"
          class="bg-surface-50 dark:bg-surface-800 border border-surface-200 dark:border-surface-700 rounded-lg p-4"
        >
          <div class="flex items-center gap-4">
            <div class="flex -space-x-3">
              <LqAvatar
                v-for="(teacher, index) in teachers.slice(0, 3)"
                :key="teacher.id"
                :initials="getInitials(teacher.name)"
                shape="circle"
                size="xl"
                :avatar-class="`border-2 border-surface-0 dark:border-surface-900 ${
                  teacher.isOwner
                    ? 'bg-primary-600 text-white'
                    : 'bg-surface-200 dark:bg-surface-700 text-surface-700 dark:text-surface-300'
                }`"
                :style="{ zIndex: 10 - index }"
              />
              <div
                v-if="teachers.length > 3"
                class="w-12 h-12 rounded-full bg-surface-300 dark:bg-surface-600 flex items-center justify-center border-2 border-surface-0 dark:border-surface-900 text-sm font-semibold text-surface-700 dark:text-surface-300"
                :style="{ zIndex: 7 }"
              >
                +{{ teachers.length - 3 }}
              </div>
            </div>
            <div class="flex flex-col flex-1">
              <span class="text-sm font-medium text-surface-900 dark:text-surface-100">
                {{ teachers[0]?.name }}
              </span>
              <span class="text-xs text-surface-600 dark:text-surface-400">{{ teachers[0]?.email }}</span>
            </div>
            <Badge v-if="teachers[0]?.isOwner" :value="$t('classes.editModal.owner')" severity="info" />
          </div>
        </div>
        <AddTeacherSection
          :show-add-teacher="showAddTeacher"
          @add="handleAddTeacher"
          @cancel="handleCancelAddTeacher"
        />
      </div>

      <!-- Students Section -->
      <div>
        <div class="flex items-center justify-between mb-3">
          <label class="block text-sm font-medium text-surface-700 dark:text-surface-300">
            {{ $t("classes.editModal.students") }} ({{ students.length }})
          </label>
          <Button
            :label="$t('classes.editModal.addStudents')"
            size="small"
            class="bg-primary-600 text-white border-0"
            @click="toggleAddStudents"
          >
            <template #icon>
              <Icon name="solar:add-circle-line-duotone" />
            </template>
          </Button>
        </div>
        <!-- Initial State: Avatar Group Card -->
        <div
          v-if="!showAddStudents && students.length > 0"
          class="bg-surface-50 dark:bg-surface-800 border border-surface-200 dark:border-surface-700 rounded-lg p-4"
        >
          <div class="flex items-center gap-4">
            <div class="flex -space-x-3">
              <LqAvatar
                v-for="(student, index) in students.slice(0, 3)"
                :key="student.id"
                :src="student.photo || undefined"
                :initials="getStudentInitials(student)"
                shape="circle"
                size="xl"
                avatar-class="border-2 border-surface-0 dark:border-surface-900 bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300"
                :style="{ zIndex: 10 - index }"
              />
              <div
                v-if="students.length > 3"
                class="w-12 h-12 rounded-full bg-surface-300 dark:bg-surface-600 flex items-center justify-center border-2 border-surface-0 dark:border-surface-900 text-sm font-semibold text-surface-700 dark:text-surface-300"
                :style="{ zIndex: 7 }"
              >
                +{{ students.length - 3 }}
              </div>
            </div>
            <div class="flex flex-col flex-1">
              <span class="text-sm font-medium text-surface-900 dark:text-surface-100">
                {{ students.length }} {{ $t("classes.editModal.studentsEnrolled") }}
              </span>
            </div>
          </div>
        </div>
        <AddStudentsSection
          :show-add-students="showAddStudents"
          :class-id="classData?.id"
          :current-students="students"
          @select-method="handleSelectMethod"
          @add-students="handleAddStudentsFromSearch"
          @close="handleCancelAddStudents"
        />
      </div>
    </div>

    <template #footer>
      <div class="flex items-center justify-end gap-3">
        <Button :label="$t('common.cancel')" variant="outlined" severity="secondary" @click="handleClose" />
        <Button
          :label="$t('classes.editModal.saveChanges')"
          class="bg-primary-600 text-white border-0"
          :disabled="!isFormValid"
          @click="saveChanges"
        />
      </div>
    </template>
  </Dialog>
</template>
