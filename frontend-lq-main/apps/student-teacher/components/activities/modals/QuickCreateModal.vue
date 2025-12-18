<script setup lang="ts">
  interface Props {
    visible: boolean;
  }

  interface Emits {
    "update:visible": [value: boolean];
    "created": [];
  }

  const props = defineProps<Props>();
  const emit = defineEmits<Emits>();

  const { t } = useI18n();

  const prompt = ref("");
  const generating = ref(false);

  const dialogVisible = computed({
    get: () => props.visible,
    set: (value) => emit("update:visible", value),
  });

  const quickSuggestions = computed(() => [
    { id: "restaurant", label: t("teacher.scenarios.quickCreateModal.suggestions.restaurant"), icon: "🍽️" },
    { id: "travel", label: t("teacher.scenarios.quickCreateModal.suggestions.travel"), icon: "✈️" },
    { id: "interview", label: t("teacher.scenarios.quickCreateModal.suggestions.interview"), icon: "💼" },
    { id: "shopping", label: t("teacher.scenarios.quickCreateModal.suggestions.shopping"), icon: "🛒" },
  ]);

  watch(
    () => props.visible,
    (newVal) => {
      if (newVal) {
        prompt.value = "";
      }
    },
  );

  const selectSuggestion = (suggestion: string) => {
    // TODO: Auto-fill prompt with suggestion based on template
    prompt.value = `Create a ${suggestion} scenario for my students...`;
  };

  const handleClose = () => {
    emit("update:visible", false);
  };

  const generateFromPrompt = async () => {
    generating.value = true;
    // Simulate AI generation
    await new Promise((resolve) => setTimeout(resolve, 2000));
    generating.value = false;
    emit("created");
    handleClose();
  };
</script>

<template>
  <Dialog
    v-model:visible="dialogVisible"
    modal
    :closable="false"
    :draggable="false"
    class="w-full max-w-4xl"
    :pt="{
      root: { class: '!rounded-2xl !overflow-hidden' },
      mask: { class: 'backdrop-blur-sm' },
      header: { class: '!hidden' },
      content: { class: '!p-0 !m-0' },
    }"
  >
    <div class="p-8 bg-surface-0 dark:bg-surface-900">
      <!-- Close Button -->
      <div class="flex justify-end mb-4">
        <button
          class="text-surface-400 hover:text-surface-600 dark:hover:text-surface-300 transition-colors"
          @click="handleClose"
        >
          <Icon name="solar:close-circle-linear" class="text-xl" />
        </button>
      </div>

      <!-- Header with Icon -->
      <div class="flex flex-col items-center mb-6">
        <div class="relative mb-4">
          <div class="absolute inset-0 bg-gradient-to-br from-purple-500 to-pink-500 opacity-60 blur-2xl" />
          <div
            class="relative w-16 h-16 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 text-white flex items-center justify-center shadow-2xl"
          >
            <Icon name="lucide:wand-sparkles" class="text-3xl" />
          </div>
        </div>
        <h2 class="text-2xl font-bold text-surface-900 dark:text-surface-0 mb-2">
          {{ t("teacher.scenarios.quickCreateModal.title") }}
        </h2>
        <p class="text-surface-600 dark:text-surface-400 text-center">
          {{ t("teacher.scenarios.quickCreateModal.subtitle") }}
        </p>
      </div>

      <!-- Textarea with AI Improve Button -->
      <div class="mb-4">
        <div class="relative">
          <Textarea
            v-model="prompt"
            rows="6"
            :placeholder="t('teacher.scenarios.quickCreateModal.placeholder')"
            class="w-full !pr-32 resize-none !border-[3px] !rounded-2xl !border-surface-100 dark:!border-surface-600"
          />
          <button
            class="absolute bottom-3 right-3 flex gap-1 items-center px-3 py-1.5 text-sm font-bold hover:bg-primary-50 dark:hover:bg-primary-900/20 rounded-lg transition-colors"
          >
            <Icon
              name="charm:lightning-bolt"
              class="text-xl bg-gradient-to-r from-[#967AFE] to-[#FFAF54] text-transparent"
            />
            <span>{{ t("teacher.scenarios.quickCreateModal.improve") }}</span>
          </button>
        </div>
      </div>

      <!-- File Upload Area -->
      <div class="mb-6">
        <div
          class="transition-all border-2 bg-surface-50/50 dark:bg-surface-900 border-surface-100 rounded-2xl p-8 text-center hover:border-primary-400 dark:hover:border-primary-500 dark:hover:bg-primary-900/10 cursor-pointer"
        >
          <Icon name="solar:upload-minimalistic-line-duotone" class="text-3xl text-surface-400 mb-3" />
          <p class="text-surface-900 dark:text-surface-0 font-medium mb-1">
            {{ t("teacher.scenarios.quickCreateModal.uploadTitle") }}
          </p>
          <p class="text-sm text-surface-500 dark:text-surface-400">
            {{ t("teacher.scenarios.quickCreateModal.uploadDesc") }}
          </p>
        </div>
      </div>

      <!-- Quick Suggestions -->
      <div class="mb-6">
        <div class="flex items-center justify-center gap-2 mb-3">
          <Icon name="solar:lightbulb-bolt-line-duotone" class="text-primary-400 dark:text-primary-400" />
          <span class="text-sm font-medium">
            {{ t("teacher.scenarios.quickCreateModal.suggestionsTitle") }}
          </span>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
          <button
            v-for="suggestion in quickSuggestions"
            :key="suggestion.id"
            class="flex flex-col items-center gap-2 p-4 bg-surface-50/50 rounded-lg border border-surface-50/50 dark:border-surface-700 hover:border-primary-400 dark:hover:border-primary-500 hover:bg-primary-50 dark:hover:bg-primary-900/10 transition-all"
            @click="selectSuggestion(suggestion.id)"
          >
            <span class="text-3xl">{{ suggestion.icon }}</span>
            <span class="text-sm font-medium text-surface-900 dark:text-surface-0">{{ suggestion.label }}</span>
          </button>
        </div>
      </div>

      <!-- Footer Actions -->
      <div class="flex justify-end pt-4 border-t border-surface-200 dark:border-surface-700">
        <Button
          :label="t('common.actions.generate')"
          :disabled="!prompt.trim() || generating"
          :loading="generating"
          @click="generateFromPrompt"
        >
          <template #icon>
            <Icon name="solar:stars-line-duotone" />
          </template>
        </Button>
      </div>
    </div>
  </Dialog>
</template>
