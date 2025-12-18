<script setup lang="ts">
  import { ref, watch, computed } from "vue";
  import { useEditClass } from "~/composables/classes/useEditClass";
  import { getMockClassStudents } from "~/composables/classes/useClassStudents";
  import { useToast } from "primevue/usetoast";
  import IconField from "primevue/iconfield";
  import InputIcon from "primevue/inputicon";
  import { LqAvatar } from "@lq/ui";
  import Badge from "primevue/badge";

  const props = defineProps<{
    showAddStudents?: boolean;
    classId?: string;
    currentStudents?: Array<{ id: string; firstName: string; lastName: string; photo?: string | null }>;
  }>();

  const emit = defineEmits<{
    "select-method": [method: "invitation-code" | "search"];
    "add-students": [studentIds: string[]];
    "close": [];
  }>();

  const toast = useToast();
  const { addStudentsMethod, setAddStudentsMethod, closeAddStudents, invitationCode } = useEditClass();
  const selectedMethod = ref<"invitation-code" | "search" | null>(addStudentsMethod.value);
  const searchQuery = ref("");
  const selectedStudentIds = ref<string[]>([]);

  // Get all available students from mock data
  const allAvailableStudents = computed(() => {
    if (!props.classId) return [];
    return getMockClassStudents(props.classId);
  });

  // Filter out already enrolled students
  const availableStudents = computed(() => {
    const currentStudentIds = props.currentStudents?.map((s) => s.id) || [];
    return allAvailableStudents.value.filter((student) => !currentStudentIds.includes(student.id));
  });

  // Filter students based on search query
  const filteredStudents = computed(() => {
    if (!searchQuery.value.trim()) {
      return availableStudents.value;
    }

    const query = searchQuery.value.toLowerCase();
    return availableStudents.value.filter(
      (student) =>
        student.firstName.toLowerCase().includes(query) ||
        student.lastName.toLowerCase().includes(query) ||
        student.email.toLowerCase().includes(query),
    );
  });

  watch(
    () => addStudentsMethod.value,
    (newValue) => {
      selectedMethod.value = newValue;
    },
  );

  const selectMethod = (method: "invitation-code" | "search") => {
    selectedMethod.value = method;
    setAddStudentsMethod(method);
    emit("select-method", method);
  };

  const backToMethodSelection = () => {
    selectedMethod.value = null;
    setAddStudentsMethod(null);
    searchQuery.value = "";
    selectedStudentIds.value = [];
  };

  const handleClose = () => {
    closeAddStudents();
    backToMethodSelection();
    emit("close");
  };

  const handleSendEmail = () => {
    // Mock email sending - show success toast
    toast.add({
      severity: "success",
      summary: "Email Sent",
      detail: "Invitation code has been sent to students",
      life: 3000,
    });
  };

  const copyInvitationCode = () => {
    if (invitationCode.value) {
      navigator.clipboard.writeText(invitationCode.value);
      toast.add({
        severity: "success",
        summary: "Copied",
        detail: "Invitation code copied to clipboard",
        life: 2000,
      });
    }
  };

  const getInitials = (firstName: string, lastName: string) => {
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
  };

  const toggleStudentSelection = (studentId: string) => {
    const index = selectedStudentIds.value.indexOf(studentId);
    if (index > -1) {
      selectedStudentIds.value.splice(index, 1);
    } else {
      selectedStudentIds.value.push(studentId);
    }
  };

  const addSelectedStudents = () => {
    if (selectedStudentIds.value.length > 0) {
      emit("add-students", selectedStudentIds.value);
      backToMethodSelection();
      handleClose();
    }
  };

  const isStudentSelected = (studentId: string) => {
    return selectedStudentIds.value.includes(studentId);
  };
</script>

<template>
  <!-- Phase 1: Method Selection -->
  <div
    v-if="showAddStudents && !selectedMethod"
    class="bg-primary-50 dark:bg-primary-900/20 border-2 border-primary-200 dark:border-primary-800 rounded-lg p-4 mt-3"
  >
    <label class="block text-base font-semibold text-primary-900 dark:text-primary-100 mb-4">
      {{ $t("classes.editModal.chooseMethodToAddStudents") }}
    </label>

    <div class="flex flex-col gap-3 mb-4">
      <div
        class="relative flex items-start gap-4 p-4 rounded-xl cursor-pointer transition-all border-2 bg-surface-0 dark:bg-surface-900 border-surface-200 dark:border-surface-700 hover:border-primary-300 dark:hover:border-primary-700 hover:shadow-sm"
        @click="selectMethod('invitation-code')"
      >
        <div
          class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm bg-primary-100 dark:bg-primary-900/50 text-primary-700 dark:text-primary-300"
        >
          1
        </div>
        <div class="flex-1 min-w-0">
          <h3 class="font-semibold text-base mb-1 text-surface-900 dark:text-surface-100">
            {{ $t("classes.editModal.invitationCode") }}
          </h3>
          <p class="text-sm text-surface-600 dark:text-surface-400">
            {{ $t("classes.editModal.invitationCodeDescription") }}
          </p>
        </div>
      </div>

      <div
        class="relative flex items-start gap-4 p-4 rounded-xl cursor-pointer transition-all border-2 bg-surface-0 dark:bg-surface-900 border-surface-200 dark:border-surface-700 hover:border-primary-300 dark:hover:border-primary-700 hover:shadow-sm"
        @click="selectMethod('search')"
      >
        <div
          class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm bg-primary-100 dark:bg-primary-900/50 text-primary-700 dark:text-primary-300"
        >
          2
        </div>
        <div class="flex-1 min-w-0">
          <h3 class="font-semibold text-base mb-1 text-surface-900 dark:text-surface-100">
            {{ $t("classes.editModal.searchStudents") }}
          </h3>
          <p class="text-sm text-surface-600 dark:text-surface-400">
            {{ $t("classes.editModal.searchStudentsDescription") }}
          </p>
        </div>
      </div>
    </div>

    <div class="flex justify-end">
      <Button :label="$t('common.close')" variant="outlined" severity="secondary" @click="handleClose" />
    </div>
  </div>

  <!-- Phase 2: Invitation Code View -->
  <div
    v-if="showAddStudents && selectedMethod === 'invitation-code'"
    class="bg-primary-50 dark:bg-primary-900/20 border-2 border-primary-200 dark:border-primary-800 rounded-lg p-4 mt-3"
  >
    <div class="flex items-center justify-between mb-3">
      <h3 class="text-base font-semibold text-primary-900 dark:text-primary-100">
        {{ $t("classes.editModal.invitationCode") }}
      </h3>
      <button
        type="button"
        class="p-1 text-surface-500 hover:text-surface-900 dark:text-surface-400 dark:hover:text-surface-100 transition-colors"
        @click="backToMethodSelection"
      >
        <Icon name="solar:close-circle-line-duotone" class="text-xl" />
      </button>
    </div>

    <p class="text-sm text-surface-600 dark:text-surface-400 mb-4">
      {{ $t("classes.editModal.shareCodeDescription") }}
    </p>

    <div
      class="bg-surface-0 dark:bg-surface-900 border-2 border-primary-500 dark:border-primary-600 rounded-lg p-6 mb-4 text-center cursor-pointer"
      @click="copyInvitationCode"
    >
      <span class="text-3xl font-bold text-primary-700 dark:text-primary-300 tracking-wider">
        {{ invitationCode }}
      </span>
    </div>

    <Button
      :label="$t('classes.editModal.sendEmail')"
      class="w-full bg-primary-600 text-white border-0 mb-4"
      @click="handleSendEmail"
    >
      <template #icon>
        <Icon name="solar:letter-line-duotone" />
      </template>
    </Button>

    <div class="bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-lg p-3">
      <div class="flex items-start gap-2">
        <Icon
          name="solar:lightbulb-line-duotone"
          class="text-lg text-primary-600 dark:text-primary-400 flex-shrink-0 mt-0.5"
        />
        <p class="text-xs text-surface-600 dark:text-surface-400">
          {{ $t("classes.editModal.studentCodeHint") }}
        </p>
      </div>
    </div>
  </div>

  <!-- Phase 3: Search Students View -->
  <div
    v-if="showAddStudents && selectedMethod === 'search'"
    class="bg-primary-50 dark:bg-primary-900/20 border-2 border-primary-200 dark:border-primary-800 rounded-lg p-4 mt-3"
  >
    <div class="flex items-center justify-between mb-3">
      <h3 class="text-base font-semibold text-primary-900 dark:text-primary-100">
        {{ $t("classes.editModal.searchStudents") }}
      </h3>
      <button
        type="button"
        class="p-1 text-surface-500 hover:text-surface-900 dark:text-surface-400 dark:hover:text-surface-100 transition-colors"
        @click="backToMethodSelection"
      >
        <Icon name="solar:close-circle-line-duotone" class="text-xl" />
      </button>
    </div>

    <IconField class="w-full mb-4">
      <InputIcon>
        <Icon name="solar:magnifer-zoom-in-line-duotone" />
      </InputIcon>
      <InputText v-model="searchQuery" :placeholder="$t('classes.editModal.searchPlaceholder')" class="w-full" />
    </IconField>

    <div class="max-h-96 overflow-y-auto space-y-2 mb-4">
      <div
        v-for="student in filteredStudents"
        :key="student.id"
        class="bg-surface-0 dark:bg-surface-900 border border-surface-200 dark:border-surface-700 rounded-lg p-3 flex items-center justify-between"
      >
        <div class="flex items-center gap-3 flex-1">
          <LqAvatar
            :src="student.photo || undefined"
            :initials="getInitials(student.firstName, student.lastName)"
            shape="square"
            size="lg"
            avatar-class="bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300"
          />
          <div class="flex flex-col flex-1">
            <span class="font-medium text-sm text-surface-900 dark:text-surface-100">
              {{ student.firstName }} {{ student.lastName }}
            </span>
            <span class="text-xs text-surface-600 dark:text-surface-400">
              {{ student.email }}
            </span>
          </div>
          <Badge v-if="student.level" :value="student.level" severity="secondary" class="text-xs" />
        </div>
        <Button
          :label="isStudentSelected(student.id) ? $t('common.added') : $t('classes.createModal.add')"
          :severity="isStudentSelected(student.id) ? 'secondary' : undefined"
          :variant="isStudentSelected(student.id) ? 'outlined' : undefined"
          :class="isStudentSelected(student.id) ? '' : 'bg-primary-600 text-white border-0'"
          size="small"
          @click="toggleStudentSelection(student.id)"
        />
      </div>

      <div v-if="filteredStudents.length === 0" class="flex flex-col items-center justify-center py-8 text-center">
        <Icon name="solar:magnifer-zoom-in-line-duotone" class="text-4xl text-surface-300 dark:text-surface-700 mb-2" />
        <p class="text-sm text-surface-600 dark:text-surface-400">
          {{ $t("common.noStudentsFound") }}
        </p>
      </div>
    </div>

    <div class="flex items-center justify-end gap-3">
      <Button :label="$t('common.cancel')" variant="outlined" severity="secondary" @click="backToMethodSelection" />
      <Button
        :label="$t('classes.editModal.addSelectedStudents', { count: selectedStudentIds.length })"
        class="bg-primary-600 text-white border-0"
        :disabled="selectedStudentIds.length === 0"
        @click="addSelectedStudents"
      />
    </div>
  </div>
</template>
