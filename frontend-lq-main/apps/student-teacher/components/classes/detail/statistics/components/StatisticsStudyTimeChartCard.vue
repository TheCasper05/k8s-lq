<script setup lang="ts">
  import { LqCard } from "@lq/ui";
  import Chart from "primevue/chart";
  import type { StudyTimeChartData } from "~/composables/classes/types";

  interface Props {
    data: StudyTimeChartData;
    options: object;
  }

  defineProps<Props>();
</script>

<template>
  <LqCard variant="default" padding="p-6">
    <div class="flex items-center gap-2 mb-4">
      <Icon name="solar:clock-circle-line-duotone" class="text-warning-500 dark:text-warning-400 text-xl" />
      <h3 class="text-base font-semibold text-surface-900 dark:text-surface-50">
        {{ $t("classes.statistics.charts.studyTime") }}
      </h3>
    </div>
    <div class="h-64">
      <Chart type="line" :data="data" :options="options" />
    </div>
  </LqCard>
</template>
