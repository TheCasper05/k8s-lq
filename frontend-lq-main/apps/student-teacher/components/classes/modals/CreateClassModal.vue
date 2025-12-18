<script setup lang="ts">
  import { computed, watch } from "vue";
  import Message from "primevue/message";
  import { useCreateClass } from "~/composables/classes/useCreateClass";
  import ClassInfoTab from "./components/ClassInfoTab.vue";
  import TeachersTab from "./components/TeachersTab.vue";
  import StudentsTab from "./components/StudentsTab.vue";
  import type { Class } from "~/composables/classes/types";

  const props = defineProps<{
    visible: boolean;
  }>();

  const emit = defineEmits<{
    "update:visible": [value: boolean];
    "create-complete": [newClass: Class];
  }>();

  const {
    activeStep,
    formData,
    errors,
    loading,
    error,
    canProceedToNextStep,
    closeModal,
    createClass,
    validateStep1,
    validateStep2,
  } = useCreateClass();

  const stepSubtitles = computed<Record<string, string>>(() => ({
    "1": "classes.createModal.subtitle.classInfo",
    "2": "classes.createModal.subtitle.teachers",
    "3": "classes.createModal.subtitle.students",
  }));

  const updateFormData = (data: Partial<typeof formData.value>) => {
    Object.assign(formData.value, data);
  };

  const handleClose = () => {
    closeModal();
    emit("update:visible", false);
  };

  const handleNext = (activateCallback: (step: string) => void) => {
    if (activeStep.value === "1") {
      if (validateStep1()) {
        activateCallback("2");
      }
    } else if (activeStep.value === "2") {
      if (validateStep2()) {
        activateCallback("3");
      }
    } else if (activeStep.value === "3") {
      handleCreate();
    }
  };

  const handleBack = (activateCallback: (step: string) => void) => {
    if (activeStep.value === "2") {
      activateCallback("1");
    } else if (activeStep.value === "3") {
      activateCallback("2");
    }
  };

  const handleCreate = async () => {
    const result = await createClass();
    if (result.success) {
      handleClose();
      emit("create-complete", result.class);
    }
    // If error, the error will be shown in the modal via the error ref
  };

  watch(
    () => props.visible,
    (newValue) => {
      if (!newValue) {
        closeModal();
      }
    },
  );
</script>

<template>
  <Dialog
    :visible="visible"
    modal
    closable
    :draggable="false"
    class="w-full max-w-4xl"
    :pt="{
      root: { class: '!rounded-xl' },
      header: { class: '!border-b-0 !pb-0' },
      content: { class: '!pt-0' },
    }"
    @update:visible="handleClose"
  >
    <!-- Custom Header -->
    <template #header>
      <div class="flex items-center gap-4 mb-4">
        <div class="bg-primary-100 dark:bg-primary-900/30 rounded-lg p-3">
          <Icon name="solar:book-line-duotone" class="text-2xl text-primary-600 dark:text-primary-400" />
        </div>
        <div class="flex flex-col flex-1">
          <h2 class="text-2xl font-bold text-surface-900 dark:text-surface-100">
            {{ $t("classes.createModal.title") }}
          </h2>
          <p class="text-sm text-surface-600 dark:text-surface-400 mt-1">
            {{ $t(stepSubtitles[activeStep]) }}
          </p>
        </div>
      </div>
    </template>

    <!-- Error Message -->
    <div v-if="error" class="mb-4">
      <Message severity="error" closable>
        <div class="flex items-center justify-between">
          <span>{{ error }}</span>
          <button
            type="button"
            class="ml-2 text-surface-600 hover:text-surface-900 dark:text-surface-400 dark:hover:text-surface-100"
            @click="error = null"
          >
            <Icon name="solar:close-circle-line-duotone" class="text-lg" />
          </button>
        </div>
      </Message>
    </div>

    <!-- Content with Stepper -->
    <Stepper v-model:value="activeStep" class="w-full" :disabled="loading">
      <StepList>
        <Step value="1">{{ $t("classes.createModal.step1") }}</Step>
        <Step value="2">{{ $t("classes.createModal.step2") }}</Step>
        <Step value="3">{{ $t("classes.createModal.step3") }}</Step>
      </StepList>
      <StepPanels>
        <StepPanel v-slot="{ activateCallback }" value="1">
          <div class="py-4">
            <ClassInfoTab :form-data="formData" :errors="errors" @update:form-data="updateFormData" />
          </div>
          <div class="flex items-center justify-between gap-3 pt-4 border-t border-surface-200 dark:border-surface-700">
            <div />
            <div class="flex gap-3">
              <Button
                :label="$t('classes.createModal.cancel')"
                variant="outlined"
                severity="secondary"
                :disabled="loading"
                @click="handleClose"
              />
              <Button
                :disabled="!canProceedToNextStep || loading"
                class="bg-primary-600 text-white border-0 flex items-center gap-2"
                @click="handleNext(activateCallback)"
              >
                {{ $t("classes.createModal.next") }}
                <Icon name="solar:alt-arrow-right-line-duotone" />
              </Button>
            </div>
          </div>
        </StepPanel>

        <StepPanel v-slot="{ activateCallback }" value="2">
          <div class="py-4">
            <TeachersTab :form-data="formData" @update:form-data="updateFormData" />
          </div>
          <div class="flex items-center justify-between gap-3 pt-4 border-t border-surface-200 dark:border-surface-700">
            <Button
              :label="$t('classes.createModal.back')"
              variant="outlined"
              :disabled="loading"
              @click="handleBack(activateCallback)"
            >
              <template #icon>
                <Icon name="solar:alt-arrow-left-line-duotone" />
              </template>
            </Button>
            <div class="flex gap-3">
              <Button
                :label="$t('classes.createModal.cancel')"
                variant="outlined"
                severity="secondary"
                :disabled="loading"
                @click="handleClose"
              />
              <Button
                :disabled="!canProceedToNextStep || loading"
                class="bg-primary-600 text-white border-0 flex items-center gap-2"
                @click="handleNext(activateCallback)"
              >
                {{ $t("classes.createModal.next") }}
                <Icon name="solar:alt-arrow-right-line-duotone" />
              </Button>
            </div>
          </div>
        </StepPanel>

        <StepPanel v-slot="{ activateCallback }" value="3">
          <div class="py-4">
            <StudentsTab :form-data="formData" @update:form-data="updateFormData" />
          </div>
          <div class="flex items-center justify-between gap-3 pt-4 border-t border-surface-200 dark:border-surface-700">
            <Button
              :label="$t('classes.createModal.back')"
              variant="outlined"
              :disabled="loading"
              @click="handleBack(activateCallback)"
            >
              <template #icon>
                <Icon name="solar:alt-arrow-left-line-duotone" />
              </template>
            </Button>
            <div class="flex gap-3">
              <Button
                :label="$t('classes.createModal.cancel')"
                variant="outlined"
                severity="secondary"
                :disabled="loading"
                @click="handleClose"
              />
              <Button
                :disabled="!canProceedToNextStep || loading"
                :loading="loading"
                class="bg-primary-600 text-white border-0 flex items-center gap-2"
                @click="handleCreate"
              >
                <template v-if="!loading">
                  {{ $t("classes.createModal.create") }}
                  <Icon name="solar:check-circle-line-duotone" />
                </template>
              </Button>
            </div>
          </div>
        </StepPanel>
      </StepPanels>
    </Stepper>
  </Dialog>
</template>
