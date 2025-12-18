<script setup lang="ts">
  import { useRoute, useRouter } from "vue-router";
  import { LqHero } from "@lq/ui";
  import Button from "primevue/button";
  import type { Activity, AiSuggestion, SidebarDetailItem, ActionButtonConfig } from "~/types/activities";
  import {
    getMockActivities,
    getMockAssignedStudents,
    getMockActivityMetrics,
    getMockWeeklyProgressChart,
    getMockScoreDistributionChart,
    getMockTopPerformers,
    getMockAnalyticsInsights,
  } from "~/utils/mockActivities";
  import CEFRBadge from "~/components/shared/CEFRBadge.vue";
  import ActivityDetailsTab from "~/components/activities/tabs/ActivityDetailsTab.vue";
  import ActivityAssignedClassesTab from "~/components/activities/tabs/ActivityAssignedClassesTab.vue";
  import ActivityAnalyticsTab from "~/components/activities/tabs/ActivityAnalyticsTab.vue";
  import AssignToClassModal from "~/components/activities/modals/AssignToClassModal.vue";
  import EditActivityModal from "~/components/activities/modals/EditActivityModal.vue";
  import EditWithAIModal from "~/components/activities/modals/EditWithAIModal.vue";
  import ShareLessonModal from "~/components/activities/modals/ShareLessonModal.vue";

  const route = useRoute();
  const router = useRouter();

  const { t } = useI18n();

  const loading = ref(true);
  const activity = ref<Activity | null>(null);
  const activityId = computed(() => route.params.id as string);

  // Mock data - centralized in utils/mockActivities.ts
  const assignedStudents = computed(() => getMockAssignedStudents(activityId.value));

  const detailMetrics = computed(() => getMockActivityMetrics(activityId.value));

  const weeklyProgressChartData = computed(() => getMockWeeklyProgressChart(activityId.value));
  const scoreDistributionChartData = computed(() => getMockScoreDistributionChart(activityId.value));
  const topPerformers = computed(() => getMockTopPerformers(activityId.value));
  const analyticsInsights = computed(() => getMockAnalyticsInsights(activityId.value));

  // Modal states
  const assignVisible = ref(false);
  const editVisible = ref(false);
  const editAIVisible = ref(false);
  const deleteDialogVisible = ref(false);
  const shareVisible = ref(false);

  const selectedTab = ref("details");

  const tabs = computed(() => [
    { label: t("teacher.scenarios.detail.tabs.details"), value: "details" },
    { label: t("teacher.scenarios.detail.tabs.assignedClasses"), value: "assignedClasses" },
    { label: t("teacher.scenarios.detail.tabs.analytics"), value: "analytics" },
  ]);

  const currentActivity = computed<Activity>(() => activity.value as Activity);

  onMounted(async () => {
    await new Promise((resolve) => setTimeout(resolve, 500));
    const activities = getMockActivities();
    activity.value = activities.find((a) => a.id === activityId.value) || null;
    loading.value = false;
  });

  const handleAssignment = (_data: { classIds: string[]; studentIds: string[] }) => {
    assignVisible.value = false;
  };

  const handleSave = (updatedActivity: Activity) => {
    activity.value = updatedActivity;
    editVisible.value = false;
  };

  const handleAIEdit = () => {
    editAIVisible.value = false;
  };

  const confirmDelete = () => {
    deleteDialogVisible.value = false;
    router.push("/teacher/activities");
  };

  const shareUrl = computed(() => (activity.value ? `https://lingoquesto.ai/lessons/share/${activity.value.id}` : ""));

  const openShare = () => {
    shareVisible.value = true;
  };

  // Handlers
  const openTest = () => {
    // TODO: Implement test logic
  };

  const openAssign = () => {
    assignVisible.value = true;
  };

  const openEdit = () => {
    editVisible.value = true;
  };

  const openDelete = () => {
    deleteDialogVisible.value = true;
  };

  // Update objective handler (called from Details tab)
  const updateObjective = () => {
    // This will be called by the ActivityDetailsTab component
    // The actual update logic is handled within the component
  };

  // AI Suggestions
  const aiSuggestions = computed<AiSuggestion[]>(() => [
    {
      id: "difficulty",
      title: t("teacher.scenarios.detail.aiSuggestions.increaseDifficulty.title"),
      description: t("teacher.scenarios.detail.aiSuggestions.increaseDifficulty.description"),
      icon: "solar:target-line-duotone",
      color: "text-red-500 bg-red-50 dark:bg-red-500/10",
    },
    {
      id: "culture",
      title: t("teacher.scenarios.detail.aiSuggestions.culturalContext.title"),
      description: t("teacher.scenarios.detail.aiSuggestions.culturalContext.description"),
      icon: "solar:book-bookmark-line-duotone",
      color: "text-green-500 bg-green-50 dark:bg-green-500/10",
    },
    {
      id: "dialogue",
      title: t("teacher.scenarios.detail.aiSuggestions.moreDialogue.title"),
      description: t("teacher.scenarios.detail.aiSuggestions.moreDialogue.description"),
      icon: "solar:chat-round-line-duotone",
      color: "text-blue-500 bg-blue-50 dark:bg-blue-500/10",
    },
    {
      id: "grammar",
      title: t("teacher.scenarios.detail.aiSuggestions.focusGrammar.title"),
      description: t("teacher.scenarios.detail.aiSuggestions.focusGrammar.description"),
      icon: "solar:mortarboard-line-duotone",
      color: "text-amber-500 bg-amber-50 dark:bg-amber-500/10",
    },
  ]);

  const headerActions = computed<ActionButtonConfig[]>(() => [
    {
      id: "test",
      icon: "solar:play-line-duotone",
      label: t("common.actions.test"),
      severity: "info",
      class: "!rounded-lg",
      onClick: openTest,
    },
    {
      id: "assign",
      icon: "solar:user-plus-broken",
      label: t("teacher.scenarios.assign"),
      severity: "success",
      class: "!rounded-lg",
      onClick: openAssign,
    },
    {
      id: "delete",
      icon: "solar:trash-bin-trash-line-duotone",
      label: t("common.actions.delete"),
      severity: "danger",
      class: "!rounded-lg",
      onClick: openDelete,
    },
  ]);

  const sidebarDetails = computed<SidebarDetailItem[]>(() => [
    {
      id: "ai-role",
      icon: "🤖",
      iconClasses:
        "w-10 h-10 rounded-xl bg-violet-100 dark:bg-violet-500/20 flex items-center justify-center text-violet-600 dark:text-violet-300 shrink-0",
      label: t("teacher.scenarios.aiRole"),
      value: currentActivity.value.aiAssistantRole,
    },
    {
      id: "student-role",
      icon: "👤",
      iconClasses:
        "w-10 h-10 rounded-xl bg-blue-100 dark:bg-blue-500/20 flex items-center justify-center text-blue-600 dark:text-blue-300 shrink-0",
      label: t("teacher.scenarios.studentRole"),
      value: currentActivity.value.studentRole,
    },
    {
      id: "theme",
      icon: "🎭",
      iconClasses:
        "w-10 h-10 rounded-xl bg-emerald-100 dark:bg-emerald-500/20 flex items-center justify-center text-emerald-600 dark:text-emerald-300 shrink-0",
      label: t("teacher.scenarios.theme"),
      value: currentActivity.value.theme,
    },
  ]);
</script>

<template>
  <div class="py-4">
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-24">
      <ProgressSpinner />
    </div>

    <!-- Activity Not Found -->
    <div v-else-if="!activity" class="flex flex-col items-center justify-center py-24 text-center">
      <div class="w-20 h-20 bg-surface-100 dark:bg-surface-800 rounded-full flex items-center justify-center mb-6">
        <Icon name="solar:danger-circle-linear" class="text-3xl text-surface-400" />
      </div>
      <h2 class="text-2xl font-bold text-surface-900 dark:text-surface-0 mb-2">
        {{ t("teacher.scenarios.detail.notFoundTitle") }}
      </h2>
      <p class="text-surface-600 dark:text-surface-400 mb-8 max-w-md mx-auto">
        {{ t("teacher.scenarios.detail.notFoundDescription") }}
      </p>
      <Button :label="t('teacher.scenarios.back')" outlined @click="router.push('/teacher/activities')">
        <template #icon>
          <Icon name="solar:arrow-left-linear" />
        </template>
      </Button>
    </div>

    <!-- Main Content -->
    <div v-else class="space-y-8">
      <!-- Activity Header -->
      <LqHero
        variant="card"
        :image="currentActivity.coverImage"
        :title="currentActivity.title"
        show-play-button
        @back="router.go(-1)"
        @image-click="openTest"
      >
        <template #metadata>
          <div class="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3">
            <CEFRBadge no-color size="md" :text="`${t('common.level')}: `" :level="currentActivity.level" />
            <span class="hidden sm:inline text-primary-400 dark:text-primary-600 text-3xl">•</span>
            <span class="text-sm text-surface-600 dark:text-surface-400">{{ currentActivity.theme }}</span>
          </div>
        </template>

        <template #header-action>
          <Button
            :label="t('common.actions.share')"
            severity="secondary"
            outlined
            size="small"
            class="!bg-surface-900 !text-white !border-surface-900 hover:!bg-surface-800 dark:!bg-surface-0 dark:!text-surface-900 h-9 text-xs sm:text-sm w-full sm:w-auto justify-center"
            @click="openShare"
          >
            <template #icon>
              <Icon name="solar:share-line-duotone" class="text-base sm:text-lg" />
            </template>
          </Button>
        </template>

        <template #actions>
          <div class="flex flex-col sm:flex-row gap-2 sm:gap-3 w-full sm:w-auto">
            <Button
              v-for="action in headerActions"
              :key="action.id"
              :label="action.label"
              :severity="action.severity"
              size="small"
              :class="[action.class, 'w-full sm:w-auto text-xs sm:text-sm']"
              @click="action.onClick?.()"
            >
              <template #icon>
                <Icon :name="action.icon" class="text-base sm:text-lg" />
              </template>
            </Button>
          </div>
        </template>
      </LqHero>

      <!-- Content Area -->
      <div>
        <!-- Tabs (Pills) -->
        <div
          class="flex justify-center lg:justify-start gap-2 mb-6 overflow-x-auto pb-2 -mx-4 px-4 sm:mx-0 sm:px-0 scrollbar-hide"
        >
          <button
            v-for="tab in tabs"
            :key="tab.value"
            class="px-3 sm:px-4 py-1.5 rounded-lg text-xs sm:text-sm font-medium transition-colors whitespace-nowrap flex-shrink-0"
            :class="[
              selectedTab === tab.value
                ? 'bg-surface-900 text-white dark:bg-surface-0 dark:text-surface-900 shadow-sm'
                : 'bg-surface-0 text-surface-600 border border-surface-200 hover:bg-surface-50 dark:bg-surface-900 dark:text-surface-400 dark:border-surface-700',
            ]"
            @click="selectedTab = tab.value"
          >
            {{ tab.label }}
          </button>
        </div>

        <div class="grid grid-cols-1 gap-8">
          <!-- Tab Content -->
          <Transition
            mode="out-in"
            enter-active-class="page-forward-enter-active"
            enter-from-class="page-forward-enter-from"
            enter-to-class="page-forward-enter-to"
            leave-active-class="page-forward-leave-active"
            leave-from-class="page-forward-leave-from"
            leave-to-class="page-forward-leave-to"
          >
            <div :key="selectedTab" class="w-full">
              <ActivityDetailsTab
                v-if="selectedTab === 'details'"
                :activity="currentActivity"
                :ai-suggestions="aiSuggestions"
                :sidebar-details="sidebarDetails"
                @update="updateObjective"
                @edit="openEdit"
                @import="() => {}"
              />

              <ActivityAssignedClassesTab v-else-if="selectedTab === 'assignedClasses'" :students="assignedStudents" />

              <ActivityAnalyticsTab
                v-else-if="selectedTab === 'analytics'"
                :metrics="detailMetrics"
                :weekly-progress="weeklyProgressChartData"
                :score-distribution="scoreDistributionChartData"
                :top-performers="topPerformers"
                :insights="analyticsInsights"
              />
            </div>
          </Transition>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <AssignToClassModal
      :visible="assignVisible"
      :activity="currentActivity"
      @update:visible="assignVisible = $event"
      @assign="handleAssignment"
    />
    <EditActivityModal v-model:visible="editVisible" :activity="currentActivity" @save="handleSave" />
    <EditWithAIModal :visible="editAIVisible" @update:visible="editAIVisible = $event" @apply="handleAIEdit" />

    <ShareLessonModal
      v-if="activity"
      :visible="shareVisible"
      :title="t('teacher.scenarios.detail.share.title') || 'Share Lesson'"
      :lesson-title="currentActivity.title"
      :share-url="shareUrl"
      @update:visible="shareVisible = $event"
    />

    <!-- Delete Dialog -->
    <Dialog
      v-model:visible="deleteDialogVisible"
      :header="t('teacher.scenarios.deleteModal.title')"
      modal
      class="w-full max-w-md"
    >
      <p class="text-surface-700 dark:text-surface-300">
        {{ t("teacher.scenarios.deleteModal.message") }}
      </p>
      <template #footer>
        <Button
          :label="t('teacher.scenarios.deleteModal.cancel')"
          severity="secondary"
          outlined
          @click="deleteDialogVisible = false"
        />
        <Button :label="t('teacher.scenarios.deleteModal.delete')" severity="danger" @click="confirmDelete" />
      </template>
    </Dialog>
  </div>
</template>
