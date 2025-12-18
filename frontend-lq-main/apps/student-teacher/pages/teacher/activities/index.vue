<script setup lang="ts">
  import { useRouter } from "vue-router";
  import { LqSegmentedControl, LqSearchInput, LqSelect } from "@lq/ui";

  import { useActivities } from "~/composables/useActivities";
  import { CEFRLevel, type Activity } from "~/types/activities";
  import ActivitiesBanner from "~/components/activities/ActivitiesBanner.vue";
  import ActivityMetricCard from "~/components/activities/cards/ActivityMetricCard.vue";
  import ActivityCard from "~/components/activities/cards/ActivityCard.vue";
  import ActivitiesListView from "~/components/activities/table/ActivitiesListView.vue";
  import EmptyState from "~/components/activities/shared/EmptyState.vue";
  import QuickCreateModal from "~/components/activities/modals/QuickCreateModal.vue";
  import EditActivityModal from "~/components/activities/modals/EditActivityModal.vue";
  import EditWithAIModal from "~/components/activities/modals/EditWithAIModal.vue";
  import AssignToClassModal from "~/components/activities/modals/AssignToClassModal.vue";
  import AIChatModal from "~/components/activities/modals/AIChatModal.vue";
  import ShareLessonModal from "~/components/activities/modals/ShareLessonModal.vue";

  const router = useRouter();

  const {
    loading,
    searchQuery,
    levelFilter,
    viewMode,
    filteredActivities,
    metrics,
    fetchActivities,
    deleteActivity,
    toggleFavorite,
    updateActivity,
  } = useActivities();

  const deleteDialogVisible = ref(false);
  const activityToDelete = ref<string | null>(null);
  const selectedActivity = ref<Activity | null>(null);

  const shareVisible = ref(false);
  const shareActivity = ref<Activity | null>(null);
  const shareUrl = computed(() =>
    shareActivity.value ? `https://app.lingoquesto.com/lessons/share/${shareActivity.value.id}` : "",
  );

  // Modal states
  const quickCreateVisible = ref(false);
  const editVisible = ref(false);
  const editAIVisible = ref(false);
  const assignVisible = ref(false);
  const aiChatVisible = ref(false);

  const levelOptions = [
    { label: "A1", value: CEFRLevel.A1 },
    { label: "A2", value: CEFRLevel.A2 },
    { label: "B1", value: CEFRLevel.B1 },
    { label: "B2", value: CEFRLevel.B2 },
    { label: "C1", value: CEFRLevel.C1 },
    { label: "C2", value: CEFRLevel.C2 },
  ];

  const { t } = useI18n();

  const viewOptions = computed(() => [
    { label: t("teacher.scenarios.grid"), value: "grid" },
    { label: t("teacher.scenarios.list"), value: "list" },
  ]);

  onMounted(() => {
    fetchActivities();
  });

  const navigateToDetail = (id: string) => {
    router.push(`/teacher/activities/${id}`);
  };

  const openWizard = () => {
    // TODO: Implement wizard modal
  };

  const handleEdit = (activity: Activity) => {
    selectedActivity.value = activity;
    editVisible.value = true;
  };

  const handleDelete = (id: string) => {
    activityToDelete.value = id;
    deleteDialogVisible.value = true;
  };

  const confirmDelete = async () => {
    if (activityToDelete.value) {
      await deleteActivity(activityToDelete.value);
      deleteDialogVisible.value = false;
      activityToDelete.value = null;
    }
  };

  const handleActivityCreated = () => {
    fetchActivities();
  };

  const handleActivitySaved = async (activity: Activity) => {
    await updateActivity(activity.id, activity);
  };

  const handleAIChangesApplied = () => {
    // AI changes applied
  };

  const handleClassesAssigned = (_data: { classIds: string[]; studentIds: string[] }) => {
    // Assigned to classes
  };

  const handleShare = (activity: Activity) => {
    shareActivity.value = activity;
    shareVisible.value = true;
  };

  const handleAssignFromList = (activity: Activity) => {
    selectedActivity.value = activity;
    assignVisible.value = true;
  };

  const handleArchive = async (id: string) => {
    // TODO: Implement archive functionality
    console.log("Archive activity:", id);
  };
</script>

<template>
  <div class="lq-container">
    <!-- Metrics -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-4 sm:mb-6">
      <ActivityMetricCard v-for="metric in metrics" :key="metric.id" :metric="metric" variant="default" />
    </div>

    <!-- Banner -->
    <ActivitiesBanner @create="quickCreateVisible = true" />

    <!-- Filters & Search -->
    <div class="flex flex-col sm:flex-row gap-3 sm:gap-4 mb-6 sm:mb-8">
      <!-- Search -->
      <div class="flex-1">
        <LqSearchInput v-model="searchQuery" :placeholder="t('teacher.scenarios.searchPlaceholder')" />
      </div>

      <!-- Filter -->
      <LqSelect
        v-model="levelFilter"
        :options="levelOptions"
        option-label="label"
        option-value="value"
        :placeholder="t('teacher.scenarios.allLevels')"
        show-clear
        class="w-full sm:w-48"
      >
        <template #value="{ value }">
          <div class="flex items-center gap-2 text-surface-600 dark:text-surface-300">
            <Icon name="solar:filter-linear" class="text-primary-500 text-lg" />
            <span v-if="value">{{ value }}</span>
            <span v-else class="font-medium text-surface-600 dark:text-surface-400">
              {{ t("teacher.scenarios.allLevels") }}
            </span>
          </div>
        </template>
      </LqSelect>

      <!-- View Toggle -->
      <LqSegmentedControl v-model="viewMode" :options="viewOptions" />

      <!-- Export -->
      <Button
        :label="t('common.export')"
        class="!bg-emerald-500 hover:!bg-emerald-600 !border-emerald-500 !text-white !rounded-xl !font-semibold !px-4 sm:!px-6 !text-sm sm:!text-base"
      >
        <template #icon>
          <Icon name="solar:export-linear" class="mr-2 text-lg" />
        </template>
      </Button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-16">
      <ProgressSpinner />
    </div>

    <!-- Empty State -->
    <EmptyState
      v-else-if="!filteredActivities.length && !searchQuery && !levelFilter"
      @action="quickCreateVisible = true"
    />

    <!-- No Results -->
    <EmptyState
      v-else-if="!filteredActivities.length"
      :title="t('teacher.scenarios.noScenarios')"
      :description="t('teacher.scenarios.noScenarios')"
      :show-action="false"
    />

    <Transition
      mode="out-in"
      enter-active-class="page-forward-enter-active"
      enter-from-class="page-forward-enter-from"
      enter-to-class="page-forward-enter-to"
      leave-active-class="page-forward-leave-active"
      leave-from-class="page-forward-leave-from"
      leave-to-class="page-forward-leave-to"
    >
      <!-- Grid View -->
      <div
        v-if="viewMode === 'grid'"
        key="grid"
        class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4 gap-4 sm:gap-6"
      >
        <ActivityCard
          v-for="activity in filteredActivities"
          :key="activity.id"
          :activity="activity"
          @detail="navigateToDetail"
          @edit="handleEdit"
          @delete="handleDelete"
          @toggle-favorite="toggleFavorite"
          @share="handleShare"
          @assign="handleAssignFromList"
          @archive="handleArchive"
        />
      </div>

      <!-- List View -->
      <div v-else key="list" class="bg-transparent shadow-sm rounded-3xl p-0.5 overflow-hidden">
        <ActivitiesListView
          :activities="filteredActivities"
          @detail="navigateToDetail"
          @assign="handleAssignFromList"
          @toggle-favorite="toggleFavorite"
          @edit="handleEdit"
          @share="handleShare"
          @delete="handleDelete"
          @archive="handleArchive"
        />
      </div>
    </Transition>

    <!-- Modals -->
    <QuickCreateModal v-model:visible="quickCreateVisible" @open-wizard="openWizard" @created="handleActivityCreated" />

    <EditActivityModal v-model:visible="editVisible" :activity="selectedActivity" @save="handleActivitySaved" />

    <EditWithAIModal v-model:visible="editAIVisible" @apply="handleAIChangesApplied" />

    <AssignToClassModal v-model:visible="assignVisible" :activity="selectedActivity" @assign="handleClassesAssigned" />

    <AIChatModal v-model:visible="aiChatVisible" @create="handleActivityCreated" />

    <ShareLessonModal
      v-model:visible="shareVisible"
      :title="t('teacher.scenarios.detail.share.title') || 'Share Lesson'"
      :lesson-title="shareActivity?.title || ''"
      :share-url="shareUrl"
    />

    <!-- Delete Confirmation Dialog -->
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
