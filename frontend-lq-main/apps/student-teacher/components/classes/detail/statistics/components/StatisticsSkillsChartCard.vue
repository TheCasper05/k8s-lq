<script setup lang="ts">
  import { LqCard } from "@lq/ui";
  import type { SkillsChartData } from "~/composables/classes/types";
  import StatisticsSkillsChart from "./StatisticsSkillsChart.vue";
  import StatisticsSkillsLegend from "./StatisticsSkillsLegend.vue";

  interface Props {
    data: SkillsChartData;
    options: object;
  }

  defineProps<Props>();
</script>

<template>
  <LqCard variant="default" padding="p-4 md:p-6">
    <div class="flex items-center gap-2 mb-4">
      <Icon name="solar:target-line-duotone" class="text-info-500 dark:text-info-400 text-xl" />
      <h3 class="text-base font-semibold text-surface-900 dark:text-surface-50">
        {{ $t("classes.statistics.charts.skills") }}
      </h3>
    </div>

    <StatisticsSkillsChart :data="data" :options="options" />
    <StatisticsSkillsLegend />
  </LqCard>
</template>
