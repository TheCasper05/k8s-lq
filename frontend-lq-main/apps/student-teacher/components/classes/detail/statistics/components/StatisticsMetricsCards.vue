<script setup lang="ts">
  import { type LqMetric, LqMetricCard } from "@lq/ui";

  interface Props {
    metrics: LqMetric[];
  }

  defineProps<Props>();
</script>

<template>
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
    <LqMetricCard
      v-for="(metric, index) in metrics"
      :key="index"
      :metric="metric"
      variant="boxed"
      label-position="bottom"
    />
  </div>
</template>
