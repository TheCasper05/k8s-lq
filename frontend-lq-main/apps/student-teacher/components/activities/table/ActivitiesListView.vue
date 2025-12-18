<script setup lang="ts">
  import { LqDataTable, type LqDataTableColumn } from "@lq/ui";
  import type { Activity } from "~/types/activities";
  import CEFRBadge from "~/components/shared/CEFRBadge.vue";
  import ActivityActionsMenu from "~/components/activities/table/shared/ActivityActionsMenu.vue";

  interface Props {
    activities: Activity[];
  }

  interface Emits {
    detail: [id: string];
    assign: [activity: Activity];
    toggleFavorite: [id: string];
    edit: [activity: Activity];
    share: [activity: Activity];
    delete: [id: string];
    archive: [id: string];
  }

  const props = defineProps<Props>();
  const emit = defineEmits<Emits>();

  const { t } = useI18n();

  const columns = computed<LqDataTableColumn[]>(() => [
    { field: "title", header: t("teacher.scenarios.scenario"), class: "min-w-[300px]" },
    { field: "level", header: t("teacher.scenarios.level"), class: "w-32" },
    { field: "theme", header: t("teacher.scenarios.theme"), class: "w-48" },
    { field: "assignedClasses", header: t("teacher.scenarios.assignedClasses"), class: "w-40" },
  ]);
</script>

<template>
  <LqDataTable :data="props.activities" :columns="columns" :loading="false">
    <template #cell-title="{ data }">
      <div class="flex items-center gap-4 group cursor-pointer" @click="emit('detail', data.id)">
        <div class="relative w-16 h-12 rounded-xl overflow-hidden shrink-0 shadow-sm">
          <img
            :src="data.coverImage"
            :alt="data.title"
            class="w-full h-full object-contain transition-transform duration-300 group-hover:scale-110"
          />
        </div>
        <span
          class="font-bold text-surface-900 dark:text-surface-0 group-hover:text-primary-600 transition-colors line-clamp-2"
        >
          {{ data.title }}
        </span>
      </div>
    </template>

    <template #cell-level="{ data }">
      <CEFRBadge no-color :level="data.level" />
    </template>

    <template #cell-theme="{ data }">
      <span class="text-surface-600 dark:text-surface-300">{{ data.theme }}</span>
    </template>

    <template #cell-assignedClasses="{ data }">
      <div class="flex items-center gap-2 text-surface-500 dark:text-surface-400">
        <Icon name="solar:users-group-rounded-linear" class="text-lg" />
        <span class="font-medium">{{ data.assignedClasses }}</span>
      </div>
    </template>

    <template #actions="{ data }">
      <ActivityActionsMenu
        :activity="data"
        @detail="emit('detail', $event)"
        @assign="emit('assign', $event)"
        @edit="emit('edit', $event)"
        @delete="emit('delete', $event)"
        @archive="emit('archive', $event)"
        @share="emit('share', $event)"
        @toggle-favorite="emit('toggleFavorite', $event)"
      />
    </template>
  </LqDataTable>
</template>
