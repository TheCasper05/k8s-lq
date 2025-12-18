<script setup lang="ts">
  import { ref, computed, watch } from "vue";
  import Dialog from "primevue/dialog";
  import Button from "primevue/button";
  import Select from "primevue/select";
  import ToggleSwitch from "primevue/toggleswitch";
  import { SUPPORTED_LOCALES } from "@lq/i18n/config";
  import { useEditAssignment } from "~/composables/classes/useEditAssignment";

  const props = defineProps<{
    visible: boolean;
    assignmentId?: string;
  }>();

  const emit = defineEmits<{
    "update:visible": [value: boolean];
    "save-complete": [];
  }>();

  const { assignmentData, closeModal, saveChanges } = useEditAssignment();

  const levels = ["A1", "A2", "B1", "B2", "C1", "C2"];

  const availableLanguages = computed(() =>
    SUPPORTED_LOCALES.map((locale) => ({
      code: locale.code,
      name: locale.name,
      flag: locale.flag,
    })),
  );

  const formData = ref({
    language: null as string | null,
    level: null as string | null,
    minutes: 0,
    viewTranscription: false,
    viewTranslation: false,
    viewHints: false,
    nativeLanguage: false,
    showScore: true,
    showProgress: true,
  });

  const _useClassroomDefaults = computed(() => {
    // If using classroom defaults, language and level would be null
    return !formData.value.language && !formData.value.level;
  });

  // Load assignment data when modal opens or assignmentId changes
  watch(
    () => [props.visible, props.assignmentId],
    ([newVisible, _newAssignmentId]) => {
      if (newVisible && assignmentData.value) {
        // Load assignment data into form
        formData.value = {
          language: assignmentData.value.language || null,
          level: assignmentData.value.level || null,
          minutes: assignmentData.value.minutes || 0,
          viewTranscription: assignmentData.value.viewTranscription ?? false,
          viewTranslation: assignmentData.value.viewTranslation ?? false,
          viewHints: assignmentData.value.viewHints ?? false,
          nativeLanguage: assignmentData.value.nativeLanguage ?? false,
          showScore: assignmentData.value.showScore ?? true,
          showProgress: assignmentData.value.showProgress ?? true,
        };
      } else if (!newVisible) {
        // Reset form when closing
        formData.value = {
          language: null,
          level: null,
          minutes: 0,
          viewTranscription: false,
          viewTranslation: false,
          viewHints: false,
          nativeLanguage: false,
          showScore: true,
          showProgress: true,
        };
      }
    },
    { immediate: true },
  );

  const handleClose = () => {
    closeModal();
    emit("update:visible", false);
  };

  const handleSave = async () => {
    await saveChanges();
    emit("update:visible", false);
    emit("save-complete");
  };

  const handleTimeInput = (event: Event) => {
    const target = event.target as HTMLInputElement;
    const value = Number.parseInt(target.value, 10);
    if (!Number.isNaN(value) && value >= 0) {
      formData.value.minutes = value;
    } else if (target.value === "") {
      // Allow empty input temporarily while typing
      return;
    } else {
      // Reset to current value if invalid
      target.value = formData.value.minutes.toString();
    }
  };

  const handleTimeBlur = (event: Event) => {
    const target = event.target as HTMLInputElement;
    const value = Number.parseInt(target.value, 10);
    if (Number.isNaN(value) || value < 0) {
      formData.value.minutes = 0;
      target.value = "0";
    } else {
      formData.value.minutes = value;
      target.value = value.toString();
    }
  };
</script>

<template>
  <Dialog
    :visible="visible"
    modal
    :closable="false"
    :draggable="false"
    class="w-full max-w-[95vw] md:max-w-5xl"
    :pt="{
      root: { class: '!rounded-xl' },
      header: { class: '!p-0 !border-0' },
      content: { class: '!p-0' },
    }"
    @update:visible="handleClose"
  >
    <template #header>
      <div
        class="bg-primary-50 dark:bg-primary-900/20 px-4 md:px-6 py-4 md:py-5 border-b border-primary-200 dark:border-primary-800 w-full rounded-t-xl"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-4">
            <div class="bg-primary-600 dark:bg-primary-500 rounded-lg p-3 flex items-center justify-center">
              <Icon name="solar:document-add-line-duotone" class="text-2xl text-white" />
            </div>
            <div class="flex flex-col">
              <h2 class="text-2xl font-bold text-surface-900 dark:text-surface-100">
                {{ $t("classes.assignments.editModal.title") }}
              </h2>
              <p class="text-sm text-surface-600 dark:text-surface-400 mt-1">
                {{ $t("classes.assignments.editModal.subtitle") }}
              </p>
            </div>
          </div>
          <button
            class="w-8 h-8 rounded-full bg-white dark:bg-surface-800 flex items-center justify-center hover:bg-surface-100 dark:hover:bg-surface-700 transition-colors"
            @click="handleClose"
          >
            <Icon name="solar:close-circle-line-duotone" class="text-xl text-surface-600 dark:text-surface-400" />
          </button>
        </div>
      </div>
    </template>

    <div class="grid grid-cols-12 gap-4 md:gap-6 p-4 md:p-6">
      <!-- Left Column (7 columns) -->
      <div class="col-span-12 lg:col-span-7 flex flex-col gap-4 md:gap-6">
        <!-- General Settings -->
        <div>
          <div class="flex items-center gap-3 mb-4">
            <Icon name="solar:settings-line-duotone" class="text-2xl text-primary-600 dark:text-primary-400" />
            <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-100">
              {{ $t("classes.assignments.editModal.generalSettings") }}
            </h3>
          </div>
          <div class="grid grid-cols-1 gap-4">
            <!-- Language -->
            <div>
              <label class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
                {{ $t("classes.createModal.language") }}
              </label>
              <Select
                v-model="formData.language"
                :options="availableLanguages"
                option-label="name"
                option-value="code"
                :placeholder="$t('classes.createModal.language')"
                class="w-full"
              >
                <template #value="{ value }">
                  <div v-if="value" class="flex items-center gap-2">
                    <Icon name="solar:global-line-duotone" class="text-lg" />
                    <span>{{ availableLanguages.find((l) => l.code === value)?.name }}</span>
                  </div>
                  <span v-else>{{ $t("classes.createModal.language") }}</span>
                </template>
                <template #option="{ option }">
                  <div class="flex items-center gap-2">
                    <img
                      :src="`https://flagcdn.com/w20/${option.flag}.png`"
                      :alt="option.name"
                      class="w-5 h-4 object-cover rounded"
                    />
                    <span>{{ option.name }}</span>
                  </div>
                </template>
              </Select>
            </div>

            <!-- Level -->
            <div>
              <label class="block text-sm font-medium text-surface-700 dark:text-surface-300 mb-2">
                {{ $t("classes.createModal.level") }}
              </label>
              <Select
                v-model="formData.level"
                :options="levels.map((l) => ({ label: l, value: l }))"
                option-label="label"
                option-value="value"
                :placeholder="$t('classes.createModal.level')"
                class="w-full"
              >
                <template #value="slotProps">
                  <div v-if="slotProps.value" class="flex items-center gap-2">
                    <Icon name="solar:target-line-duotone" class="text-lg" />
                    <span>{{ slotProps.value }}</span>
                  </div>
                </template>
                <template #option="slotProps">
                  <div class="flex items-center gap-2">
                    <Icon name="solar:target-line-duotone" class="text-lg" />
                    <span>{{ slotProps.option.value }}</span>
                  </div>
                </template>
              </Select>
            </div>
          </div>
        </div>

        <!-- Time Requirements -->
        <div>
          <div class="flex items-center gap-3 mb-4">
            <Icon name="solar:clock-circle-line-duotone" class="text-2xl text-yellow-500 dark:text-yellow-400" />
            <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-100">
              {{ $t("classes.assignments.editModal.timeRequirements") }}
            </h3>
          </div>
          <div
            class="flex items-center gap-3 bg-yellow-50 dark:bg-yellow-900/20 border-2 border-yellow-300 dark:border-yellow-700 rounded-xl p-4"
          >
            <button
              class="w-12 h-12 rounded-lg bg-white dark:bg-surface-800 border border-surface-200 dark:border-surface-600 hover:bg-surface-50 dark:hover:bg-surface-700 flex items-center justify-center transition-colors shadow-sm flex-shrink-0"
              @click="formData.minutes = Math.max(0, formData.minutes - 1)"
            >
              <Icon name="solar:minus-circle-line-duotone" class="text-2xl text-surface-700 dark:text-surface-300" />
            </button>
            <div class="flex-1 flex flex-col items-center justify-center py-4">
              <div
                class="w-20 h-20 rounded-full bg-gradient-to-br from-yellow-400 via-yellow-500 to-yellow-600 dark:from-yellow-500 dark:via-yellow-600 dark:to-yellow-700 flex items-center justify-center shadow-lg mb-2"
              >
                <input
                  type="number"
                  :value="formData.minutes"
                  min="0"
                  class="w-full h-full text-4xl font-bold text-white drop-shadow-sm bg-transparent border-0 outline-none text-center [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                  @input="handleTimeInput"
                  @blur="handleTimeBlur"
                />
              </div>
              <span class="text-xs text-surface-600 dark:text-surface-400 text-center font-medium">
                {{ $t("classes.assignments.editModal.minutes") }}
              </span>
              <span class="text-xs text-surface-500 dark:text-surface-500 text-center mt-1">
                {{ $t("classes.assignments.editModal.minimumTimeRequired") }}
              </span>
            </div>
            <button
              class="w-12 h-12 rounded-lg bg-white dark:bg-surface-800 border border-surface-200 dark:border-surface-600 hover:bg-surface-50 dark:hover:bg-surface-700 flex items-center justify-center transition-colors shadow-sm flex-shrink-0"
              @click="formData.minutes++"
            >
              <Icon name="solar:add-circle-line-duotone" class="text-2xl text-surface-700 dark:text-surface-300" />
            </button>
          </div>
        </div>
      </div>

      <!-- Right Column (5 columns) -->
      <div class="col-span-12 lg:col-span-5 flex flex-col gap-4 md:gap-6">
        <!-- Limit Helpers -->
        <div>
          <div class="flex items-center gap-3 mb-4">
            <Icon name="solar:eye-line-duotone" class="text-2xl text-green-500 dark:text-green-400" />
            <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-100">
              {{ $t("classes.assignments.editModal.limitHelpers") }}
            </h3>
          </div>
          <div class="flex flex-col gap-3">
            <div
              class="flex items-center gap-3 p-4 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800"
            >
              <Icon
                name="solar:document-text-line-duotone"
                class="text-2xl text-green-600 dark:text-green-400 flex-shrink-0"
              />
              <div class="flex-1 min-w-0">
                <label class="text-sm font-medium text-surface-900 dark:text-surface-100 block">
                  {{ $t("classes.assignments.editModal.viewTranscription") }}
                </label>
              </div>
              <ToggleSwitch v-model="formData.viewTranscription" class="flex-shrink-0" />
            </div>

            <div
              class="flex items-center gap-3 p-4 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800"
            >
              <Icon
                name="solar:clipboard-list-line-duotone"
                class="text-2xl text-green-600 dark:text-green-400 flex-shrink-0"
              />
              <div class="flex-1 min-w-0">
                <label class="text-sm font-medium text-surface-900 dark:text-surface-100 block">
                  {{ $t("classes.assignments.editModal.viewSuggestions") }}
                </label>
              </div>
              <ToggleSwitch v-model="formData.viewHints" class="flex-shrink-0" />
            </div>

            <div
              class="flex items-center gap-3 p-4 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800"
            >
              <Icon
                name="solar:translation-line-duotone"
                class="text-2xl text-green-600 dark:text-green-400 flex-shrink-0"
              />
              <div class="flex-1 min-w-0">
                <label class="text-sm font-medium text-surface-900 dark:text-surface-100 block">
                  {{ $t("classes.assignments.editModal.viewTranslation") }}
                </label>
              </div>
              <ToggleSwitch v-model="formData.viewTranslation" class="flex-shrink-0" />
            </div>

            <div
              class="flex items-center gap-3 p-4 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800"
            >
              <Icon
                name="solar:global-line-duotone"
                class="text-2xl text-green-600 dark:text-green-400 flex-shrink-0"
              />
              <div class="flex-1 min-w-0">
                <label class="text-sm font-medium text-surface-900 dark:text-surface-100 block">
                  {{ $t("classes.assignments.editModal.nativeLanguage") }}
                </label>
              </div>
              <ToggleSwitch v-model="formData.nativeLanguage" class="flex-shrink-0" />
            </div>
          </div>
        </div>

        <!-- Show/Hide -->
        <div>
          <div class="flex items-center gap-3 mb-4">
            <Icon name="solar:eye-closed-line-duotone" class="text-2xl text-blue-500 dark:text-blue-400" />
            <h3 class="text-lg font-semibold text-surface-900 dark:text-surface-100">
              {{ $t("classes.assignments.editModal.showHide") }}
            </h3>
          </div>
          <div class="flex flex-col gap-3">
            <div
              class="flex items-center gap-3 p-4 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800"
            >
              <Icon
                name="solar:document-text-line-duotone"
                class="text-2xl text-green-600 dark:text-green-400 flex-shrink-0"
              />
              <div class="flex-1 min-w-0">
                <label class="text-sm font-medium text-surface-900 dark:text-surface-100 block">
                  {{ $t("classes.assignments.editModal.viewDescription") }}
                </label>
              </div>
              <ToggleSwitch v-model="formData.showScore" class="flex-shrink-0" />
            </div>

            <div
              class="flex items-center gap-3 p-4 rounded-lg bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800"
            >
              <Icon
                name="solar:checklist-line-duotone"
                class="text-2xl text-green-600 dark:text-green-400 flex-shrink-0"
              />
              <div class="flex-1 min-w-0">
                <label class="text-sm font-medium text-surface-900 dark:text-surface-100 block">
                  {{ $t("classes.assignments.editModal.viewRubrics") }}
                </label>
              </div>
              <ToggleSwitch v-model="formData.showProgress" class="flex-shrink-0" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div
        class="flex items-center justify-between px-4 md:px-6 py-4 border-t border-surface-200 dark:border-surface-700 w-full"
      >
        <div class="flex items-center gap-2 px-4 py-2 rounded-full bg-green-100 dark:bg-green-900/30">
          <Icon name="solar:check-circle-line-duotone" class="text-lg text-green-600 dark:text-green-400" />
          <span class="text-sm font-medium text-green-700 dark:text-green-300">
            {{ $t("classes.assignments.editModal.usingClassroomDefaults") }}
          </span>
        </div>
        <div class="flex items-center gap-3">
          <Button
            :label="$t('common.cancel')"
            variant="outlined"
            severity="secondary"
            class="flex items-center gap-2"
            @click="handleClose"
          >
            <template #icon>
              <Icon name="solar:close-circle-line-duotone" />
            </template>
          </Button>
          <Button
            :label="$t('classes.assignments.editModal.saveChanges')"
            class="bg-primary-600 text-white border-0 flex items-center gap-2"
            @click="handleSave"
          >
            <template #icon>
              <Icon name="solar:diskette-line-duotone" />
            </template>
          </Button>
        </div>
      </div>
    </template>
  </Dialog>
</template>
