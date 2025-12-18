<script setup lang="ts">
  import { LqDataTable, type LqDataTableColumn } from "@lq/ui";
  import type { LeaderboardEntry } from "~/composables/classes/types";

  interface Props {
    leaderboard: LeaderboardEntry[];
    getBadgeClass: (level: string) => string;
    getRankBadgeClass: (rank: number) => string;
  }

  const props = defineProps<Props>();

  const { t } = useI18n();

  const columns = computed<LqDataTableColumn[]>(() => [
    {
      field: "rank",
      header: t("classes.statistics.rank"),
      class: "min-w-[90px]",
    },
    {
      field: "student",
      header: t("classes.statistics.student"),
      class: "min-w-[220px]",
    },
    {
      field: "score",
      header: t("classes.statistics.score"),
      class: "min-w-[170px]",
    },
    {
      field: "completed",
      header: t("classes.statistics.completed"),
      class: "min-w-[200px]",
    },
    {
      field: "time",
      header: t("classes.statistics.time"),
      class: "min-w-[160px]",
    },
  ]);

  const tablePT = {
    root: { class: "border-0 bg-transparent" },
    thead: { class: "" },
    column: {
      headerCell: {
        class:
          "text-left py-2 md:py-3 px-3 md:px-4 text-xs md:text-sm font-semibold text-surface-700 dark:text-surface-300 border-b border-surface-200 dark:border-surface-700",
      },
    },
    bodyRow: {
      class: "border-b border-surface-200 dark:border-surface-700",
    },
    bodyCell: { class: "py-2 md:py-3 px-3 md:px-4 align-middle" },
  };

  const rowClass = (entry: LeaderboardEntry) => {
    return [entry.rank === 1 ? "bg-warning-50 dark:bg-warning-900/10" : ""];
  };
</script>

<template>
  <div class="overflow-x-auto -mx-4 md:mx-0">
    <LqDataTable
      :data="props.leaderboard"
      :columns="columns"
      :scrollable="false"
      embedded
      :pt="tablePT"
      :row-class="rowClass"
      class="w-full min-w-[600px]"
    >
      <template #cell-rank="{ data }">
        <div
          :class="[
            'w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold',
            props.getRankBadgeClass(data.rank),
          ]"
        >
          {{ data.rank }}
        </div>
      </template>

      <template #cell-student="{ data }">
        <div class="flex items-center gap-3">
          <img
            :src="data.studentPhoto || 'https://i.pravatar.cc/150?img=' + data.rank"
            :alt="data.studentName"
            class="w-10 h-10 rounded-full"
          />
          <span class="font-medium text-surface-900 dark:text-surface-50">
            {{ data.studentName }}
          </span>
        </div>
      </template>

      <template #cell-score="{ data }">
        <div class="flex items-center gap-2">
          <span class="px-3 py-1 rounded bg-info-500 dark:bg-info-600 text-white text-sm font-semibold">
            {{ data.score }}%
          </span>
          <span :class="props.getBadgeClass(data.cefrLevel)">
            {{ data.cefrLevel }}
          </span>
        </div>
      </template>

      <template #cell-completed="{ data }">
        <div class="flex items-center gap-3">
          <span class="text-sm text-surface-700 dark:text-surface-300">
            {{ data.completedCount }}/{{ data.totalCount }}
          </span>
          <div class="flex-1 max-w-[100px]">
            <div class="w-full bg-surface-200 dark:bg-surface-700 rounded-full h-2">
              <div
                class="bg-primary-600 dark:bg-primary-500 h-2 rounded-full"
                :style="{
                  width: `${(data.completedCount / data.totalCount) * 100}%`,
                }"
              />
            </div>
          </div>
        </div>
      </template>

      <template #cell-time="{ data }">
        <div class="flex items-center gap-2 text-surface-700 dark:text-surface-300">
          <Icon name="solar:clock-circle-line-duotone" class="text-lg" />
          <span class="text-sm">{{ data.practiceTime }}</span>
        </div>
      </template>
    </LqDataTable>
  </div>
</template>
