<script setup lang="ts">
  import { computed } from "vue";
  import { LqMetricCard, type LqMetric } from "@lq/ui";
  import type { ActivityMetric } from "~/types/activities";

  interface Props {
    metric: ActivityMetric;
    variant?: "default" | "horizontal" | "boxed";
  }

  const props = withDefaults(defineProps<Props>(), {
    variant: "boxed",
  });

  // Convert ActivityMetric to LqMetric (reactive)
  const lqMetric = computed<LqMetric>(() => ({
    icon: props.metric.icon,
    label: props.metric.label,
    value: props.metric.value,
    color: props.metric.color,
    trend: props.metric.trend,
  }));
</script>

<template>
  <LqMetricCard :metric="lqMetric" :variant="variant" label-position="bottom" />
</template>
