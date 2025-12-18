<script setup lang="ts">
  import { LqDataTable, LqSearchInput, type LqDataTableColumn, LqAvatar } from "@lq/ui";

  type StudentStatus = "completed" | "pending";

  export interface AssignedStudent {
    id: string;
    name: string;
    avatarUrl?: string;
    className: string;
    status: StudentStatus;
    score?: number | null;
  }

  interface Props {
    students: AssignedStudent[];
  }

  const props = defineProps<Props>();

  const searchQuery = ref("");
  const completedCount = computed(() => props.students.filter((s) => s.status === "completed").length);
  const pendingCount = computed(() => props.students.filter((s) => s.status === "pending").length);

  const { t } = useI18n();

  const columns = computed<LqDataTableColumn[]>(() => [
    { field: "name", header: t("common.student"), class: "min-w-[150px]" },
    { field: "className", header: t("common.class"), class: "min-w-[150px]" },
    { field: "status", header: t("common.status"), class: "w-40" },
    { field: "score", header: t("common.score"), class: "w-32" },
  ]);
</script>

<template>
  <LqDataTable :data="students" :columns="columns" :loading="false">
    <template #header>
      <div>
        <h3 class="text-base font-bold text-surface-900 dark:text-surface-0 mb-2">
          {{ t("teacher.scenarios.detail.assignedStudents.title") }}
        </h3>
        <div class="flex items-center gap-4 text-xs font-medium">
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-emerald-500" />
            <span class="text-surface-600 dark:text-surface-400">
              {{ completedCount }} {{ t("teacher.scenarios.detail.assignedStudents.completed") }}
            </span>
          </div>
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-amber-400" />
            <span class="text-surface-600 dark:text-surface-400">
              {{ pendingCount }} {{ t("teacher.scenarios.detail.assignedStudents.pending") }}
            </span>
          </div>
        </div>
      </div>

      <LqSearchInput
        v-model="searchQuery"
        :placeholder="t('teacher.scenarios.detail.assignedStudents.filterPlaceholder')"
        icon-name="solar:filter-linear"
        container-class="w-64"
      />
    </template>

    <template #cell-name="{ data }">
      <div class="flex items-center gap-4">
        <div class="relative">
          <LqAvatar
            :src="data.avatarUrl"
            :initials="data.name.charAt(0)"
            size="md"
            avatar-class="bg-surface-100 dark:bg-surface-800 text-surface-600 dark:text-surface-200"
          />
        </div>
        <div class="font-bold text-surface-700 dark:text-surface-0 text-sm">
          {{ data.name }}
        </div>
      </div>
    </template>

    <template #cell-className="{ data }">
      <div class="text-surface-500 dark:text-surface-400 text-sm">
        {{ data.className }}
      </div>
    </template>

    <template #cell-status="{ data }">
      <span
        v-if="data.status === 'completed'"
        class="inline-flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-bold bg-emerald-100/50 text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-400"
      >
        <Icon name="lucide:check" class="text-sm" />
        {{ t("teacher.scenarios.detail.assignedStudents.completed") }}
      </span>
      <span
        v-else
        class="inline-flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-bold bg-orange-100/50 text-orange-600 dark:bg-orange-500/10 dark:text-orange-400"
      >
        <Icon name="solar:clock-circle-linear" class="text-sm" />
        {{ t("teacher.scenarios.detail.assignedStudents.pending") }}
      </span>
    </template>

    <template #cell-score="{ data }">
      <span
        v-if="typeof data.score === 'number'"
        class="inline-flex items-center justify-center px-3 py-1 rounded-md text-xs font-bold bg-violet-100 text-violet-600 dark:bg-violet-500/10 dark:text-violet-300 min-w-[3rem]"
      >
        {{ data.score }}%
      </span>
      <span v-else class="text-surface-300 dark:text-surface-600 text-xs px-3">—</span>
    </template>

    <template #actions="{ data }">
      <div class="flex justify-end">
        <button
          v-if="data.status === 'pending'"
          class="inline-flex items-center gap-2 px-3 py-1.5 rounded-md bg-surface-900 text-white text-xs font-medium shadow-sm hover:bg-surface-800 dark:bg-surface-0 dark:text-surface-900 transition-colors"
        >
          <Icon name="solar:letter-linear" class="text-sm" />
          <span>{{ t("teacher.scenarios.detail.assignedStudents.sendReminder") }}</span>
        </button>
      </div>
    </template>
  </LqDataTable>
</template>
