<script setup lang="ts">
  import { ref } from "vue";

  interface Props {
    activeTab?: "assignments" | "gradebook" | "students" | "statistics";
  }

  const props = withDefaults(defineProps<Props>(), {
    activeTab: undefined,
  });

  const emit = defineEmits<{
    "update:active-tab": [value: "assignments" | "gradebook" | "students" | "statistics"];
  }>();

  const activeTabValue = ref<"assignments" | "gradebook" | "students" | "statistics">(props.activeTab || "assignments");

  const setActiveTab = (tab: "assignments" | "gradebook" | "students" | "statistics") => {
    activeTabValue.value = tab;
    emit("update:active-tab", tab);
  };
</script>

<template>
  <div class="w-full border border-surface-200 dark:border-surface-700 rounded-lg">
    <!-- Tabs Container -->
    <div class="w-full border-b border-surface-200 dark:border-surface-700 mb-4 md:mb-6">
      <div class="flex w-full overflow-x-auto flex-nowrap scrollbar-hide">
        <!-- Assignments Tab -->
        <button
          type="button"
          :class="[
            'flex-1 min-w-0 flex items-center justify-center gap-1 md:gap-2 px-2 md:px-4 py-2 md:py-3 font-semibold rounded-t-lg transition-colors cursor-pointer whitespace-nowrap',
            activeTabValue === 'assignments'
              ? 'bg-black dark:bg-white text-white dark:text-black'
              : 'text-surface-600 dark:text-surface-400 hover:text-surface-900 dark:hover:text-surface-100',
          ]"
          @click="setActiveTab('assignments')"
        >
          <Icon name="solar:document-line-duotone" class="text-base md:text-lg flex-shrink-0" />
          <span class="text-xs md:text-sm lg:text-base truncate">Assignments</span>
        </button>

        <!-- Gradebook Tab -->
        <button
          type="button"
          :class="[
            'flex-1 min-w-0 flex items-center justify-center gap-1 md:gap-2 px-2 md:px-4 py-2 md:py-3 font-semibold rounded-t-lg transition-colors cursor-pointer whitespace-nowrap',
            activeTabValue === 'gradebook'
              ? 'bg-black dark:bg-white text-white dark:text-black'
              : 'text-surface-600 dark:text-surface-400 hover:text-surface-900 dark:hover:text-surface-100',
          ]"
          @click="setActiveTab('gradebook')"
        >
          <Icon name="solar:chart-2-line-duotone" class="text-base md:text-lg flex-shrink-0" />
          <span class="text-xs md:text-sm lg:text-base truncate">Gradebook</span>
        </button>

        <!-- Students Tab -->
        <button
          type="button"
          :class="[
            'flex-1 min-w-0 flex items-center justify-center gap-1 md:gap-2 px-2 md:px-4 py-2 md:py-3 font-semibold rounded-t-lg transition-colors cursor-pointer whitespace-nowrap',
            activeTabValue === 'students'
              ? 'bg-black dark:bg-white text-white dark:text-black'
              : 'text-surface-600 dark:text-surface-400 hover:text-surface-900 dark:hover:text-surface-100',
          ]"
          @click="setActiveTab('students')"
        >
          <Icon name="solar:users-group-rounded-line-duotone" class="text-base md:text-lg flex-shrink-0" />
          <span class="text-xs md:text-sm lg:text-base truncate">Students</span>
        </button>

        <!-- Statistics Tab -->
        <button
          type="button"
          :class="[
            'flex-1 min-w-0 flex items-center justify-center gap-1 md:gap-2 px-2 md:px-4 py-2 md:py-3 font-semibold rounded-t-lg transition-colors cursor-pointer whitespace-nowrap',
            activeTabValue === 'statistics'
              ? 'bg-black dark:bg-white text-white dark:text-black'
              : 'text-surface-600 dark:text-surface-400 hover:text-surface-900 dark:hover:text-surface-100',
          ]"
          @click="setActiveTab('statistics')"
        >
          <Icon name="solar:chart-2-line-duotone" class="text-base md:text-lg flex-shrink-0" />
          <span class="text-xs md:text-sm lg:text-base truncate">Statistics</span>
        </button>
      </div>
    </div>

    <!-- Tab Content -->
    <div class="w-full px-3 md:px-6 pb-4 md:pb-6">
      <Transition
        mode="out-in"
        enter-active-class="page-forward-enter-active"
        enter-from-class="page-forward-enter-from"
        enter-to-class="page-forward-enter-to"
        leave-active-class="page-forward-leave-active"
        leave-from-class="page-forward-leave-from"
        leave-to-class="page-forward-leave-to"
      >
        <div :key="activeTabValue" class="w-full">
          <div v-if="activeTabValue === 'assignments'">
            <slot name="assignments" />
          </div>
          <div v-else-if="activeTabValue === 'gradebook'">
            <slot name="gradebook" />
          </div>
          <div v-else-if="activeTabValue === 'students'">
            <slot name="students" />
          </div>
          <div v-else-if="activeTabValue === 'statistics'">
            <slot name="statistics" />
          </div>
        </div>
      </Transition>
    </div>
  </div>
</template>
