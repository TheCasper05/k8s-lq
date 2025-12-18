<script setup lang="ts">
  import { LqCard } from "@lq/ui";
  import Chart from "primevue/chart";
  import type { ChartConfig } from "~/types/activities";

  interface Props {
    chartData: ChartConfig;
  }

  defineProps<Props>();

  const { t } = useI18n();
</script>

<template>
  <LqCard variant="boxed" padding="p-6" class="xl:col-span-2 flex flex-col gap-4">
    <div>
      <h3 class="text-base font-bold text-surface-900 dark:text-surface-0">
        {{ t("teacher.scenarios.detail.analytics.scoreDistribution.title") }}
      </h3>
      <p class="text-xs text-surface-500 dark:text-surface-400 mt-1">
        {{ t("teacher.scenarios.detail.analytics.scoreDistribution.description") }}
      </p>
    </div>
    <div class="mt-2 h-64">
      <Chart type="bar" :data="chartData.data" :options="chartData.options" />
    </div>
  </LqCard>
</template>
