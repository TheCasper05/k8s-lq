<script setup lang="ts">
  import Dialog from "primevue/dialog";
  import Button from "primevue/button";
  import InputText from "primevue/inputtext";
  import Textarea from "primevue/textarea";
  import Select from "primevue/select";
  import { CEFRLevel, type Activity } from "~/types/activities";

  interface Props {
    visible: boolean;
    activity: Activity | null;
  }

  interface Emits {
    "update:visible": [value: boolean];
    "save": [activity: Activity];
  }

  const props = defineProps<Props>();
  const emit = defineEmits<Emits>();

  const { t } = useI18n();

  const localActivity = ref<Activity | null>(null);
  const saving = ref(false);

  const dialogVisible = computed({
    get: () => props.visible,
    set: (value) => emit("update:visible", value),
  });

  const levelOptions = [
    { label: "A1", value: CEFRLevel.A1 },
    { label: "A2", value: CEFRLevel.A2 },
    { label: "B1", value: CEFRLevel.B1 },
    { label: "B2", value: CEFRLevel.B2 },
    { label: "C1", value: CEFRLevel.C1 },
    { label: "C2", value: CEFRLevel.C2 },
  ];

  watch(
    () => props.activity,
    (newActivity) => {
      if (newActivity) {
        localActivity.value = { ...newActivity };
      }
    },
    { immediate: true },
  );

  const saveChanges = async () => {
    if (!localActivity.value) return;

    saving.value = true;
    await new Promise((resolve) => setTimeout(resolve, 1000));
    emit("save", localActivity.value);
    saving.value = false;
    emit("update:visible", false);
  };
</script>

<template>
  <Dialog v-model:visible="dialogVisible" :header="t('teacher.scenarios.modal.title')" modal class="w-full max-w-3xl">
    <div v-if="localActivity" class="space-y-6">
      <!-- Header Gradient -->
      <div class="rounded-lg bg-gradient-to-r from-primary-600 to-primary-700 p-6 -m-6 mb-6">
        <h3 class="text-xl font-semibold text-white">{{ t("teacher.scenarios.modal.header") }}</h3>
        <p class="text-primary-100">{{ t("teacher.scenarios.modal.subtitle") }}</p>
      </div>

      <!-- Cover Image -->
      <div>
        <label class="block text-sm font-medium text-surface-900 dark:text-surface-0 mb-2">
          {{ t("teacher.scenarios.modal.coverImage") }}
        </label>
        <InputText
          v-model="localActivity.coverImage"
          :placeholder="t('teacher.scenarios.modal.coverImagePlaceholder')"
          class="w-full"
        />
      </div>

      <!-- Title -->
      <div>
        <label class="block text-sm font-medium text-surface-900 dark:text-surface-0 mb-2">
          {{ t("teacher.scenarios.modal.activityTitle") }} *
        </label>
        <InputText
          v-model="localActivity.title"
          :placeholder="t('teacher.scenarios.modal.activityTitlePlaceholder')"
          class="w-full"
        />
      </div>

      <!-- Learning Objective -->
      <div>
        <label class="block text-sm font-medium text-surface-900 dark:text-surface-0 mb-2">
          {{ t("teacher.scenarios.modal.learningObjective") }} *
        </label>
        <Textarea
          v-model="localActivity.learningObjective"
          rows="3"
          :placeholder="t('teacher.scenarios.modal.learningObjectivePlaceholder')"
          class="w-full"
        />
      </div>

      <!-- Roles Row -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-surface-900 dark:text-surface-0 mb-2">
            {{ t("teacher.scenarios.modal.aiRole") }}
          </label>
          <InputText
            v-model="localActivity.aiAssistantRole"
            :placeholder="t('teacher.scenarios.modal.aiRolePlaceholder')"
            class="w-full"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-surface-900 dark:text-surface-0 mb-2">
            {{ t("teacher.scenarios.modal.studentRole") }}
          </label>
          <InputText
            v-model="localActivity.studentRole"
            :placeholder="t('teacher.scenarios.modal.studentRolePlaceholder')"
            class="w-full"
          />
        </div>
      </div>

      <!-- Level and Theme Row -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-surface-900 dark:text-surface-0 mb-2">
            {{ t("teacher.scenarios.modal.cefrLevel") }} *
          </label>
          <Select
            v-model="localActivity.level"
            :options="levelOptions"
            option-label="label"
            option-value="value"
            :placeholder="t('teacher.scenarios.modal.selectLevel')"
            class="w-full"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-surface-900 dark:text-surface-0 mb-2">
            {{ t("teacher.scenarios.modal.theme") }}
          </label>
          <InputText
            v-model="localActivity.theme"
            :placeholder="t('teacher.scenarios.modal.themePlaceholder')"
            class="w-full"
          />
        </div>
      </div>

      <!-- Description -->
      <div>
        <label class="block text-sm font-medium text-surface-900 dark:text-surface-0 mb-2">
          {{ t("teacher.scenarios.modal.description") }}
        </label>
        <Textarea
          v-model="localActivity.description"
          rows="4"
          :placeholder="t('teacher.scenarios.modal.descriptionPlaceholder')"
          class="w-full"
        />
      </div>
    </div>

    <template #footer>
      <div class="flex gap-2">
        <Button
          :label="t('common.actions.cancel')"
          severity="secondary"
          outlined
          @click="$emit('update:visible', false)"
        />
        <Button :label="t('common.actions.save')" :loading="saving" @click="saveChanges">
          <template #icon>
            <Icon name="solar:check-circle-line-duotone" />
          </template>
        </Button>
      </div>
    </template>
  </Dialog>
</template>
