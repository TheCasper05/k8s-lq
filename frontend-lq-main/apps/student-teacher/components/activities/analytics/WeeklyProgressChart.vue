<script setup lang="ts">
  import { LqCard } from "@lq/ui";
  import Chart from "primevue/chart";
  import Badge from "primevue/badge";
  import type { ChartConfig } from "~/types/activities";

  interface Props {
    chartData: ChartConfig;
    improvementPercentage?: string;
  }

  defineProps<Props>();

  const { t } = useI18n();
</script>

<template>
  <LqCard variant="default" padding="p-6" class="xl:col-span-2 flex flex-col gap-4">
    <div class="flex items-start justify-between gap-4">
      <div>
        <h3 class="text-base font-bold text-surface-900 dark:text-surface-0">
          {{ t("teacher.scenarios.detail.analytics.weeklyProgress.title") }}
        </h3>
        <p class="text-xs text-surface-500 dark:text-surface-400 mt-1">
          {{ t("teacher.scenarios.detail.analytics.weeklyProgress.description") }}
        </p>
      </div>
      <Badge
        v-if="improvementPercentage"
        :value="improvementPercentage"
        severity="success"
        size="large"
        class="!bg-emerald-50 !text-sm !text-emerald-500 !border-emerald-100 !h-10"
      >
        <template #default>
          <Icon name="solar:arrow-up-bold" class="text-base mr-1.5" />
          {{ improvementPercentage }}
        </template>
      </Badge>
    </div>
    <div class="mt-2 h-64">
      <Chart type="line" :data="chartData.data" :options="chartData.options" />
    </div>
  </LqCard>
</template>
