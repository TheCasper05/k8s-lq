<script setup lang="ts">
  import Chart from "primevue/chart";
  import type { SkillsChartData } from "~/composables/classes/types";

  interface Props {
    data: SkillsChartData;
    options: object;
  }

  defineProps<Props>();
</script>

<template>
  <div class="h-64 flex items-center justify-center">
    <div class="w-full max-w-xs">
      <Chart type="doughnut" :data="data" :options="options" />
    </div>
  </div>
</template>
