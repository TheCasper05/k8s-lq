<script setup lang="ts">
  import type { Activity, AiSuggestion, SidebarDetailItem, ActionButtonConfig } from "~/types/activities";
  import AiSuggestionsGrid from "~/components/activities/shared/AiSuggestionsGrid.vue";

  interface Props {
    activity: Activity;
    aiSuggestions: AiSuggestion[];
    sidebarDetails: SidebarDetailItem[];
  }

  const props = defineProps<Props>();
  const emit = defineEmits<{
    (e: "update" | "edit" | "import"): void;
  }>();

  const { t } = useI18n();

  const isEditing = ref(false);
  const editingObjective = ref("");
  const showAiSuggestions = ref(false);
  const aiSuggestionsSectionRef = ref<HTMLElement | null>(null);

  const startEditing = () => {
    isEditing.value = true;
    editingObjective.value = props.activity.learningObjective;
  };

  const cancelEditing = () => {
    isEditing.value = false;
    editingObjective.value = "";
    showAiSuggestions.value = false;
  };

  const updateObjective = () => {
    // Emit update event to parent
    emit("update");
    isEditing.value = false;
    showAiSuggestions.value = false;
  };

  const openEdit = () => {
    emit("edit");
  };

  const toggleAI = () => {
    showAiSuggestions.value = !showAiSuggestions.value;

    if (showAiSuggestions.value) {
      setTimeout(() => {
        if (aiSuggestionsSectionRef.value) {
          aiSuggestionsSectionRef.value.scrollIntoView({
            behavior: "smooth",
            block: "center",
          });
        }
      }, 200);
    }
  };

  const applyAiSuggestion = (suggestion: AiSuggestion) => {
    editingObjective.value = `${editingObjective.value}\n\n[AI Adjustment: ${suggestion.title}]`;
    if (!isEditing.value) {
      startEditing();
    }
    showAiSuggestions.value = false;
  };

  const viewActions = computed<ActionButtonConfig[]>(() => [
    {
      id: "import",
      icon: "solar:upload-minimalistic-line-duotone",
      label: t("common.actions.import"),
      severity: "secondary",
      outlined: true,
      class: "px-4 py-2 font-semibold border-surface-300 hover:bg-surface-50",
      onClick: () => emit("import"),
    },
    {
      id: "ai-edit",
      icon: "lucide:wand-sparkles",
      label: t("teacher.scenarios.detail.editAI"),
      severity: "help",
      outlined: true,
      class: "px-4 py-2 font-semibold text-violet-600 border-violet-200 bg-violet-50 hover:bg-violet-100",
      onClick: toggleAI,
    },
    {
      id: "update-disabled",
      icon: "lucide:sparkles",
      label: t("common.actions.update"),
      severity: "secondary",
      disabled: true,
      class:
        "px-6 py-2 font-semibold bg-surface-900 text-surface-0 border-surface-900 hover:bg-surface-800 dark:bg-surface-0 dark:text-surface-900",
      onClick: openEdit,
    },
  ]);

  const editActions = computed<ActionButtonConfig[]>(() => [
    {
      id: "cancel",
      icon: "solar:close-circle-linear",
      label: t("common.actions.cancel"),
      severity: "danger",
      outlined: true,
      class: "px-4 py-2",
      onClick: cancelEditing,
    },
    {
      id: "import-edit",
      icon: "solar:upload-minimalistic-line-duotone",
      label: t("common.actions.import"),
      severity: "secondary",
      outlined: true,
      class: "px-4 py-2 font-semibold border-surface-300 hover:bg-surface-50",
      onClick: () => emit("import"),
    },
    {
      id: "ai-edit-edit",
      icon: "lucide:wand-sparkles",
      label: t("teacher.scenarios.detail.editAI"),
      severity: "help",
      outlined: true,
      class: "px-4 py-2 font-semibold text-violet-600 border-violet-200 bg-violet-50 hover:bg-violet-100",
      onClick: toggleAI,
    },
    {
      id: "update",
      icon: "solar:check-circle-line-duotone",
      label: t("common.actions.update"),
      severity: "primary",
      class: "px-6 py-2 bg-violet-500 border-violet-500 hover:bg-violet-600",
      onClick: updateObjective,
    },
  ]);
</script>

<template>
  <div class="grid grid-cols-1 xl:grid-cols-3 gap-8">
    <!-- Main Column -->
    <div class="xl:col-span-2 space-y-6 animate-fade-in">
      <!-- Learning Goal Card (Primary Focus) -->
      <div
        class="bg-surface-0 dark:bg-surface-900 rounded-2xl p-8 border shadow-sm flex flex-col items-center text-center transition-colors duration-200"
        :class="[isEditing ? 'border-violet-500 ring-1 ring-violet-500' : 'border-surface-200 dark:border-surface-700']"
      >
        <h3 class="text-2xl font-bold text-surface-900 dark:text-surface-0 mb-2">
          {{ t("teacher.scenarios.detail.learningGoalQuestion") }}
        </h3>
        <p class="text-surface-500 dark:text-surface-400 mb-8 max-w-lg mx-auto">
          {{ t("teacher.scenarios.detail.learningGoalHint") }}
        </p>

        <!-- Textarea look-alike (Read Mode) -->
        <div
          v-if="!isEditing"
          class="w-full min-h-[200px] p-6 rounded-xl border border-surface-200 dark:border-surface-700 bg-white dark:bg-surface-800 text-left text-lg text-surface-600 dark:text-surface-300 shadow-sm mb-2 relative group cursor-pointer transition-all hover:border-violet-300"
          @click="startEditing"
        >
          <div class="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
            <Button text rounded severity="secondary" size="small">
              <template #icon>
                <Icon name="solar:pen-new-square-linear" />
              </template>
            </Button>
          </div>
          {{ activity.learningObjective }}
        </div>

        <!-- Textarea (Edit Mode) -->
        <div v-else class="w-full relative mb-2">
          <div class="absolute top-4 right-4 z-10">
            <span
              class="bg-violet-500 text-white text-[10px] font-bold px-2 py-1 rounded-md shadow-sm uppercase tracking-wider"
            >
              {{ t("teacher.scenarios.detail.editing") }}
            </span>
          </div>
          <Textarea
            v-model="editingObjective"
            class="w-full min-h-[200px] p-6 rounded-xl border-violet-500 bg-violet-50 dark:bg-violet-500/10 text-lg shadow-sm focus:ring-0 !text-surface-900 dark:!text-surface-0 placeholder:text-surface-400"
            auto-resize
          />
        </div>

        <!-- AI Suggestions Grid (between textarea and actions) -->
        <div ref="aiSuggestionsSectionRef" class="w-full">
          <AiSuggestionsGrid
            :visible="showAiSuggestions"
            :title="t('teacher.scenarios.detail.aiSuggestions.title')"
            :suggestions="aiSuggestions"
            @apply="applyAiSuggestion"
          />
        </div>

        <div class="w-full flex flex-col sm:flex-row items-stretch sm:items-center justify-end gap-2 sm:gap-3 mt-6">
          <template v-if="!isEditing">
            <Button
              v-for="action in viewActions"
              :key="action.id"
              :severity="action.severity"
              :outlined="action.outlined"
              :disabled="action.disabled"
              :class="[action.class, 'w-full sm:w-auto justify-center text-sm']"
              @click="action.onClick && action.onClick()"
            >
              <Icon :name="action.icon" />
              {{ action.label }}
            </Button>
          </template>

          <!-- Edit Mode Actions -->
          <template v-else>
            <Button
              v-for="action in editActions"
              :key="action.id"
              :label="action.label"
              :severity="action.severity"
              :outlined="action.outlined"
              :disabled="action.disabled"
              :class="[action.class, 'w-full sm:w-auto justify-center text-sm']"
              @click="action.onClick && action.onClick()"
            >
              <template #icon>
                <Icon :name="action.icon" />
              </template>
            </Button>
          </template>
        </div>
      </div>
    </div>

    <!-- Sidebar Column -->
    <div class="xl:col-span-1 space-y-6">
      <div class="space-y-6">
        <!-- Scenario Details -->
        <div
          class="bg-surface-0 dark:bg-surface-900 rounded-2xl p-6 border border-surface-200 dark:border-surface-700 shadow-sm"
        >
          <h3 class="text-base font-bold text-surface-900 dark:text-surface-0 mb-6">
            {{ t("teacher.scenarios.detail.details") }}
          </h3>

          <div class="space-y-4">
            <div
              v-for="item in sidebarDetails"
              :key="item.id"
              class="flex items-center gap-3 p-2 hover:bg-surface-50 dark:hover:bg-surface-800 rounded-lg transition-colors"
            >
              <div :class="item.iconClasses">
                <span class="text-xl">{{ item.icon }}</span>
              </div>
              <div class="text-sm">
                <span class="font-semibold text-surface-600 dark:text-surface-400">
                  {{ item.label }}
                </span>
                <span class="mx-2 text-surface-400">→</span>
                <span class="font-bold text-surface-900 dark:text-surface-100">
                  {{ item.value }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Description Sidebar Card -->
        <div
          class="bg-surface-0 dark:bg-surface-900 rounded-2xl p-6 border border-surface-200 dark:border-surface-700 shadow-sm"
        >
          <h3 class="text-base font-bold text-surface-900 dark:text-surface-0 mb-4">
            {{ t("teacher.scenarios.description") }}
          </h3>
          <p class="text-surface-600 dark:text-surface-400 text-sm leading-relaxed">
            {{ activity.description }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
