<script setup lang="ts">
  import Dialog from "primevue/dialog";
  import Button from "primevue/button";
  import Textarea from "primevue/textarea";
  import ProgressSpinner from "primevue/progressspinner";

  interface Props {
    visible: boolean;
  }

  interface Emits {
    "update:visible": [value: boolean];
    "apply": [];
  }

  const props = defineProps<Props>();
  const emit = defineEmits<Emits>();

  const { t } = useI18n();

  const prompt = ref("");
  const generating = ref(false);
  const hasChanges = ref(false);

  const suggestions = computed(() => [
    t("teacher.scenarios.editAIModal.suggestions.challenging"),
    t("teacher.scenarios.editAIModal.suggestions.context"),
    t("teacher.scenarios.editAIModal.suggestions.simplify"),
    t("teacher.scenarios.editAIModal.suggestions.vocabulary"),
  ]);

  watch(
    () => props.visible,
    (newVal) => {
      if (newVal) {
        prompt.value = "";
        hasChanges.value = false;
      }
    },
  );

  const applySuggestion = (suggestion: string) => {
    prompt.value = suggestion;
  };

  const generateChanges = async () => {
    generating.value = true;
    await new Promise((resolve) => setTimeout(resolve, 2500));
    generating.value = false;
    hasChanges.value = true;
  };

  const applyChanges = () => {
    emit("apply");
    emit("update:visible", false);
  };
</script>

<template>
  <Dialog
    :visible="visible"
    :header="t('teacher.scenarios.editAIModal.title')"
    modal
    class="w-full max-w-3xl"
    @update:visible="emit('update:visible', $event)"
  >
    <div class="space-y-6">
      <!-- Triple Gradient Header -->
      <div class="rounded-lg bg-gradient-to-r from-primary-600 via-pink-500 to-orange-500 p-6 -m-6 mb-6">
        <div class="flex items-center gap-3 mb-2">
          <Icon name="solar:stars-line-duotone" class="text-2xl text-white" />
          <h3 class="text-xl font-semibold text-white">{{ t("teacher.scenarios.editAIModal.header") }}</h3>
        </div>
        <p class="text-white/90">{{ t("teacher.scenarios.editAIModal.subtitle") }}</p>
      </div>

      <!-- Prompt Input -->
      <div>
        <label class="block text-sm font-medium text-surface-900 dark:text-surface-0 mb-2">
          {{ t("teacher.scenarios.editAIModal.label") }}
        </label>
        <Textarea
          v-model="prompt"
          rows="6"
          :maxlength="500"
          :placeholder="t('teacher.scenarios.editAIModal.placeholder')"
          class="w-full"
        />
        <div class="flex justify-between items-center mt-1">
          <small class="text-surface-500 dark:text-surface-400">{{ prompt.length }}/500 characters</small>
        </div>
      </div>

      <!-- Quick Suggestions -->
      <div>
        <p class="text-sm font-medium text-surface-900 dark:text-surface-0 mb-2">
          {{ t("teacher.scenarios.editAIModal.quickSuggestions") }}
        </p>
        <div class="flex flex-wrap gap-2">
          <Button
            v-for="suggestion in suggestions"
            :key="suggestion"
            :label="suggestion"
            size="small"
            outlined
            @click="applySuggestion(suggestion)"
          />
        </div>
      </div>

      <!-- Generating State -->
      <div v-if="generating" class="flex flex-col items-center justify-center py-8">
        <ProgressSpinner style="width: 50px; height: 50px" />
        <p class="text-surface-600 dark:text-surface-400 mt-4">{{ t("teacher.scenarios.editAIModal.generating") }}</p>
      </div>

      <!-- Generated Changes Preview -->
      <div
        v-if="hasChanges && !generating"
        class="bg-surface-50 dark:bg-surface-800 rounded-lg p-4 border border-surface-200 dark:border-surface-700"
      >
        <div class="flex items-center gap-2 mb-3">
          <Icon name="solar:check-circle-line-duotone" class="text-success-500" />
          <h4 class="font-semibold text-surface-900 dark:text-surface-0">
            {{ t("teacher.scenarios.editAIModal.generated") }}
          </h4>
        </div>
        <p class="text-sm text-surface-600 dark:text-surface-400">
          {{ t("teacher.scenarios.editAIModal.generatedDesc") }}
        </p>
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
        <Button
          v-if="!hasChanges"
          :label="t('common.actions.generate')"
          :disabled="!prompt || !prompt.trim()"
          :loading="generating"
          @click="generateChanges"
        >
          <template #icon>
            <Icon name="solar:stars-line-duotone" />
          </template>
        </Button>
        <Button v-else :label="t('common.actions.apply')" @click="applyChanges">
          <template #icon>
            <Icon name="solar:check-circle-line-duotone" />
          </template>
        </Button>
      </div>
    </template>
  </Dialog>
</template>
