<script setup lang="ts">
  import { LqMetricCard, type LqMetric } from "@lq/ui";

  // Mock data for metrics - will be replaced with real data later
  const metrics: LqMetric[] = [
    {
      icon: "solar:document-text-line-duotone",
      label: "Activities Progress",
      value: "45/30",
      description: "150% completed",
      color: "primary",
    },
    {
      icon: "solar:clock-circle-line-duotone",
      label: "Total Practice Time",
      value: "127h 45m",
      description: "Across all students",
      color: "info",
    },
    {
      icon: "solar:users-group-rounded-line-duotone",
      label: "Active Students (30d)",
      value: "18/3",
      description: "600% active",
      color: "success",
    },
  ];
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-3 md:gap-4">
    <LqMetricCard v-for="(metric, index) in metrics" :key="index" :metric="metric" variant="boxed" />
  </div>
</template>
