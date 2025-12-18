<script setup lang="ts">
  import { LqCard } from "@lq/ui";
  import Chart from "primevue/chart";
  import type { AssignmentsChartData } from "~/composables/classes/types";

  interface Props {
    data: AssignmentsChartData;
    options: object;
  }

  defineProps<Props>();
</script>

<template>
  <LqCard variant="default" padding="p-4 md:p-6">
    <div class="flex items-center gap-2 mb-4">
      <Icon name="solar:document-line-duotone" class="text-primary-500 dark:text-primary-400 text-xl" />
      <h3 class="text-base font-semibold text-surface-900 dark:text-surface-50">
        {{ $t("classes.statistics.charts.assignments") }}
      </h3>
    </div>
    <div class="h-64">
      <Chart type="bar" :data="data" :options="options" />
    </div>
  </LqCard>
</template>
